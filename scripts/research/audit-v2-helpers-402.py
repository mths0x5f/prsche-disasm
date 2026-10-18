"""Independent acceptance audit for Run 402 helper cluster (6 functions, 199 PE bytes)."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/402-frame-clock-helpers'
OUT = ROOT / 'local/experiments/v2-helpers-402'

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
    expected_vas = ['0046d960', '0046d9b0', '004659e0', '00471b60', '004a54e0', '004a54b0']
    assert summary['original_vas'] == expected_vas
    assert summary['original_selected_bytes'] == 199
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    targets = [
        ('0046d960', 0x0046d960, 17),
        ('0046d9b0', 0x0046d9b0, 6),
        ('004659e0', 0x004659e0, 116),
        ('00471b60', 0x00471b60, 11),
        ('004a54e0', 0x004a54e0, 5),
        ('004a54b0', 0x004a54b0, 44),
    ]

    fixture_text = (OUT / 'helpers_fixture.cpp').read_text(encoding='utf8')
    total_bytes = 0
    for name, va, sz in targets:
        pe_bytes = pe_read(original, va, sz)
        assert len(pe_bytes) == sz
        total_bytes += sz
        match = re.search(rf'kOrig_{name}\[{sz}\]\s*=\s*\{{([^}}]+)\}}', fixture_text)
        assert match is not None, name
        slab_bytes = bytes(int(x.strip()) for x in match.group(1).split(','))
        assert slab_bytes == pe_bytes, name

    assert total_bytes == 199

    coff = module('coff402_audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects' / 'frame_helpers_402.obj'
    symbols = coff.coff_symbols(obj)
    assert not symbols['common'] and not symbols['weak']
    assert any('frame_clock_predicate_0046d960' in s for s in symbols['defined'])
    assert any('frame_clock_get_items_0046d9b0' in s for s in symbols['defined'])
    assert any('frame_clock_adjust_rate_004659e0' in s for s in symbols['defined'])
    assert any('application_main_function_00471b60' in s for s in symbols['defined'])
    assert any('application_main_function_004a54e0' in s for s in symbols['defined'])
    assert any('application_main_function_004a54b0' in s for s in symbols['defined'])

    validation = json.loads((RUN / 'validation.json').read_bytes())
    assert validation['summary_sha256'] == sha(RUN / 'summary.json')
    assert validation['actual_pe_body_bytes'] == 199
    assert validation['native_cases_passed'] == 9
    assert validation['game_object_count'] == 1
    assert set(validation['actual_coff_defined_symbols']) == set(symbols['defined'])

    print(f'Run 402 verified: PE 199B across 6 functions, physical x86 slab verified, 9 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
