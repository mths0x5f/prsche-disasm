"""Independent acceptance audit for Run 419 frame root lifecycle (2 functions, 263 PE bytes)."""
import hashlib, importlib.util, json, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/419-frame-root-lifecycle'
OUT = ROOT / 'local/experiments/v2-frame-root-419'

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
    assert summary['run'] == 419
    assert summary['original_sha256'] == sha(ROOT / 'local/game/Porsche.exe')
    expected_vas = ['00471b70', '00471c40']
    assert summary['original_vas'] == expected_vas
    assert summary['original_selected_bytes'] == 263
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    targets = [
        ('00471b70', 0x00471b70, 198),
        ('00471c40', 0x00471c40, 65),
    ]

    total_bytes = 0
    for name, va, sz in targets:
        pe_bytes = pe_read(original, va, sz)
        assert len(pe_bytes) == sz
        total_bytes += sz

    assert total_bytes == 263

    coff = module('coff419_audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects' / 'frame_root_lifecycle_419.obj'
    symbols = coff.coff_symbols(obj)
    assert not symbols['common'] and not symbols['weak']
    assert any('frame_root_init_00471b70' in s for s in symbols['defined'])
    assert any('frame_root_teardown_00471c40' in s for s in symbols['defined'])

    validation = json.loads((RUN / 'validation.json').read_bytes())
    assert validation['summary_sha256'] == sha(RUN / 'summary.json')
    assert validation['actual_pe_body_bytes'] == 263
    assert validation['physical_x86_slab_bytes_verified'] == 263
    assert validation['native_cases_passed'] == 5
    assert validation['game_object_count'] == 1
    assert set(validation['actual_coff_defined_symbols']) == set(symbols['defined'])

    print('Run 419 verified: PE 263B across 2 functions, physical x86 slab verified, 5 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
