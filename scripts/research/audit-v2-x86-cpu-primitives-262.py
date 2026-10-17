"""Independent artifact-only audit. No compilation, linking or native execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

import capstone

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/262-x86-cpu-primitives'
OUT=ROOT/'local/experiments/v2-x86-cpu-primitives-262'
BACKEND_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
HEX=('02e1c3','2ae1c3','1ae1c3','6603c1c3','662bc1c3','661bc1c3','03c1c3','2bc1c3','1bc1c3','f6dcc3','66f7d8c3','f7d8c3',
     '8ae1668bd0c3','5458c3','5cc3','8f0424c3','ff14248d642404c3','ff642404','f7d8c3')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def main():
    s=load(RUN/'summary.json');proof=load(RUN/'proof-before-compile.json')
    assert s['kind']=='synthetic-x86-cpu-primitives' and s['backend_sha256']==BACKEND_SHA
    assert s['original_game_functions']==s['new_accepted_functions']==s['native_game_execution_commands']==0
    assert s['production_or_union_changed'] is False and s['before_after_guards']
    assert s['actual_compiler_batches']==1 and s['compiled_tus']==2 and not s['resumed_existing_compile']
    assert digest(ROOT/'scripts/research/x86-cpp-backend-257.py')==BACKEND_SHA
    for name,h in s['input_sha256'].items():
        p=Path(name);p=p if p.is_absolute() else ROOT/p
        assert digest(p)==h,('input hash drift',name)
    for path in [Path(__file__),*RUN.glob('*.json'),*OUT.glob('*.cpp'),*OUT.glob('*.h'),*OUT.glob('*.py'),*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:
        assert b'\r' not in path.read_bytes(),('LF',path)
    driver=module('driver262_audit','scripts/research/experiment-v2-x86-cpu-primitives-262.py')
    backend=module('backend257_audit262','scripts/research/x86-cpp-backend-257.py')
    coff=module('coff262_audit','scripts/research/build-v2-compile-corpus.py')
    parser=module('oracle262_audit','scripts/research/audit-v2-nested-calls-229.py')
    rows=driver.entries();assert rows==proof['fragments'] and tuple(r['hex'] for r in rows)==HEX
    assert s['synthetic_entries']==[f'{0x10001000+i*0x100:08x}' for i in range(19)]
    assert proof['entries_are_original_game_functions'] is False and proof['planned_cases']==15744
    assert proof['planned_compiler_batches']==1 and proof['planned_tus']==2
    assert proof['case_groups']==dict(arithmetic=9600,views=1024,stack_aliasing=3072,indirect=2048)
    header=backend.HEADER+'\n'+''.join('void translated_'+r['synthetic_entry']+'(Machine257&);\n' for r in rows)
    assert (OUT/'machine257.h').read_text(encoding='utf8')==header
    assert (OUT/'state-fixture.cpp').read_text(encoding='utf8')==driver.fixture(rows)
    assert digest(OUT/'captured-compile-driver.py')==digest(ROOT/'scripts/research/experiment-v2-x86-cpu-primitives-262.py')
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    sources=[];instruction_count=0;decoded=[]
    for row in rows:
        raw=bytes.fromhex(row['hex']);instructions=list(decoder.disasm(raw,int(row['synthetic_entry'],16)));decoded.append(instructions)
        assert sum(i.size for i in instructions)==len(raw)
        source,witness=backend.translate(raw,int(row['synthetic_entry'],16));sources.append(source)
        assert witness==proof['instruction_lowering'][row['name']]
        assert source.count('if(!step257(')==len(instructions)
        body,relocs=parser.coff_function(OUT/'objects/state-fixture.obj','?oracle262_'+str(row['id'])+'@@YAXXZ')
        assert body==raw and relocs==[],('exact synthetic COFF oracle',row['name'])
        assert s['oracles'][row['id']]==dict(name=row['name'],id=row['id'],bytes=raw.hex(),relocations=[])
        instruction_count+=len(instructions)
    generated='\n'.join(sources)+'\n'+driver.dispatcher(rows)
    assert (OUT/'primitives262.cpp').read_text(encoding='utf8')==generated
    assert '__asm' not in generated and 'FUN_' not in generated
    assert s['synthetic_bytes']==sum(len(bytes.fromhex(h)) for h in HEX)==70
    assert s['synthetic_instructions']==instruction_count==40
    assert [(d[0].mnemonic,d[0].op_str) for d in decoded[:12]]==[
        ('add','ah, cl'),('sub','ah, cl'),('sbb','ah, cl'),('add','ax, cx'),('sub','ax, cx'),('sbb','ax, cx'),
        ('add','eax, ecx'),('sub','eax, ecx'),('sbb','eax, ecx'),('neg','ah'),('neg','ax'),('neg','eax')]
    assert [(i.mnemonic,i.op_str) for i in decoded[12]]==[('mov','ah, cl'),('mov','dx, ax'),('ret','')]
    assert [(i.mnemonic,i.op_str) for i in decoded[13]]==[('push','esp'),('pop','eax'),('ret','')]
    assert [(i.mnemonic,i.op_str) for i in decoded[14]]==[('pop','esp'),('ret','')]
    assert [(i.mnemonic,i.op_str) for i in decoded[15]]==[('pop','dword ptr [esp]'),('ret','')]
    assert decoded[16][0].mnemonic=='call' and decoded[16][0].op_str=='dword ptr [esp]'
    assert decoded[17][0].mnemonic=='jmp' and decoded[17][0].op_str=='dword ptr [esp + 4]'
    call=proof['instruction_lowering']['indirect-call-esp'][0]['cpp']
    assert call=='U target=read257((0x00000000u+s.r[4]*1u),4u);if(!call257(s,target,0x10002003u))return;'
    helper=backend.HEADER[backend.HEADER.index('static inline bool call257'):]
    assert helper.index('s.r[4]-=4u')<helper.index('write257(')<helper.index('dispatch257(')
    push=proof['instruction_lowering']['push-esp'][0]['cpp']
    assert push=='U value=s.r[4];s.r[4]-=4u;write257(s.r[4],4u,value);'
    pop=proof['instruction_lowering']['pop-esp'][0]['cpp']
    assert pop=='U value=read257(s.r[4],4u);s.r[4]+=4u;s.r[4]=value;'
    popmem=proof['instruction_lowering']['pop-memory-esp'][0]['cpp']
    assert popmem=='U value=read257(s.r[4],4u);s.r[4]+=4u;write257((0x00000000u+s.r[4]*1u),4u,value);'
    actual_symbols=coff.coff_symbols(OUT/'objects/primitives262.obj')
    assert set(actual_symbols['defined'])=={'?dispatch257@@YAXAAUMachine257@@I@Z',*[f'?translated_{r["synthetic_entry"]}@@YAXAAUMachine257@@@Z' for r in rows]}
    # MSVC Win32 lowers the U64 sum>>bits in add257 to its pinned CRT shift helper.
    assert set(actual_symbols['undefined'])=={'?read257@@YAIII@Z','?write257@@YAXIII@Z','__aullshr'} and not actual_symbols['common'] and not actual_symbols['weak']
    hook,hook_relocs=parser.coff_function(OUT/'objects/state-fixture.obj','?capture262@@YAXXZ')
    hook_instructions=list(decoder.disasm(hook,0x1000))
    assert [i.mnemonic for i in hook_instructions]==['mov']*9+['pushfd','pop']+['mov']*4+['jmp']
    assert [i.reg_name(i.operands[1].reg) for i in hook_instructions[:8]]==['eax','ecx','edx','ebx','esp','ebp','esi','edi']
    assert hook_instructions[8].reg_name(hook_instructions[8].operands[0].reg)=='esp'
    assert hook_relocs[8]['symbol']=='?saved_sp262@@3IA' and hook_relocs[-1]['symbol']=='?continuation262@@3IA'
    edge,_=parser.coff_function(OUT/'objects/state-fixture.obj','?native_edge262@@YAXXZ')
    assert [i.mnemonic for i in decoder.disasm(edge,0x2000)]==['mov']*7+['push','popfd']+['mov']*8+['jmp','ret']
    fixture=driver.fixture(rows)
    assert 'case 0:return 0;case 1:return 1;case 2:return mask;case 3:return sign-1u;case 4:return sign;case 5:return sign+1u;case 6:return mask-1u;default:return 2;' in fixture
    assert 'flags<16' in fixture and 'align<8' in fixture and 'seed<8' in fixture
    assert 'state.r[i]==seen262[i]' in fixture and '(state.flags^seen_flags262)&0x8c1u' in fixture
    assert 'stack262[i]==native_stack262[i]' in fixture
    assert 'if(id==13u)require262(state.r[0]==sp)' in fixture
    assert 'require262(value==native_pc)' in fixture
    assert fixture.count('normalize_slot262(')==6  # definition plus five exact slot cases
    assert 'normalize_slot262(124u+align,reinterpret_cast<U>(targets262[16])+3u,entry+3u)' in fixture
    assert 'if(id==16u)write257(sp,4u,leaf_pc262)' in fixture and 'if(id==17u)write257(sp+4u,4u,leaf_pc262)' in fixture
    assert s['state_comparisons']==9*8*8*16+3*8*16+8*8*16+3*8*16*8+2*8*16*8==15744
    result=load(OUT/'fixture-result.json')
    assert result==s['case_groups']==dict(provenance='syntheticCPUfixture',native_game_execution=False,cases=15744,failures=0,
                                         arithmetic_cases=9600,view_cases=1024,stack_alias_cases=3072,indirect_cases=2048,normalized_exact_slots=19840)
    assert 9600+1024+2*1024+2*1024+3*1024+2*1024==19840
    receipts={name:load(OUT/(name+'.execution.json')) for name in ['compile-001','link-001','native-001']}
    assert sorted(p.stem for p in OUT.glob('*.execution.json'))==['compile-001.execution','link-001.execution','native-001.execution']
    assert s['unique_execution_receipts']==list(receipts)
    assert all(r['exit_code']==0 and r['cwd']==str(OUT) and r['elapsed_seconds']>0 for r in receipts.values())
    assert receipts['compile-001']['command']==s['command'] and receipts['compile-001']['elapsed_seconds']==s['compile_seconds']
    assert receipts['native-001']['elapsed_seconds']==s['native_seconds'] and receipts['native-001']['command']==[str(OUT/'state-fixture.exe')]
    assert '/MP6' in s['command'] and '/showIncludes' not in s['command'] and len([x for x in s['command'] if x.endswith('.cpp')])==2
    assert len(list((OUT/'objects').glob('*.obj')))==2 and len([x for x in receipts['link-001']['command'] if x.endswith('.obj')])==2
    assert not re.search(rb'(?:warning|error) [CDL]\d+',b'\n'.join(p.read_bytes() for p in OUT.glob('*.log')))
    validation=dict(passed=True,kind='read-only-independent-synthetic-CPU-audit',summary_sha256=digest(RUN/'summary.json'),audit_source_sha256=digest(__file__),
                    backend_sha256=BACKEND_SHA,input_pins=len(s['input_sha256']),synthetic_entries=19,synthetic_bytes=70,synthetic_instructions=40,
                    exact_oracle_relocations=0,native_comparisons=15744,normalized_exact_slots=19840,compiled_tus=2,compiler_batches=1,
                    compiler_warnings=0,receipts_immutable_unique=True,generated_coff_symbols=actual_symbols,original_game_functions=0,new_accepted_functions=0,
                    native_game_execution=False,limits=proof['limits'])
    (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:validation[k] for k in ['passed','input_pins','synthetic_bytes','native_comparisons','compiler_batches','new_accepted_functions']}))


if __name__=='__main__':main()
