"""Independent audit for Run 423 (input _getstate 00532e10, every mode).

Re-derives from the retail image: the body range, RET and SHA-256; both jump
tables and which body offset each mode / device type lands on; the three .rdata
strings and that the canonical source contains them byte for byte; the two
diagnostic lines; the absolute operands the fixture patches. Then checks the
COFF symbols, the native result and the receipts.
"""
import argparse
import importlib.util
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/423-input-getstate-modes'
EXP = ROOT / 'local/experiments/v2-input-getstate-423'
SRC = ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/input_state.cpp'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BODY = (0x00532e10, 293, 'f8f0b37499524cfa089f53c5d4737bd8e14e6e5e7185a7513011c03d038c3a4a')
CASES = 24

# mode n -> handler offset inside the body; type n -> size handler offset
MODES = {1: 0xc6, 2: 0xce, 3: 0xfa, 4: 0xfa, 5: 0xfa, 6: 0x4b, 7: 0xfa, 8: 0xeb}
TYPES = {1: 0x97, 2: 0x6a, 3: 0x90, 4: 0x97}
STRINGS = {0x005bb2f8: '\\real\\patch3\\pc\\input.c',
           0x005bb37c: '[INPUT] _getstate, Internal error in devicetype\n',
           0x005bb358: '[INPUT] - Invalid getstate (%d)\n'}
OPERANDS = [(0x07, 0x0069cb0c), (0x26, 0x006be040), (0x47, 0x00532f38), (0x4d, 0x006be048),
            (0x53, 0x006be048), (0x66, 0x00532f58), (0x71, 0x006be04c), (0x9f, 0x005bb37c),
            (0xa5, 0x005deb74), (0xa9, 0x005bb2f8), (0xaf, 0x005deb78), (0xb9, 0x005debf0),
            (0xcf, 0x006bde20), (0xe1, 0x006bde20), (0xfc, 0x005bb358), (0x104, 0x005deb74),
            (0x108, 0x005bb2f8), (0x10e, 0x005deb78), (0x118, 0x005debf0)]
LINES = {0xad: 0x1fa, 0x10c: 0x219}   # mov dword ptr [005deb78], imm32
EXPECTED_DEFINED = {'?fe_input_getstate_00532e10@porsche@@YAPAXII@Z',
                    '?input_poll_0056fd00@porsche@@YAIPAUInputDevice@1@@Z',
                    '?input_poll_read_0056fce0@porsche@@YAIPAUInputDevice@1@PAXI@Z',
                    '?input_read_0056fd30@porsche@@YAIPAUInputDevice@1@IPAX@Z',
                    '?input_count_0069cb0c@porsche@@3HA',
                    '?input_caps_buffer_006bde20@porsche@@3PAEA',
                    '?input_slots_006be040@porsche@@3PAUInputSlot@1@A'}


SUMMARY = None

