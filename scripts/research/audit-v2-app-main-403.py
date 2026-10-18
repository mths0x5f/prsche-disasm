"""Independent acceptance audit for Run 403 app_main helpers (4 functions, 509 PE bytes)."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/403-app-main-helpers'
OUT = ROOT / 'local/experiments/v2-app-main-403'

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
    expected_vas = ['0048da60', '004acb80', '00425780', '004b4cd0']
    assert summary['original_vas'] == expected_vas
    assert summary['original_selected_bytes'] == 509
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    targets = [
        ('0048da60', 0x0048da60, 99),
        ('004acb80', 0x004acb80, 141),
        ('00425780', 0x00425780, 135),
        ('004b4cd0', 0x004b4cd0, 134),
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

    assert total_bytes == 509

    coff = module('coff403_audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects' / 'app_main_helpers_403.obj'
    symbols = coff.coff_symbols(obj)
    assert not symbols['common'] and not symbols['weak']
    assert any('application_main_function_0048da60' in s for s in symbols['defined'])
    assert any('application_main_function_004acb80' in s for s in symbols['defined'])
    assert any('application_main_function_00425780' in s for s in symbols['defined'])
    assert any('application_main_function_004b4cd0' in s for s in symbols['defined'])

    validation = json.loads((RUN / 'validation.json').read_bytes())
    assert validation['summary_sha256'] == sha(RUN / 'summary.json')
    assert validation['actual_pe_body_bytes'] == 509
    assert validation['native_cases_passed'] == 8
    assert validation['game_object_count'] == 1
    assert set(validation['actual_coff_defined_symbols']) == set(symbols['defined'])

    print(f'Run 403 verified: PE 509B across 4 functions, physical x86 slab verified, 8 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
