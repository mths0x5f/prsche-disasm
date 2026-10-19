"""Run 427: the audio module's static storage as one block with original offsets.

Every C++ name that refers to a cell of the audio module's zero-initialized
storage (006b00c0..006b4a44) is placed by one MASM data object at its original
offset, so all names share one block exactly as in Porsche.exe. The script:

1. checks the original PE: the block lies in the virtual (zero-fill) tail of
   .data, and every HIGHLOW target inside it is referenced from code;
2. generates audio_backend_state_427.asm from LAYOUT (or checks it, --check);
3. assembles it, reads the COFF symbol offsets back, and builds and runs a native
   fixture that checks symbol distances, initial zero bytes and aliasing through
   the canonical headers.

Usage: py -3 scripts/research/experiment-v2-audio-state-block-427.py [--check]
"""
import argparse
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / 'iterations/v2/001-original-recovery'
RUN = V2 / 'runs/427-audio-backend-state-block'
OUT = ROOT / 'local/experiments/v2-audio-state-block-427'
PE = ROOT / 'local/game/Porsche.exe'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
ASM = RUN / 'audio_backend_state_427.asm'
FIXTURE = RUN / 'layout_fixture_427.cpp'

BLOCK_BEGIN, BLOCK_END = 0x006b00c0, 0x006b4a44
BLOCK_LABEL = '_audio_state_block_006b00c0'
# (original VA, decorated name, bytes owned by the name, C++ declaration)
LAYOUT = [
    (0x006b1800, '?audio_backend_lock_cs_006b1800@porsche@@3PAEA', 24,
     'std::uint8_t audio_backend_lock_cs_006b1800[24]  (Run 421)'),
    (0x006b489c, '?audio_voice_table_006b489c@porsche@@3IA', 4,
     'std::uint32_t audio_voice_table_006b489c  (Run 425)'),
    (0x006b48b0, '?application_audio_device_state_006b48c0@porsche@@3UApplicationAudioDeviceStateStorage@1@A', 0x18c,
     'ApplicationAudioDeviceStateStorage application_audio_device_state_006b48c0 (canonical; data() = 006b48c0)'),
    (0x006b499c, '?audio_system_active_006b499c@porsche@@3EA', 1,
     'std::uint8_t audio_system_active_006b499c  (Run 400)'),
    (0x006b499f, '?audio_backend_lock_depth_006b499f@porsche@@3EA', 1,
     'std::uint8_t audio_backend_lock_depth_006b499f  (Run 421)'),
    (0x006b49a4, '?audio_backend_channel_count_006b49a4@porsche@@3FA', 2,
     'std::int16_t audio_backend_channel_count_006b49a4  (Run 421)'),
    (0x006b49a8, '?audio_backend_stamp_006b49a8@porsche@@3IA', 4,
     'std::uint32_t audio_backend_stamp_006b49a8  (Run 425)'),
    (0x006b4a00, '?audio_backend_channels_006b4a00@porsche@@3IA', 4,
     'std::uint32_t audio_backend_channels_006b4a00  (Run 421)'),
    (0x006b4a18, '?audio_backend_pool_006b4a18@porsche@@3IA', 4,
     'std::uint32_t audio_backend_pool_006b4a18  (Run 421)'),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pe_checks():
    d = PE.read_bytes()
    assert hashlib.sha256(d).hexdigest() == PE_SHA, 'original PE SHA mismatch'
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    nsec = struct.unpack_from('<H', d, pe + 6)[0]
    opt = struct.unpack_from('<H', d, pe + 20)[0]
    base = struct.unpack_from('<I', d, pe + 52)[0]
    reloc_rva, reloc_size = struct.unpack_from('<II', d, pe + 24 + 96 + 5 * 8)
    secs = []
    off = pe + 24 + opt
    for _ in range(nsec):
        name = d[off:off + 8].rstrip(b'\0').decode()
        vsz, va, rsz, raw, = struct.unpack_from('<IIII', d, off + 8)
        flags = struct.unpack_from('<I', d, off + 36)[0]
        secs.append((name, va, vsz, raw, rsz, flags))
        off += 40
    data = [s for s in secs if s[0] == '.data'][0]
    _, dva, dvsz, _, drsz, dflags = data
    assert dflags & 0xc0000000 == 0xc0000000 and not dflags & 0x20000000, '.data is not RW non-exec'
    assert base + dva + drsz <= BLOCK_BEGIN and BLOCK_END <= base + dva + dvsz, \
        'block is not inside the zero-fill tail of .data'

    def r2o(rva):
        for _n, va, vsz, raw, rsz, _f in secs:
            if va <= rva < va + max(vsz, rsz):
                return raw + rva - va
        return None

    targets = {}
    p = r2o(reloc_rva)
    end = p + reloc_size
    while p < end:
        page, size = struct.unpack_from('<II', d, p)
        if size == 0:
            break
        for i in range((size - 8) // 2):
            e = struct.unpack_from('<H', d, p + 8 + 2 * i)[0]
            if e >> 12 == 3:
                o = r2o(page + (e & 0xfff))
                v = struct.unpack_from('<I', d, o)[0]
                if BLOCK_BEGIN <= v < BLOCK_END:
                    targets.setdefault(v, []).append(base + page + (e & 0xfff))
        p += size
    for va, *_ in LAYOUT:
        assert va in targets or va == 0x006b48b0, f'{va:08x} has no HIGHLOW reference'
    below = [v for v in targets if v < BLOCK_BEGIN]
    return dict(data_raw_end=f'{base + dva + drsz:08x}', data_virtual_end=f'{base + dva + dvsz:08x}',
                highlow_targets=len(targets), highlow_sites=sum(len(s) for s in targets.values()),
                lowest_target=f'{min(targets):08x}', highest_target=f'{max(targets):08x}', below=below)


def generate_asm():
    lines = [
        '; Original Porsche.exe SHA-256 ' + PE_SHA,
        '; GENERATED by scripts/research/experiment-v2-audio-state-block-427.py; do not edit.',
        ';',
        '; The audio module\'s zero-initialized storage, 006b00c0..006b4a44, as ONE block.',
        '; Each public label sits at its original offset, so every C++ name for a cell of',
        '; this block refers to the same memory as in the original (arrays at 006b4886 and',
        '; 006b4a08 index into neighbouring cells, see README). Bytes between labels are',
        '; storage whose owners are not recovered yet; they are not separate objects.',
        '.686',
        '.model flat',
        'option casemap:none',
        '',
        f'PUBLIC {BLOCK_LABEL}',
    ]
    lines += [f'PUBLIC {name}' for _, name, _, _ in LAYOUT]
    lines += ['', "_AUDSTATE SEGMENT ALIGN(64) READ WRITE 'BSS'", f'{BLOCK_LABEL} LABEL BYTE']
    # Labels mark positions only; a name may lie inside another (the device state
    # view spans 006b48b0..006b4a3c and contains several cells). Bytes are reserved
    # from each label to the next, so the block is exactly BLOCK_END - BLOCK_BEGIN.
    for va, name, size, _ in LAYOUT:
        assert BLOCK_BEGIN <= va and va + size <= BLOCK_END, f'{name} outside the block'
    marks = sorted(LAYOUT)
    cursor = BLOCK_BEGIN
    for idx, (va, name, size, decl) in enumerate(marks):
        if va > cursor:
            lines.append(f'    BYTE 0{va - cursor:x}h DUP (?)    ; {cursor:08x}..{va - 1:08x}')
        cursor = va
        lines += [f'; {va:08x}..{va + size - 1:08x}: {decl}', f'{name} LABEL BYTE']
    lines.append(f'    BYTE 0{BLOCK_END - cursor:x}h DUP (?)    ; {cursor:08x}..{BLOCK_END - 1:08x}')
    lines += ['_AUDSTATE ENDS', 'END', '']
    return '\n'.join(lines)


def toolchain():
    roots = [Path(r'C:\Program Files\Microsoft Visual Studio'), Path(r'C:\Program Files (x86)\Microsoft Visual Studio')]
    cls = sorted(c for r in roots if r.exists() for c in r.glob('*/*/VC/Tools/MSVC/*/bin/Hostx64/x86/cl.exe'))
    assert cls, 'no x86 cl.exe'
    cl = cls[-1]
    sdk_inc = sorted(p for p in Path(r'C:\Program Files (x86)\Windows Kits\10\Include').iterdir() if (p / 'um').exists())[-1]
    sdk_lib = sdk_inc.parent.parent / 'Lib' / sdk_inc.name / 'um' / 'x86'
    vc = cl.parents[3]
    includes = [vc / 'include', sdk_inc / 'ucrt', sdk_inc / 'shared', sdk_inc / 'um']
    return cl, cl.parent / 'ml.exe', cl.parent / 'link.exe', includes, sdk_lib


def run(cmd, name):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, cwd=OUT)
    (OUT / f'{name}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    assert r.returncode == 0, f'{name} failed:\n{r.stdout}\n{r.stderr}'
    return r


def coff_symbols(obj):
    """External symbols defined in the object: name -> (section number, value)."""
    d = obj.read_bytes()
    _nsec, _time, symptr, nsym = struct.unpack_from('<HIII', d, 2)
    strtab = symptr + nsym * 18
    out = {}
    i = 0
    while i < nsym:
        e = d[symptr + 18 * i:symptr + 18 * i + 18]
        name = e[:8]
        if name[:4] == b'\0\0\0\0':
            o = strtab + struct.unpack_from('<I', name, 4)[0]
            name = d[o:d.index(b'\0', o)]
        else:
            name = name.rstrip(b'\0')
        value, secno, _typ, cls, naux = struct.unpack_from('<IhHBB', e, 8)
        if cls == 2 and secno > 0:
            out[name.decode()] = (secno, value)
        i += 1 + naux
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='fail if the committed .asm differs from generation')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    pe = pe_checks()
    text = generate_asm()
    if args.check:
        assert ASM.read_bytes().decode() == text, 'committed .asm differs from generation'
    else:
        ASM.write_bytes(text.encode())

    cl, ml, link, includes, sdk_lib = toolchain()
    run([ml, '/nologo', '/c', '/coff', f'/Fo{OUT / "audio_backend_state_427.obj"}', ASM], 'assemble')
    obj = OUT / 'audio_backend_state_427.obj'
    syms = coff_symbols(obj)
    block_sec, block_val = syms[BLOCK_LABEL]
    offsets = {}
    for va, name, _, _ in LAYOUT:
        sec, val = syms[name]
        assert sec == block_sec, f'{name} not in the block section'
        offsets[name] = val - block_val
        assert offsets[name] == va - BLOCK_BEGIN, f'{name}: offset {offsets[name]:#x} != {va - BLOCK_BEGIN:#x}'

    inc = [f'/I{p}' for p in includes + [V2 / 'source/include', V2 / 'runs/421-audio-backend-lock-pool',
                                          V2 / 'runs/425-audio-voice-stop']]
    run([cl, '/nologo', '/c', '/std:c++17', '/Od', '/GS-', '/GR-', '/EHsc', '/TP', '/W4', '/Zl',
         *inc, f'/Fo{OUT / "layout_fixture_427.obj"}', FIXTURE], 'compile')
    exe = OUT / 'layout-fixture.exe'
    run([link, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/ENTRY:entry', '/NODEFAULTLIB', '/INCREMENTAL:NO',
         f'/MAP:{OUT / "layout-fixture.map"}', f'/OUT:{exe}', OUT / 'layout_fixture_427.obj', obj,
         sdk_lib / 'kernel32.Lib'], 'link')
    r = subprocess.run([str(exe)], capture_output=True, text=True, cwd=OUT)
    (OUT / 'native.log').write_text(r.stdout, encoding='utf-8')
    ok = r.stdout.count(' OK')
    print(r.stdout.strip())
    assert r.returncode == 0 and 'FAIL' not in r.stdout, 'native fixture failed'

    summary = dict(schema=1, run='427-audio-backend-state-block', original_sha256=PE_SHA,
                   block=dict(begin=f'{BLOCK_BEGIN:08x}', end=f'{BLOCK_END:08x}', bytes=BLOCK_END - BLOCK_BEGIN),
                   pe=pe, names=[dict(va=f'{va:08x}', symbol=n, bytes=s, offset=f'{va - BLOCK_BEGIN:#x}')
                                 for va, n, s, _ in LAYOUT],
                   asm_sha256=sha(ASM), fixture_sha256=sha(FIXTURE), native_checks_ok=ok,
                   native_exit_code=r.returncode)
    (RUN / 'summary.json').write_bytes((json.dumps(summary, indent=2) + '\n').encode())
    print(json.dumps(dict(ok=True, checks=ok, highlow_targets=pe['highlow_targets'], highlow_sites=pe['highlow_sites'])))


if __name__ == '__main__':
    main()
