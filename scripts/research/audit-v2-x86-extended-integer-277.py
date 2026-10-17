"""Independent artifact-only validation of the synthetic277 native proof."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import capstone

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/277-x86-extended-integer'
OUT=ROOT/'local/experiments/v2-x86-extended-integer-277'
BASE_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
BACKEND_SHA='7dd257f43dc304ad183f25dd483a33dd9f76f285b8a7478dd3c9762debbab42b'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def main():
    s=load(RUN/'summary.json');p=load(RUN/'proof-before-compile.json')
    assert s['kind']=='synthetic-x86-extended-integer' and s['backend_sha256']==BACKEND_SHA
    assert s['original_game_functions']==s['new_accepted_functions']==s['native_game_execution_commands']==0
    assert s['production_or_union_changed'] is False and s['before_after_guards'] and not s['resumed_existing_compile']
    assert digest(ROOT/'scripts/research/x86-cpp-backend-257.py')==BASE_SHA and digest(ROOT/'scripts/research/x86-cpp-backend-277.py')==BACKEND_SHA
    for name,h in s['input_sha256'].items():assert digest(ROOT/name)==h,('pin drift',name)
    for path in [Path(__file__),*RUN.glob('*.json'),*OUT.glob('*.cpp'),*OUT.glob('*.h'),*OUT.glob('*.py'),*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:
        assert b'\r' not in path.read_bytes(),('LF',path)
    driver=module('driver277audit','scripts/research/experiment-v2-x86-extended-integer-277.py')
    backend=module('backend277audit','scripts/research/x86-cpp-backend-277.py')
    base=module('fixture262audit277','scripts/research/experiment-v2-x86-cpu-primitives-262.py')
    coff=module('coff277','scripts/research/build-v2-compile-corpus.py');oracle=module('oracle277audit','scripts/research/audit-v2-nested-calls-229.py')
    rows=driver.fragments();assert rows==p['fragments'] and len(rows)==26
    assert backend.HEADER==backend._base.HEADER and hashlib.sha256(backend.HEADER.encode()).hexdigest()==p['baseline_header_sha256']
    assert p['unchanged_helper_header'] and s['unchanged257_header_helpers']
    assert [list(x) for x in backend.PATCHES]==p['lowering_patches']
    assert backend.DERIVED_SOURCE==(OUT/'derived-backend277.py').read_text(encoding='utf8')
    header=backend.HEADER+'\n'+''.join('void translated_'+r['entry']+'(Machine257&);\n' for r in rows)
    assert header==(OUT/'machine257.h').read_text(encoding='utf8') and digest(OUT/'machine257.h')==p['header_sha256']==s['header_sha256']
    fixture=driver.fixture(rows,base);assert fixture==(OUT/'state-fixture.cpp').read_text(encoding='utf8')
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    sources=[];ninstructions=0
    for r in rows:
        raw=bytes.fromhex(r['hex']);decoded=list(decoder.disasm(raw,int(r['entry'],16)));assert sum(i.size for i in decoded)==len(raw)
        src,witness=backend.translate(raw,int(r['entry'],16));sources.append(src);assert witness==p['instruction_lowering'][r['name']]
        assert src.count('if(!step257(')==len(decoded);ninstructions+=len(decoded)
        body,relocs=oracle.coff_function(OUT/'objects/state-fixture.obj','?oracle277_'+str(r['id'])+'@@YAXXZ')
        assert body==raw and relocs==[] and s['oracles'][r['id']]==dict(id=r['id'],name=r['name'],bytes=raw.hex(),relocations=[])
        if r['id']<14:
            i=decoded[0];assert i.mnemonic in ['movsx','movzx']
            assert i.operands[0].size in(2,4) and i.operands[1].size in(1,2) and i.operands[0].size>i.operands[1].size
            code=witness[0]['cpp'];assert code.startswith('U value=')
            if i.mnemonic=='movsx':assert 'value=(value^0x' in code and code.index('value=(value^0x')<code.rindex(';')
        elif r['id']<17:assert decoded[0].mnemonic=='or' and 'logical257(s,a|b,' in witness[0]['cpp']
        elif r['id']<20:assert decoded[0].mnemonic=='not' and 'U value=~(' in witness[0]['cpp'] and 'logical257' not in witness[0]['cpp']
        else:assert decoded[0].mnemonic==r['name'] and r['name'] in ['jg','jle','ja','jbe','jb','jae']
    dispatch='\nvoid dispatch257(Machine257&s,U target){s.pc=target;switch(target){\n'+''.join('case 0x'+r['entry']+'u:translated_'+r['entry']+'(s);return;\n' for r in rows)+'default:s.stop=Stop257::MissingEntry;return;}}\n'
    generated='\n'.join(sources)+dispatch;assert generated==(OUT/'extended277.cpp').read_text(encoding='utf8')
    assert '__asm' not in generated and 'FUN_' not in generated
    assert sum(len(bytes.fromhex(r['hex'])) for r in rows)==s['synthetic_bytes']==164 and ninstructions==s['synthetic_instructions']==70
    # No source is written after its destination: explicit temporaries cover overlap.
    for name in ['movsx-eax-al','movsx-eax-ah','movsx-ax-cl']:
        code=p['instruction_lowering'][name][0]['cpp'];assert code.index('U value=')<code.index('value=(value^')<code.index('s.r[0]=')
    hook,relocs=oracle.coff_function(OUT/'objects/state-fixture.obj','?capture277@@YAXXZ')
    ins=list(decoder.disasm(hook,0x1000));assert [i.mnemonic for i in ins]==['mov']*9+['pushfd','pop']+['mov']*4+['jmp']
    assert ins[8].reg_name(ins[8].operands[0].reg)=='esp' and relocs[8]['symbol']=='?saved_sp277@@3IA'
    assert 'state.r[i]==seen277[i]' in fixture and '(state.flags^seen_flags277)&0x8c1u' in fixture
    assert fixture.count('memory277[i]==before_mem277[i]')==2 and 'stack277[i]==native_stack277[i]' in fixture
    assert '((state.flags^seed_flags277)&0x8c1u)==0' in fixture and '(state.flags&0x801u)==0' in fixture
    assert 'mask<<shift' in fixture and 'seed277[0]&0xffff00ffu' in fixture
    assert 'for(U align=0;align<((id>=6u && id<=11u)?4u:1u);++align)' in fixture
    assert 'flags<16' in fixture and 'seed<4' in fixture and 'seed<8' in fixture
    assert 'case 2:return mask;case 3:return sign-1u;case 4:return sign;case 5:return sign+1u' in fixture
    result=load(OUT/'fixture-result.json')
    assert result==s['case_groups']==dict(provenance='syntheticCPUfixture',native_game_execution=False,cases=30976,failures=0,extensions=16384,logic=13824,conditions=768)
    assert 8*8*16*4+6*8*16*4*4==16384 and 3*8*8*16*4+3*8*16*4==13824 and 6*16*8==768
    assert s['state_comparisons']==16384+13824+768==30976
    symbols=coff.coff_symbols(OUT/'objects/extended277.obj')
    assert set(symbols['defined'])=={'?dispatch257@@YAXAAUMachine257@@I@Z',*[f'?translated_{r["entry"]}@@YAXAAUMachine257@@@Z' for r in rows]}
    # Selected fragments read source/RET memory but write only VM registers.
    assert symbols['undefined']==['?read257@@YAIII@Z'] and not symbols['common'] and not symbols['weak']
    receipts={n:load(OUT/(n+'.execution.json')) for n in ['compile-001','link-001','native-001']}
    assert sorted(x.stem for x in OUT.glob('*.execution.json'))==['compile-001.execution','link-001.execution','native-001.execution']
    assert all(r['exit_code']==0 and r['cwd']==str(OUT) for r in receipts.values())
    assert receipts['compile-001']['command']==s['command'] and receipts['compile-001']['elapsed_seconds']==s['compile_seconds']
    assert receipts['native-001']['elapsed_seconds']==s['native_seconds']
    assert '/MP6' in s['command'] and '/showIncludes' not in s['command'] and len([x for x in s['command'] if x.endswith('.cpp')])==2
    assert len(list((OUT/'objects').glob('*.obj')))==2 and not re.search(rb'(?:warning|error) [CDL]\d+',b'\n'.join(x.read_bytes() for x in OUT.glob('*.log')))
    assert digest(OUT/'captured-compile-driver.py')==digest(ROOT/'scripts/research/experiment-v2-x86-extended-integer-277.py')
    for raw in [b'\xd1\xe0\xc3',b'\xd9\xe8\xc3',b'\x0f\x94\xc0\xc3',b'\x0f\xbe']:
        try:backend.translate(raw,0x1000)
        except ValueError:pass
        else:raise AssertionError(('unsupported accepted',raw.hex()))
    validation=dict(passed=True,kind='artifact-only-independent-native-audit',summary_sha256=digest(RUN/'summary.json'),audit_source_sha256=digest(__file__),
                    backend_sha256=BACKEND_SHA,baseline_backend_sha256=BASE_SHA,header_sha256=s['header_sha256'],input_pins=len(s['input_sha256']),
                    synthetic_entries=26,synthetic_bytes=164,synthetic_instructions=70,exact_oracle_relocations=0,native_comparisons=30976,
                    compiler_batches=1,compiled_tus=2,compiler_warnings=0,generated_coff_symbols=symbols,original_game_functions=0,new_accepted_functions=0,
                    limits=p['limits'])
    (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:validation[k] for k in ['passed','input_pins','native_comparisons','synthetic_bytes','compiler_batches']}))


if __name__=='__main__':main()
