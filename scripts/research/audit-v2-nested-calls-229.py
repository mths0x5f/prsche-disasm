"""Read-only native/original229 audit, including the explicit uncompiled queue."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/229-nested-call-recovery'
OUT=ROOT/'local/experiments/v2-nested-call-recovery-229'
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
    s=load(RUN/'summary.json');p=load(RUN/'proof-before-compile.json');q=load(RUN/'005907b0-proof-queue.json');pins=s['input_sha256']
    for path,h in pins.items():assert digest(ROOT/path)==h,('input drift',path)
    assert s['objects_compiled']==s['real_coff_objects']==s['actual_compiler_batches']==s['changed_game_TUs']==1
    assert s['compiled_vas']==['00590070'] and s['uncompiled_vas']==['005907b0']
    assert s['Ghidra_decompilations']==0 and not s['production_or_union_changes']
    assert all(v==dict(canonical_exact_or_interior=[],WIP=[],already_compiled=False)for v in p['ownership'].values())
    raw=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()==s['original_sha256']
    pe=struct.unpack_from('<I',raw,0x3c)[0];machine,n,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0];sections=[struct.unpack_from('<IIII',raw,pe+24+opt+i*40+8)[1:]for i in range(n)]
    verified=0
    for ins in list(p['original_instructions'].values())+[w['instructions']for w in q['static_witnesses']]:
        for i in ins:
            rva=int(i['va'],16)-base;length=len(i['bytes'])//2;start,size,offset=next(v for v in sections if v[0]<=rva and rva+length<=v[0]+v[1])
            assert raw[offset+rva-start:offset+rva-start+length].hex()==i['bytes'];verified+=1
    small=p['original_instructions']['00590070'];large=p['original_instructions']['005907b0']
    assert len(small)==20 and len(large)==208
    original=bytes.fromhex(''.join(i['bytes']for i in small));assert len(original)==s['original_bytes']==58
    assert not any(i['instruction'].startswith('CALL')for i in small)
    assert [i['bytes']for i in small if i['instruction'].startswith('RET')]==['c3','c3']
    assert sum(len(i['bytes'])//2 for i in large)==q['body_bytes']==708 and q['original_instructions']==large
    assert q['status']=='uncompiled_proof_queue' and q['no_native_body_or_guessed_callback']
    assert [f['offset']for f in q['callback_packet']['fields']]==[0,4,8,12]
    assert q['callback_packet']['call']=='00590965 CALL[EDI]' and q['callback_packet']['slots_base']=='006b49e0'
    assert not (OUT/'objects/005907b0.obj').exists()
    by_pc={i['va']:i for ins in p['original_instructions'].values()for i in ins}
    assert by_pc['0059911e']['bytes']=='8986a0000000' and by_pc['00590955']['bytes']=='89442440'
    row=s['results'][0];assert row['va']=='00590070' and row['compiled'] and row['owned_error_count']==row['owned_warning_count']==0
    for pk,hk in [('object','object_sha256'),('generated_source','generated_source_sha256'),('disassembly','disassembly_sha256')]:assert digest(ROOT/row[pk])==row[hk]
    for path,h in row['dependency_sha256'].items():assert digest(ROOT/path)==h
    spec=importlib.util.spec_from_file_location('coff229audit',ROOT/'scripts/research/build-v2-compile-corpus.py');coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    assert coff.coff_symbols(ROOT/row['object'])==row['symbols']
    assert row['defined_external_symbols']==['?FUN_00590070@@YAIH@Z']
    assert set(row['undefined_external_symbols'])=={'?DAT_006b48d8@@3IA','?DAT_006b4a04@@3HA'}
    oracle,rel=coff_function(OUT/'objects/original-comparison-fixture.obj','?original229@@YAIH@Z')
    assert rel==[dict(offset=0xa,symbol='?DAT_006b48d8@@3IA',type=6),dict(offset=0x1c,symbol='?DAT_006b4a04@@3HA',type=6)]
    normalized=bytearray(original)
    for r in rel:normalized[r['offset']:r['offset']+4]=b'\0'*4
    assert len(oracle)==58 and oracle==bytes(normalized),'reference original instruction mismatch'
    helper,_=coff_function(ROOT/row['object'],'?load32_229@@YAIPBX@Z');assert b'\x8b\x08'in helper
    asm=(ROOT/row['disassembly']).read_text().split('?FUN_00590070@@YAIH@Z (',1)[1].split('\n?',1)[0]
    assert re.search(r'mov\s+eax,dword ptr \[\?DAT_006b48d8',asm) and 'and         eax,0FFFFh'in asm
    assert re.search(r'mov\s+\w+,byte ptr \[\w+\+8\]',asm)
    rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',asm,re.M)
    assert rets==[''] and row['native_ret_bytes']==[0] and row['original_ret_bytes']==[0,0]
    execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['elapsed_seconds']==s['compile_seconds']>0
    assert execution['command']==s['compiler_command'] and execution['command'].count('/MP6')==1
    assert len([x for x in execution['command']if x.endswith('.cpp')])==2
    assert not re.search(r'(?:warning|error) C\d+',(OUT/'compile.log').read_text())
    assert load(OUT/'fixture-link.execution.json')['exit_code']==load(OUT/'fixture-native.execution.json')['exit_code']==0
    assert s['fixture']['comparisons']==10*6*3*2*256*4==368640 and not s['fixture']['full_game_fidelity_claimed']
    for file in [Path(__file__),RUN/'summary.json',RUN/'proof-before-compile.json',RUN/'005907b0-proof-queue.json',ROOT/row['generated_source'],OUT/'consumer229.h',OUT/'original-comparison-fixture.cpp']:
        assert b'\r'not in file.read_bytes(),('LF required',file)
    for path,h in pins.items():assert digest(ROOT/path)==h,('final input drift',path)
    result=dict(status='PASS',summary_sha256=digest(RUN/'summary.json'),audit_script_sha256=digest(__file__),input_pins_checked=len(pins),original_PE_instructions_verified=verified,
        compiled=['00590070'],uncompiled=['005907b0'],consumer_instructions=20,consumer_bytes=58,queued_instructions=208,queued_bytes=708,
        oracle_bytes=58,oracle_normalized_exact_original_bytes=True,oracle_relocations_proved=2,real_i386_COFF=1,compiler_batches=1,compiler_warnings=0,
        native_RET0_count=1,original_RET0_paths=2,native_original_comparisons=368640,exact223_symbol_binding=True,
        queue='5907b0: recover actual006b49e0 targets/input contracts, contiguous parserout>=a4 and fourDWORD callbackpacket; no guessed callback cast supplied.',
        remaining=['005907b0 implementation','006b48d8 and006b4a04 canonical owners/initializers','Fault/register/concurrency/game fidelity'])
    (RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(result))


if __name__=='__main__':main()
