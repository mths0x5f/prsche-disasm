"""Read-only WIP canonical selector baseline for the separate Run240 pilot."""
import importlib.util
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[5]
RUNS = ROOT/'iterations/v2/001-original-recovery/runs'
RUN = RUNS/'237-crt-lock-selectors'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def main():
    hp = ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'
    spec = importlib.util.spec_from_file_location('helpers237',hp)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    pins = {}
    def pin(path, expected=None):
        path = Path(path).resolve()
        actual = h.digest(path)
        assert expected is None or expected==actual, path
        pins[path] = actual
        return path
    pin(Path(__file__))
    pin(hp)
    audit = h.module('coff237',pin(RUNS/'226-writable-scalar-storage/audit.py'))
    RUN.mkdir(parents=True,exist_ok=True)
    assert not (RUN/'summary.json').exists(), 'Fresh237 preflight required'
    old_path = pin(RUNS/'175-formatter-stdio/verification.json')
    old = json.loads(old_path.read_bytes())
    source_pins = {n:sha for n,sha in old['source_sha256'].items() if '/source/' in n}
    assert len(source_pins)==18
    for name,sha in source_pins.items():
        pin(ROOT/name,sha)
    source_path = ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_stdio.cpp'
    source = source_path.read_text(encoding='utf8')
    header_path = ROOT/'iterations/v2/001-original-recovery/source/include/porsche/formatter_stdio.hpp'
    obj_path = pin(ROOT/'local/builds/v2/formatter-stdio-175/formatter_stdio_probe.dir/Release/formatter_stdio.obj',
        '837e17652f2975e3a8ec3c2f2de8348c02dc53a7724140db7f5fd50790cadb07')
    obj = audit.coff(obj_path)
    coffpath = pin(ROOT/'scripts/research/build-v2-compile-corpus.py')
    coff = h.module('symbols237',coffpath)
    symbols = coff.coff_symbols(obj_path)
    assert not any('trace' in s.lower() for s in symbols['undefined'])
    registry = json.loads(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    assert not any(r['module']=='Porsche.exe' and r['entry_va'] in ('005a3719','005a376b') for r in registry)
    baseline_path = pin(RUNS/'233-initialized-and-nested-union/summary.json')
    baseline = json.loads(baseline_path.read_bytes())
    image = pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes()
    sections = h.sections(image)
    def offset(va):
        s = next(s for s in sections if s['va']<=va<s['va']+s['rawsize'])
        return s['raw']+va-s['va']
    asm = pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text(encoding='utf8')
    instructions = []
    for line in asm.splitlines():
        m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        if m:
            instructions.append(dict(va=m[1],bytes=m[2],instruction=m[3]))
    raw_obj = obj['bytes']
    symptr, nsym = struct.unpack_from('<II',raw_obj,8)
    strings = raw_obj[symptr+18*nsym:]
    def symbol_name(index):
        raw = raw_obj[symptr+18*index:symptr+18*index+8]
        if raw[:4]==b'\0'*4:
            return strings[struct.unpack_from('<I',raw,4)[0]:].split(b'\0',1)[0].decode()
        return raw.split(b'\0',1)[0].decode()
    rows = []
    for va, operation, boundary in [('005a3719','lock','enter'),('005a376b','unlock','leave')]:
        canonical_name = f'formatter_stdio_{operation}_index_{va}'
        canonical_symbol = f'?{canonical_name}@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z'
        symbol = next(s for s in obj['symbols'] if s['name']==canonical_symbol)
        section = obj['sections'][symbol['section']-1]
        assert section['size']==39 and section['chars']&0x1000 and section['reloc_count']==2
        reloc_at = struct.unpack_from('<I',raw_obj,20+40*(symbol['section']-1)+24)[0]
        relocs = []
        for i in range(section['reloc_count']):
            address, target, type_ = struct.unpack_from('<IIH',raw_obj,reloc_at+10*i)
            relocs.append(dict(offset=address,target=symbol_name(target),type=type_))
        assert {r['target'] for r in relocs}=={
            f'?exit_registry_{operation}_api_'+('005a4ba4' if operation=='lock' else '005a4c05')+'@porsche@@YAXI@Z',
            f'?formatter_lowio_critical_{boundary}@porsche@@YGXPAX@Z'}
        start = int(va,16)
        original = [i for i in instructions if start<=int(i['va'],16)<start+35]
        cursor = start
        for ins in original:
            raw = bytes.fromhex(ins['bytes'])
            assert int(ins['va'],16)==cursor and image[offset(cursor):offset(cursor)+len(raw)]==raw
            cursor += len(raw)
        assert cursor==start+35 and original[-1]['instruction']=='RET'
        frontier = next(r for r in baseline['frontier'] if r.get('va')==va)
        assert frontier['symbol']==f'?FUN_{va}@@YAXHH@Z'
        m = re.search(r'(?m)^void __cdecl '+canonical_name+r'\([^\n]+\) \{\n.*?\n\}',source,re.S)
        assert m
        rows.append(dict(va=va,original_bytes=35,original_instructions=original,
            source=h.relative(source_path),definition_line=source[:m.start()].count('\n')+1,
            exact_existing_definition=m.group(0),header=h.relative(header_path),
            registry_accepted_owner=False,WIP_canonical_owner=True,raw_missing_symbol=frontier['symbol'],
            referring_object_vas=frontier['referring_object_vas'],actual_canonical_symbol=canonical_symbol,
            cached_COMDAT=dict(section_index=symbol['section'],section=section,bytes=raw_obj[section['raw']:section['raw']+39].hex(),relocations=relocs),
            binding_contract='Candidate only: both cdecl two DWORD slots/void return; slot1 signed index, slot2 pointer bits; no descriptor dereference in selector. Require240 native original/typed-raw fixture before binding',
            original_dispatch='signed index<20 -> modulo32 index+28 passed to CRT lock; otherwise raw second slot+32 passed to stdcall critical-section API'))
    overlap = next(r for r in baseline['results'] if r.get('va')=='005a76a1')
    overlap_obj = pin(ROOT/overlap['object'],overlap['object_sha256'])
    overlap_symbols = coff.coff_symbols(overlap_obj)
    prefix_header = ROOT/'iterations/v2/001-original-recovery/source/include/porsche/formatter_crt_runtime.hpp'
    prefix_source = ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_crt_runtime.cpp'
    assert 'formatter_crt_locks_005e57a8[26]' in prefix_header.read_text()
    assert 'formatter_crt_locks_005e57a8[26]' in prefix_source.read_text()
    for p,sha in pins.items():
        assert h.digest(p)==sha, ('Input mutation',p)
    report = dict(schema=1,kind='canonical-WIP-selector-preflight',original_sha256=SHA,
        baseline=h.relative(baseline_path),baseline_sha256=h.digest(baseline_path),
        selected_vas=['005a3719','005a376b'],rows=rows,source_pins_matching175=source_pins,
        source_pins_matched=18,cached_owner_object=h.relative(obj_path),cached_owner_sha256=h.digest(obj_path),
        actual_cached_owner_symbols=symbols,cached_owner_uninstrumented=True,
        whole_TU=dict(function_definitions=8,data_definitions=['porsche::formatter_stdio_buffers_006afd60[2]'],
            actual_existing_VA_overlap=dict(va='005a76a1',object=overlap['object'],symbols=overlap_symbols),
            external_provider_symbols=symbols['undefined'],scope='WholeTU is not selected; no duplicate recovered algorithms or wholeTU native ownership implied'),
        real_provider_boundary=dict(published_lock_prefix=26,required_stdio_prefix=48,required_static_ids=[28,47],
            original_prefix_proof=old['canonical_lock_prefix'],current_header=h.relative(prefix_header),current_source=h.relative(prefix_source),
            production_ready=False,reason='Selector boundary proof does not expand canonical157 lock owner;48-entry extent is a proven prefix only'),
        handoff240=dict(owner='Strong agent240',approach='Mechanically extract exact existing canonical selector fragments and proven ABI binding pilot; two ordinary rows plus support; do not link wholeTU',
            pending=['Exact fragment/helper provenance and include closure','Typed int/pointer vs rawint/int native ABI fixture','Explicit provider boundaries; no real lock-table composition until prefix owner reviewed']),
        generated_CXX=0,compiler_commands=0,linker_commands=0,native_execution_commands=0,
        original_relative_layout_claim=False,input_sha256={h.relative(p):sha for p,sha in pins.items()},
        limits=['237 is an abandoned uncompiled algorithm-recovery preflight, replaced by canonical-fragment reuse in240',
                'No generated source, alias object, allocation, canonical/source/registry edit, union or production change'])
    h.write(RUN/'summary.json',report)
    h.write(RUN/'validation.json',dict(passed=True,summary_sha256=h.digest(RUN/'summary.json'),guarded_inputs=len(pins),
        mutation_guard_passed=True,source_pins_matching175=18,original_PE_matched_bytes=70,actual_canonical_COMDATs=2,
        cached_owner_uninstrumented=True,published_lock_prefix=26,required_stdio_prefix=48,
        generated_CXX=0,compiler_commands=0,native_execution_commands=0))
    print(json.dumps(dict(source_pins=18,original_bytes=70,COMDATs=2,whole_TU_overlap='005a76a1',compile=0,pins=len(pins))))


if __name__=='__main__':
    main()
