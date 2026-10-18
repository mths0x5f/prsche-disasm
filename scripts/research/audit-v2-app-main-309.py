"""Independent acceptance audit for the app_main render driver sync (004d3420)."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/309-app-main-render-driver-sync'
OUT = ROOT / 'local/experiments/v2-app-main-309'


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
    assert summary['original_vas'] == ['004d3420'] and summary['original_selected_bytes'] == 8592

    assert summary['source_sha256'] == sha(ROOT / summary['source'])
    assert summary['header_sha256'] == sha(ROOT / summary['header'])

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    pe_bytes = pe_read(original, 0x004d3420, 8592)
    assert len(pe_bytes) == 8592

    cof = module('coff309audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects/app_main_render_driver_sync_309.obj'
    symbols = cof.coff_symbols(obj)
    assert '?execute_004d3420@RenderDriverSync_309@porsche@@QAEIPBDPAXH@Z' in symbols['defined'], symbols['defined']

    # Verify execution receipts
    receipt = json.loads((OUT / 'fixture-native-001.execution.json').read_bytes())
    assert receipt['exit_code'] == 0

    log = (ROOT / receipt['log']).read_text()
    for i in range(1, 11):
        assert f'TC {i} OK' in log

    validation = dict(
        schema=1,
        summary_sha256=sha(RUN / 'summary.json'),
        actual_pe_body_bytes=8592,
        native_cases_passed=10,
        symbols_defined=symbols['defined'],
        symbols_undefined_count=len(symbols['undefined']),
    )
    (RUN / 'validation.json').write_bytes((json.dumps(validation, indent=2) + '\n').encode())
    print('Audit 309 SUCCESS: 8,592 PE bytes, 10/10 native slab cases OK, symbols verified.')


if __name__ == '__main__':
    main()