def main():
    image = (ROOT / 'local/game/Porsche.exe').read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA
    rd = lambda va, n: image[va - 0x400000: va - 0x400000 + n]   # .text/.rdata raw == RVA
    va, size, body_sha = BODY
    body = rd(va, size)
    assert hashlib.sha256(body).hexdigest() == body_sha and body[-1] == 0xc3

    for i in range(8):
        target = struct.unpack('<I', rd(0x00532f38 + 4 * i, 4))[0]
        assert target - va == MODES[i + 1], f'mode {i + 1}: {target:08x}'
    for i in range(4):
        target = struct.unpack('<I', rd(0x00532f58 + 4 * i, 4))[0]
        assert target - va == TYPES[i + 1], f'type {i + 1}: {target:08x}'

    source = SRC.read_text(encoding='utf-8')
    for sva, text in STRINGS.items():
        raw = rd(sva, len(text) + 1)
        assert raw == text.encode('latin-1') + b'\0', f'{sva:08x}: string mismatch'
        escaped = text.replace('\\', '\\\\').replace('\n', '\\n')
        assert escaped in source, f'canonical source lacks the string at {sva:08x}'

    for off, expected in OPERANDS:
        assert struct.unpack('<I', body[off:off + 4])[0] == expected, f'+{off:x}'
    for off, line in LINES.items():
        assert body[off:off + 6] == b'\xc7\x05\x78\xeb\x5d\x00', f'+{off:x}: not a line store'
        assert struct.unpack('<I', body[off + 6:off + 10])[0] == line
        assert f'diagnostic_line_005deb78 = 0x{line:x};' in source

    summary_path = SUMMARY or RUN / 'summary.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    resolve = lambda p: Path(p) if Path(p).is_absolute() else ROOT / p
    for path_key, hash_key in [('source','source_sha256'), ('header','header_sha256'),
                               ('fixture','fixture_sha256'), ('compiler','compiler_sha256')]:
        assert sha(resolve(summary[path_key])) == summary[hash_key], f'input drift: {path_key}'
    assert resolve(summary['source']).resolve() == SRC.resolve()
    assert resolve(summary['fixture']).resolve() == (EXP / 'input_getstate_fixture.cpp').resolve()
    prepare = json.loads((EXP / 'prepare-001.json').read_text(encoding='utf-8'))
    for path, expected in prepare['input_sha256'].items():
        assert sha(resolve(path)) == expected, f'prepared input drift: {path}'
    spec = importlib.util.spec_from_file_location('coff423audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    coff = importlib.util.module_from_spec(spec); spec.loader.exec_module(coff)
    assert coff.coff_symbols(EXP / 'objects/input_state.obj') == summary['symbols'], 'COFF mismatch'
    assert '?input_caps_buffer_006bde20@porsche@@3PAEA' not in summary['symbols']['undefined']
    defined = set(summary['symbols']['defined'])
    assert EXPECTED_DEFINED <= defined, EXPECTED_DEFINED - defined
    assert all(s.startswith('??_C@') for s in defined - EXPECTED_DEFINED), 'only string literals beyond the functions'
    for gone in ('input_unrecovered_mode_00532e10', 'input_invalid_type_00532eae'):
        assert gone not in source and not any(gone in s for s in summary['symbols']['undefined'])
    assert summary['native_fixture']['cases'] == CASES == summary['native_fixture']['cases_passed']
    v = json.loads((summary_path.parent / 'validation.json').read_text(encoding='utf-8'))
    assert v['status'] == 'PASS' and v['cases_passed'] == CASES
    for name in ('compile-001', 'fixture-link-001', 'fixture-native-001'):
        receipt = json.loads((EXP / (name + '.execution.json')).read_text(encoding='utf-8'))
        assert receipt['exit_code'] == 0
        assert sha(resolve(receipt['log'])) == receipt['log_sha256'], f'log drift: {name}'
        expected_receipt = summary['compile'] if name == 'compile-001' else summary['link'] if name == 'fixture-link-001' else summary['native_fixture']['execution']
        assert receipt == expected_receipt, f'receipt mismatch: {name}'
    log = (EXP / 'fixture-native-001.log').read_text(encoding='utf-8')
    assert log.count(' OK ') == CASES and 'FAILED' not in log

    print('Run 423 verified: 00532e10 293B; 8 mode and 4 type table entries; 3 .rdata strings '
          'byte-identical in the canonical source; lines 0x1fa/0x219; 19 operands; the two removed '
          f'boundaries gone; {CASES}/{CASES} differential cases on the physical x86 slab')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--summary', type=Path)
    parser.add_argument('--experiment', type=Path)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    RUN = ROOT / 'iterations/v2/001-original-recovery/runs/423-input-getstate-modes'
    SRC = ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/input_state.cpp'
    EXP = args.experiment.resolve() if args.experiment else ROOT / 'local/experiments/v2-input-getstate-423'
    SUMMARY = args.summary.resolve() if args.summary else None
    main()
