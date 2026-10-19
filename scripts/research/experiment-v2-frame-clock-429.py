"""Run 429: differential test of the corrected 00413ea0 against the original bytes.

Generates the fixture from the versioned template: the 296 original bytes and
every absolute/rel32 operand site are taken from the PE at run time (capstone).
The corrected source must pass all 9 cases. The uncorrected Run 401 source must
fail, which shows that the count-mutation cases detect the cached count.

Usage: py -3 scripts/research/experiment-v2-frame-clock-429.py
"""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / 'iterations/v2/001-original-recovery'
RUN = V2 / 'runs/429-unified-game-integration'
OUT = ROOT / 'local/experiments/v2-frame-clock-429'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VA, SIZE = 0x00413ea0, 296
TARGETS = {0x005e99f4, 0x005e99f8, 0x005e99fc, 0x005e9a00, 0x005e9a04, 0x00606850, 0x00606854, 0x00606858,
           0x00606860, 0x00606864, 0x00606868, 0x0060686c, 0x00606870, 0x005ed848, 0x006573e8, 0x0065741c,
           0x005e8bfc, 0x005e8c00, 0x0046d960, 0x0046d890, 0x00413960, 0x004659e0}


def original_body():
    d = (ROOT / 'local/game/Porsche.exe').read_bytes()
    assert hashlib.sha256(d).hexdigest() == PE_SHA
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    opt = struct.unpack_from('<H', d, pe + 20)[0]
    base = struct.unpack_from('<I', d, pe + 52)[0]
    off = pe + 24 + opt
    for k in range(struct.unpack_from('<H', d, pe + 6)[0]):
        vsz, va, rsz, raw = struct.unpack_from('<IIII', d, off + 40 * k + 8)
        rva = VA - base
        if va <= rva < va + rsz:
            return d[raw + rva - va:raw + rva - va + SIZE]
    raise AssertionError('body not in a section')


def operand_sites(body):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    sites = []
    covered = 0
    for ins in md.disasm(body, VA):
        covered += ins.size
        if ins.mnemonic == 'call' and ins.bytes[0] == 0xe8:
            target = ins.operands[0].imm
            assert target in TARGETS, f'unexpected call target {target:08x}'
            sites.append((ins.address - VA + 1, 1, target))
            continue
        for slot in (ins.disp_offset, ins.imm_offset):
            if slot:
                v = struct.unpack_from('<I', ins.bytes, slot)[0] if slot + 4 <= ins.size else None
                if v in TARGETS:
                    sites.append((ins.address - VA + slot, 0, v))
    assert covered == SIZE, 'body does not decode to its full size'
    return sorted(set(sites))


def toolchain():
    roots = [Path(r'C:\Program Files\Microsoft Visual Studio'), Path(r'C:\Program Files (x86)\Microsoft Visual Studio')]
    cl = sorted(c for r in roots if r.exists() for c in r.glob('*/*/VC/Tools/MSVC/*/bin/Hostx64/x86/cl.exe'))[-1]
    sdk_inc = sorted(p for p in Path(r'C:\Program Files (x86)\Windows Kits\10\Include').iterdir() if (p / 'um').exists())[-1]
    sdk_lib = sdk_inc.parent.parent / 'Lib' / sdk_inc.name / 'um' / 'x86'
    vc = cl.parents[3]
    return cl, cl.parent / 'link.exe', [vc / 'include', sdk_inc / 'ucrt', sdk_inc / 'shared', sdk_inc / 'um'], sdk_lib


def build_and_run(source, tag, fixture, cl, link, includes, sdk_lib):
    objs = OUT / f'objects-{tag}'
    objs.mkdir(parents=True, exist_ok=True)
    inc = [f'/I{p}' for p in includes + [V2 / 'source/include', V2 / 'runs/401-frame-clock-dispatch']]
    cmd = [cl, '/nologo', '/c', '/std:c++17', '/Od', '/Oi', '/Gy', '/GS-', '/GR-', '/EHsc', '/TP', '/W4', '/Zl',
           *inc, f'/Fo{objs}\\', source, fixture]
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, cwd=OUT)
    (OUT / f'compile-{tag}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    assert r.returncode == 0, r.stdout
    exe = OUT / f'fixture-{tag}.exe'
    cmd = [link, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/ENTRY:entry', '/NODEFAULTLIB', '/INCREMENTAL:NO',
           f'/OUT:{exe}', *sorted(objs.glob('*.obj')), sdk_lib / 'kernel32.Lib']
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, cwd=OUT)
    (OUT / f'link-{tag}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    assert r.returncode == 0, r.stdout
    return subprocess.run([str(exe)], capture_output=True, text=True, cwd=OUT).returncode


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    body = original_body()
    sites = operand_sites(body)
    tpl = (RUN / 'frame_clock_fixture_429.tpl.cpp').read_bytes().decode()
    fixture = OUT / 'frame_clock_fixture_429.cpp'
    fixture.write_bytes(tpl.replace('/*@ORIGINAL_BYTES@*/', ', '.join(str(b) for b in body))
                        .replace('/*@RELOC_COUNT@*/', str(len(sites)))
                        .replace('/*@SLAB_RELOCS@*/', ',\n'.join(f'    {{{o}u, {r}u, 0x{t:08x}u}}' for o, r, t in sites))
                        .encode())
    cl, link, includes, sdk_lib = toolchain()
    corrected = build_and_run(RUN / 'frame_clock_00413ea0_429.cpp', 'corrected', fixture, cl, link, includes, sdk_lib)
    # Negative control: Run 401's source with its own names mapped onto the canonical ones.
    old = (V2 / 'runs/401-frame-clock-dispatch/00413ea0.cpp').read_bytes().decode()
    old = ('#include "porsche/application_main.hpp"\n' + old) \
        .replace('frame_clock_mode_005e99f4', 'global_005e99f4') \
        .replace('frame_clock_session_state_006573e8', 'global_006573e8')
    negative_src = OUT / 'uncorrected_00413ea0_401.cpp'
    negative_src.write_bytes(old.encode())
    uncorrected = build_and_run(negative_src, 'uncorrected', fixture, cl, link, includes, sdk_lib)
    result = dict(schema=1, run='429-unified-game-integration', function='00413ea0', original_sha256=PE_SHA,
                  original_bytes=SIZE, operand_sites=len(sites), cases=9,
                  corrected_exit_code=corrected, uncorrected_401_exit_code=uncorrected,
                  template_sha256=hashlib.sha256((RUN / 'frame_clock_fixture_429.tpl.cpp').read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256((RUN / 'frame_clock_00413ea0_429.cpp').read_bytes()).hexdigest())
    print(json.dumps(result))
    assert corrected == 0, 'corrected 00413ea0 differs from the original'
    assert uncorrected != 0, 'the cases do not detect the cached count'
    (RUN / 'frame-clock-validation.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())


if __name__ == '__main__':
    main()
