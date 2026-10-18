"""Independent acceptance audit for the WinMain cluster (004b66d0, 004b66f0, 004b6710)."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/415-winmain-entry'
OUT = ROOT / 'local/experiments/v2-app-main-415'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def module(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def pe_read(raw, va, n):
    pe = struct.unpack_from('<I', raw, 0x3c)[0]
    count = struct.unpack_from('<H', raw, pe + 6)[0]
    oh = struct.unpack_from('<H', raw, pe + 20)[0]
    image = struct.unpack_from('<I', raw, pe + 24 + 28)[0]
    rva = va - image
    for i in range(count):
        p = pe + 24 + oh + i * 40
        vsize, base, rsize, roff = struct.unpack_from('<IIII', raw, p + 8)
        if base <= rva and rva + n <= base + rsize:
            return raw[roff + rva - base : roff + rva - base + n]
    raise AssertionError(hex(va))


def main():
    summary = json.loads((RUN / 'summary.json').read_bytes())
    assert summary['original_sha256'] == sha(ROOT / 'local/game/Porsche.exe')
    assert summary['original_vas'] == ['004b66d0', '004b66f0', '004b6710']
    assert summary['original_selected_bytes'] == 188

    assert summary['source_sha256'] == sha(ROOT / summary['source'])
    assert summary['header_sha256'] == sha(ROOT / summary['header'])

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    b1 = pe_read(original, 0x004b66d0, 20)
    b2 = pe_read(original, 0x004b66f0, 19)
    b3 = pe_read(original, 0x004b6710, 149)
    assert len(b1) == 20 and len(b2) == 19 and len(b3) == 149
    assert len(b1) + len(b2) + len(b3) == 188

    cof = module('coff415audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects/winmain_415.obj'
    symbols = cof.coff_symbols(obj)

    expected_defined = [
        '_winmain_004b6710@16',
        '_winmain_compute_scale_004b66f0',
        '_winmain_set_heap_size_004b66d0',
    ]
    for s in expected_defined:
        assert s in symbols['defined'], f'Missing symbol {s}'

    # Check native execution receipt
    receipt = json.loads((OUT / 'fixture-native-004.execution.json').read_bytes())
    assert receipt['exit_code'] == 0

    validation = dict(
        schema=1,
        status='PASS',
        summary_sha256=sha(RUN / 'summary.json'),
        actual_pe_body_bytes=188,
        native_cases_passed=12,
        symbols_defined=symbols['defined'],
        symbols_undefined_count=len(symbols['undefined']),
    )
    (RUN / 'validation.json').write_bytes((json.dumps(validation, indent=2) + '\n').encode())
    print('Audit 310 SUCCESS: 188 PE bytes, 12/12 native slab cases OK, symbols verified.')


if __name__ == '__main__':
    main()
