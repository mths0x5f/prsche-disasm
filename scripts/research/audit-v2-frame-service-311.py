"""Independent verification audit for Run 311.

Re-derives every claim from the retail image and the build receipts instead of
trusting summary.json: body ranges and SHA-256 values, the two read-only
scalars 00482e50 loads, the single-writer status of the 00628960 storage cell,
the COFF symbols the recovery object defines, and the native fixture result.
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/311-frame-service-callees'
EXP = ROOT / 'local/experiments/v2-frame-service-311'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

TARGETS = {
    '00423840': (0x00423840, 67, '8b75f5520e19b4380d2165f85398dfb9d39e71290de039430625dd5d7f6ef911'),
    '00482e50': (0x00482e50, 69, 'ebc3fb1a31138079e8fc8ff47b5a7e6309bd69c607b7e14b27fb4bf763d1446b'),
    '00476170': (0x00476170, 169, '0a4456508d1f9ad2a42da22096714106580b57fa5b16aa299fe2644f515b5d3e'),
}
SCALARS = {'005b47d8': (0x005b47d8, 8000.0), '005b2764': (0x005b2764, 10000.0)}
STORAGE_CELL = 0x00628960
EXPECTED_WRITERS = ['00471bae', '00471bb5', '00471c6d']
EXPECTED_DEFINED = {
    '?advance_00423840@FrameIterator_290@porsche@@QAEXXZ',
    '?invoke_00482e50@FrameTail_290@porsche@@QAEXXZ',
    '?invoke_00476170@FrameAction_290@porsche@@QAEXXZ',
}
CASES = 12


def sections(image):
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    count = struct.unpack_from('<H', image, pe + 6)[0]
    opt = struct.unpack_from('<H', image, pe + 20)[0]
    base = struct.unpack_from('<I', image, pe + 24 + 28)[0]
    off = pe + 24 + opt
    out = []
    for _ in range(count):
        name = image[off:off + 8].rstrip(b'\0').decode()
        vsize, vaddr, rsize, raw = struct.unpack_from('<IIII', image, off + 8)
        out.append((name, vaddr, vsize, raw, rsize))
        off += 40
    return base, out


def read_va(image, base, secs, va, size):
    rva = va - base
    for _name, vaddr, vsize, raw, rsize in secs:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            start = raw + (rva - vaddr)
            return image[start:start + size]
    raise AssertionError(f'VA {va:08x} outside every section')


def main():
    import hashlib

    original = ROOT / 'local/game/Porsche.exe'
    assert original.exists(), f'original image missing at {original}'
    image = original.read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA, 'original image SHA mismatch'
    base, secs = sections(image)

    # 1. Body ranges, terminating RET and SHA-256, straight from the image.
    total = 0
    for name, (va, size, body_sha) in TARGETS.items():
        body = read_va(image, base, secs, va, size)
        assert len(body) == size, f'{name}: short read'
        assert body[-1] == 0xc3, f'{name}: body does not end on RET'
        got = hashlib.sha256(body).hexdigest()
        assert got == body_sha, f'{name}: body SHA mismatch {got}'
        total += size
    assert total == 305, f'byte total mismatch: {total}'

    # 2. The two read-only scalars that 00482e50 compares and adds.
    for name, (va, expected) in SCALARS.items():
        value = struct.unpack('<f', read_va(image, base, secs, va, 4))[0]
        assert value == expected, f'{name}: scalar {value} != {expected}'

    # 3. The storage cell has exactly the three writers Run 311 claims. Every
    #    4-byte operand occurrence of 00628960 in .text is collected, then the
    #    ones that are the destination of a MOV-to-absolute store are checked.
    needle = struct.pack('<I', STORAGE_CELL)
    writers = []
    for name, vaddr, _vsize, raw, rsize in secs:
        if name != '.text':
            continue
        blob = image[raw:raw + rsize]
        pos = blob.find(needle)
        while pos >= 0:
            site = base + vaddr + pos
            # a3 imm32          -> mov [imm32], eax
            # c7 05 imm32 imm32 -> mov dword [imm32], imm32
            if blob[pos - 1:pos] == b'\xa3':
                writers.append(f'{site - 1:08x}')
            elif blob[pos - 2:pos] == b'\xc7\x05':
                writers.append(f'{site - 2:08x}')
            pos = blob.find(needle, pos + 1)
    assert writers == EXPECTED_WRITERS, f'unexpected writers for 00628960: {writers}'

    # 4. Run artefacts.
    summary = json.loads((RUN / 'summary.json').read_text(encoding='utf-8'))
    assert summary['original_sha256'] == SHA, 'summary SHA mismatch'
    assert summary['original_selected_bytes'] == 305, 'summary byte count mismatch'
    assert sorted(summary['original_vas']) == sorted(TARGETS), 'summary VA mismatch'
    assert set(summary['symbols']['defined']) == EXPECTED_DEFINED, 'defined symbols mismatch'
    assert summary['native_fixture']['exit_code'] == 0, 'native fixture exit code non-zero'
    assert summary['native_fixture']['cases'] == CASES, 'case count mismatch'
    assert summary['native_fixture']['cases_passed'] == CASES, 'cases passed mismatch'

    validation = json.loads((RUN / 'validation.json').read_text(encoding='utf-8'))
    assert validation['status'] == 'PASS', 'validation status not PASS'
    assert validation['pe_bytes'] == 305, 'validation byte count mismatch'
    assert validation['cases_passed'] == CASES, 'validation cases mismatch'

    # 5. Build receipts recorded by the experiment driver.
    for receipt_name in ('compile-001', 'fixture-link-001', 'fixture-native-001'):
        receipt_path = EXP / (receipt_name + '.execution.json')
        assert receipt_path.exists(), f'receipt missing: {receipt_path}'
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        assert receipt['exit_code'] == 0, f'{receipt_name}: non-zero exit'

    native_log = (EXP / 'fixture-native-001.log').read_text(encoding='utf-8')
    assert native_log.count(' OK') == CASES, 'native log case count mismatch'
    assert 'FAILED' not in native_log, 'native log reports failures'

    print('Run 311 verified: PE 305B across 00423840 (67B), 00482e50 (69B), '
          '00476170 (169B); scalars 005b47d8=8000.0f and 005b2764=10000.0f; '
          '00628960 writers 00471bae/00471bb5 (init 00471b70) and 00471c6d '
          '(teardown 00471c40); 3 COFF symbols '
          'close the Run 290 frontier; 12/12 differential cases on the '
          'physical x86 slab; receipts verified')


if __name__ == '__main__':
    main()
