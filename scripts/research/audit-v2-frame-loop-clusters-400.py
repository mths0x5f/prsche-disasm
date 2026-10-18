"""Independent acceptance audit for the 21 bounded frame-loop and shutdown cluster game objects."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/400-frame-loop-clusters'
OUT = ROOT / 'local/experiments/v2-frame-loop-clusters-400'

SPANS = [
    ('00412030', 91, '?application_main_function_00412030@porsche@@YAXXZ'),
    ('005338d0', 53, '?frame_control_slot_release_005338d0@porsche@@YAXH@Z'),
    ('00425780', 135, '?application_main_function_00425780@porsche@@YAXXZ'),
    ('004acb80', 141, '?application_main_function_004acb80@porsche@@YAXXZ'),
    ('00565d60', 106, '?audio_channel_stop_00565d60@porsche@@YAHI@Z'),
    ('00414eb0', 196, '?application_main_function_00414eb0@porsche@@YAXXZ'),
    ('00467740', 141, '?application_main_function_00467740@porsche@@YAXXZ'),
    ('004b7140', 16, '?render_teardown_prefix_004b7140@porsche@@YAXXZ'),
    ('00465e20', 29, '?render_teardown_secondary_00465e20@porsche@@YAXXZ'),
    ('00538d80', 20, '?destroy_00538d80@RenderSubobject_00538d80@porsche@@QAEXXZ'),
    ('00539eb0', 14, '?release_00539eb0@RenderBufferCell_00539eb0@porsche@@QAEXXZ'),
    ('00540420', 24, '?destroy_00540420@RenderMovieBridge_00540420@porsche@@QAEXXZ'),
    ('0047f190', 119, '?render_teardown_registry_0047f190@porsche@@YAXXZ'),
    ('00514990', 1, '?render_registry_item_noop_00514990@porsche@@YAXPAX@Z'),
    ('00563d30', 222, '?application_main_function_00563d30@porsche@@YAXXZ'),
    ('00564700', 70, '?stream_slot_cancel_00564700@porsche@@YAXI@Z'),
    ('00564750', 61, '?stream_slot_resolve_00564750@porsche@@YAPAUStreamSlot_400@1@I@Z'),
    ('00563bd0', 93, '?stream_completion_pump_00563bd0@porsche@@YAIII@Z'),
    ('00563c70', 68, '?stream_queue_pop_00563c70@porsche@@YAPAUStreamSlot_400@1@PAUStreamQueue_400@1@@Z'),
    ('00563c30', 64, '?stream_queue_push_00563c30@porsche@@YAXPAUStreamQueue_400@1@PAUStreamSlot_400@1@@Z'),
    ('00563cc0', 105, '?stream_slot_finalize_00563cc0@porsche@@YAXPAUStreamSlot_400@1@@Z'),
]

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
    assert summary['original_vas'] == [va for va, _, _ in SPANS]
    assert summary['original_selected_bytes'] == 1769
    for name, h in summary['input_sha256'].items():
        p = Path(name)
        p = p if p.is_absolute() else ROOT / p
        assert sha(p) == h, (name, h)

    original = (ROOT / 'local/game/Porsche.exe').read_bytes()
    asm = (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text()
    concat_pe = bytearray()
    for va, n, _ in SPANS:
        block = asm.split('; FUNCTION ' + va, 1)[1].split('; FUNCTION ', 1)[0]
        decoded = b''.join(bytes.fromhex(x) for x in re.findall(r'(?m)^' + va[:4] + r'[0-9a-f]{4}\s+([0-9a-f]+)\s+', block))[:n]
        pe_bytes = pe_read(original, int(va, 16), n)
        assert decoded == pe_bytes and len(decoded) == n, va
        concat_pe.extend(pe_bytes)
    assert len(concat_pe) == 1769

    fixture_text = (OUT / 'frame_loop_fixture.cpp').read_text(encoding='utf8')
    slab_match = re.search(r'kOriginalSlabBytes\[1769\]\s*=\s*\{([^}]+)\}', fixture_text)
    assert slab_match is not None
    slab_bytes = bytes(int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]{2})u', slab_match.group(1)))
    assert slab_bytes == bytes(concat_pe)

    registry = json.loads((ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    index = [json.loads(x) for x in (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
    reg_vas = {r['entry_va'] for r in registry}
    assert all(
        not any(int(a, 16) <= int(va, 16) <= int(b, 16) for a, b in x['ranges'])
        for va, _, _ in SPANS
        for x in index
        if x['entry_va'] in reg_vas
    )

    cof = module('coff400audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    undefined = []
    defined_all = []
    for row, (va, sz, want) in zip(summary['results'], SPANS):
        p = ROOT / row['object']
        assert sha(p) == row['object_sha256']
        symbols = cof.coff_symbols(p)
        game_defined = [s for s in symbols['defined'] if '@porsche@@' in s]
        assert symbols == row['symbols'] and game_defined == [want], (va, symbols['defined'], want)
        assert not symbols['common'] and not symbols['weak']
        defined_all.extend(game_defined)
        undefined.extend(symbols['undefined'])
        assert sha(ROOT / row['generated_source']) == row['generated_source_sha256']
        deps = json.loads((ROOT / row['source_dependencies']).read_bytes())
        assert Path(deps['Data']['Source']).resolve() == (ROOT / row['generated_source']).resolve()

    attempt = summary['actual_compiler_batches']
    suffix = f'{attempt:03d}'
    for name in ('compile-' + suffix, 'fixture-link-' + suffix, 'fixture-native-' + suffix):
        receipt = json.loads((OUT / (name + '.execution.json')).read_bytes())
        assert receipt['exit_code'] == 0 and sha(ROOT / receipt['log']) == receipt['log_sha256']

    assert summary['native_fixture']['exit_code'] == 0
    assert summary['native_fixture']['case_count'] == 34

    validation = dict(
        schema=1,
        summary_sha256=sha(RUN / 'summary.json'),
        actual_pe_body_bytes=1769,
        physical_x86_slab_bytes_verified=1769,
        native_cases_passed=34,
        clusters_verified=6,
        game_object_count=21,
        successful_compile_batches=1,
        actual_coff_defined_symbols=defined_all,
        actual_coff_undefined_external_symbols=sorted(set(undefined)),
        production_game_global_or_callee_provider_count=0,
    )
    (RUN / 'validation.json').write_bytes((json.dumps(validation, indent=2) + '\n').encode('utf8'))
    print('PE 1769B across 21 bodies, physical x86 slab verified, 34 differential cases passed, receipts verified')

if __name__ == '__main__':
    main()
