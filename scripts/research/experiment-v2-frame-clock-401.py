"""Compile 00413ea0 and run physical x86 CPU differential fixture for Run 401."""
import argparse, hashlib, importlib.util, json, os, re, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/401-frame-clock-dispatch'
OUT = ROOT / 'local/experiments/v2-frame-clock-401'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rel(p):
    p = Path(p).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()

def write(p, v):
    p.write_bytes((json.dumps(v, indent=2, ensure_ascii=False) + '\n').encode('utf8'))

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
            cwd=OUT,
            env={**os.environ, 'VSLANG': '1033', 'CL': '', '_CL_': '', 'INCLUDE': ''},
            capture_output=True,
            timeout=120,
        )
        log = OUT / (name + '.log')
        log.write_bytes((process.stdout + process.stderr).replace(b'\r\n', b'\n'))
        receipt = dict(
            command=cmd,
            exit_code=process.returncode,
            seconds=round(time.perf_counter() - started, 6),
            log=rel(log),
            log_sha256=sha(log),
        )
        write(OUT / (name + '.execution.json'), receipt)
        return receipt

    baseline = json.loads(pin(ROOT / 'iterations/v2/001-original-recovery/runs/276-file-operation-reuse/summary.json').read_bytes())
    original = pin(ROOT / 'local/game/Porsche.exe', SHA)
    for p in [
        __file__,
        ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',
        ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json',
        RUN / 'frame_clock_401.hpp',
        RUN / '00413ea0.cpp',
    ]:
        pin(p)

    registry = json.loads((ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    assert all(x['entry_va'] != '00413ea0' for x in registry)

    index = {x['entry_va']: x['body_bytes'] for x in map(json.loads, (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
    assert index['00413ea0'] == 296

    source = pin(RUN / '00413ea0.cpp')
    fixture = pin(OUT / 'frame_clock_fixture.cpp')
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

    coff = module('coff401', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = pin(OUT / 'objects' / '00413ea0.obj')
    fixture_obj = pin(OUT / 'objects' / 'frame_clock_fixture.obj')
    view = coff.coff_symbols(obj)
    assert not view['common'] and not view['weak']
    assert any('application_main_function_00413ea0' in s for s in view['defined'])

    exe = OUT / 'native-fixture.exe'
    mapfile = OUT / 'native-fixture.map'
    link = [
        linker, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/ENTRY:entry',
        '/NODEFAULTLIB', '/INCREMENTAL:NO', '/OPT:NOREF',
        '/OUT:' + str(exe), '/MAP:' + str(mapfile),
        obj, fixture_obj, kernel,
    ]
    if finalize and (OUT / (link_name + '.execution.json')).exists():
        linked = json.loads(pin(OUT / (link_name + '.execution.json')).read_bytes())
    else:
        linked = run(link, link_name)
    assert linked['exit_code'] == 0, (OUT / (link_name + '.log')).read_text(errors='replace')

    if finalize and (OUT / (native_name + '.execution.json')).exists():
        native = json.loads(pin(OUT / (native_name + '.execution.json')).read_bytes())
    else:
        native = run([exe], native_name)
    assert native['exit_code'] == 0, (OUT / (native_name + '.log')).read_text(errors='replace')

    for p in [exe, mapfile, *OUT.glob('*.log'), *OUT.glob('*.execution.json')]:
        pin(p)
    guard()

    result = dict(
        va='00413ea0',
        body_bytes=296,
        generated_source=rel(source),
        generated_source_sha256=sha(source),
        object=rel(obj),
        object_sha256=sha(obj),
        symbols=view,
        compiler_command=list(map(str, command)),
        compiler_execution_receipt=rel(OUT / (compile_name + '.execution.json')),
        include_directories=[rel(x) for x in roots],
        source_dependencies=rel(OUT / 'dependencies' / (source.name + '.json')),
        source_dependencies_sha256=sha(OUT / 'dependencies' / (source.name + '.json')),
        compiled=True,
        compiler_exit_code=0,
        actual_i386_coff_validated=True,
    )

    summary = dict(
        schema=1,
        kind='original-frame-clock-dispatch',
        module='Porsche.exe',
        original_sha256=SHA,
        original_vas=['00413ea0'],
        original_selected_bytes=296,
        new_distinct_function_VAs=1,
        objects_compiled=1,
        real_coff_objects=1,
        results=[result],
        game_objects=[dict(path=rel(obj), sha256=sha(obj))],
        compiler_sha256=sha(compiler),
        compiler_batch_exit_code=0,
        actual_compiler_batches=attempt,
        actual_MP6_requested=True,
        compile_seconds=compiled['seconds'],
        compiler_command=list(map(str, command)),
        compiler_execution_receipt=rel(OUT / (compile_name + '.execution.json')),
        native_fixture=dict(
            executable=rel(exe),
            sha256=sha(exe),
            exit_code=native['exit_code'],
            seconds=native['seconds'],
            case_count=7,
        ),
        sourceDependencies_format='MSVC1.2',
        input_sha256={rel(p): h for p, h in pins.items()},
        input_guards_before=True,
        input_guards_after=True,
        production_ready=False,
        limits=[
            'External callees 0046d960, 0046d890, 00413960, 004659e0 remain explicit boundaries',
            'Fixture providers and executable slab are excluded from game_objects',
        ],
    )
    write(RUN / 'summary.json', summary)
    print(json.dumps(dict(compile=compiled['exit_code'], native=native['exit_code'], cases=7, game_objects=1, bytes=296)))

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--finalize-existing', action='store_true')
    a.add_argument('--attempt', type=int, default=1)
    args = a.parse_args()
    main(args.finalize_existing, args.attempt)
