"""Independent read-only audit of Run253; never compiles, links or executes code."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

import capstone
from capstone.x86 import X86_OP_MEM, X86_OP_REG

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/253-x86-tail-dispatch'
OUT=ROOT/'local/experiments/v2-x86-tail-dispatch-253'
VAS=('00468100','004d8230','004d8240')
EXPECTED={'00468100':(0x74,0x536050,8),'004d8230':(0x264,0x4c7e10,11),'004d8240':(0x264,0x4c7df0,11)}
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def original_bytes(image,va,n):
    pe=struct.unpack_from('<I',image,0x3c)[0]
    assert image[pe:pe+4]==b'PE\0\0'
    sections=struct.unpack_from('<H',image,pe+6)[0]
    optional=struct.unpack_from('<H',image,pe+20)[0]
    base=struct.unpack_from('<I',image,pe+24+28)[0];rva=int(va,16)-base
    for i in range(sections):
        p=pe+24+optional+40*i
        size,start,rawsize,offset=struct.unpack_from('<IIII',image,p+8)
        if start<=rva and rva+n<=start+rawsize:
            assert rva+n<=start+size
            return image[offset+rva-start:offset+rva-start+n]
    raise AssertionError(('not file backed',va))


def main():
    s=load(RUN/'summary.json');proof=load(RUN/'proof-before-compile.json')
    assert s['kind']=='isolated-x86-tail-dispatch-pilot' and s['original_sha256']==SHA
    assert tuple(s['experimental_vas'])==VAS and set(proof['original_hex'])==set(VAS)
    assert s['new_accepted_functions']==0 and s['production_or_union_changed'] is False
    assert s['native_game_execution_commands']==s['planner_cli_executions']==0
    assert s['actual_compiler_batches']==1 and s['before_after_guards']
    # The summary is already finalized; validation is a separate audit artifact.
    for name,h in s['input_sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        assert digest(path)==h,('input pin drift',name)
    for path in [Path(__file__),RUN/'summary.json',RUN/'proof-before-compile.json',
                 *OUT.glob('*.cpp'),*OUT.glob('*.h'),*OUT.glob('*.py'),*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:
        assert b'\r' not in path.read_bytes(),('LF normalization',path)
    driver=module('driver253_audit','scripts/research/experiment-v2-x86-tail-dispatch-253.py')
    coff=module('coff253_audit','scripts/research/build-v2-compile-corpus.py')
    parser=module('oracle253_audit','scripts/research/audit-v2-nested-calls-229.py')
    planner=module('planner245_audit253','scripts/research/plan-v2-link-frontier-245.py')
    translate,derived,patches=driver.backend()
    assert derived==(OUT/'derived-backend253.py').read_text(encoding='utf8')
    assert [list(p) for p in patches]==proof['backend_patches']
    assert driver.header()==(OUT/'machine253.h').read_text(encoding='utf8')
    assert driver.DISPATCH==(OUT/'dispatch253.cpp').read_text(encoding='utf8')
    assert driver.FIXTURE==(OUT/'state-fixture.cpp').read_text(encoding='utf8')
    assert driver.guard_tests(translate)==s['guard_tests']==proof['guard_tests']
    assert len(s['guard_tests'])==8
    image=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    actual_symbols={}
    for va in VAS:
        displacement,target,n=EXPECTED[va]
        raw=original_bytes(image,va,n)
        assert raw.hex()==proof['original_hex'][va]
        decoded=list(decoder.disasm(raw,int(va,16)))
        assert [i.mnemonic for i in decoded]==['mov','jmp']
        mov,jmp=decoded
        assert mov.operands[0].type==X86_OP_REG and mov.reg_name(mov.operands[0].reg)=='ecx'
        op=mov.operands[1];assert op.type==X86_OP_MEM and op.size==4
        assert mov.reg_name(op.mem.base)=='ecx' and op.mem.index==op.mem.segment==0 and op.mem.disp==displacement
        assert jmp.bytes[0]==0xe9 and jmp.size==5
        assert (jmp.address+5+struct.unpack_from('<i',jmp.bytes,1)[0])&0xffffffff==target
        generated,witness=translate(raw,int(va,16))
        assert generated==(OUT/(va+'.cpp')).read_text(encoding='utf8')
        assert witness==proof['instruction_lowering'][va]
        assert witness[0]['cpp']==f's.r[1]=read253((0x{displacement:08x}u+s.r[1]*1u),4u);'
        assert witness[1]['cpp']==f'dispatch253(s,0x{target:08x}u);return;'
        assert 's.r[4]+=' not in generated and 'Stop253::Returned' not in generated
        assert '__asm' not in generated and 'FUN_' not in generated
        symbols=coff.coff_symbols(OUT/'objects'/(va+'.obj'));actual_symbols[va]=symbols
        assert symbols['defined']==[f'?translated_{va}@@YAXAAUMachine253@@@Z']
        assert symbols['undefined']==['?dispatch253@@YAXAAUMachine253@@I@Z','_memcpy']
        assert not symbols['common'] and not symbols['weak']
        body,relocs=parser.coff_function(OUT/'objects/state-fixture.obj',f'?original_{va}_253@@YAXXZ')
        assert relocs==[dict(offset=n-4,symbol='?capture253@@YAXXZ',type=20)]
        expected=bytearray(raw);expected[-4:]=bytes(4)
        assert body==expected,('only JMP REL32 normalization',va)
        oracle=next(r for r in s['oracle'] if r['va']==va)
        assert oracle==dict(va=va,bytes=n,relocations=relocs,normalized_only_jmp_rel32=True)
    dispatch=coff.coff_symbols(OUT/'objects/dispatch253.obj');actual_symbols['dispatcher']=dispatch
    assert dispatch['defined']==['?dispatch253@@YAXAAUMachine253@@I@Z']
    assert set(dispatch['undefined'])=={'?note_missing253@@YAXI@Z',*[f'?translated_{va}@@YAXAAUMachine253@@@Z' for va in VAS]}
    assert not dispatch['common'] and not dispatch['weak']
    assert 'default:s.stop=Stop253::MissingEntry;note_missing253(target);return;' in driver.DISPATCH
    assert driver.DISPATCH.count('case ')==3
    # Independently decode the actual COFF capture hook, not just the C++ text.
    body,relocs=parser.coff_function(OUT/'objects/state-fixture.obj','?capture253@@YAXXZ')
    hook=list(decoder.disasm(body,0x1000))
    assert [i.mnemonic for i in hook]==['mov']*8+['pushfd','pop']+['mov']*5+['jmp']
    for i,name in zip(hook[:8],['eax','ecx','edx','ebx','esp','ebp','esi','edi']):
        assert i.operands[0].type==X86_OP_MEM and i.operands[1].type==X86_OP_REG
        assert i.reg_name(i.operands[1].reg)==name
    assert [i.operands[0].mem.disp for i in hook[:8]]==list(range(0,32,4))
    assert all(r['type']==6 for r in relocs)
    assert [r['symbol'] for r in relocs[:8]]==['?seen253@@3PAIA']*8
    assert relocs[-1]['symbol']=='?continuation253@@3IA' and 'ret' not in [i.mnemonic for i in hook]
    body,edge_relocs=parser.coff_function(OUT/'objects/state-fixture.obj','?original_edge253@@YAXXZ')
    edge=list(decoder.disasm(body,0x2000));mn=[i.mnemonic for i in edge]
    assert mn==['mov']*7+['push','popfd']+['mov']*7+['jmp','ret']
    assert 'call' not in mn and edge_relocs[-1]['symbol']=='?target253@@3IA'
    # RET is fixture transport after the capture hook resumes host execution;
    # no RET occurs in any original wrapper or in its normalized tail-transfer hook.
    assert 'for(U wrapper=0;wrapper<3' in driver.FIXTURE
    assert 'align<8' in driver.FIXTURE and 'value<6' in driver.FIXTURE and 'flags<16' in driver.FIXTURE and 'seed<8' in driver.FIXTURE
    assert '0x7fffffffu,0x80000000u,0x80000001u,0xffffffffu' in driver.FIXTURE
    assert s['state_comparisons']==3*8*6*16*8==18432
    assert 'state.r[i]==seen253[i]' in driver.FIXTURE and 'state.flags==seed_flags253' in driver.FIXTURE
    assert driver.FIXTURE.count('arena253[i]==before253[i]')==2
    assert 'seen253[i]==(i==1?values[value]:seed253[i])' in driver.FIXTURE
    assert 'state.pc==targets[wrapper] && state.stop==Stop253::MissingEntry' in driver.FIXTURE
    compile_receipt=load(OUT/'compile.execution.json')
    link=load(OUT/'fixture-link.execution.json');native=load(OUT/'fixture-native.execution.json')
    assert compile_receipt['exit_code']==s['compiler_exit_code']==0
    assert compile_receipt['elapsed_seconds']==s['compile_seconds'] and compile_receipt['command']==s['command']
    assert '/MP6' in s['command'] and '/showIncludes' not in s['command']
    assert len([x for x in s['command'] if x.endswith('.cpp')])==5
    assert link['exit_code']==native['exit_code']==s['native_fixture_exit_code']==0
    assert native['elapsed_seconds']==s['native_seconds'] and native['command']==[str(OUT/'state-fixture.exe')]
    assert not re.search(rb'(?:warning|error) [CDL]\d+',b'\n'.join((OUT/p).read_bytes() for p in ['compile.log','fixture-link.log','fixture-native.log']))
    assert s['compile_warnings']==[] and not s['resumed_existing_compile']
    assert digest(OUT/'captured-compile-driver.py')==digest(ROOT/'scripts/research/experiment-v2-x86-tail-dispatch-253.py')
    objects=[str(OUT/'objects'/(va+'.obj')) for va in VAS]+[str(OUT/'objects/dispatch253.obj'),str(OUT/'objects/state-fixture.obj')]
    assert [x for x in link['command'] if x.endswith('.obj')]==objects
    assert len(list((OUT/'objects').glob('*.obj')))==5
    runtime=load(OUT/'runtime-misses.json');parser_proof=load(RUN/'runtime-parser-identity.json')
    assert runtime==dict(original_sha256=SHA,module='Porsche.exe',provenance='isolatedVMpilot',native_game_execution=False,
                         scope='three-tail-wrappers',missing_entry_vas=['00536050','004c7e10','004c7df0'])
    catalog={r['entry_va']:r for r in map(json.loads,(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text(encoding='utf8').splitlines())}
    assert planner.runtime_input(runtime,catalog)==parser_proof['output']
    assert parser_proof['parser_only'] and parser_proof['planner_cli_executions']==0 and parser_proof['queue_unchanged']
    assert parser_proof['input_provenance']=='isolatedVMpilot' and parser_proof['native_game_execution'] is False
    assert parser_proof['wrong_sha_rejected']
    try:planner.runtime_input({**runtime,'original_sha256':'0'*64},catalog)
    except ValueError:pass
    else:raise AssertionError('runtime identity guard failed')
    assert not any(proof[k][va] for k in ['accepted_exact_owners','wip_exact_definitions','accepted_interior_owners'] for va in VAS)
    assert s['translated_original_bytes']==30 and s['translated_original_instructions']==6
    validation=dict(passed=True,kind='read-only-independent-audit',summary_sha256=digest(RUN/'summary.json'),
                    audit_source_sha256=digest(__file__),input_pins=len(s['input_sha256']),original_bytes=30,instructions=6,
                    oracle_normalization='Only terminal JMP REL32 to the controlled capture hook',
                    native_comparisons=18432,compiler_batches=1,compiled_tus=5,compiler_warnings=0,
                    generated_coff_symbols=actual_symbols,missing_entry_vas=runtime['missing_entry_vas'],
                    runtime_provenance='isolatedVMpilot',planner_queue_feed=False,native_game_execution=False,
                    new_accepted_functions=0,guard_tests=8)
    (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:validation[k] for k in ['passed','input_pins','original_bytes','native_comparisons','compiler_batches','new_accepted_functions']}))


if __name__=='__main__':main()
