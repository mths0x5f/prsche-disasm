"""Run 429: differential test of the corrected frame root lifecycle (00471b70, 00471c40).

Fills the versioned fixture template with the original bodies, their absolute and
rel32 operand sites, and the original string literals they reference, all read
from the PE. Links the real frame_root_block_429.asm. Then two negative controls
mutate the corrected source and must fail: a void 005323a0 (no fstp st(0) pop) and
Run 419's truncated error format.

Usage: py -3 scripts/research/experiment-v2-frame-root-429.py
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
OUT = ROOT / 'local/experiments/v2-frame-root-429'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BODIES = [(0x00471b70, 198), (0x00471c40, 65)]
DATA = {0x00657444, 0x00628940, 0x00628960, 0x00628964, 0x0065b2b8, 0x005e8e50, 0x00628bc0}
CALLS = {0x0059ef90, 0x004874a0, 0x005a0fbf, 0x004876e0, 0x0059fd90, 0x005323a0, 0x005a177b, 0x00487590, 0x0059f050}


class Pe:
    def __init__(self):
        self.d = (ROOT / 'local/game/Porsche.exe').read_bytes()
        assert hashlib.sha256(self.d).hexdigest() == PE_SHA
        pe = struct.unpack_from('<I', self.d, 0x3c)[0]
        opt = struct.unpack_from('<H', self.d, pe + 20)[0]
        self.base = struct.unpack_from('<I', self.d, pe + 52)[0]
        off = pe + 24 + opt
        self.secs = []
        for k in range(struct.unpack_from('<H', self.d, pe + 6)[0]):
            name = self.d[off + 40 * k:off + 40 * k + 8].rstrip(b'\0').decode()
            vsz, va, rsz, raw = struct.unpack_from('<IIII', self.d, off + 40 * k + 8)
            self.secs.append((name, va, rsz, raw))

    def at(self, va, n):
        rva = va - self.base
        for _name, sva, rsz, raw in self.secs:
            if sva <= rva < sva + rsz:
                return self.d[raw + rva - sva:raw + rva - sva + n]
        raise AssertionError(f'{va:08x} has no file bytes')

    def section(self, va):
        rva = va - self.base
        return next((n for n, sva, rsz, _ in self.secs if sva <= rva < sva + rsz), None)

    def cstring(self, va):
        b = self.at(va, 512)
        return b[:b.index(b'\0')]


def scan(pe):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    sites, strings, bodies = [], {}, []
    for index, (va, size) in enumerate(BODIES):
        body = pe.at(va, size)
        bodies.append(body)
        covered = 0
        for ins in md.disasm(body, va):
            covered += ins.size
            if ins.mnemonic == 'call' and ins.bytes[0] == 0xe8:
                assert ins.operands[0].imm in CALLS, f'call {ins.operands[0].imm:08x}'
                sites.append((index, ins.address - va + 1, 1, ins.operands[0].imm))
                continue
            for slot in (ins.disp_offset, ins.imm_offset):
                if slot and slot + 4 <= ins.size:
                    v = struct.unpack_from('<I', ins.bytes, slot)[0]
                    if v in DATA:
                        sites.append((index, ins.address - va + slot, 0, v))
                    elif pe.section(v) in ('.rdata', '.data'):  # literals: these bodies keep them in .data
                        strings[v] = pe.cstring(v)
                        sites.append((index, ins.address - va + slot, 0, v))
        assert covered == size
    return bodies, sorted(set(sites)), strings


def c_bytes(b):
    return ', '.join(str(x) for x in b)


def c_string(b):
    out = ''
    for x in b:
        c = chr(x)
        out += {'\\': '\\\\', '"': '\\"', '\n': '\\n'}.get(c, c) if 32 <= x < 127 or x == 10 else f'\\x{x:02x}'
    return '"' + out + '"'


def toolchain():
    roots = [Path(r'C:\Program Files\Microsoft Visual Studio'), Path(r'C:\Program Files (x86)\Microsoft Visual Studio')]
    cl = sorted(c for r in roots if r.exists() for c in r.glob('*/*/VC/Tools/MSVC/*/bin/Hostx64/x86/cl.exe'))[-1]
    sdk_inc = sorted(p for p in Path(r'C:\Program Files (x86)\Windows Kits\10\Include').iterdir() if (p / 'um').exists())[-1]
    sdk_lib = sdk_inc.parent.parent / 'Lib' / sdk_inc.name / 'um' / 'x86'
    vc = cl.parents[3]
    return cl, [vc / 'include', sdk_inc / 'ucrt', sdk_inc / 'shared', sdk_inc / 'um'], sdk_lib


def build_and_run(source, tag, fixture, block_obj, cl, includes, sdk_lib):
    objs = OUT / f'objects-{tag}'
    objs.mkdir(parents=True, exist_ok=True)
    for p in objs.glob('*.obj'):
        p.unlink()
    inc = [f'/I{p}' for p in includes + [V2 / 'source/include', V2 / 'runs/419-frame-root-lifecycle']]
    r = subprocess.run([str(c) for c in [cl, '/nologo', '/c', '/std:c++17', '/Od', '/GS-', '/GR-', '/EHsc', '/TP',
                                         '/W4', '/Zl', *inc, f'/Fo{objs}\\', source, fixture]],
                       capture_output=True, text=True, cwd=OUT)
    (OUT / f'compile-{tag}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    assert r.returncode == 0, r.stdout
    exe = OUT / f'fixture-{tag}.exe'
    r = subprocess.run([str(c) for c in [cl.parent / 'link.exe', '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE',
                                         '/ENTRY:entry', '/NODEFAULTLIB', '/INCREMENTAL:NO', '/SAFESEH:NO',
                                         f'/OUT:{exe}', *sorted(objs.glob('*.obj')), block_obj,
                                         sdk_lib / 'kernel32.Lib']],
                       capture_output=True, text=True, cwd=OUT)
    (OUT / f'link-{tag}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    assert r.returncode == 0, r.stdout
    run = subprocess.run([str(exe)], capture_output=True, text=True, cwd=OUT)
    (OUT / f'native-{tag}.log').write_text(run.stdout, encoding='utf-8')
    return run.returncode, run.stdout


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pe = Pe()
    bodies, sites, strings = scan(pe)
    tpl = (RUN / 'frame_root_fixture_429.tpl.cpp').read_bytes().decode()
    fixture = OUT / 'frame_root_fixture_429.cpp'
    fixture.write_bytes(tpl.replace('/*@INIT_SIZE@*/', str(len(bodies[0]))).replace('/*@INIT_BYTES@*/', c_bytes(bodies[0]))
                        .replace('/*@TEARDOWN_SIZE@*/', str(len(bodies[1]))).replace('/*@TEARDOWN_BYTES@*/', c_bytes(bodies[1]))
                        .replace('/*@SITES@*/', ',\n'.join(f'    {{{b}u, {o}u, {r}u, 0x{t:08x}u}}' for b, o, r, t in sites))
                        .replace('/*@STRINGS@*/', ',\n'.join(f'    {{0x{v:08x}u, {c_string(s)}}}' for v, s in sorted(strings.items())))
                        .encode())
    cl, includes, sdk_lib = toolchain()
    block_obj = OUT / 'frame_root_block_429.obj'
    r = subprocess.run([str(cl.parent / 'ml.exe'), '/nologo', '/c', '/coff', f'/Fo{block_obj}',
                        str(RUN / 'frame_root_block_429.asm')], capture_output=True, text=True, cwd=OUT)
    assert r.returncode == 0, r.stdout
    source = RUN / 'frame_root_lifecycle_429.cpp'
    code, log = build_and_run(source, 'corrected', fixture, block_obj, cl, includes, sdk_lib)
    print(log.strip())
    text = source.read_bytes().decode()
    mutations = {
        'void-005323a0': text.replace('float __cdecl bworld_init_subsystem_005323a0', 'void __cdecl bworld_init_subsystem_005323a0')
                             .replace('static_cast<void>(bworld_init_subsystem_005323a0', '(bworld_init_subsystem_005323a0'),
        'truncated-error-format': text.replace("track: '%s'\\n\"", "track: '\""),
    }
    negative = {}
    for tag, mutated in mutations.items():
        assert mutated != text, f'mutation {tag} did not apply'
        p = OUT / f'mutated-{tag}.cpp'
        p.write_bytes(mutated.encode())
        negative[tag] = build_and_run(p, tag, fixture, block_obj, cl, includes, sdk_lib)[0]
    result = dict(schema=1, run='429-unified-game-integration', functions=['00471b70', '00471c40'],
                  original_sha256=PE_SHA, original_bytes=[len(b) for b in bodies], operand_sites=len(sites),
                  rdata_strings={f'{v:08x}': s.decode('latin-1') for v, s in sorted(strings.items())},
                  native_checks=log.count(' OK'), corrected_exit_code=code, negative_exit_codes=negative,
                  template_sha256=hashlib.sha256((RUN / 'frame_root_fixture_429.tpl.cpp').read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  block_sha256=hashlib.sha256((RUN / 'frame_root_block_429.asm').read_bytes()).hexdigest())
    print(json.dumps(dict(corrected=code, negative=negative, checks=result['native_checks'], sites=len(sites))))
    assert code == 0, 'corrected frame root lifecycle differs from the original'
    assert all(v != 0 for v in negative.values()), 'a mutation was not detected'
    (RUN / 'frame-root-validation.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())


if __name__ == '__main__':
    main()
