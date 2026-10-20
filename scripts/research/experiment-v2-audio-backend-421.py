"""Compile the PE-derived Run 421 audio backend lock/pool bodies and run the native x86 fixture."""
import argparse
import hashlib
import importlib.util
import json
import os
import struct
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/421-audio-backend-lock-pool'
SRC_INCLUDE = ROOT / 'iterations/v2/001-original-recovery/source/include'
OUT = ROOT / 'local/experiments/v2-audio-backend-421'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

TARGETS = [
    ('0058e2d0', 0x0058e2d0, 12), ('0058e2e0', 0x0058e2e0, 12),
    ('0058e2f0', 0x0058e2f0, 12), ('0058e300', 0x0058e300, 12),
    ('005896d0', 0x005896d0, 18), ('005896f0', 0x005896f0, 17),
    ('0058aa90', 0x0058aa90, 44), ('0058aac0', 0x0058aac0, 31),
    ('0058fef0', 0x0058fef0, 31), ('0058ff10', 0x0058ff10, 50),
]
SCALARS = []
CASES = 30


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
    local = ROOT / 'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86/cl.exe'
    if local.exists():
        return local
    roots = [
        Path(r'C:\Program Files\Microsoft Visual Studio'),
        Path(r'C:\Program Files (x86)\Microsoft Visual Studio'),
    ]
    found = []
    for root in roots:
        if root.exists():
            found.extend(root.glob('*/*/VC/Tools/MSVC/*/bin/Hostx64/x86/cl.exe'))
            found.extend(root.glob('*/*/VC/Tools/MSVC/*/bin/Hostx86/x86/cl.exe'))
    assert found, 'No x86-target cl.exe found under the Visual Studio roots'
    return sorted(found)[-1]


def resolve_roots(compiler: Path):
    vc_dir = compiler.parents[3]
    sdk_root = Path(r'C:\Program Files (x86)\Windows Kits\10\Include')
    assert sdk_root.exists(), f'Windows SDK includes missing at {sdk_root}'
    sdk_include = sorted(p for p in sdk_root.iterdir() if (p / 'um').exists())[-1]
    roots = [
        vc_dir / 'include',
        sdk_include / 'ucrt',
        sdk_include / 'shared',
        sdk_include / 'um',
        RUN,
        SRC_INCLUDE,
    ]
    for r in roots:
        assert r.exists(), f'Include root missing at {r}'
    return roots


def resolve_sdk_lib(sdk_include: Path):
    lib = sdk_include.parent.parent / 'Lib' / sdk_include.name / 'um' / 'x86'
    assert lib.exists(), f'Windows SDK x86 libs missing at {lib}'
    return lib


def pe_text_bytes(image: bytes, va: int, size: int) -> bytes:
    """Read `size` bytes at `va`, resolving through the PE section table."""
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    sections = struct.unpack_from('<H', image, pe + 6)[0]
    opt = struct.unpack_from('<H', image, pe + 20)[0]
    base = struct.unpack_from('<I', image, pe + 24 + 28)[0]
    off = pe + 24 + opt
    rva = va - base
    for _ in range(sections):
        vsize, vaddr, rsize, raw = struct.unpack_from('<IIII', image, off + 8)
        if vaddr <= rva < vaddr + max(vsize, rsize):
            start = raw + (rva - vaddr)
            return image[start:start + size]
        off += 40
    raise AssertionError(f'VA {va:08x} not inside any section')


