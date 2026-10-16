"""Read-only independent Run258 audit; no compiler/linker/native/Ghidra commands."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

import capstone
from capstone.x86 import X86_OP_IMM

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/258-x86-call-chain'
OUT=ROOT/'local/experiments/v2-x86-call-chain-258'
VAS=('00515ca0','004bc610','00466e60','00466e80','004cecc0','004e0dc0')
CHAINS=(('00515ca0','004bc610'),('00466e60','00466e80'),('004cecc0','004e0dc0'))
SIZES=(18,5,29,9,20,23)
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BACKEND_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def original_bytes(image,va,n):
    # Independent PE file-offset translation; not the generator's index helper.
    pe=struct.unpack_from('<I',image,0x3c)[0];assert image[pe:pe+4]==b'PE\0\0'
    count=struct.unpack_from('<H',image,pe+6)[0];optional=struct.unpack_from('<H',image,pe+20)[0]
    base=struct.unpack_from('<I',image,pe+24+28)[0];rva=int(va,16)-base
    for i in range(count):
        p=pe+24+optional+40*i;virtual,start,size,offset=struct.unpack_from('<IIII',image,p+8)
        if start<=rva and rva+n<=start+size:
            assert rva+n<=start+virtual
            return image[offset+rva-start:offset+rva-start+n]
    raise AssertionError(('not file backed',va))


def main():
    s=load(RUN/'summary.json');proof=load(RUN/'proof-before-compile.json');selection=load(RUN/'selection.json')
    assert s['kind']=='isolated-x86-call-chain-pilot' and s['original_sha256']==SHA
    assert tuple(s['experimental_vas'])==VAS and [tuple(x) for x in s['chains']]==list(CHAINS)
    assert s['new_accepted_functions']==0 and s['production_or_union_changed'] is False
    assert s['native_game_execution_commands']==0 and not s['planner_queue_feed']
    assert s['actual_compiler_batches']==1 and s['before_after_guards'] and not s['resumed_existing_compile']
    assert proof['backend_sha256']==BACKEND_SHA==digest(ROOT/'scripts/research/x86-cpp-backend-257.py')
    for name,h in s['input_sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        assert digest(path)==h,('input hash drift',name)
    for path in [Path(__file__),*RUN.glob('*.json'),*OUT.glob('*.cpp'),*OUT.glob('*.h'),*OUT.glob('*.py'),*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:
        assert b'\r' not in path.read_bytes(),('LF',path)
    driver=module('driver258_audit','scripts/research/experiment-v2-x86-call-chain-258.py')
    backend=module('backend257_audit258','scripts/research/x86-cpp-backend-257.py')
    coff=module('coff258_audit','scripts/research/build-v2-compile-corpus.py')
    oracle=module('oracle258_audit','scripts/research/audit-v2-nested-calls-229.py')
    header=backend.HEADER+'\n'+''.join('void translated_'+va+'(Machine257&);\n' for va in VAS)
    assert (OUT/'machine257.h').read_text(encoding='utf8')==header
    assert (OUT/'dispatch258.cpp').read_text(encoding='utf8')==driver.DISPATCH
    assert (OUT/'state-fixture.cpp').read_text(encoding='utf8')==driver.FIXTURE
    assert digest(OUT/'captured-compile-driver.py')==digest(ROOT/'scripts/research/experiment-v2-x86-call-chain-258.py')
    image=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    decoded={};actual_symbols={};instruction_count=0
    for va,n in zip(VAS,SIZES):
        raw=original_bytes(image,va,n);assert raw.hex()==proof['original_hex'][va]
        instructions=list(decoder.disasm(raw,int(va,16)));decoded[va]=instructions
        assert sum(i.size for i in instructions)==n and instructions[-1].mnemonic=='ret'
        generated,witness=backend.translate(raw,int(va,16))
        assert generated==(OUT/(va+'.cpp')).read_text(encoding='utf8') and witness==proof['instruction_lowering'][va]
        assert generated.count('if(!step257(')==len(instructions)
        assert '__asm' not in generated and 'FUN_' not in generated
        instruction_count+=len(instructions)
        calls=[i for i in instructions if i.mnemonic=='call']
        if va in dict(CHAINS):
            assert len(calls)==1 and calls[0].operands[0].type==X86_OP_IMM
            assert calls[0].operands[0].imm==int(dict(CHAINS)[va],16)
            offset=calls[0].address-int(va,16)+1
            expected_relocs=[dict(offset=offset,symbol='?original_'+dict(CHAINS)[va]+'_258@@YAXXZ',type=20)]
            call_code=next(w['cpp'] for w in witness if w['mnemonic']=='call')
            return_pc=calls[0].address+calls[0].size
            assert f'call257(s,target,0x{return_pc:08x}u)' in call_code
        else:assert calls==[];expected_relocs=[]
        body,relocs=oracle.coff_function(OUT/'objects/state-fixture.obj','?original_'+va+'_258@@YAXXZ')
        expected=bytearray(raw)
        for row in expected_relocs:expected[row['offset']:row['offset']+4]=bytes(4)
        assert body==expected and relocs==expected_relocs,('exact original oracle',va)
        assert next(r for r in s['oracle'] if r['va']==va)==dict(va=va,bytes=n,relocations=relocs,normalized_only_call_rel32=True)
        symbols=coff.coff_symbols(OUT/'objects'/(va+'.obj'));actual_symbols[va]=symbols
        assert symbols['defined']==[f'?translated_{va}@@YAXAAUMachine257@@@Z']
        assert not symbols['common'] and not symbols['weak'] and not any('FUN_' in x for x in symbols['defined']+symbols['undefined'])
    assert instruction_count==s['translated_original_instructions']==34 and sum(SIZES)==s['translated_original_bytes']==104
    assert sum(len(r['relocations']) for r in s['oracle'])==3
    assert [[i.operands[0].imm if i.operands else 0 for i in decoded[v] if i.mnemonic=='ret'] for v in VAS]==[[0],[0],[4],[4],[0],[8]]
    expected_mappings=[dict(caller=a,callee=b,original_return_pc=pc,native_oracle_offset=offset,guest_call_slot_delta=delta,caller_cleanup=cleanup)
                       for (a,b),pc,offset,delta,cleanup in zip(CHAINS,['00515ca8','00466e7a','004cecd3'],[8,26,19],[-8,-8,-12],[0,4,0])]
    assert proof['return_pc_mapping']==expected_mappings
    # These are the only two normalized slots: top-level capture return and
    # the actually executed CALL slot, with native/original PCs checked first.
    fixture=driver.FIXTURE
    assert 'read257(sp,4)==reinterpret_cast<U>(&capture258)' in fixture
    assert 'read257(call_slot,4)==reinterpret_cast<U>(originals[chain])+return_offsets[chain]' in fixture
    assert 'if(chain!=2 || present)' in fixture
    assert fixture.count('memcpy(native_stack258+')==2
    assert 'memcpy(native_stack258+offset,&original_pc,4u)' in fixture and 'memcpy(native_stack258+128,&halt258,4u)' in fixture
    assert 'state.r[4]==sp+(chain==1?8u:4u)' in fixture
    assert 'callee_entry_sp258==call_slot && callee_entry_return258==return_pcs[chain]' in fixture
    assert 'state.r[i]==seen258[i]' in fixture and '(state.flags^seen_flags258)&0x8c1u' in fixture
    assert 'arena258[i]==native_memory258[i]' in fixture and 'stack258[i]==native_stack258[i]' in fixture
    assert s['state_comparisons']==3*8*6*16*8*2==36864
    # Actual hook moves ESP off the guest arena before PUSHFD. No original
    # stack or return slot can be overwritten by post-RET flag capture.
    hook,hook_relocs=oracle.coff_function(OUT/'objects/state-fixture.obj','?capture258@@YAXXZ')
    hook_ins=list(decoder.disasm(hook,0x1000))
    assert [i.mnemonic for i in hook_ins]==['mov']*9+['pushfd','pop']+['mov']*4+['jmp']
    assert [i.reg_name(i.operands[1].reg) for i in hook_ins[:8]]==['eax','ecx','edx','ebx','esp','ebp','esi','edi']
    assert hook_ins[8].reg_name(hook_ins[8].operands[0].reg)=='esp'
    assert hook_relocs[8]['symbol']=='?saved_sp258@@3IA' and hook_relocs[-1]['symbol']=='?continuation258@@3IA'
    assert all(r['type']==6 for r in hook_relocs) and 'ret' not in [i.mnemonic for i in hook_ins]
    edge,edge_relocs=oracle.coff_function(OUT/'objects/state-fixture.obj','?original_edge258@@YAXXZ')
    edge_ins=list(decoder.disasm(edge,0x2000))
    assert [i.mnemonic for i in edge_ins]==['mov']*7+['push','popfd']+['mov']*8+['jmp','ret']
    assert edge_relocs[-2]['symbol']=='?guest_sp258@@3IA' and edge_relocs[-1]['symbol']=='?target258@@3IA'
    for key in ['accepted_exact_owners','wip_exact_definitions','accepted_interior_owners']:
        assert not any(proof[key][va] for va in VAS)
    assert s['existing_compiled_regression_vas']==['00466e80','004bc610','004e0dc0']
    assert set(proof['existing_compiled_regressions'])==set(s['existing_compiled_regression_vas'])
    assert selection['closed_candidates']==13 and selection['indexed_bodies_scanned']==2949 and selection['native_execution_commands']==0
    for caller,callee in CHAINS:
        row=next(r for r in selection['candidates'] if r['caller']==caller)
        assert row['callees']==[callee] and row['bodies'][caller]['hex']==proof['original_hex'][caller]
    for raw in [b'\xf7\xf1\xc3',b'\xe8\x00',b'\xd9\xe8\xc3',b'\xcc']:
        try:backend.translate(raw,0x1000)
        except ValueError:pass
        else:raise AssertionError(('unsupported accepted',raw.hex()))
    assert proof['unsupported_rejected']==['DIV','truncated CALL','x87','INT3']
    assert 'bad_return_injection258=1;dispatch257(bad,0x00515ca0u);bad_return_injection258=0;' in fixture
    assert 'bad.stop==Stop257::BadReturn && bad.pc==(0x00515ca8u^1u)' in fixture
    assert 'arena258[3+0x2c]==0xa5u && arena258[3+0x2d]==0xa5u' in fixture
    assert 'missing_call.stop==Stop257::MissingEntry' in fixture and '!resumed' in fixture
    assert 'exhausted.budget=0' in fixture and 'exhausted.stop==Stop257::BudgetExhausted' in fixture
    result=load(OUT/'fixture-result.json')
    assert result==dict(original_sha256=SHA,module='Porsche.exe',provenance='isolatedVMpilot',native_game_execution=False,
                        scope='closed-call-chain-and-synthetic-negative-tests',cases=36864,failures=0,
                        synthetic_missing_entry_events=2,synthetic_missing_entry_pc='00ff1234')
    compile_receipt=load(OUT/'compile.execution.json');link=load(OUT/'fixture-link.execution.json');native=load(OUT/'fixture-native.execution.json')
    assert compile_receipt['command']==s['command'] and compile_receipt['exit_code']==s['compiler_exit_code']==0
    assert compile_receipt['elapsed_seconds']==s['compile_seconds'] and compile_receipt['cwd']==str(OUT)
    assert '/MP6' in s['command'] and '/showIncludes' not in s['command'] and len([x for x in s['command'] if x.endswith('.cpp')])==8
    assert link['exit_code']==native['exit_code']==s['native_fixture_exit_code']==0
    assert native['elapsed_seconds']==s['native_seconds'] and native['command']==[str(OUT/'state-fixture.exe')]
    assert all(r['cwd']==str(OUT) for r in [compile_receipt,link,native])
    assert len(list((OUT/'objects').glob('*.obj')))==8
    assert len([x for x in link['command'] if x.endswith('.obj')])==8
    assert not re.search(rb'(?:warning|error) [CDL]\d+',b'\n'.join((OUT/p).read_bytes() for p in ['compile.log','fixture-link.log','fixture-native.log']))
    assert s['compiler_warnings']==0
    validation=dict(passed=True,kind='read-only-independent-audit',summary_sha256=digest(RUN/'summary.json'),audit_source_sha256=digest(__file__),
                    input_pins=len(s['input_sha256']),original_bytes=104,instructions=34,original_oracles=6,normalized_call_rel32=3,
                    native_comparisons=36864,compiler_batches=1,compiled_tus=8,compiler_warnings=0,backend_sha256=BACKEND_SHA,
                    exact_guest_return_slot_mappings=expected_mappings,generated_coff_symbols=actual_symbols,
                    negative_tests=s['negative_tests'],unsupported_rejections=4,fixture_provenance='isolatedVMpilot',native_game_execution=False,
                    new_accepted_functions=0,planner_queue_feed=False,
                    limits='Only selected6original bodies have native proof; other257instructions/widths and gameexecution remain unvalidated here.')
    (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:validation[k] for k in ['passed','input_pins','original_bytes','native_comparisons','compiler_batches','new_accepted_functions']}))


if __name__=='__main__':main()
