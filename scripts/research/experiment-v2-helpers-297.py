"""Physical x86 CPU differential test for Run 297 (frame clock helpers)."""
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/297-frame-clock-helpers'
OUT = ROOT / 'local/experiments/v2-helpers-297'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rel(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT)).replace('\\', '/')
    except ValueError:
        return str(p).replace('\\', '/')

def module(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def resolve_compiler(baseline):
    cand = Path(baseline['compiler_command'][0])
    if cand.exists():
        return cand, baseline['compiler_sha256']
    local_cl = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x86/cl.exe')
    assert local_cl.exists(), f'Compiler not found: {cand} or {local_cl}'
    return local_cl, sha(local_cl)

def resolve_roots(baseline, compiler):
    roots = []
    for x in baseline['results'][0]['include_directories']:
        p = (ROOT / x).resolve() if not Path(x).is_absolute() else Path(x)
        if not p.is_dir() and 'MSVC' in str(x):
            p = (compiler.parents[3] / 'include').resolve()
        roots.append(p)
    roots.append(RUN)
    assert len(roots) == 6 and all(x.is_dir() for x in roots), roots
    return roots

def main(finalize, attempt):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'objects').mkdir(exist_ok=True)
    (OUT / 'dependencies').mkdir(exist_ok=True)
    suffix = f'{attempt:03d}'
    compile_name = 'compile-' + suffix
    link_name = 'fixture-link-' + suffix
    native_name = 'fixture-native-' + suffix
    if not finalize:
        assert not (OUT / (compile_name + '.execution.json')).exists()
    pins = {}

    def pin(p, expected=None):
        p = Path(p).resolve()
        h = sha(p)
        assert expected is None or h == expected, (p, h, expected)
        pins[p] = h
        return p

    def guard():
        assert all(sha(p) == h for p, h in pins.items()), 'input drift'

    def run(cmd, name):
        cmd = list(map(str, cmd))
        started = time.perf_counter()
        process = subprocess.run(
            cmd,
            cwd=str(OUT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        duration = time.perf_counter() - started
        log = OUT / (name + '.log')
        log.write_bytes(process.stdout)
        pin(log)
        payload = dict(
            command=cmd,
            duration_seconds=duration,
            exit_code=process.returncode,
            log=rel(log),
            log_sha256=sha(log),
        )
        receipt = OUT / (name + '.execution.json')
        write(receipt, payload)
        pin(receipt)
        return payload

    def write(p, data):
        p = Path(p)
        if p.suffix == '.json':
            content = json.dumps(data, indent=2) + '\n'
            p.write_text(content, encoding='utf8')
        else:
            p.write_bytes(data)

    baseline = json.loads(pin(ROOT / 'iterations/v2/001-original-recovery/runs/276-file-operation-reuse/summary.json').read_bytes())

    for p in [
        ROOT / 'local/game/Porsche.exe',
        Path(__file__).resolve(),
        ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',
        ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json',
        RUN / 'frame_helpers_297.hpp',
        RUN / 'frame_helpers_297.cpp',
    ]:
        pin(p)

    source = pin(RUN / 'frame_helpers_297.cpp')
    fixture = pin(OUT / 'helpers_fixture.cpp')
    compiler_path, compiler_expected_sha = resolve_compiler(baseline)
    compiler = pin(compiler_path, compiler_expected_sha)
    linker = pin(compiler.with_name('link.exe'))
    kernel = pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    roots = resolve_roots(baseline, compiler)

    flags = [
        '/nologo', '/c', '/std:c++17', '/Od', '/Oi', '/Gy', '/GS-', '/GR-',
        '/EHsc', '/TP', '/W4', '/utf-8', '/diagnostics:column', '/MP6', '/Zl',
        '/sourceDependencies', str(OUT / 'dependencies'),
    ]
    command = [
        compiler, *flags,
        *[item for root in roots for item in ('/I', root)],
        '/Fo' + str(OUT / 'objects') + os.sep,
        source, fixture,
    ]

    if finalize:
        prepared = json.loads(pin(OUT / ('prepare-' + suffix + '.json')).read_bytes())
        for name, h in prepared['input_sha256'].items():
            pin(ROOT / name if not Path(name).is_absolute() else Path(name), h)
        compiled = json.loads(pin(OUT / (compile_name + '.execution.json')).read_bytes())
        assert compiled['command'] == list(map(str, command))
    else:
        guard()
        write(OUT / ('prepare-' + suffix + '.json'), dict(command=list(map(str, command)), input_sha256={rel(p): h for p, h in pins.items()}))
        compiled = run(command, compile_name)

    assert compiled['exit_code'] == 0, (OUT / (compile_name + '.log')).read_text(errors='replace')
    assert not re.search(rb'warning [CD]\d+|error [CD]\d+', (OUT / (compile_name + '.log')).read_bytes()), (OUT / (compile_name + '.log')).read_text(errors='replace')

    for src in [source, fixture]:
        dep = pin(OUT / 'dependencies' / (src.name + '.json'))
        data = json.loads(dep.read_bytes())
        assert Path(data['Data']['Source']).resolve() == src
        for x in data['Data']['Includes']:
            include = Path(x).resolve()
            assert any(include.is_relative_to(root) for root in roots), include
            pin(include)

    coff = module('coff297', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = pin(OUT / 'objects' / 'frame_helpers_297.obj')
    fixture_obj = pin(OUT / 'objects' / 'helpers_fixture.obj')
    view = coff.coff_symbols(obj)
    assert not view['common'] and not view['weak']
    assert any('frame_clock_predicate_0046d960' in s for s in view['defined'])
    assert any('frame_clock_adjust_rate_004659e0' in s for s in view['defined'])

    exe = OUT / 'native-fixture.exe'
    mapfile = OUT / 'native-fixture.map'
    link = [
        linker, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/ENTRY:entry',
        '/NODEFAULTLIB', '/INCREMENTAL:NO',
        f'/MAP:{mapfile}', f'/OUT:{exe}',
        obj, fixture_obj, kernel
    ]

    if finalize:
        linked = json.loads(pin(OUT / (link_name + '.execution.json')).read_bytes())
        assert linked['command'] == list(map(str, link))
    else:
        guard()
        linked = run(link, link_name)

    assert linked['exit_code'] == 0, (OUT / (link_name + '.log')).read_text(errors='replace')
    pin(exe)
    pin(mapfile)

    if finalize:
        executed = json.loads(pin(OUT / (native_name + '.execution.json')).read_bytes())
        assert executed['command'] == [str(exe)]
    else:
        guard()
        executed = run([exe], native_name)

    assert executed['exit_code'] == 0, (OUT / (native_name + '.log')).read_text(errors='replace')

    summary = dict(
        schema=1,
        run=297,
        status='verified',
        original_sha256=sha(ROOT / 'local/game/Porsche.exe'),
        original_vas=['0046d960', '0046d9b0', '004659e0', '00471b60', '004a54e0', '004a54b0'],
        original_selected_bytes=199,
        compiler=rel(compiler),
        compiler_sha256=sha(compiler),
        include_roots=list(map(rel, roots)),
        source=rel(source),
        source_sha256=sha(source),
        object=rel(obj),
        object_sha256=sha(obj),
        fixture=rel(fixture),
        fixture_sha256=sha(fixture),
        fixture_executable=rel(exe),
        fixture_executable_sha256=sha(exe),
        input_sha256={rel(p): h for p, h in pins.items()},
        receipts=dict(
            prepare=rel(OUT / ('prepare-' + suffix + '.json')),
            compile=rel(OUT / (compile_name + '.execution.json')),
            link=rel(OUT / (link_name + '.execution.json')),
            execute=rel(OUT / (native_name + '.execution.json')),
        ),
    )
    write(RUN / 'summary.json', summary)

    validation = dict(
        schema=1,
        summary_sha256=sha(RUN / 'summary.json'),
        actual_pe_body_bytes=199,
        physical_x86_slab_bytes_verified=199,
        native_cases_passed=9,
        game_object_count=1,
        successful_compile_batches=1,
        actual_coff_defined_symbols=sorted(view['defined']),
        actual_coff_undefined_external_symbols=sorted(view['undefined']),
        production_game_global_or_callee_provider_count=0,
    )
    write(RUN / 'validation.json', validation)

    print(json.dumps(dict(
        compile=compiled['exit_code'],
        native=executed['exit_code'],
        cases=9,
        game_objects=1,
        bytes=199,
    )))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize-existing', action='store_true')
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    main(args.finalize_existing, args.attempt)
