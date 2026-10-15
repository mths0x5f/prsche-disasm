"""Read-only frozen214 consumer/COFF/call-boundary audit; no tool reexecution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/214-sound-output-consumer'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('coff214audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def main():
    summary=load(RUN/'summary.json');proof=load(RUN/'proof-before-compile.json')
    assert summary['original_sha256']==proof['original_sha256']==coff.ORIGINAL_SHA
    for name,expected in summary['input_sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        assert digest(path)==expected,('input drift',name)
    assert summary['original_instruction_count']==len(proof['original_instructions'])==42
    assert summary['ownership_preflight']==dict(canonical_exact_or_interior=0,WIP=0)
    by_pc={r['va']:r for r in proof['original_instructions']}
    assert by_pc['0058f5f8']['bytes']=='8b442400' and by_pc['0058f602']['bytes']=='d1e8'
    assert by_pc['0058f5ed']['bytes']=='ff5110'
    assert by_pc['0058f608']['bytes']=='8b0ddc486b00'
    assert by_pc['0058f62d']['bytes']=='668b0dda486b00'
    assert by_pc['0058f616']['bytes']=='f7f1' and by_pc['0058f63e']['bytes']=='f7f9'
    original_rets=[p for p in proof['original_instructions']if p['instruction'].startswith('RET')]
    assert len(original_rets)==3 and all(r['bytes']=='c3'for r in original_rets)
    row=summary['results'][0];assert row['va']=='0058f5d0' and row['compiled'] and row['compiler_exit_code']==0
    symbols=coff.coff_symbols(ROOT/row['object']);assert symbols==row['symbols']
    source=(ROOT/row['generated_source']).read_text(encoding='utf8')
    assert 'uint local_4;'in source and 'uVar2 = local_4 >> 1;'in source
    assert 'uVar2 = (uint)piVar3'not in source
    assert '(**(GetCurrentPosition214 *)(*piVar3 + 0x10))(piVar3,&local_4,0)'in source
    assert 'uint distance_bits = static_cast<uint>(DAT_006ad78c) - uVar2;'in source
    assert 'distance_bits & 0x80000000u'in source and 'distance_bits * 1000u'in source
    assert 'signed_bits214(scaled_bits) / static_cast<int>(WORD_006b48da_214)'in source
    header=ROOT/'local/experiments/v2-sound-output-consumer-214/consumer214.h'
    text=header.read_text(encoding='utf8')
    assert 'typedef int (__stdcall *GetCurrentPosition214)(int*,uint*,uint*);'in text
    assert 'extern uint _DAT_006b48dc;'in text
    assert 'extern ushort WORD_006b48da_214;'in text and 'base006b48d8+2'in text
    before=(ROOT/row['frozen184_source']).read_text(encoding='utf8')
    reconstructed=source
    for edit in reversed(proof['edits']):
        assert reconstructed.count(edit['replacement'])==1
        reconstructed=reconstructed.replace(edit['replacement'],edit['original'])
    reconstructed=reconstructed.replace('#include "'+header.as_posix()+'"','#include "'+(ROOT/'local/experiments/v2-declaration-compat-184/full/0058f5d0-globals.h').as_posix()+'"')
    assert reconstructed==before, 'unexpected source/algorithm edit'
    asm=(ROOT/row['disassembly']).read_text(encoding='utf8')
    consumer=asm.split('\n?signed_bits214',1)[0]
    assert len(re.findall(r'\bret\s*\n',consumer))==1
    assert not re.search(r'\bret\s+[0-9]',consumer)
    assert row['native_ret_bytes']==[0] and row['native_ret_site_count']==1 and row['original_ret_path_count']==3
    assert summary['metadata_finalization']['compiler_link_native_Ghidra_commands']==0
    assert re.search(r'\bshr\s+\w+,1',consumer)
    assert re.search(r'\bdiv\s',consumer) and re.search(r'\bidiv\s',asm)
    assert re.search(r'mov\s+\w+,dword ptr \[\?_DAT_006b48dc',consumer)
    assert re.search(r'movzx\s+\w+,word ptr \[\?WORD_006b48da_214',asm)
    assert re.search(r'\bcdq\b',asm)
    assert not re.search(r'__ftol|\b(?:fld|fstp|addss|subss|cvtsi)\b',asm,re.I)
    execution=load(ROOT/'local/experiments/v2-sound-output-consumer-214/compile.execution.json')
    assert execution['exit_code']==summary['compiler_batch_exit_code']==0
    assert execution['elapsed_seconds']==summary['compile_seconds']>0
    assert len(execution['command'])==len(summary['compiler_command']) and execution['command']==summary['compiler_command']
    fixture=summary['fixture'];assert fixture['native_exit_code']==0 and fixture['integer_reference_cases']==36864 and fixture['error_or_null_guard_cases']==3
    native=load(ROOT/'local/experiments/v2-sound-output-consumer-214/fixture-native.execution.json')
    assert native['exit_code']==0 and native['elapsed_seconds']==fixture['seconds']
    fixture_asm=(ROOT/'local/experiments/v2-sound-output-consumer-214/fixture-disassembly.log').read_text(encoding='utf8')
    assert re.search(r'\bret\s+0?Ch',fixture_asm)
    baseline=RUN.parent/'215-native-union/summary.json'
    if not baseline.exists():
        candidates=list(RUN.parent.glob('215*/summary.json'));assert len(candidates)==1;baseline=candidates[0]
    existing={r['va']for r in load(baseline)['results']};assert len(existing)==1107 and row['va']not in existing
    paths=[RUN/'summary.json',RUN/'proof-before-compile.json',Path(__file__),ROOT/row['generated_source'],header]
    assert all(b'\r'not in p.read_bytes()for p in paths)
    result=dict(schema=1,summary_sha256=digest(RUN/'summary.json'),audit_source_sha256=digest(Path(__file__)),
                compiled_VA=row['va'],original_PE_instructions=42,original_RET0_paths=3,native_RET0_epilogues=1,
                callback_contract='HRESULT32 stdcall(self,DWORD*play,DWORD*write),callee cleanup12',
                corrected_output_DWORD_dataflow=True,modulo32_SUB_ADD_scale_and_signedIDIV=True,exact_RAM4_RAM1_RAM2_views=True,
                callback_integer_reference_cases=36864,callback_failure_or_null_cases=3,native_fixture_exit_code=0,
                actual_compiler_batches=1,changed_game_TUs=1,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=summary['compile_seconds'],
                all_input_SHA_guards_passed=True,frozen184_source_unchanged=True,canonical_interior_WIP_owners=0,
                private_word_alias=dict(name='WORD_006b48da_214',original_RAM='006b48da',bytes=2,overlaps_base='DAT_006b48d8',offset=2,native_shared_owner_binding_deferred=True),
                run215_summary_sha256=digest(baseline),disjoint_with_1107_run215=True,combined_unique_VAs=1108,
                new_text_LF_before_SHA=True,game_union_changes=False,full_provider_fault_register_fidelity=False)
    (RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(result))


if __name__=='__main__':main()
