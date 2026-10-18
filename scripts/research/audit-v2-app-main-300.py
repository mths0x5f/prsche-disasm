"""Independent acceptance audit for Run 300 app_main timer, display, SIMD and stream cluster (4 functions, 420 PE bytes)."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/300-app-main-timer-display'
OUT = ROOT / 'local/experiments/v2-app-main-300'

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
    expected_vas = ['0053c290', '004b6660', '00467fc0', '005366e0']
    assert summary['original_vas'] == expected_vas
    assert summary['original_selected_bytes'] == 420
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    targets = [
        ('0053c290', 0x0053c290, 77),
        ('004b6660', 0x004b6660, 99),
        ('00467fc0', 0x00467fc0, 112),
        ('005366e0', 0x005366e0, 132),
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

    assert total_bytes == 420

    coff = module('coff300_audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    obj = OUT / 'objects' / 'app_main_timer_display_300.obj'
    symbols = coff.coff_symbols(obj)
    assert not symbols['common'] and not symbols['weak']
    assert any('application_main_function_0053c290' in s for s in symbols['defined'])
    assert any('application_main_function_004b6660' in s for s in symbols['defined'])
    assert any('application_main_function_00467fc0' in s for s in symbols['defined'])
    assert any('application_main_function_005366e0' in s for s in symbols['defined'])

    validation = json.loads((RUN / 'validation.json').read_bytes())
    assert validation['summary_sha256'] == sha(RUN / 'summary.json')
    assert validation['actual_pe_body_bytes'] == 420
    assert validation['native_cases_passed'] == 10
    assert validation['game_object_count'] == 1
    assert set(validation['actual_coff_defined_symbols']) == set(symbols['defined'])

    print(f'Run 300 verified: PE 420B across 4 functions, physical x86 slab verified, 10 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