def main(finalize: bool, attempt: int):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'objects').mkdir(exist_ok=True)
    (OUT / 'dependencies').mkdir(exist_ok=True)

    gen = module('gen421', ROOT / 'scripts/research/gen_run_421.py')
    gen.main()

    suffix = f'{attempt:03d}'
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
            timeout=180,
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
    image = original.read_bytes()

    # Evidence pinned straight out of the retail image, before any build runs.
    bodies = []
    for name, va, size in TARGETS:
        body = pe_text_bytes(image, va, size)
        assert len(body) == size, (name, len(body))
        # a body ends on RET, or on a tail JMP rel32 (005896f0 jumps to 0058e300)
        assert body[-1] == 0xc3 or body[-5] == 0xe9, f'{name} does not end on RET or JMP rel32'
        bodies.append(dict(va=name, bytes=size, body_sha256=hashlib.sha256(body).hexdigest()))

    scalars = []
    for name, va, expected in SCALARS:
        raw = pe_text_bytes(image, va, 4)
        value = struct.unpack('<f', raw)[0]
        assert value == expected, (name, value, expected)
        scalars.append(dict(va=name, raw=raw.hex(), float_value=value))

    compiler = pin(resolve_compiler())
    roots = resolve_roots(compiler)
    sdk_lib = resolve_sdk_lib(roots[1].parent)

    provenance = module('audio_provenance', ROOT / 'scripts/research/audio_recovery_provenance.py')
    for path in (Path(__file__), ROOT / 'scripts/research/gen_run_421.py', ROOT / 'scripts/research/build-v2-compile-corpus.py', ROOT / 'scripts/research/audio_recovery_provenance.py'):
        pin(path)
    for path in (compiler.parent / 'c1xx.dll', compiler.parent / 'c2.dll', compiler.parent / 'link.exe', sdk_lib / 'kernel32.Lib', sdk_lib / 'user32.Lib'):
        pin(path)
    for path in SRC_INCLUDE.rglob('*'):
        if path.is_file():
            pin(path)

    source = pin(RUN / 'audio_backend_lock_pool_421.cpp')
    header = pin(RUN / 'audio_backend_lock_pool_421.hpp')
    fixture = pin(OUT / 'audio_backend_fixture.cpp')

    prepare = dict(
        command=[str(compiler)],
        input_sha256={rel(p): h for p, h in sorted(pins.items(), key=lambda x: str(x[0]))},
        roots=list(map(rel, roots)),
        targets=[dict(va=v, bytes=b) for v, _, b in TARGETS],
        original_bodies=bodies,
        original_scalars=scalars,
    )
    prepare_path = OUT / ('prepare-' + suffix + '.json')
    write(prepare_path, prepare)
    pin(prepare_path)

    obj = OUT / 'objects' / 'audio_backend_lock_pool_421.obj'
    fixture_obj = OUT / 'objects' / 'audio_backend_fixture.obj'
    includes = []
    for r in roots:
        includes.extend(['/I', str(r)])

    compile_cmd = [
        str(compiler), '/nologo', '/c', '/std:c++17',
        '/Od', '/Oi', '/Gy', '/GS-', '/GR-', '/EHsc', '/TP', '/W4',
        '/utf-8', '/diagnostics:column', '/MP2', '/Zl',
        '/sourceDependencies', str(OUT / 'dependencies'),
    ] + includes + [
        f'/Fo{OUT / "objects"}\\',
        str(source),
        str(fixture),
    ]

    # Discover actual system-header closure, then pin it before the authoritative
    # compile. The probe is not the accepted object/native result.
    guard()
    probe = run(compile_cmd, 'dependency-probe-' + suffix)
    assert probe['exit_code'] == 0, 'dependency probe failed'
    dependency_inputs = provenance.dependency_paths(OUT)
    for path in dependency_inputs:
        pin(path)
    guard()
    compiled = run(compile_cmd, 'compile-' + suffix)
    assert compiled['exit_code'] == 0, (OUT / ('compile-' + suffix + '.log')).read_text()

    guard()
    assert provenance.dependency_paths(OUT) == dependency_inputs, 'dependency closure changed'
    pin(obj)
    pin(fixture_obj)

    linker = compiler.parent / 'link.exe'
    exe = OUT / 'native-fixture.exe'
    map_file = OUT / 'native-fixture.map'
    link_cmd = [
        str(linker), '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE',
        '/ENTRY:entry', '/NODEFAULTLIB', '/INCREMENTAL:NO',
        '/SECTION:.data,ERW', '/SECTION:.bss,ERW',
        f'/MAP:{map_file}', f'/OUT:{exe}',
        str(obj), str(fixture_obj),
        str(sdk_lib / 'kernel32.Lib'), str(sdk_lib / 'user32.Lib'),
    ]

    guard()
    linked = run(link_cmd, 'fixture-link-' + suffix)
    assert linked['exit_code'] == 0, (OUT / ('fixture-link-' + suffix + '.log')).read_text()
    guard()
    pin(exe)
    pin(map_file)

    guard()
    executed = run([str(exe)], 'fixture-native-' + suffix)
    native_log = (OUT / ('fixture-native-' + suffix + '.log')).read_text()
    assert executed['exit_code'] == 0, native_log
    guard()
    passed = native_log.count(' OK')
    assert passed == CASES, native_log

    coff = module('coff421', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    view = coff.coff_symbols(obj)

    # Persist the checked manifest separately so tracked summaries remain small.
    provenance_path = OUT / ('provenance-' + suffix + '.json')
    outputs = [obj, fixture_obj, exe, map_file]
    outputs += list((OUT / 'dependencies').glob('*.json'))
    for prefix in ('dependency-probe-', 'compile-', 'fixture-link-', 'fixture-native-'):
        outputs.extend([OUT / (prefix + suffix + '.execution.json'), OUT / (prefix + suffix + '.log')])
    write(provenance_path, dict(
        input_sha256={rel(p): h for p, h in sorted(pins.items(), key=lambda x: str(x[0]))},
        output_sha256={rel(p): sha(p) for p in outputs},
        dependency_input_paths=sorted(map(str, dependency_inputs)),
        source_file=source.name, header_file=header.name, fixture_file=fixture.name,
        object_file=obj.name,
        guards_before_and_after_compile_link_native=True,
    ))
    guard()

    summary = dict(
        provenance=rel(provenance_path),
        provenance_sha256=sha(provenance_path),
        schema=1,
        run='421-audio-backend-lock-pool',
        original_sha256=sha(ROOT / 'local/game/Porsche.exe'),
        original_vas=[v for v, _, _ in TARGETS],
        original_selected_bytes=sum(b for _, _, b in TARGETS),
        original_bodies=bodies,
        original_scalars=scalars,
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
            cases=CASES,
            cases_passed=passed,
            execution=executed,
        ),
    )

    validation = dict(
        status='PASS',
        run='421-audio-backend-lock-pool',
        functions=len(TARGETS),
        pe_bytes=sum(b for _, _, b in TARGETS),
        cases_passed=passed,
        cases_total=CASES,
    )

    if finalize:
        write(RUN / 'summary.json', summary)
        write(RUN / 'validation.json', validation)
        print(f'Wrote final summary.json and validation.json ({passed}/{CASES} cases)')
    else:
        write(OUT / 'summary.json', summary)
        write(OUT / 'validation.json', validation)
        print(f'Wrote draft summary.json and validation.json ({passed}/{CASES} cases)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize', action='store_true')
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    main(args.finalize, args.attempt)
