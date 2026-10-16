"""Independent read-only acceptance of canonical fragments, COFF aliases and oracle."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT/'iterations/v2/001-original-recovery/runs'
RUN = RUNS/'240-canonical-lock-reuse'
OUT = ROOT/'local/experiments/v2-canonical-lock-reuse-240'
EXPECTED_SHA = 'e55111c22a4f6ce2d2b23fb868635c71c7c7a3e1ae4dcbe45ad5fec0f759d27c'
VAS = ['005a3719','005a376b']
digest = lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    import capstone
    spec = importlib.util.spec_from_file_location('audit226',RUNS/'226-writable-scalar-storage/audit.py')
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    spec = importlib.util.spec_from_file_location('coff240audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    summary_path,binding_path = RUN/'summary.json',RUN/'bindings/summary.json'
    s,b,p = [json.loads(x.read_bytes()) for x in [summary_path,binding_path,RUN/'proof-before-compile.json']]
    assert digest(summary_path)==EXPECTED_SHA==b['ordinary_summary_sha256']
    assert s['compiled_vas']==VAS and s['objects_compiled']==2 and len(s['results'])==2
    assert s['actual_compiler_batches']==1 and not s['actual_parallel_compilation'] and s['recompilations']==0
    assert s['resumed_existing_successful_compile'] and not s['production_ready'] and not b['production_ready']
    inputs = dict(s['input_sha256'])
    for name,sha in b['input_sha256'].items():
        assert name not in inputs or inputs[name]==sha
        inputs[name]=sha
    for name,sha in inputs.items():
        assert digest(ROOT/name)==sha, ('Current input closure drift',name)
    assert len(p['canonical175_project_pins'])==18
    for name,sha in p['canonical175_project_pins'].items():
        assert digest(ROOT/name)==sha
    source = (ROOT/p['canonical_source']).read_bytes()
    assert digest(ROOT/p['canonical_source'])==p['canonical_source_sha256']
    actual_fragment_rows = []
    for row in s['results']:
        parts = p['mechanically_copied_slices'][row['va']]
        for part in parts:
            if part['kind']=='canonical_bytes':
                raw = source[part['offset']:part['offset']+part['length']]
                assert hashlib.sha256(raw).hexdigest()==part['sha256'] and raw==part['text'].encode('utf8')
            else:
                assert part['kind']=='wrapper' and part['text'] in ('namespace porsche {\nnamespace {\n','}\n')
        generated = ''.join(part['text'] for part in parts).encode('utf8')
        assert (ROOT/row['generated_source']).read_bytes()==generated
        assert digest(ROOT/row['generated_source'])==row['generated_source_sha256']
        for name,sha in row['dependency_sha256'].items():
            assert digest(ROOT/name)==sha
        actual = c.coff_symbols(ROOT/row['object'])
        assert actual==row['symbols'] and digest(ROOT/row['object'])==row['object_sha256']
        assert len(actual['defined'])==1 and 'formatter_stdio_'+('lock' if row['va']==VAS[0] else 'unlock')+'_index_' in actual['defined'][0]
        assert not any('trace' in name or '005a76a1' in name or 'buffers_' in name for name in actual['defined']+actual['undefined'])
        assert row['owned_error_count']==0 and row['owned_warning_count']==0 and row['compiler_exit_code']==0
        actual_fragment_rows.append(dict(va=row['va'],object=row['object'],object_sha256=row['object_sha256'],actual_symbols=actual))
    actual_aliases = []
    for alias,row in zip(b['aliases'],b['support_objects']):
        assert alias['support_object_id']==row['id'] and alias['va'] in VAS
        assert alias['to']==next(r['symbols']['defined'][0] for r in s['results'] if r['va']==alias['va'])
        assert alias['from']=='?FUN_'+alias['va']+'@@YAXHH@Z'
        assert digest(ROOT/row['object'])==row['object_sha256']
        assert digest(ROOT/row['generated_source'])==row['generated_source_sha256']
        actual = c.coff_symbols(ROOT/row['object'])
        assert actual==row['symbols'] and not any(actual.values())
        obj = h.coff(ROOT/row['object'])
        sec = next(x for x in obj['sections'] if x['name']=='.drectve')
        directive = obj['bytes'][sec['raw']:sec['raw']+sec['size']].decode('ascii').strip()
        assert directive=='/alternatename:'+alias['from']+'='+alias['to']==alias['directive']==row['directive']
        assert all(not x['reloc_count'] and not x['chars']&0xa0000000 and
            (not x['size'] or x['name'] in ('.drectve','.debug$S','.chks64')) for x in obj['sections'])
        actual_aliases.append(dict(va=alias['va'],directive=directive,object_sha256=obj['sha256']))
    original = h.pe(ROOT/'local/game/Porsche.exe')
    assert original['sha256']==s['original_sha256']==p['original_sha256']
    def pe_offset(image,address):
        rva = address-image['image_base']
        sec = next(x for x in image['sections'] if x['va']<=rva< x['va']+x['raw_size'])
        return sec['raw']+rva-sec['va']
    matched = 0
    for va,ins in p['original_instructions'].items():
        for i in ins:
            raw = bytes.fromhex(i['bytes'])
            at = pe_offset(original,int(i['va'],16))
            assert original['bytes'][at:at+len(raw)]==raw
            matched += len(raw)
        if va in VAS:
            assert len(ins)==13 and sum(len(i['bytes'])//2 for i in ins)==35
            assert [i['bytes'] for i in ins if i['instruction'].startswith('RET')]==['c3','c3']
    assert len(p['indexed_callers'])==8
    for caller in p['indexed_callers']:
        address = int(caller['from_va'],16)
        at = pe_offset(original,address)
        assert original['bytes'][at]==0xe8
        target = address+5+struct.unpack_from('<i',original['bytes'],at+1)[0]
        assert target==int(caller['to_function'],16)
    image = original['bytes']
    peoff = struct.unpack_from('<I',image,0x3c)[0]
    import_rva = struct.unpack_from('<I',image,peoff+24+96+8)[0]
    pos = pe_offset(original,original['image_base']+import_rva)
    actual_imports = {}
    while True:
        lookup,stamp,chain,name,first = struct.unpack_from('<IIIII',image,pos)
        if not any((lookup,stamp,chain,name,first)):
            break
        dll = image[pe_offset(original,original['image_base']+name):].split(b'\0',1)[0].decode()
        n = 0
        while True:
            thunk = struct.unpack_from('<I',image,pe_offset(original,original['image_base']+(lookup or first)+4*n))[0]
            if not thunk:
                break
            slot = original['image_base']+first+4*n
            if slot in (0x5b2078,0x5b206c):
                assert not thunk&0x80000000
                impname = image[pe_offset(original,original['image_base']+thunk)+2:].split(b'\0',1)[0].decode()
                actual_imports[f'{slot:08x}']=dict(dll=dll,symbol=impname)
            n += 1
        pos += 20
    assert actual_imports=={'005b2078':dict(dll='KERNEL32.dll',symbol='EnterCriticalSection'),
                           '005b206c':dict(dll='KERNEL32.dll',symbol='LeaveCriticalSection')}
    fixture_obj = h.coff(OUT/'objects/native-fixture.obj')
    raw = fixture_obj['bytes']
    sp,nsym = struct.unpack_from('<II',raw,8)
    strings = raw[sp+18*nsym:]
    def symbol_name(index):
        value = raw[sp+18*index:sp+18*index+8]
        if value[:4]==b'\0'*4:
            value = strings[struct.unpack_from('<I',value,4)[0]:]
        return value.split(b'\0',1)[0].decode()
    normalized = []
    raw_sym = next(x for x in fixture_obj['symbols'] if x['name']=='?raw_edge240@@YAXPAXHI@Z')
    raw_sec = fixture_obj['sections'][raw_sym['section']-1]
    raw_edge = raw[raw_sec['raw']:raw_sec['raw']+raw_sec['size']]
    assert bytes.fromhex('5251bbd3926b17be81043ca5bf2fb7e059bde58a13c7ffd0') in raw_edge
    for va,operation,slot in [(VAS[0],'lock','enter'),(VAS[1],'unlock','leave')]:
        name = '?original_'+operation+'240@porsche@@YAXHH@Z'
        sym = next(x for x in fixture_obj['symbols'] if x['name']==name)
        sec = fixture_obj['sections'][sym['section']-1]
        assert sym['value']==0 and sec['size']==35 and sec['reloc_count']==2
        pointer = struct.unpack_from('<I',raw,20+40*(sym['section']-1)+24)[0]
        relocs = []
        for i in range(sec['reloc_count']):
            offset,index,type_ = struct.unpack_from('<IIH',raw,pointer+10*i)
            relocs.append(dict(offset=offset,target=symbol_name(index),type=type_))
        api_va = '005a4ba4' if operation=='lock' else '005a4c05'
        assert relocs==[dict(offset=14,target='?exit_registry_'+operation+'_api_'+api_va+'@porsche@@YAXI@Z',type=20),
                        dict(offset=30,target='?'+slot+'_slot240@@3P6GXPAX@ZA',type=6)]
        compiled = bytearray(raw[sec['raw']:sec['raw']+35])
        expected = bytearray.fromhex(''.join(i['bytes'] for i in p['original_instructions'][va]))
        # Normalize only the independently typed CALL REL32 and absolute IAT slot.
        for at in (14,30):
            compiled[at:at+4]=b'\0'*4
            expected[at:at+4]=b'\0'*4
        assert compiled==expected
        normalized.append(dict(va=va,bytes=35,normalized_bytes=compiled.hex(),relocations=relocs))
    log_path = ROOT/s['compiler_log']
    log = log_path.read_text(encoding='utf8')
    assert digest(log_path)==s['compiler_log_sha256'] and b'\r' not in log_path.read_bytes()
    warnings = re.findall(r'warning ([CD]\d+)',log)
    assert sorted(warnings)==['C4731','C4731','D9030'] and not re.search(r'error [CD]\d+',log)
    for line in log.splitlines():
        if 'warning C4731' in line:
            assert 'native-fixture.cpp' in line and 'raw_edge240' in line
    headers = set()
    for line in log.splitlines():
        if not re.search(r'(?:including file|включение файла):',line,re.I):
            continue
        m = re.search(r'([A-Za-z]:[\\/].*?)\s*$',line)
        if m:
            path = Path(m[1]).resolve()
            if path.is_file():
                headers.add(path)
    assert len(headers)==28
    for row in s['results']:
        assert headers=={(ROOT/name).resolve() for name in row['dependency_sha256'] if not name.endswith('.cpp')}
    execution = json.loads((ROOT/s['compiler_execution_receipt']).read_bytes())
    assert execution['exit_code']==0 and execution['command']==s['compiler_command']==b['compiler_command']
    assert execution['elapsed_seconds']==s['compile_seconds']==2.0717989000258967
    assert '/MP6' in execution['command'] and '/showIncludes' in execution['command'] and 'D9030' in log
    # Statically inspect the captured driver constant without importing/executing it.
    def fixture_constant(path):
        tree = ast.parse(Path(path).read_text(encoding='utf8'))
        node = next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FIXTURE' for t in n.targets))
        return ast.literal_eval(node.value)
    fixture_source = (OUT/'native-fixture.cpp').read_text(encoding='utf8')
    assert fixture_source==fixture_constant(ROOT/s['captured_compile_driver'])
    assert fixture_source==fixture_constant(ROOT/'scripts/research/experiment-v2-canonical-lock-reuse-240.py')
    for token in ['cases240!=2268u','typed_calls240!=2268u','raw_calls240!=6804u','provider_calls240!=9072u',
                  'raw[0]!=canonical[0]||raw[1]!=canonical[1]','seen_sp240!=save_sp240-8','clean_sp240!=save_sp240',
                  'seen_bp240!=0xc7138ae5u','seen_bx240!=0x176b92d3u','seen_si240!=0xa53c0481u','seen_di240!=0x59e0b72fu']:
        assert token in fixture_source
    fixture = h.pe(ROOT/s['fixture']['executable'])
    assert fixture['sha256']==s['fixture']['executable_sha256']
    mapping = (OUT/'native-fixture.map').read_text(encoding='utf8')
    addresses = {}
    for line in mapping.splitlines():
        m = re.match(r'\s*[0-9a-f]{4}:[0-9a-f]{8}\s+(\S+)\s+([0-9a-f]{8})\b',line,re.I)
        if m:
            addresses[m[1]]=int(m[2],16)
    for alias in b['aliases']:
        assert addresses[alias['from']]==addresses[alias['to']]
    native = json.loads((OUT/'fixture-native.execution.json').read_bytes())
    linked = json.loads((OUT/'fixture-link.execution.json').read_bytes())
    assert native['exit_code']==linked['exit_code']==0 and native['command']==[str((ROOT/s['fixture']['executable']).resolve())]
    assert native['elapsed_seconds']==s['fixture']['seconds'] and s['fixture']['cases']==2268
    assert '/OPT:NOREF' in linked['command']
    owner_header = ROOT/p['table_prefix']['owner']
    assert 'formatter_crt_locks_005e57a8[26]' in owner_header.read_text()
    assert p['table_prefix']['published']==26 and p['table_prefix']['required']==48 and not p['table_prefix']['production_ready']
    validation = dict(schema=1,passed=True,summary_sha256=digest(summary_path),bindings_summary_sha256=digest(binding_path),
        audit_script_sha256=digest(Path(__file__)),input_pins_checked=len(inputs),canonical175_pins_checked=18,
        exact_canonical_fragments=True,original_entry_bytes=70,original_and_caller_bytes_PE_matched=matched,indexed_callers=8,
        ordinary_COFF_objects=actual_fragment_rows,directive_only_COFF_objects=actual_aliases,
        actual_fixture_original_oracles=normalized,actual_header_closure=28,
        actual_PE_imports=actual_imports,actual_fixture_COFF_nonvolatile_marker_sequence=True,
        actual_compiler_batches=1,actual_parallel_compilation=False,compiler_exit_code=0,compiler_seconds=execution['elapsed_seconds'],
        warnings=dict(game=0,fixture=['C4731','C4731'],driver=['D9030']),
        native_fixture_cases=2268,alias_address_identity=True,ESP_and_nonvolatile_fixture_checks=True,native_fixture_exit=0,
        fixture_sha256=fixture['sha256'],published_lock_prefix=26,required_stdio_prefix=48,production_ready=False,
        compiler_commands_this_audit=0,native_commands_this_audit=0,linker_commands_this_audit=0,Ghidra_commands_this_audit=0)
    # Recheck only these two frozen summaries after reads; other input pins were
    # inspected once, avoiding a second full closure hash pass.
    assert digest(summary_path)==EXPECTED_SHA and digest(binding_path)==validation['bindings_summary_sha256']
    (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
    (RUN/'bindings/validation.json').write_text(json.dumps(dict(schema=1,passed=True,summary_sha256=digest(binding_path),
        ordinary_summary_sha256=EXPECTED_SHA,audit_script_sha256=digest(Path(__file__)),aliases_checked=2,
        actual_COFF_directives=[r['directive'] for r in actual_aliases],native_alias_identity=True,
        native_fixture_cases=2268,ordinary_COFFs=2,support_COFFs=2,production_ready=False),indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(passed=True,input_pins=len(inputs),exact_original_oracle_bytes=70,original_and_caller_bytes=matched,
        callers=8,headers=28,cases=2268,ordinary_COFFs=2,directive_COFFs=2,compile_seconds=execution['elapsed_seconds'],production_ready=False)))


if __name__=='__main__':
    main()
