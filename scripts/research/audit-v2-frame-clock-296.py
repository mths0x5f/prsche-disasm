"""Independent acceptance audit for 00413ea0 frame-clock game object (Run 296)."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/296-frame-clock-dispatch'
OUT = ROOT / 'local/experiments/v2-frame-clock-296'

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
    assert summary['original_vas'] == ['00413ea0']
    assert summary['original_selected_bytes'] == 296
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    asm = (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text()
    block = asm.split('; FUNCTION 00413ea0', 1)[1].split('; FUNCTION ', 1)[0]
    decoded = b''.join(bytes.fromhex(x) for x in re.findall(r'(?m)^0041[0-9a-f]{4}\s+([0-9a-f]+)\s+', block))[:296]
    pe_bytes = pe_read(original, 0x00413ea0, 296)
    assert decoded == pe_bytes and len(decoded) == 296

    fixture_text = (OUT / 'frame_clock_fixture.cpp').read_text(encoding='utf8')
    slab_match = re.search(r'kOriginalBytes\[296\]\s*=\s*\{([^}]+)\}', fixture_text)
    assert slab_match is not None
    slab_bytes = bytes(int(x.strip()) for x in slab_match.group(1).split(','))
    assert slab_bytes == pe_bytes

    registry = json.loads((ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    index = [json.loads(x) for x in (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
    reg_vas = {r['entry_va'] for r in registry}
    assert all(
        not any(int(a, 16) <= 0x00413ea0 <= int(b, 16) for a, b in x['ranges'])
        for x in index
        if x['entry_va'] in reg_vas
    )

    cof = module('coff296audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    row = summary['results'][0]
    p = ROOT / row['object']
    assert sha(p) == row['object_sha256']
    symbols = cof.coff_symbols(p)
    game_defined = [s for s in symbols['defined'] if '@porsche@@' in s]
    assert game_defined == ['?application_main_function_00413ea0@porsche@@YAXXZ']
    assert not symbols['common'] and not symbols['weak']

    attempt = summary['actual_compiler_batches']
    suffix = f'{attempt:03d}'
    for name in ('compile-' + suffix, 'fixture-link-' + suffix, 'fixture-native-' + suffix):
        receipt = json.loads((OUT / (name + '.execution.json')).read_bytes())
        assert receipt['exit_code'] == 0 and sha(ROOT / receipt['log']) == receipt['log_sha256']

    assert summary['native_fixture']['exit_code'] == 0
    assert summary['native_fixture']['case_count'] == 7

    validation = dict(
        schema=1,
        summary_sha256=sha(RUN / 'summary.json'),
        actual_pe_body_bytes=296,
        physical_x86_slab_bytes_verified=296,
        native_cases_passed=7,
        game_object_count=1,
        successful_compile_batches=1,
        actual_coff_defined_symbols=game_defined,
        actual_coff_undefined_external_symbols=sorted(symbols['undefined']),
        production_game_global_or_callee_provider_count=0,
    )
    (RUN / 'validation.json').write_bytes((json.dumps(validation, indent=2) + '\n').encode('utf8'))
    print('Run 296 verified: PE 296B, 1 body, physical x86 slab verified, 7 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
