"""Read-only audit of the bounded202 representation repair and native capture."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/202-float-bit-stores'
OUT=ROOT/'local/experiments/v2-float-bits-202'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('coff202audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def main():
    summary=load(RUN/'summary.json');proof=load(RUN/'proof-before-compile.json')
    assert summary['original_sha256']==proof['original_sha256']==coff.ORIGINAL_SHA
    for name,expected in summary['input_sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        assert digest(path)==expected,('input drift',name)
    provenance=load(OUT/'capture-provenance.json')
    assert provenance['original_project_unchanged'] and provenance['headless_exit_code']==0
    assert provenance['read_only'] and not provenance['autoanalysis']
    assert proof['original_instruction_count']==summary['original_instructions_checked']==97
    assert proof['all_other_body_lines_preserved'] and summary['all_other_body_lines_preserved']
    edits=proof['edits'];assert len(edits)==18
    assert sum(e['kind']=='raw_MOV4_store' for e in edits)==8
    assert sum(e['kind']=='raw_MOV4_capture_before_FSTP' for e in edits)==1
    assert sum(e['kind']=='raw_MOV4_store_after_FSTP' for e in edits)==1
    reads=[e for e in edits if e['kind']=='raw32_to_float4_view'];assert len(reads)==8
    for e in reads:
        p=e['witness']['high_CAST'];assert p['opcode']=='CAST'
        assert p['inputs'][0]['bytes']==p['output']['bytes']==4
        assert p['inputs'][0]['high_type']=='/undefined4' and p['output']['high_type']=='/float'
    producer=next(e for e in edits if e['kind']=='raw_MOV4_capture_before_FSTP')
    final=next(e for e in edits if e['kind']=='raw_MOV4_store_after_FSTP')
    assert producer['pcs']==['004851e0'] and final['pcs']==['004851e5']
    assert producer['witness']['instruction']['bytes']=='8b470c'
    assert producer['witness']['intervening_FSTP']['bytes']=='d91e'
    row=summary['results'][0];assert row['va']=='00485100' and row['compiled']
    assert coff.coff_symbols(ROOT/row['object'])['defined']==row['defined_external_symbols']
    assert '__ftol3' not in row['undefined_external_symbols']
    source=(ROOT/row['generated_source']).read_text(encoding='utf8')
    assert source.index(producer['replacement'])<source.index('*pfVar2 = fVar4;')<source.index(final['replacement'])
    assert source.count('original_float4_view(&param_1[')==8
    assert not re.search(r'\(float\)param_1\[(5|9)\]',source)
    assert 'return param_1;' in source
    old=load(ROOT/'iterations/v2/001-original-recovery/runs/200-global-float-views/summary.json')
    baseline=next(r for r in old['results'] if r['va']=='00485100')
    assert digest(ROOT/baseline['object'])==baseline['object_sha256']
    assert '__ftol3' in baseline['undefined_external_symbols']
    assert len(baseline['diagnostics'])==9 and all(d['code']=='C4244' for d in baseline['diagnostics'])
    native=(OUT/'native/corrected-disassembly.txt').read_text(encoding='utf8')
    first=native.split('?original_float4_view',1)[0]
    assert not re.search(r'\bcall\b',first)
    assert re.findall(r'\bret\s+([0-9A-Fa-f]+)',first)==['8']
    assert re.search(r'mov\s+esi,ecx',first) and re.search(r'mov\s+eax,esi',first)
    assert not re.search(r'__ftol3|\b(?:cvtdq2pd|cvtpd2ps|cvtsi2ss|cvtsi2sd|cvttss2si|fild|fistp)\b',native,re.I)
    assert summary['fixture']['exit_code']==0 and summary['fixture']['representation_cases']==1024
    assert summary['fixture']['patterns']==16 and summary['fixture']['alignments']==4
    assert summary['fixture']['overlap_deltas']==list(range(-3,4))
    assert summary['metadata_finalize_existing'] and summary['compiler_commands_this_pass']==summary['native_execution_commands_this_pass']==0
    assert summary['actual_compiler_batches']==1 and summary['changed_game_TUs']==1 and summary['synthetic_fixture_TUs']==1
    for path in [RUN/'summary.json',RUN/'proof-before-compile.json',OUT/'native/00485100.cpp',OUT/'native/original-raw4-202.h',
                 OUT/'native/bitcopy-fixture.cpp',OUT/'native/compile.log',OUT/'native/capture-incomplete.json']:
        assert b'\r' not in path.read_bytes(),('nonLF artifact',path)
    result=dict(schema=1,summary_sha256=digest(RUN/'summary.json'),audit_source_sha256=digest(Path(__file__)),
                original_instructions_checked=97,raw_MOV_store_repairs=9,raw32_float4_CAST_views=8,original_project_unchanged=True,
                native_representation_cases=1024,final_count_check=1,native_fixture_exit_code=0,all_input_SHA_guards_passed=True,
                unsafe200_object_preserved=True,numeric_conversion_helpers_removed=True,receiver_input_return_this_RET8_preserved=True,
                physical_outgoing_ECX_register_equivalence=False,branch_arithmetic_source_preserved=True,
                actual_compiler_batches=1,metadata_finalization_reexecution_commands=0,new_game_COFF_objects=1,
                no_game_union_integration=True,original_x87_fullbody_acceptance=False)
    (RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result))


if __name__=='__main__':main()
