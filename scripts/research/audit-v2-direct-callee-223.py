"""Independent read-only proof/COFF/relocated-original-oracle audit for223."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/223-direct-callee-recovery'
OUT=ROOT/'local/experiments/v2-direct-callee-recovery-223'
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def coff_function(path,name):
    raw=Path(path).read_bytes();machine,nsections,_,symoff,nsymbols,opt,_=struct.unpack_from('<HHIIIHH',raw)
    assert machine==0x14c and opt==0
    stroff=symoff+nsymbols*18;symbols={};index=0
    while index<nsymbols:
        n,value,section,kind,storage,aux=struct.unpack_from('<8sIhHBB',raw,symoff+index*18)
        if n[:4]==b'\0'*4:
            start=stroff+struct.unpack_from('<I',n,4)[0];n=raw[start:raw.index(b'\0',start)].decode()
        else:n=n.rstrip(b'\0').decode()
        symbols[index]=dict(name=n,value=value,section=section);index+=1+aux
    fn=next(v for v in symbols.values()if v['name']==name);assert fn['value']==0 and fn['section']>0
    at=20+40*(fn['section']-1);size,offset,reloff=struct.unpack_from('<III',raw,at+16);nrel=struct.unpack_from('<H',raw,at+32)[0]
    rel=[]
    for i in range(nrel):
        address,symidx,kind=struct.unpack_from('<IIH',raw,reloff+i*10)
        rel.append(dict(offset=address,symbol=symbols[symidx]['name'],type=kind))
    return raw[offset:offset+size],rel


def main():
    s=load(RUN/'summary.json');p=load(RUN/'proof-before-compile.json');pins=s['input_sha256']
    for path,h in pins.items():assert digest(ROOT/path)==h,('input drift',path)
    assert s['objects_compiled']==s['real_coff_objects']==s['actual_compiler_batches']==s['changed_game_TUs']==1
    assert s['Ghidra_decompilations']==0 and not s['production_or_union_changes']
    assert p['ownership']==dict(canonical_exact_or_interior=[],WIP=[],already_compiled=False)
    assert p['indirect_calls_in_target']==0
    original=p['original_instructions']['00565ea0']
    assert len(original)==s['original_instruction_count']==38
    original_bytes=bytes.fromhex(''.join(i['bytes']for i in original));assert len(original_bytes)==s['original_bytes']==93
    assert [i['bytes']for i in original if i['instruction'].startswith('RET')]==['c3','c3']
    assert [i['va']for i in original if '[ESP' in i['instruction']]==['00565ea2']
    raw=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()==s['original_sha256']
    pe=struct.unpack_from('<I',raw,0x3c)[0];machine,n,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0];sections=[struct.unpack_from('<IIII',raw,pe+24+opt+i*40+8)[1:]for i in range(n)]
    verified=0
    for instructions in p['original_instructions'].values():
        for ins in instructions:
            rva=int(ins['va'],16)-base;length=len(ins['bytes'])//2
            start,size,off=next(v for v in sections if v[0]<=rva and rva+length<=v[0]+v[1])
            assert raw[off+rva-start:off+rva-start+length].hex()==ins['bytes'];verified+=1
    row=s['results'][0]
    assert row['va']=='00565ea0' and row['compiled'] and row['owned_error_count']==row['owned_warning_count']==0
    for pk,hk in [('object','object_sha256'),('generated_source','generated_source_sha256'),('disassembly','disassembly_sha256')]:assert digest(ROOT/row[pk])==row[hk]
    for path,h in row['dependency_sha256'].items():assert digest(ROOT/path)==h
    spec=importlib.util.spec_from_file_location('coff223audit',ROOT/'scripts/research/build-v2-compile-corpus.py');coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    assert coff.coff_symbols(ROOT/row['object'])==row['symbols']
    assert row['defined_external_symbols']==['?FUN_00565ea0@@YAIPAXI@Z']
    assert set(row['undefined_external_symbols'])=={'?DAT_006b4a04@@3HA','?FUN_00590070@@YAIH@Z','?FUN_00590170@@YAHHH@Z','?FUN_005907b0@@YAHHHH@Z'}
    oracle,rel=coff_function(OUT/'objects/original-comparison-fixture.obj','?original223@@YAIPAXI@Z')
    expected_rel=[dict(offset=0x0c,symbol='?FUN_00590070@@YAIH@Z',type=0x14),dict(offset=0x18,symbol='?DAT_006b4a04@@3HA',type=6),
        dict(offset=0x39,symbol='?FUN_00590170@@YAHHH@Z',type=0x14),dict(offset=0x42,symbol='?DAT_006b4a04@@3HA',type=6),dict(offset=0x4b,symbol='?FUN_005907b0@@YAHHHH@Z',type=0x14)]
    assert rel==expected_rel and len(oracle)==93
    normalized=bytearray(original_bytes)
    for r in rel:normalized[r['offset']:r['offset']+4]=b'\0'*4
    assert bytes(normalized)==oracle,'oracle differs from original opcode/branch/dataflow bytes'
    game=OUT/'objects/00565ea0.obj'
    helper32,_=coff_function(game,'?load32_223@@YAIPBX@Z');helper16,_=coff_function(game,'?load16_223@@YAGPBX@Z')
    assert bytes.fromhex('8b08') in helper32 and bytes.fromhex('668b08')in helper16
    asm=(ROOT/row['disassembly']).read_text().split('?FUN_00565ea0@@YAIPAXI@Z (',1)[1].split('\n?',1)[0]
    game_body,_=coff_function(game,'?FUN_00565ea0@@YAIPAXI@Z')
    assert bytes.fromhex('b801000000c1e0028b4d080fb61401')in game_body,'native BYTE input+4 producer/load'
    rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',asm,re.M)
    assert rets==[''] and row['native_ret_bytes']==[0] and row['original_ret_bytes']==[0,0]
    execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['elapsed_seconds']==s['compile_seconds']>0
    assert execution['command']==s['compiler_command'] and execution['command'].count('/MP6')==1
    assert len([v for v in execution['command']if v.endswith('.cpp')])==2
    assert not re.search(r'(?:warning|error) C\d+',(OUT/'compile.log').read_text())
    assert load(OUT/'fixture-link.execution.json')['exit_code']==load(OUT/'fixture-native.execution.json')['exit_code']==0
    assert s['fixture']['comparisons']==256*7*4*4*2*4==229376
    assert not s['fixture']['full_provider_fidelity_claimed']
    for file in [Path(__file__),RUN/'summary.json',RUN/'proof-before-compile.json',ROOT/row['generated_source'],OUT/'consumer223.h',OUT/'original-comparison-fixture.cpp']:
        assert b'\r'not in file.read_bytes(),('LF required',file)
    for path,h in pins.items():assert digest(ROOT/path)==h,('final input drift',path)
    result=dict(status='PASS',summary_sha256=digest(RUN/'summary.json'),audit_script_sha256=digest(__file__),input_pins_checked=len(pins),original_PE_instructions_verified=verified,
        consumer_instructions=38,consumer_bytes=93,oracle_bytes=93,oracle_relocations_proved=5,oracle_normalized_exact_original_bytes=True,
        native_BYTE_DWORD_WORD_representation_verified=True,real_i386_COFF=1,compiler_batches=1,native_RET0_count=1,original_RET0_paths=2,
        native_original_comparisons=229376,exact211_symbol_binding=True,remaining=['00590070 implementation','005907b0 implementation','DAT006b4a04 canonical data owner/initializer','Nested provider/lifetime/concurrency/fault/register/game fidelity'])
    (RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(result))


if __name__=='__main__':main()
