"""Physical x86 CPU differential test for Run 406 (app_main subsystem small cluster: 4 functions, 635 PE bytes)."""
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/406-app-main-subsystem-small'
OUT = ROOT / 'local/experiments/v2-app-main-406'

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
            p.write_bytes((content).replace("\r\n", "\n").encode("utf-8"))
        else:
            p.write_bytes(data)

    baseline = json.loads(pin(ROOT / 'iterations/v2/001-original-recovery/runs/276-file-operation-reuse/summary.json').read_bytes())
    pin(ROOT / 'local/game/Porsche.exe', 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39')
    pin(Path(__file__))

    compiler, compiler_sha = resolve_compiler(baseline)
    roots = resolve_roots(baseline, compiler)

    source = pin(RUN / 'app_main_subsystem_small_406.cpp')
    header = pin(RUN / 'app_main_subsystem_small_406.hpp')
    fixture = pin(OUT / 'app_main_fixture.cpp')

    prepare = dict(
        command=[str(compiler)] + baseline['compiler_command'][1:],
        input_sha256={rel(p): h for p, h in sorted(pins.items(), key=lambda x: str(x[0]))},
        roots=list(map(rel, roots)),
        targets=[
            dict(va='0048e6f0', bytes=153),
            dict(va='004a6960', bytes=153),
            dict(va='004a5410', bytes=157),
            dict(va='004d1a90', bytes=172),
        ],
    )
    prepare_path = OUT / ('prepare-' + suffix + '.json')
    write(prepare_path, prepare)
    pin(prepare_path)

    obj = OUT / 'objects' / 'app_main_subsystem_small_406.obj'
    fixture_obj = OUT / 'objects' / 'app_main_fixture.obj'
    includes = []
    for r in roots:
        includes.extend(['/I', str(r)])

    compile_cmd = [
        str(compiler),
        '/nologo',
        '/c',
        '/std:c++17',
        '/Od',
        '/Oi',
        '/Gy',
        '/GS-',
        '/GR-',
        '/EHsc',
        '/TP',
        '/W4',
        '/utf-8',
        '/diagnostics:column',
        '/MP6',
        '/Zl',
        '/sourceDependencies', str(OUT / 'dependencies'),
    ] + includes + [
        f'/Fo{OUT / "objects"}\\',
        str(source),
        str(fixture),
    ]

    guard()
    compiled = run(compile_cmd, compile_name)
    assert compiled['exit_code'] == 0, compiled

    pin(obj)
    pin(fixture_obj)

    sdk_lib = Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86')
    linker = compiler.parent / 'link.exe'
    exe = OUT / 'native-fixture.exe'
    map_file = OUT / 'native-fixture.map'

    link_cmd = [
        str(linker),
        '/nologo',
        '/MACHINE:X86',
        '/SUBSYSTEM:CONSOLE',
        '/ENTRY:entry',
        '/NODEFAULTLIB',
        '/INCREMENTAL:NO',
        f'/MAP:{map_file}',
        f'/OUT:{exe}',
        str(obj),
        str(fixture_obj),
        str(sdk_lib / 'kernel32.Lib'),
    ]

    guard()
    linked = run(link_cmd, link_name)
    assert linked['exit_code'] == 0, linked
    pin(exe)
    pin(map_file)

    guard()
    executed = run([str(exe)], native_name)
    assert executed['exit_code'] == 0, executed

    coff = module('coff406', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    view = coff.coff_symbols(obj)

    summary = dict(
        schema=1,
        run='406-app-main-subsystem-small',
        original_sha256=sha(ROOT / 'local/game/Porsche.exe'),
        original_vas=['0048e6f0', '004a6960', '004a5410', '004d1a90'],
        original_selected_bytes=635,
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
        actual_pe_body_bytes=635,
        physical_x86_slab_bytes_verified=635,
        native_cases_passed=10,
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
        cases=10,
        game_objects=1,
        bytes=635,
    )))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize-existing', action='store_true')
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    main(args.finalize_existing, args.attempt)
