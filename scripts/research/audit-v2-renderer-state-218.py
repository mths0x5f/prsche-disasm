"""Read-only independent audit of bounded218's existing capture/COFF/fixture."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/218-renderer-state-consumer'
OUT=ROOT/'local/experiments/v2-renderer-state-consumer-218'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))


def main():
    summary=load(RUN/'summary.json');proof=load(RUN/'proof-before-compile.json')
    pins=summary['input_sha256']
    for path,h in pins.items():assert digest(ROOT/path)==h,('input drift',path)
    assert summary['objects_compiled']==summary['real_coff_objects']==summary['actual_compiler_batches']==summary['changed_game_TUs']==1
    assert summary['recompilations']==summary['Ghidra_decompilations']==0
    assert summary['resumed_existing_successful_compile'] and not summary['production_or_union_changes']
    assert proof['ownership']==dict(canonical_exact_or_interior=[],WIP=[])
    assert len(proof['original_instructions'])==summary['original_instruction_count']==119
    assert sum(len(i['bytes'])//2 for i in proof['original_instructions'])==summary['original_bytes']==416
    assert [i['bytes']for i in proof['original_instructions']if i['instruction'].startswith('RET')]==['c3','c3']
    by_pc={i['va']:i for i in proof['original_instructions']}
    assert by_pc['00537b81']['bytes']=='895c2410' and by_pc['00537bfe']['bytes']=='8b542410'
    assert by_pc['00537c13']['bytes']=='8b942420040000' and by_pc['00537c1b']['bytes']=='8b842420040000'
    assert len(proof['providers'])==6
    binaries=[json.loads(l)for l in (ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()]
    verified=0
    for name in ['Porsche.exe','opengl1z.dll','opengl3z.dll','voodoo2z.dll']:
        b=next(b for b in binaries if b['file']==name);raw=(ROOT/'local/game'/b['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==b['sha256']
        pe=struct.unpack_from('<I',raw,0x3c)[0];machine,count,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
        base=struct.unpack_from('<I',raw,pe+24+28)[0]
        sections=[struct.unpack_from('<IIII',raw,pe+24+opt+i*40+8)[1:]for i in range(count)]
        if name=='Porsche.exe':
            ins=proof['original_instructions']+[i for v in proof['direct_callees'].values()for i in v]+[i for w in proof['loader_windows']for i in w['instructions']]
        else:
            ins=[i for p in proof['providers']if p['module']==name for i in p['instructions']]
            for provider in [p for p in proof['providers']if p['module']==name]:
                assert provider['module_sha256']==b['sha256']
                assert [r['bytes']for r in provider['rets']]==(['c3']if provider['name']=='_THRASH_about@0'else['c20400'])
        for i in ins:
            rva=int(i['va'],16)-base;n=len(i['bytes'])//2
            start,size,offset=next(s for s in sections if s[0]<=rva and rva+n<=s[0]+s[1])
            assert raw[offset+rva-start:offset+rva-start+n].hex()==i['bytes'],i
        verified+=len(ins)
    execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['elapsed_seconds']==summary['compile_seconds']>0
    assert execution['command']==summary['compiler_command'] and execution['command'].count('/MP6')==1
    assert len([a for a in execution['command']if a.endswith('.cpp')])==2
    codes=re.findall(r'warning (C\d+)',(OUT/'compile.log').read_text())
    assert sorted(codes)==['C4146','C4244']
    assert load(OUT/'fixture-link.execution.json')['exit_code']==load(OUT/'fixture-native.execution.json')['exit_code']==0
    assert summary['fixture']['cases']==28 and summary['fixture']['native_exit_code']==0
    assert not summary['fixture']['full_original_or_provider_fidelity_claimed']
    row=summary['results'][0];assert row['va']=='00537b40' and row['compiled'] and row['owned_warning_count']==1
    for pathkey,hashkey in [('generated_source','generated_source_sha256'),('object','object_sha256'),('disassembly','disassembly_sha256')]:assert digest(ROOT/row[pathkey])==row[hashkey]
    for path,h in row['dependency_sha256'].items():assert digest(ROOT/path)==h
    obj=ROOT/row['object'];assert struct.unpack_from('<H',obj.read_bytes())[0]==0x14c
    spec=importlib.util.spec_from_file_location('coff218audit',ROOT/'scripts/research/build-v2-compile-corpus.py');coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    actual=coff.coff_symbols(obj);assert actual==row['symbols']
    assert actual['defined']==['?FUN_00537b40@@YAXHII@Z']
    assert '?FUN_00571630@@YAXHHHPAI@Z' in actual['undefined']
    asm=(ROOT/row['disassembly']).read_text().split('?FUN_00537b40@@YAXHII@Z (',1)[1].split('\n?signed_bits218@@',1)[0]
    rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',asm,re.M)
    assert rets==[''] and row['native_ret_bytes']==[0] and row['original_ret_bytes']==[0,0]
    source=(ROOT/row['generated_source']).read_text()
    assert 'uStack_' not in source and 'uVar9 = uVar3;' in source and 'alignas(4) undefined1 local_400 [1024];' in source
    assert source.count('signed_bits218(param_2)')==source.count('signed_bits218(param_3)')==2
    assert 'void FUN_00571630(int param_1,' in source
    for path in [Path(__file__),RUN/'summary.json',RUN/'proof-before-compile.json',ROOT/row['generated_source'],OUT/'consumer218.h',OUT/'call-boundary-fixture.cpp']:
        assert b'\r' not in path.read_bytes(),('LF required',path)
    for path,h in pins.items():assert digest(ROOT/path)==h,('final input drift',path)
    result=dict(status='PASS',summary_sha256=digest(RUN/'summary.json'),audit_script_sha256=digest(__file__),input_pins_checked=len(pins),original_PE_instructions_verified=verified,
        consumer_instructions=119,consumer_bytes=416,real_i386_game_COFF=1,compiler_batches=1,recompilations=0,native_RET0_count=1,original_RET0_paths=2,native_fixture_cases=28,
        warnings=dict(game='C4146 original modulo32 NEG',fixture='C4244 deliberate char0x80'),
        remaining=['FUN_00571630 int-vs-code* native symbol binding; original data-pointer payload proven.','Overlapping scalar/indexed data owner aliases; extern views are not allocations.','Full original/provider/lifetime/concurrency/fault/register fidelity not claimed.'])
    (RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result))


if __name__=='__main__':main()
