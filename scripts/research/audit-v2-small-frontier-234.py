"""Read-only independent PE/COFF/call-storage/SDK fixture audit for234."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/234-small-frontier-bodies'
OUT=ROOT/'local/experiments/v2-small-frontier-bodies-234'
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def coff_function(path,name):
    raw=Path(path).read_bytes();machine,nsec,_,symoff,nsym,opt,_=struct.unpack_from('<HHIIIHH',raw);assert machine==0x14c and opt==0
    strings=symoff+nsym*18;symbols={};index=0
    while index<nsym:
        n,value,section,kind,storage,aux=struct.unpack_from('<8sIhHBB',raw,symoff+index*18)
        if n[:4]==b'\0'*4:
            start=strings+struct.unpack_from('<I',n,4)[0];n=raw[start:raw.index(b'\0',start)].decode()
        else:n=n.rstrip(b'\0').decode()
        symbols[index]=dict(name=n,value=value,section=section);index+=1+aux
    fn=next(v for v in symbols.values()if v['name']==name);assert fn['value']==0 and fn['section']>0
    at=20+(fn['section']-1)*40;size,offset,ro=struct.unpack_from('<III',raw,at+16);nr=struct.unpack_from('<H',raw,at+32)[0];rel=[]
    for i in range(nr):
        a,s,t=struct.unpack_from('<IIH',raw,ro+i*10);rel.append(dict(offset=a,symbol=symbols[s]['name'],type=t))
    return raw[offset:offset+size],rel


def main():
    s=load(RUN/'summary.json');p=load(RUN/'proof-before-compile.json');q=load(RUN/'lost-receiver-queue.json');pins=s['input_sha256']
    for path,h in pins.items():assert digest(ROOT/path)==h,('input drift',path)
    compiled=['0058e2f0','0058e300','0050cbf0','0050d310'];deferred=['00468100','004d8230','004d8240','00538d80']
    assert s['objects_compiled']==s['real_coff_objects']==s['changed_game_TUs']==4 and s['actual_compiler_batches']==1
    assert s['compiled_vas']==compiled and s['uncompiled_vas']==deferred
    assert all(v==dict(canonical_exact_or_interior=[],WIP=[],already_compiled=False)for v in p['ownership'].values())
    assert s['Ghidra_decompilations']==0 and not s['production_or_union_changes']
    assert [r['va']for r in q]==deferred
    assert all(r['mismatched_frontier_symbol']=='?FUN_'+r['va']+'@@YAXXZ'for r in q)
    assert not any((OUT/'objects'/(va+'.obj')).exists()for va in deferred)
    raw=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()==s['original_sha256']
    pe=struct.unpack_from('<I',raw,0x3c)[0];machine,n,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0];sections=[struct.unpack_from('<IIII',raw,pe+24+opt+i*40+8)[1:]for i in range(n)]
    verified=0
    for ins in p['original_instructions'].values():
        for i in ins:
            rva=int(i['va'],16)-base;length=len(i['bytes'])//2;start,size,offset=next(v for v in sections if v[0]<=rva and rva+length<=v[0]+v[1])
            assert raw[offset+rva-start:offset+rva-start+length].hex()==i['bytes'];verified+=1
    assert sum(len(p['original_instructions'][va])for va in compiled)==s['original_instruction_count']==16
    assert sum(len(i['bytes'])//2 for va in compiled for i in p['original_instructions'][va])==s['original_bytes']==59
    for va in compiled:assert [i['bytes']for i in p['original_instructions'][va]if i['instruction'].startswith('RET')]==['c3']
    for va,ret in [('004d23f0','c20400'),('004d2100','c20c00')]:assert [i['bytes']for i in p['original_instructions'][va]if i['instruction'].startswith('RET')]==[ret]
    assert {r['symbol']:r['iat_rva']for r in p['imports']}==dict(EnterCriticalSection='0x1b2078',LeaveCriticalSection='0x1b206c',InitializeCriticalSection='0x1b207c',DeleteCriticalSection='0x1b2068')
    assert p['SDK']['critical_section_x86_size']==24 and p['SDK']['recursion_count_offset']==8
    for path,h in p['SDK']['paths'].items():assert digest(ROOT/path)==h
    spec=importlib.util.spec_from_file_location('coff234audit',ROOT/'scripts/research/build-v2-compile-corpus.py');coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    methods={'0050cbf0':'?FUN_004d23f0@OriginalECX234@@QAEXI@Z','0050d310':'?FUN_004d2100@OriginalECX234@@QAEXPAXII@Z'}
    expected_symbols={'0058e2f0':{'?DAT_006b1800@@3PAEA','__imp__EnterCriticalSection@4'},'0058e300':{'?DAT_006b1800@@3PAEA','__imp__LeaveCriticalSection@4'},
        '0050cbf0':{'?DAT_0065b928@@3HA',methods['0050cbf0']},'0050d310':{'?DAT_0065b928@@3HA','?s_options_005cc804@@3PADA',methods['0050d310']}}
    fixture_obj=OUT/'objects/call-boundary-fixture.obj'
    for row in s['results']:
        va=row['va'];assert row['compiled'] and row['owned_error_count']==row['owned_warning_count']==0
        for pk,hk in [('object','object_sha256'),('generated_source','generated_source_sha256'),('disassembly','disassembly_sha256')]:assert digest(ROOT/row[pk])==row[hk]
        for path,h in row['dependency_sha256'].items():assert digest(ROOT/path)==h
        assert coff.coff_symbols(ROOT/row['object'])==row['symbols']
        assert row['defined_external_symbols']==['?FUN_'+va+'@@YAXXZ'] and set(row['undefined_external_symbols'])==expected_symbols[va]
        body,rel=coff_function(ROOT/row['object'],'?FUN_'+va+'@@YAXXZ')
        asm=(ROOT/row['disassembly']).read_text().split('?FUN_'+va+'@@YAXXZ (',1)[1].split('\n?',1)[0]
        rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',asm,re.M)
        assert rets==[''] and row['native_ret_bytes']==row['original_ret_bytes']==[0]
        if va in methods:
            call=next(r for r in rel if r['symbol']==methods[va]);receiver=next(r for r in rel if r['symbol']=='?DAT_0065b928@@3HA')
            assert call['type']==0x14 and body[call['offset']-1]==0xe8
            assert receiver['type']==6 and body[receiver['offset']-2:receiver['offset']]==b'\x8b\x0d' and receiver['offset']<call['offset']
            assert b'\x6a\x00'in body[:call['offset']]
            if va=='0050d310':assert b'\x6a\x01\x6a\x00'in body and any(r['symbol']=='?s_options_005cc804@@3PADA'for r in rel)
            controlled,_=coff_function(fixture_obj,methods[va]);assert controlled.endswith(bytes.fromhex('c20400'if va=='0050cbf0'else'c20c00'))
        else:
            imported='__imp__EnterCriticalSection@4'if va=='0058e2f0'else'__imp__LeaveCriticalSection@4'
            call=next(r for r in rel if r['symbol']==imported);assert call['type']==6 and body[call['offset']-2:call['offset']]==b'\xff\x15'
    oracle_bytes=0
    for va,which in [('0058e2f0','enter'),('0058e300','leave')]:
        oracle,rel=coff_function(fixture_obj,'?original_'+which+'234@@YAXXZ')
        assert rel==[dict(offset=1,symbol='?DAT_006b1800@@3PAEA',type=6),dict(offset=7,symbol='?'+which+'_slot234@@3P6GXPAX@ZA',type=6)]
        original=bytearray.fromhex(''.join(i['bytes']for i in p['original_instructions'][va]))
        for r in rel:original[r['offset']:r['offset']+4]=b'\0'*4
        assert oracle==bytes(original) and len(oracle)==12;oracle_bytes+=len(oracle)
    assert set(s['new_explicit_thiscall_dependencies'])==set(methods.values())
    execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['elapsed_seconds']==s['compile_seconds']>0
    assert execution['command']==s['compiler_command'] and execution['command'].count('/MP6')==1 and len([v for v in execution['command']if v.endswith('.cpp')])==5
    assert not re.search(r'(?:warning|error) C\d+',(OUT/'compile.log').read_text())
    assert load(OUT/'fixture-link.execution.json')['exit_code']==load(OUT/'fixture-native.execution.json')['exit_code']==0
    assert s['fixture']['critical_section_original_native_pairs']==s['fixture']['controlled_thiscall_boundary_calls']==2048
    assert not s['fixture']['full_game_fidelity_claimed']
    for file in [Path(__file__),RUN/'summary.json',RUN/'proof-before-compile.json',RUN/'lost-receiver-queue.json',OUT/'consumer234.h',OUT/'call-boundary-fixture.cpp',*[ROOT/r['generated_source']for r in s['results']]]:
        assert b'\r'not in file.read_bytes(),('LF required',file)
    for path,h in pins.items():assert digest(ROOT/path)==h,('final input drift',path)
    result=dict(status='PASS',summary_sha256=digest(RUN/'summary.json'),audit_script_sha256=digest(__file__),input_pins_checked=len(pins),original_PE_instructions_verified=verified,
        compiled=compiled,deferred=deferred,real_i386_COFF=4,compiler_batches=1,compiler_warnings=0,compiled_original_instructions=16,compiled_original_bytes=59,
        original_oracle_bytes=oracle_bytes,original_oracle_relocations_proved=4,original_oracle_normalized_exact_bytes=True,native_wrapper_RET0_counts=[1,1,1,1],
        thiscall_original_and_controlled_cleanup=[4,12],critical_section_original_native_pairs=2048,controlled_thiscall_boundary_calls=2048,
        new_distinct_callee_dependencies=list(methods.values()),
        remaining=['Four originalECX/nativevoid(void) receiver-contract mismatches preserved, not bound.','New thiscallcallee implementations and three global data owners/initializers.','Provider/register/fault/concurrency/game fidelity.'])
    (RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(result))


if __name__=='__main__':main()
