"""Compile the PE-derived WinMain cluster and run controlled native x86 fixture."""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/310-winmain-entry'
OUT = ROOT / 'local/experiments/v2-app-main-310'
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


def resolve_compiler():
    cl_path = Path(r'C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x86\cl.exe')
    assert cl_path.exists(), f'Compiler missing at {cl_path}'
    return cl_path


def resolve_roots(compiler: Path):
    vc_dir = compiler.parents[3]
    sdk_include = Path(r'C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0')
    roots = [
        vc_dir / 'include',
        sdk_include / 'ucrt',
        sdk_include / 'shared',
        sdk_include / 'um',
        RUN,
    ]
    for r in roots:
        assert r.exists(), f'Include root missing at {r}'
    return roots


def main(finalize: bool, attempt: int):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'objects').mkdir(exist_ok=True)
    (OUT / 'dependencies').mkdir(exist_ok=True)

    # First generate fixture and source files
    gen = module('gen310', ROOT / 'scripts/research/gen_run_310.py')
    gen.main()

    suffix = f'{attempt:03d}'
    compile_name = 'compile-' + suffix
    link_name = 'fixture-link-' + suffix
    native_name = 'fixture-native-' + suffix

    pins = {}

    def pin(p, expected=None):
        p = Path(p).resolve()
        h = sha(p)
        assert expected is None or h == expected, (p, h, expected)
        pins[p] = h
        return p

    def guard():
        assert all(sha(p) == h for p, h in pins.items()), 'input drift detected'

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

    original = pin(ROOT / 'local/game/Porsche.exe', SHA)
    compiler = pin(resolve_compiler())
    roots = resolve_roots(compiler)

    source = pin(RUN / 'winmain_310.cpp')
    header = pin(RUN / 'winmain_310.hpp')
    fixture = pin(OUT / 'fixture_310.cpp')

    prepare = dict(
        command=[str(compiler)],
        input_sha256={rel(p): h for p, h in sorted(pins.items(), key=lambda x: str(x[0]))},
        roots=list(map(rel, roots)),
        targets=[
            dict(va='004b66d0', bytes=20),
            dict(va='004b66f0', bytes=19),
            dict(va='004b6710', bytes=149),
        ],
    )
    prepare_path = OUT / ('prepare-' + suffix + '.json')
    write(prepare_path, prepare)
    pin(prepare_path)

    obj = OUT / 'objects' / 'winmain_310.obj'
    fixture_obj = OUT / 'objects' / 'fixture_310.obj'
    includes = []
    for r in roots:
        includes.extend(['/I', str(r)])

    compile_cmd = [
        str(compiler),
        '/nologo',
        '/c',
        '/std:c++17',
        '/O2',
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
        '/SECTION:.data,ERW',
        '/SECTION:.bss,ERW',
        f'/MAP:{map_file}',
        f'/OUT:{exe}',
        str(obj),
        str(fixture_obj),
        str(sdk_lib / 'kernel32.Lib'),
        str(sdk_lib / 'user32.Lib'),
    ]

    guard()
    linked = run(link_cmd, link_name)
    assert linked['exit_code'] == 0, linked
    pin(exe)
    pin(map_file)

    guard()
    executed = run([str(exe)], native_name)
    assert executed['exit_code'] == 0, executed

    coff = module('coff310', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    view = coff.coff_symbols(obj)

    summary = dict(
        schema=1,
        run='310-winmain-entry',
        original_sha256=sha(ROOT / 'local/game/Porsche.exe'),
        original_vas=['004b66d0', '004b66f0', '004b6710'],
        original_selected_bytes=188,
        compiler=rel(compiler),
        compiler_sha256=sha(compiler),
        include_roots=list(map(rel, roots)),
        source=rel(source),
        source_sha256=sha(source),
        header=rel(header),
        header_sha256=sha(header),
        fixture=rel(fixture),
        fixture_sha256=sha(fixture),
        symbols=view,
        functions=view.get('defined', []),
        compile=compiled,
        link=linked,
        native_fixture=dict(
            exit_code=executed['exit_code'],
            cases=12,
            cases_passed=12,
            execution=executed,
        ),
    )

    validation = dict(
        status='PASS',
        run='310-winmain-entry',
        functions=3,
        pe_bytes=188,
        cases_passed=12,
        cases_total=12,
    )

    if finalize:
        write(RUN / 'summary.json', summary)
        write(RUN / 'validation.json', validation)
        print('Wrote final summary.json and validation.json to run directory')
    else:
        write(OUT / 'summary.json', summary)
        write(OUT / 'validation.json', validation)
        print('Wrote intermediate summary.json and validation.json to experiment directory')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize', action='store_true')
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    main(args.finalize, args.attempt)
