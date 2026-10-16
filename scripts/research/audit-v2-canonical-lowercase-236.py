"""Read-only canonical lowercase feasibility; no native tool invocation."""
import importlib.util
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT/'iterations/v2/001-original-recovery/runs'
RUN = RUNS/'236-canonical-lowercase-contract'
SRC = ROOT/'iterations/v2/001-original-recovery/source'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
STATE = {
    '006afd80':('formatter_text_locale_006afd80','uint32','formatter_text.cpp'),
    '006c02e4':('formatter_text_locale_writer_006c02e4','uint32','formatter_text.cpp'),
    '006c02e8':('formatter_text_locale_readers_006c02e8','int32','formatter_text.cpp'),
    '005b2258':('formatter_text_increment_005b2258','stdcall int32(int32*) pointer','formatter_text.cpp'),
    '005b2254':('formatter_text_decrement_005b2254','stdcall int32(int32*) pointer','formatter_text.cpp'),
    '005e52d0':('formatter_ctype_table_005e52d0','mutable pointer to const uint8','formatter_parser.cpp'),
    '005e54dc':('formatter_float_character_width_005e54dc','int32','formatter_float_helpers.cpp'),
}


def main():
    spec = importlib.util.spec_from_file_location('h236', ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py')
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    pins = {}
    def read(path, expected=None):
        path = Path(path).resolve()
        raw = path.read_bytes()
        digest = h.digest(path)
        assert expected is None or expected==digest, path
        pins[path] = digest
        return raw
    read(Path(__file__))
    read(Path(h.__file__))
    RUN.mkdir(parents=True, exist_ok=True)
    assert not (RUN/'summary.json').exists(), 'Fresh236 summary required'
    image = read(ROOT/'local/game/Porsche.exe',SHA)
    sections = h.sections(image)
    def memory(va, n=4):
        s = next(s for s in sections if s['va']<=va and va+n<=s['va']+s['size'])
        backed = va+n<=s['va']+s['rawsize']
        offset = s['raw']+va-s['va']
        return dict(section=s['name'],flags=f"{s['flags']:08x}",file_backed=backed,
                    bits=image[offset:offset+n].hex() if backed else None,
                    virtual_zero_fill=not backed)
    def offset(va):
        s = next(s for s in sections if s['va']<=va<s['va']+s['rawsize'])
        return s['raw']+va-s['va']
    baseline_path = RUNS/'233-initialized-and-nested-union/summary.json'
    baseline = json.loads(read(baseline_path))
    assert baseline['original_sha256']==SHA
    registry_path = SRC/'recovered/functions.json'
    registry = json.loads(read(registry_path))['functions']
    owner = next(r for r in registry if r['module']=='Porsche.exe' and r['entry_va']=='005a2248')
    source_path = ROOT/owner['source']
    source = read(source_path).decode()
    include_root = SRC/'include'
    headers = {}
    def header(path):
        if path in headers:
            return
        text = read(path).decode()
        headers[path] = text
        for name in re.findall(r'^#include "(porsche/[^\n]+)"',text,re.M):
            header(include_root/name)
    header(include_root/'porsche/formatter_text.hpp')
    canonical_sources = {}
    for name in ['formatter_text.cpp','formatter_parser.cpp','formatter_float_helpers.cpp',
                 'formatter_locale.cpp','formatter_output.cpp','formatter_search.cpp',
                 'formatter_float_parse.cpp','formatter_crt_runtime.cpp']:
        path = SRC/'recovered/Porsche.exe'/name
        canonical_sources[path] = read(path).decode()
    platform_path = SRC/'platform/formatter_crt_links.cpp'
    canonical_sources[platform_path] = read(platform_path).decode()
    read(RUNS/'158-formatter-text/README.md')
    read(RUNS/'158-formatter-text/verification.json')
    read(RUNS/'162-formatter-locale/README.md')
    read(RUNS/'166-formatter-output/README.md')
    corpus_path = ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm'
    lines = read(corpus_path).decode().splitlines()
    instructions = []
    for line in lines:
        m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        if m:
            instructions.append(dict(va=m[1],bytes=m[2],instruction=m[3]))
    body = [i for i in instructions if 0x5a2248<=int(i['va'],16)<=0x5a22b6]
    cursor = 0x5a2248
    for i in body:
        raw = bytes.fromhex(i['bytes'])
        assert int(i['va'],16)==cursor and image[offset(cursor):offset(cursor)+len(raw)]==raw
        cursor += len(raw)
    assert cursor==0x5a22b7 and body[-1]['instruction']=='RET'
    callers = []
    for i, ins in enumerate(instructions):
        if ins['instruction']=='CALL 0x005a2248':
            window = instructions[max(0,i-4):i+7]
            for x in window:
                pc, raw = int(x['va'],16), bytes.fromhex(x['bytes'])
                assert image[offset(pc):offset(pc)+len(raw)]==raw
            callers.append(dict(callsite=ins['va'],window=window))
    assert len(callers)==39
    parser_path = ROOT/'scripts/research/build-v2-compile-corpus.py'
    read(parser_path)
    parser = h.module('coff236',parser_path)
    census = json.loads(read(RUNS/'224-canonical-owner-bindings/summary.json'))
    old = next(r for r in census['rows'] if r['va']=='005a2248')['native_object']
    obj_path = ROOT/old['object']
    raw_obj = read(obj_path,old['object_sha256'])
    native = parser.coff_symbols(obj_path)
    assert '?formatter_text_read_trace@@YAXPBXII@Z' in native['undefined']
    consumer_rows = []
    missing = next(r for r in baseline['frontier'] if r.get('va')=='005a2248')
    assert missing['symbol']=='?FUN_005a2248@@YAHH@Z'
    for va in missing['referring_object_vas']:
        r = next(r for r in baseline['results'] if r['va']==va)
        p = ROOT/r['object']
        read(p,r['object_sha256'])
        actual = parser.coff_symbols(p)
        assert missing['symbol'] in actual['undefined']
        for path in r['include_closure']:
            read(ROOT/path,baseline['input_sha256'][path])
        consumer_rows.append(dict(va=va,object=r['object'],object_sha256=r['object_sha256'],actual_undefined_symbol=missing['symbol']))
    # Read actual PE import descriptors/thunks, not a name guessed from the slot.
    pe = struct.unpack_from('<I',image,0x3c)[0]
    base = struct.unpack_from('<I',image,pe+52)[0]
    imports_rva = struct.unpack_from('<I',image,pe+24+96+8)[0]
    imports = {}
    at = offset(base+imports_rva)
    while True:
        lookup,stamp,chain,name,first = struct.unpack_from('<IIIII',image,at)
        if not any((lookup,stamp,chain,name,first)):
            break
        dll = image[offset(base+name):].split(b'\0',1)[0].decode()
        n = 0
        while True:
            thunk = struct.unpack_from('<I',image,offset(base+(lookup or first)+4*n))[0]
            if not thunk:
                break
            slot = f'{base+first+4*n:08x}'
            if slot in ('005b2254','005b2258'):
                assert not thunk&0x80000000
                impname = image[offset(base+thunk)+2:].split(b'\0',1)[0].decode()
                imports[slot] = dict(dll=dll,symbol=impname,iat_va=slot,unbound_file_bits=memory(int(slot,16))['bits'])
            n += 1
        at += 20
    assert imports['005b2258']['symbol']=='InterlockedIncrement' and imports['005b2254']['symbol']=='InterlockedDecrement'
    assert all(r['dll'].lower()=='kernel32.dll' for r in imports.values())
    state_rows = []
    for va,(name,type_,provider) in STATE.items():
        current = []
        for r in baseline['results']:
            for direction in ('defined','undefined'):
                for symbol in r['symbols'][direction]:
                    if va in symbol:
                        current.append(dict(object=r['object'],va=r.get('va'),direction=direction,symbol=symbol))
        refs = [i for i in instructions if '0x'+va in i['instruction'].lower()]
        usages = []
        for path,text in canonical_sources.items():
            usages.extend(dict(source=h.relative(path),line=i+1,text=line.strip()) for i,line in enumerate(text.splitlines()) if name in line)
        state_rows.append(dict(va=va,canonical_name='porsche::'+name,type=type_,provider=h.relative(SRC/'recovered/Porsche.exe'/provider),
            original_memory=memory(int(va,16)),original_indexed_references=refs,canonical_source_usages=usages,
            actual_cached_owner_symbol_mentions=[s for direction in ('defined','undefined') for s in native[direction] if name in s],
            current233_symbol_mentions=current,iat_import=imports.get(va),
            coalescing_requirement='One mutable original-address identity shared across canonical and any future raw/native consumers; no aliases emitted',
            current_binding_status='No233 native symbol mentions this address; no existing raw-to-canonical storage binding'))
        assert not current
    pointer_bits = memory(0x5e52d0)['bits']
    table_va = int.from_bytes(bytes.fromhex(pointer_bits),'little')
    table_source = canonical_sources[SRC/'recovered/Porsche.exe/formatter_parser.cpp']
    initializer = re.search(r'kInitialCtypeTable\[512\]\s*=\s*\{([^}]+)\}',table_source).group(1)
    table = bytes(int(x,16) for x in re.findall(r'0x([0-9a-fA-F]{2})',initializer))
    assert len(table)==512 and table==image[offset(table_va):offset(table_va)+512]
    assert image[offset(table_va-2):offset(table_va)]==b'\0\0'
    overlap = []
    for va in ['005a2210','005a2e70','005a2870']:
        r = next(r for r in baseline['results'] if r.get('va')==va)
        p = ROOT/r['object']
        read(p,r['object_sha256'])
        symbols = parser.coff_symbols(p)
        overlap.append(dict(va=va,existing_object=r['object'],actual_defined_symbols=symbols['defined']))
    blockers = [
        dict(id='instrumented-cache',evidence='Actual cached COFF has undefined formatter_text_read_trace; do not link it as production owner'),
        dict(id='ctype-EOF-prefix',evidence='Original pointer005e52d0→005e52da with valid0000 WORD at005e52d8; canonical512-byte table starts at index0 and has no explicit preceding EOF word. Private158 replaces pointer with a514-byte arena; initial production predecessor storage is not thereby established'),
        dict(id='canonical-provider-closure',evidence='Eight nontrace native dependencies require accepted CRT lock19, ctype/width, locale map/type and atomic platform providers;233 contains no corresponding original-address state symbols. No namespace/storage coalescing contract is installed'),
        dict(id='whole-TU-ownership',evidence='Whole canonicalTU includes005a2210/005a2e70/005a2870 already ordinary-compiled under different names. Canonical/native VA ownership policy is needed before linking wholeTU'),
    ]
    for path,digest in pins.items():
        assert h.digest(path)==digest, ('Input mutation',path)
    report = dict(schema=1,kind='canonical-lowercase-contract',original_sha256=SHA,
        baseline=h.relative(baseline_path),baseline_sha256=h.digest(baseline_path),canonical_owner=owner,
        original_entry=dict(va='005a2248',bytes=111,instructions=body,abi='cdecl one signed int32 stack slot, EAX int32 result, RET0; EBX/ESI/EDI preserved by indexed body'),
        incoming_original_call_sites=callers,current_native_consumers=consumer_rows,
        missing_symbol=missing['symbol'],canonical_target_symbol='?formatter_float_lower_005a2248@porsche@@YAHH@Z',
        cached_owner=dict(object=h.relative(obj_path),object_sha256=h.digest(obj_path),symbols=native,instrumented=True,usable=False),
        project_header_closure=[h.relative(p) for p in headers],state_contracts=state_rows,
        exact_PE_IAT_imports=imports,ctype_initializer_contract=dict(pointer_cell='005e52d0',original_table_va=f'{table_va:08x}',
            original_EOF_prefix_va=f'{table_va-2:08x}',original_EOF_prefix_bits='0000',canonical_bytes=512,
            canonical512_bytes_match=True,canonical_EOF_predecessor_storage_proven=False),
        whole_TU_existing_VA_implementations=overlap,blockers=blockers,
        decision='Do not compile/bind in236: shared initial ctype/state/provider and whole-TU ownership closure not established',
        next_trace=['First prove/fix canonical initial EOF table storage with original514-byte layout and canonical pointer identity; separate authorized packet',
                    'Select one canonical storage/provider composition for seven state identities, stdcall IAT slots and CRT lock19; inspect current raw consumers before any alias',
                    'Review three whole-TU existing VA implementations and object-selection policy, then permit an uninstrumented compile plus original/native state-mutation fixture'],
        compiler_commands=0,native_execution_commands=0,link_commands=0,ghidra_commands=0,
        input_sha256={h.relative(p):digest for p,digest in pins.items()},
        limits=['Read-only feasibility; no source/header/registry edits, aliases, new storage, union changes or new behavior',
                'No whole-program computed-pointer/alias/loader/lifetime proof inferred from address navigation'])
    h.write(RUN/'summary.json',report)
    h.write(RUN/'validation.json',dict(passed=True,summary_sha256=h.digest(RUN/'summary.json'),guarded_inputs=len(pins),
        mutation_guard_passed=True,actual_original_entry_bytes=111,actual_PE_matched_incoming_calls=39,
        actual_native_consumer_objects=2,actual_instrumented_owner_objects=1,actual_existing_VA_objects=3,
        exact_PE_IAT_slots=2,canonical_table_bytes_matched=512,compiler_commands=0,native_execution_commands=0))
    print(json.dumps(dict(decision=report['decision'],original_calls=39,consumer_objects=2,state_identities=7,blockers=len(blockers),pins=len(pins))))


if __name__=='__main__':
    main()
