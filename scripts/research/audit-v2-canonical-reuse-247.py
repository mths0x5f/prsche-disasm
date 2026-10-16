"""Independent read-only canonical fragment/ABI/oracle acceptance for Run247."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'247-canonical-reuse-batch';OUT=ROOT/'local/experiments/v2-canonical-reuse-247'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED='ad670f0520fe8a9d8974ba3836af578ca1d9e89b5876bac9118b7e330e6a336d'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    h=module('a247',RUNS/'226-writable-scalar-storage/audit.py')
    c=module('c247',ROOT/'scripts/research/build-v2-compile-corpus.py')
    s,b,p=[json.loads(x.read_bytes())for x in [RUN/'summary.json',RUN/'bindings/summary.json',RUN/'proof-before-compile.json']]
    assert digest(RUN/'summary.json')==EXPECTED==b['ordinary_summary_sha256']
    assert s['objects_compiled']==3 and len(s['results'])==3 and s['actual_compiler_batches']==1 and s['recompilations']==0
    assert not s['production_ready']and not b['production_ready']
    pins=dict(b['input_sha256'])
    for name,sha in s['input_sha256'].items():assert pins[name]==sha
    for name,sha in pins.items():assert digest(ROOT/name)==sha,('Input drift',name)
    fragment_rows=[]
    for r in s['results']:
        description=p['mechanically_copied_slices'][r['va']];source=(ROOT/description['canonical_source']).read_bytes()
        for part in description['parts']:
            if part['kind']=='canonical_bytes':
                raw=source[part['offset']:part['offset']+part['length']]
                assert raw==part['text'].encode()and hashlib.sha256(raw).hexdigest()==part['sha256']
            else:assert part['kind']=='wrapper'and part['text']in ('namespace porsche {\n','namespace {\n','}\n')
        assert (ROOT/r['generated_source']).read_bytes()==''.join(x['text']for x in description['parts']).encode()
        assert digest(ROOT/r['generated_source'])==r['generated_source_sha256']
        actual=c.coff_symbols(ROOT/r['object']);assert actual==r['symbols']and len(actual['defined'])==1
        assert digest(ROOT/r['object'])==r['object_sha256']
        assert not any('buffers_'in n or 'flush_'in n or 'trace'in n for n in actual['defined']+actual['undefined'])
        dep=json.loads((ROOT/r['source_dependencies']).read_bytes())
        assert digest(ROOT/r['source_dependencies'])==r['source_dependencies_sha256']and dep['Version']=='1.2'
        assert Path(dep['Data']['Source']).resolve()==(ROOT/r['generated_source']).resolve()
        includes={(ROOT/name).resolve()for name in r['dependency_sha256']if name!=r['generated_source']}
        assert includes=={Path(name).resolve()for name in dep['Data']['Includes']}and len(includes)==28
        for name,sha in r['dependency_sha256'].items():assert digest(ROOT/name)==sha
        fragment_rows.append(dict(va=r['va'],symbols=actual,object_sha256=r['object_sha256'],observed_header_count=len(includes)))
    directives=[]
    for row,alias in zip(b['support_objects'],b['aliases']):
        actual=c.coff_symbols(ROOT/row['object']);assert actual==row['symbols']and not any(actual.values())
        assert digest(ROOT/row['object'])==row['object_sha256']and digest(ROOT/row['generated_source'])==row['generated_source_sha256']
        obj=h.coff(ROOT/row['object']);sec=next(x for x in obj['sections']if x['name']=='.drectve')
        directive=obj['bytes'][sec['raw']:sec['raw']+sec['size']].decode().strip()
        assert directive=='/alternatename:'+alias['from']+'='+alias['to']==row['directive']==alias['directive']
        assert alias['support_object_id']==row['id']and alias['to']==next(r['symbols']['defined'][0]for r in s['results']if r['va']==alias['va'])
        assert all(not x['reloc_count']and not x['chars']&0xa0000000 and(not x['size']or x['name']in('.drectve','.debug$S','.chks64'))for x in obj['sections'])
        directives.append(directive)
    original=h.pe(ROOT/'local/game/Porsche.exe');assert original['sha256']==s['original_sha256']
    def offset(image,va):
        rva=va-image['image_base'];sec=next(x for x in image['sections']if x['va']<=rva<x['va']+x['raw_size']);return sec['raw']+rva-sec['va']
    for va,ins in p['original_instructions'].items():
        for i in ins:
            pc=int(i['va'],16);raw=bytes.fromhex(i['bytes']);at=offset(original,pc);assert original['bytes'][at:at+len(raw)]==raw
    for caller in p['indexed_incoming_calls']:
        pc=int(caller['from_va'],16);at=offset(original,pc);assert original['bytes'][at]==0xe8
        assert pc+5+struct.unpack_from('<i',original['bytes'],at+1)[0]==int(caller['to_function'],16)
    fixture_obj=h.coff(OUT/'objects/native-fixture.obj');raw=fixture_obj['bytes'];sp,count=struct.unpack_from('<II',raw,8);strings=raw[sp+18*count:]
    def symname(index):
        value=raw[sp+18*index:sp+18*index+8]
        if value[:4]==b'\0'*4:value=strings[struct.unpack_from('<I',value,4)[0]:]
        return value.split(b'\0',1)[0].decode()
    def code(name):
        sym=next(x for x in fixture_obj['symbols']if x['name']==name);sec=fixture_obj['sections'][sym['section']-1]
        at=struct.unpack_from('<I',raw,20+40*(sym['section']-1)+24)[0];relocs=[]
        for i in range(sec['reloc_count']):
            off,idx,type_=struct.unpack_from('<IIH',raw,at+10*i);relocs.append(dict(offset=off,target=symname(idx),type=type_))
        return bytearray(raw[sec['raw']:sec['raw']+sec['size']]),relocs
    oracles=[]
    for va,operation,slot in [('005a36ea','lock','enter'),('005a373c','unlock','leave')]:
        native,relocs=code('?original_'+operation+'247@porsche@@YAXI@Z')
        expected=bytearray.fromhex(''.join(x['bytes']for x in p['original_instructions'][va]))
        table='?formatter_iob_entries_005e54e8@porsche@@3PAUFormatterOriginalDescriptor32@1@A'
        api='005a4ba4'if operation=='lock'else'005a4c05'
        assert len(native)==len(expected)==47
        assert relocs==[dict(offset=5,target=table,type=6),dict(offset=14,target=table,type=6),
            dict(offset=30,target='?exit_registry_'+operation+'_api_'+api+'@porsche@@YAXI@Z',type=20),dict(offset=42,target='?'+slot+'_slot247@@3P6GXPAX@ZA',type=6)]
        assert struct.unpack_from('<I',native,5)[0]==0 and struct.unpack_from('<I',native,14)[0]==608
        assert struct.unpack_from('<I',expected,5)[0]==0x5e54e8 and struct.unpack_from('<I',expected,14)[0]==0x5e5748
        # Preserve relative last-FILE-start addend608, not a generic address mask.
        expected[5:9]=b'\0'*4;expected[14:18]=struct.pack('<I',608)
        for at in (30,42):native[at:at+4]=expected[at:at+4]=b'\0'*4
        assert native==expected
        oracles.append(dict(va=va,bytes=47,normalized_bytes=native.hex(),relocations=relocs,FILE_last_start_addend=608))
    native,relocs=code('?original_errno247@porsche@@YAPAXXZ')
    expected=bytearray.fromhex(''.join(x['bytes']for x in p['original_instructions']['005a669e']))
    assert relocs==[dict(offset=1,target='?formatter_crt_thread_005a545c@porsche@@YAPAXXZ',type=20)]and len(native)==len(expected)==9
    native[1:5]=expected[1:5]=b'\0'*4;assert native==expected
    oracles.append(dict(va='005a669e',bytes=9,normalized_bytes=native.hex(),relocations=relocs))
    marker,_=code('?raw247@@YAXPAXII@Z');assert bytes.fromhex('bbd3926b17be81043ca5bf2fb7e059bde58a13c7ffd0')in marker
    fixture=h.pe(ROOT/s['fixture']['executable']);assert fixture['sha256']==s['fixture']['executable_sha256']
    before=json.loads((OUT/'fixture-before-execution.json').read_bytes());assert before['executable_sha256']==fixture['sha256']and before['fixture_object_sha256']==fixture_obj['sha256']
    mapping=(OUT/'native-fixture.map').read_text();addresses={}
    for line in mapping.splitlines():
        m=re.match(r'\s*[0-9a-f]{4}:[0-9a-f]{8}\s+(\S+)\s+([0-9a-f]{8})\b',line,re.I)
        if m:addresses[m[1]]=int(m[2],16)
    for alias in b['aliases']:assert addresses[alias['from']]==addresses[alias['to']]
    execution=json.loads((ROOT/s['compiler_execution_receipt']).read_bytes());assert execution['exit_code']==0 and execution['command']==s['compiler_command']==b['compiler_command']
    assert execution['elapsed_seconds']==s['compile_seconds']and '/MP6'in execution['command']and '/showIncludes'not in execution['command']and '/sourceDependencies'in execution['command']
    log=(ROOT/s['compiler_log']).read_text(encoding='utf8');assert digest(ROOT/s['compiler_log'])==s['compiler_log_sha256']
    assert re.findall(r'warning ([CD]\d+)',log)==['C4731','C4731']and not re.search(r'error [CD]\d+',log)
    assert all('native-fixture.cpp'in line and 'raw247'in line for line in log.splitlines()if 'warning C4731'in line)
    driver=ast.parse((ROOT/s['captured_compile_driver']).read_text(encoding='utf8'))
    constant=next(x for x in driver.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIXTURE'for t in x.targets))
    fixture_source=(OUT/'native-fixture.cpp').read_text(encoding='utf8');assert ast.literal_eval(constant.value)==fixture_source
    for token in ['pointer_cases247!=3544','errno_cases247!=512','typed_calls247!=4056','raw_calls247!=12168','provider_calls247!=14176','thread_calls247!=2048',
                  'seen_sp247!=save_sp247-stack_bytes247','clean_sp247!=save_sp247','seen_bp247!=0xc7138ae5u','arena247[i]!=0xa5']:
        assert token in fixture_source
    native_receipt=json.loads((OUT/'fixture-native.execution.json').read_bytes());link_receipt=json.loads((OUT/'fixture-link.execution.json').read_bytes())
    assert native_receipt['exit_code']==link_receipt['exit_code']==0 and native_receipt['elapsed_seconds']==s['fixture']['seconds']
    assert native_receipt['command']==[str((ROOT/s['fixture']['executable']).resolve())]
    assert p['deferred']['va']=='005a4c05'and p['deferred']['published_prefix']==26 and p['deferred']['required_stdio_prefix']==48
    assert 'formatter_crt_locks_005e57a8[26]'in(ROOT/'iterations/v2/001-original-recovery/source/include/porsche/formatter_crt_runtime.hpp').read_text()
    validation=dict(schema=1,passed=True,summary_sha256=digest(RUN/'summary.json'),bindings_summary_sha256=digest(RUN/'bindings/summary.json'),
        audit_script_sha256=digest(Path(__file__)),input_pins_checked=len(pins),exact_canonical_fragments=True,ordinary_COFF_objects=fragment_rows,
        actual_COFF_directives=directives,actual_normalized_original_oracles=oracles,original_selected_bytes=103,indexed_incoming_calls_PE_matched=len(p['indexed_incoming_calls']),
        source_dependencies_version='1.2',actual_headers_per_game_TU=28,one_MP6_batch_without_showIncludes=True,
        compiler_exit=0,compile_seconds=s['compile_seconds'],fixture_warnings=['C4731','C4731'],game_driver_warnings=0,
        native_cases=4056,native_fixture_exit=0,alias_address_identity=True,EAX_pointer_return=True,ESP_nonvolatile=True,TLS_arena_unchanged=True,
        deferred_unlock='Canonical[26] vs required48 prefix; not compiled or bound',production_ready=False,
        audit_compiler_commands=0,audit_native_commands=0,audit_linker_commands=0)
    for path,value in [(RUN/'validation.json',validation),(RUN/'bindings/validation.json',dict(schema=1,passed=True,summary_sha256=validation['bindings_summary_sha256'],
        ordinary_summary_sha256=EXPECTED,audit_script_sha256=digest(Path(__file__)),aliases=3,directives=directives,native_cases=4056,native_exit=0,production_ready=False))]:
        path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
    assert digest(RUN/'summary.json')==EXPECTED
    print(json.dumps(dict(passed=True,pins=len(pins),ordinary=3,support=3,oracle_bytes=103,cases=4056,production_ready=False)))


if __name__=='__main__':main()
