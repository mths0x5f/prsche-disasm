"""Independent acceptance audit for Run 301 app_main subsystem small cluster (4 functions, 635 PE bytes)."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/301-app-main-subsystem-small'
OUT = ROOT / 'local/experiments/v2-app-main-301'

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
    expected_vas = ['0048e6f0', '004a6960', '004a5410', '004d1a90']
    assert summary['original_vas'] == expected_vas
    assert summary['original_selected_bytes'] == 635
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    targets = [
        ('0048e6f0', 0x0048e6f0, 153),
        ('004a6960', 0x004a6960, 153),
        ('004a5410', 0x004a5410, 157),
        ('004d1a90', 0x004d1a90, 172),
    ]

    fixture_text = (OUT / 'app_main_fixture.cpp').read_text(encoding='utf8')
    total_bytes = 0
    for name, va, sz in targets:
        pe_bytes = pe_read(original, va, sz)
        assert len(pe_bytes) == sz
        total_bytes += sz
        match = re.search(rf'kOrig_{name}\[{sz}\]\s*=\s*\{{([^}}]+)\}}', fixture_text)
        assert match is not None, name
        slab_bytes = bytes(int(x.strip()) for x in match.group(1).split(','))
        assert slab_bytes == pe_bytes, name

    assert total_bytes == 635

    coff = module('coff301_audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects' / 'app_main_subsystem_small_301.obj'
    symbols = coff.coff_symbols(obj)
    assert not symbols['common'] and not symbols['weak']
    assert any('update_mode_0048e6f0' in s for s in symbols['defined'])
    assert any('application_main_function_004a6960' in s for s in symbols['defined'])
    assert any('application_main_function_004a5410' in s for s in symbols['defined'])
    assert any('init_004d1a90' in s for s in symbols['defined'])

    validation = json.loads((RUN / 'validation.json').read_bytes())
    assert validation['summary_sha256'] == sha(RUN / 'summary.json')
    assert validation['actual_pe_body_bytes'] == 635
    assert validation['native_cases_passed'] == 10
    assert validation['game_object_count'] == 1
    assert set(validation['actual_coff_defined_symbols']) == set(symbols['defined'])

    print(f'Run 301 verified: PE 635B across 4 functions, physical x86 slab verified, 10 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
