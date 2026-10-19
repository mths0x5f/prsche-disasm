"""Independent audit for Run 421 (audio backend lock and pool helpers).

Re-derives every claim from the retail image and the receipts instead of
trusting summary.json: body ranges, terminators and SHA-256 values; the absolute
operands each body uses, including which KERNEL32 import each lock primitive
calls through the IAT; the COFF symbols the recovery object defines; and the
native fixture result.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/421-audio-backend-lock-pool'
EXP = ROOT / 'local/experiments/v2-audio-backend-421'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CASES = 30

BODIES = {
    0x0058e2d0: (12, 'c18c8d5c01e36176e27f003e1121d2729387a31f66fd7f7993bdcbb18ca27b0b'),
    0x0058e2e0: (12, 'a6226eb7f2aae6e22745a6f303ebe061d53c9fa24095775d1595d624772ad92e'),
    0x0058e2f0: (12, '190b028a580459671dd5968b047688a0b854bbea0439bb79d1f4d8adef13c410'),
    0x0058e300: (12, 'd15f037561e5740cad63aff2f03fc207d39d331d26c0aa76c97af5df7122b27b'),
    0x005896d0: (18, '9021e6ce3cdd9eb979bc2e8c1e58337ba0529f13beea79507209ed677a786339'),
    0x005896f0: (17, '9be3da08ee0c2cb0cbcfb754f7cbb6663fd3bab080b58cc21fa4a6c3d799db6c'),
    0x0058aa90: (44, 'e28ca7509211e5e0e22297b8c47094f8b1b51a0886f09c5e19073a6a2c4b3c27'),
    0x0058aac0: (31, '8667c58ce1362cb46671ea2d717ada2acacedf3844d3c00fbb962d62b979bc9b'),
    0x0058fef0: (31, 'f8d8826bcf8d778264a09c146ab87a65162d08fc2120de7a58269bf7ca6c3419'),
    0x0058ff10: (50, '3a781d72cc94ed6385bd5780e1bf0d02605de11dbc432ee6d9d0ee0978d0e80f'),
}

# (body, offset, expected absolute operand)
OPERANDS = [
    (0x0058e2d0, 1, 0x006b1800), (0x0058e2e0, 1, 0x006b1800),
    (0x0058e2f0, 1, 0x006b1800), (0x0058e300, 1, 0x006b1800),
    (0x005896d0, 6, 0x006b499f), (0x005896d0, 13, 0x006b499f),
    (0x005896f0, 1, 0x006b499f), (0x005896f0, 8, 0x006b499f),
    (0x0058aa90, 9, 0x006b4a18), (0x0058aac0, 2, 0x006b4a18),
    (0x0058ff10, 6, 0x006b49a4), (0x0058ff10, 16, 0x006b4a00),
    (0x0058ff10, 32, 0x006b49a4),
]

# lock primitive -> IAT cell it calls through -> the KERNEL32 import there
IAT_CALLS = {
    0x0058e2d0: (0x005b207c, 'InitializeCriticalSection'),
    0x0058e2e0: (0x005b2068, 'DeleteCriticalSection'),
    0x0058e2f0: (0x005b2078, 'EnterCriticalSection'),
    0x0058e300: (0x005b206c, 'LeaveCriticalSection'),
}

# rel32 control transfers: (body, offset, opcode, target VA)
TRANSFERS = [
    (0x005896d0, 0, 0xe8, 0x0058e2f0),   # call enter
    (0x005896f0, 12, 0xe9, 0x0058e300),  # tail jmp leave
    (0x0058ff10, 24, 0xe8, 0x00565d60),  # call audio_channel_stop
]

EXPECTED_DEFINED = {
    '?application_audio_backend_close_0058aac0@porsche@@YAHXZ',
    '?application_audio_backend_configure_0058aa90@porsche@@YAXII@Z',
    '?application_audio_backend_configure_0058fef0@porsche@@YAXII@Z',
    '?application_audio_backend_quiet_0058ff10@porsche@@YAXXZ',
    '?application_audio_backend_start_0058e2d0@porsche@@YAXXZ',
    '?application_audio_backend_stop_0058e2e0@porsche@@YAXXZ',
    '?audio_backend_enter_0058e2f0@porsche@@YAXXZ',
    '?audio_backend_leave_0058e300@porsche@@YAXXZ',
    '?audio_backend_lock_005896d0@porsche@@YAXXZ',
    '?audio_backend_unlock_005896f0@porsche@@YAXXZ',
}
# weak value the MSVC STL emits into any TU that includes <array>/<xstring>
STL_WEAK = {'__Avx2WmemEnabledWeakValue'}


def sections(image):
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    count = struct.unpack_from('<H', image, pe + 6)[0]
    opt = struct.unpack_from('<H', image, pe + 20)[0]
    base = struct.unpack_from('<I', image, pe + 24 + 28)[0]
    off = pe + 24 + opt
    out = []
    for _ in range(count):
        vsize, vaddr, rsize, raw = struct.unpack_from('<IIII', image, off + 8)
        out.append((vaddr, vsize, raw, rsize))
        off += 40
    return base, out


def reader(image):
    base, secs = sections(image)

    def read(va, n):
        rva = va - base
        for vaddr, vsize, raw, rsize in secs:
            if vaddr <= rva < vaddr + max(vsize, rsize):
                return image[raw + rva - vaddr: raw + rva - vaddr + n]
        raise AssertionError(f'VA {va:08x} outside every section')
    return base, read


def main():
    image = (ROOT / 'local/game/Porsche.exe').read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA, 'original image SHA mismatch'
    base, read = reader(image)

    total = 0
    for va, (size, body_sha) in BODIES.items():
        body = read(va, size)
        assert hashlib.sha256(body).hexdigest() == body_sha, f'{va:08x}: body SHA mismatch'
        assert body[-1] == 0xc3 or body[-5] == 0xe9, f'{va:08x}: no RET or tail JMP'
        total += size
    assert total == 239, total

    for body, off, expected in OPERANDS:
        got = struct.unpack('<I', read(body + off, 4))[0]
        assert got == expected, f'{body:08x}+{off}: operand {got:08x} != {expected:08x}'

    imports = {}
    for line in (ROOT / 'research/binary-index/static/imports.jsonl').read_text(encoding='utf-8').splitlines():
        d = json.loads(line)
        if d.get('path') == 'Porsche.exe':
            imports[base + int(d['iat_rva'], 16)] = (d['dll'], d['symbol'])
    for body, (cell, name) in IAT_CALLS.items():
        insn = read(body + 5, 6)
        assert insn[:2] == b'\xff\x15', f'{body:08x}: expected call dword ptr [imm32]'
        assert struct.unpack('<I', insn[2:])[0] == cell, f'{body:08x}: IAT cell mismatch'
        assert imports.get(cell) == ('KERNEL32.dll', name), f'{body:08x}: {imports.get(cell)} != {name}'

    for body, off, opcode, target in TRANSFERS:
        insn = read(body + off, 5)
        assert insn[0] == opcode, f'{body:08x}+{off}: opcode {insn[0]:02x}'
        rel = struct.unpack('<i', insn[1:])[0]
        assert body + off + 5 + rel == target, f'{body:08x}+{off}: target mismatch'

    summary = json.loads((RUN / 'summary.json').read_text(encoding='utf-8'))
    assert summary['original_sha256'] == SHA
    assert summary['original_selected_bytes'] == 239
    defined = set(summary['symbols']['defined'])
    assert EXPECTED_DEFINED <= defined, f'missing: {EXPECTED_DEFINED - defined}'
    assert defined - EXPECTED_DEFINED <= STL_WEAK, f'unexpected definitions: {defined - EXPECTED_DEFINED}'
    assert summary['native_fixture']['exit_code'] == 0
    assert summary['native_fixture']['cases'] == CASES == summary['native_fixture']['cases_passed']

    validation = json.loads((RUN / 'validation.json').read_text(encoding='utf-8'))
    assert validation['status'] == 'PASS' and validation['cases_passed'] == CASES
    assert validation['pe_bytes'] == 239 and validation['functions'] == 10

    for name in ('compile-001', 'fixture-link-001', 'fixture-native-001'):
        receipt = json.loads((EXP / (name + '.execution.json')).read_text(encoding='utf-8'))
        assert receipt['exit_code'] == 0, f'{name}: non-zero exit'
    log = (EXP / 'fixture-native-001.log').read_text(encoding='utf-8')
    assert log.count(' OK ') == CASES and 'FAILED' not in log, 'native log mismatch'

    print('Run 421 verified: 10 bodies / 239 PE bytes; 13 absolute operands and 3 rel32 '
          'transfers re-derived; the four lock primitives call KERNEL32 '
          'Initialize/Delete/Enter/LeaveCriticalSection through the IAT; 10 COFF '
          f'definitions; {CASES}/{CASES} differential cases on the physical x86 slab')


if __name__ == '__main__':
    main()
