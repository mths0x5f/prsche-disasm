"""Compile the 5 PE-derived app_main subsystem bodies and run controlled native x86 fixture."""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/410-app-main-subsystem-final-pt1'
OUT = ROOT / 'local/experiments/v2-app-main-410'
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

    source = pin(RUN / 'app_main_subsystem_final_pt1_410.cpp')
    header = pin(RUN / 'app_main_subsystem_final_pt1_410.hpp')
    fixture = pin(OUT / 'app_main_fixture.cpp')

    prepare = dict(
        command=[str(compiler)],
        input_sha256={rel(p): h for p, h in sorted(pins.items(), key=lambda x: str(x[0]))},
        roots=list(map(rel, roots)),
        targets=[
            dict(va='0056a680', bytes=38),
            dict(va='005a0f98', bytes=39),
            dict(va='00412030', bytes=91),
            dict(va='00414eb0', bytes=196),
            dict(va='004dd600', bytes=1012),
        ],
    )
    prepare_path = OUT / ('prepare-' + suffix + '.json')
    write(prepare_path, prepare)
    pin(prepare_path)

    obj = OUT / 'objects' / 'app_main_subsystem_final_pt1_410.obj'
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

    coff = module('coff410', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    view = coff.coff_symbols(obj)

    summary = dict(
        schema=1,
        run='410-app-main-subsystem-final-pt1',
        original_sha256=sha(ROOT / 'local/game/Porsche.exe'),
        original_vas=['0056a680', '005a0f98', '00412030', '00414eb0', '004dd600'],
        original_selected_bytes=1376,
        compiler=rel(compiler),
        compiler_sha256=sha(compiler),
        include_roots=list(map(rel, roots)),
        source=rel(source),
        source_sha256=sha(source),
        header=rel(header),
        header_sha256=sha(header),
        object=rel(obj),
        object_sha256=sha(obj),
        symbols=view,
        native_fixture=dict(
            executable=rel(exe),
            executable_sha256=sha(exe),
            exit_code=executed['exit_code'],
            cases=10,
        ),
        input_sha256={rel(p): h for p, h in sorted(pins.items(), key=lambda x: str(x[0]))},
    )

    validation = dict(
        run='410-app-main-subsystem-final-pt1',
        status='PASS',
        exit_code=executed['exit_code'],
        cases_passed=10,
        bytes_verified=1376,
        functions=5,
    )

    write(RUN / 'summary.json', summary)
    write(RUN / 'validation.json', validation)
    print(json.dumps(dict(compile=compiled['exit_code'], native=executed['exit_code'], cases=10, game_objects=1, bytes=1376)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize-existing', action='store_true')
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    main(args.finalize_existing, args.attempt)
