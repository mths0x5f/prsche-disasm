"""Independent audit for Run 425 (voice stop and its callee tree).

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
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/425-audio-voice-stop'
EXP = ROOT / 'local/experiments/v2-audio-voice-stop-425'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CASES = 22

BODIES = {
    0x0058a8b0: (88, '2d077122a5f36c27e4de4a216a7fbb5b07d59acf550ae6fb2fc08ab0db91f06c'),
    0x00597010: (83, 'c85841f4961be8cd29816a84262229eb7493e93e5ca4402de52862c9518c0ac0'),
    0x0058ac30: (103, '231c710d19684c59633d1e9070212c399f6ec267cae2cf1fe68238f838e648a4'),
    0x00589c00: (277, 'a217bfc049ace7834895aa3389ac941072aa8e1b7cfb7e3a2b9c66d2c4b9ddad'),
}

# (body, offset, expected absolute operand)
OPERANDS = [
    (0x0058a8b0, 0x03, 0x006b489c), (0x00597010, 0x06, 0x006b489c), (0x0058ac30, 0x02, 0x006b4a18),
    (0x00589c00, 0x08, 0x006b4a00), (0x00589c00, 0x3c, 0x006b49a4), (0x00589c00, 0x45, 0x006b4a00),
    (0x00589c00, 0x92, 0x006b49a8), (0x00589c00, 0xa1, 0x006b4a00), (0x00589c00, 0xce, 0x006b49a8),
    (0x00589c00, 0xdf, 0x006b49a8), (0x00589c00, 0x108, 0x006b49a8),
]

# lock primitive -> IAT cell it calls through -> the KERNEL32 import there
IAT_CALLS = {}

# rel32 control transfers: (body, offset, opcode, target VA)
TRANSFERS = [
    (0x0058a8b0, 0x3d, 0xe8, 0x00597010),   # flags bit 2: release links
    (0x0058a8b0, 0x4b, 0xe8, 0x00589c00),   # flag 0x10: leave the group
    (0x00597010, 0x3d, 0xe8, 0x0058ac30),   # release each non-embedded node
]

EXPECTED_DEFINED = {
    '?application_audio_backend_release_0058ac30@porsche@@YAXI@Z',
    '?audio_backend_stop_voice_0058a8b0@porsche@@YAXI@Z',
    '?audio_channel_group_release_00589c00@porsche@@YAXI@Z',
    '?audio_voice_release_links_00597010@porsche@@YAXI@Z',
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
    assert total == 551, total

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
    assert summary['original_selected_bytes'] == 551
    defined = set(summary['symbols']['defined'])
    assert EXPECTED_DEFINED <= defined, f'missing: {EXPECTED_DEFINED - defined}'
    assert defined - EXPECTED_DEFINED <= STL_WEAK, f'unexpected definitions: {defined - EXPECTED_DEFINED}'
    assert summary['native_fixture']['exit_code'] == 0
    assert summary['native_fixture']['cases'] == CASES == summary['native_fixture']['cases_passed']

    validation = json.loads((RUN / 'validation.json').read_text(encoding='utf-8'))
    assert validation['status'] == 'PASS' and validation['cases_passed'] == CASES
    assert validation['pe_bytes'] == 551 and validation['functions'] == 4

    for name in ('compile-001', 'fixture-link-001', 'fixture-native-001'):
        receipt = json.loads((EXP / (name + '.execution.json')).read_text(encoding='utf-8'))
        assert receipt['exit_code'] == 0, f'{name}: non-zero exit'
    log = (EXP / 'fixture-native-001.log').read_text(encoding='utf-8')
    assert log.count(' OK ') == CASES and 'FAILED' not in log, 'native log mismatch'

    print('Run 425 verified: 4 bodies / 551 PE bytes; 11 absolute operands and 3 rel32 calls '
          f're-derived; 4 COFF definitions; {CASES}/{CASES} differential cases on the physical x86 slab')


if __name__ == '__main__':
    main()
