"""Independent acceptance audit for Run 418 heap shutdown closure (5 functions, 623 PE bytes)."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/418-heap-shutdown-closure'
OUT = ROOT / 'local/experiments/v2-heap-shutdown-418'

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
    assert summary['run'] == 418
    assert summary['original_sha256'] == sha(ROOT / 'local/game/Porsche.exe')
    expected_vas = ['0055ec30', '005678f0', '005699f0', '0059eb20', '0059ee30']
    assert summary['original_vas'] == expected_vas
    assert summary['original_selected_bytes'] == 623
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    targets = [
        ('0055ec30', 0x0055ec30, 20),
        ('005678f0', 0x005678f0, 248),
        ('005699f0', 0x005699f0, 72),
        ('0059eb20', 0x0059eb20, 159),
        ('0059ee30', 0x0059ee30, 124),
    ]

    fixture_text = (OUT / 'heap_shutdown_fixture.cpp').read_text(encoding='utf8')
    total_bytes = 0
    for name, va, sz in targets:
        pe_bytes = pe_read(original, va, sz)
        assert len(pe_bytes) == sz
        total_bytes += sz
        match = re.search(rf'kOrig_{name}\[{sz}\]\s*=\s*\{{([^}}]+)\}}', fixture_text)
        assert match is not None, name
        raw_items = [x.strip() for x in match.group(1).split(',') if x.strip()]
        slab_bytes = bytes(int(x, 0) for x in raw_items)
        assert slab_bytes == pe_bytes, name

    assert total_bytes == 623

    coff = module('coff418_audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects' / 'heap_shutdown_418.obj'
    symbols = coff.coff_symbols(obj)
    assert not symbols['common'] and not symbols['weak']
    assert any('printf_shutdown_0055ec30' in s for s in symbols['defined'])
    assert any('application_pool_shutdown_005678f0' in s for s in symbols['defined'])
    assert any('heap_destroy_slot_005699f0' in s for s in symbols['defined'])
    assert any('queue_drain_0059ee30' in s for s in symbols['defined'])
    assert any('platform_flush_0059eb20' in s for s in symbols['defined'])

    validation = json.loads((RUN / 'validation.json').read_bytes())
    assert validation['summary_sha256'] == sha(RUN / 'summary.json')
    assert validation['actual_pe_body_bytes'] == 623
    assert validation['physical_x86_slab_bytes_verified'] == 623
    assert validation['native_cases_passed'] == 8
    assert validation['game_object_count'] == 1
    assert set(validation['actual_coff_defined_symbols']) == set(symbols['defined'])

    print('Run 418 verified: PE 623B across 5 functions, physical x86 slab verified, 8 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
