"""Validate frozen197 bytes, corrected storage, COFF and historical identities.

Read-only artifact audit: no Ghidra, compilation, native/original execution or link.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/197-call-free-abi'
EXPORT=RUN/'export/attempt-002'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('coff197audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
coff=importlib.util.module_from_spec(spec)
spec.loader.exec_module(coff)
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def main():
    summary=load(RUN/'summary.json')
    contracts=load(RUN/'contracts-before-analysis.json')
    provenance=load(EXPORT/'provenance.json')
    assert summary['original_sha256']==contracts['original_sha256']==coff.ORIGINAL_SHA
    assert provenance['headless_exit_code']==0 and provenance['original_project_unchanged']
    assert provenance['original_project_before']==provenance['original_project_after']
    assert '-readOnly' in provenance['command'] and '-noanalysis' in provenance['command']
    for name,expected in summary['input_sha256'].items():
        assert digest(ROOT/name)==expected,('input drift',name)
    historical=load(RUN/'historical-artifacts.json')
    checkpoint=load(RUN/'checkpoint.json')
    for row in historical['files']:
        assert digest(ROOT/row['preserved_path'])==row['sha256']==checkpoint['files_sha256'][row['historical_path']]
    assert checkpoint['compiled_objects']==0 and checkpoint['attempt002_tool_status']=='aborted by user after 436.0s'
    raw=(ROOT/'local/game/Porsche.exe').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==coff.ORIGINAL_SHA
    pe=struct.unpack_from('<I',raw,0x3c)[0]
    machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4)
    assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0]
    sections=[struct.unpack_from('<IIII',raw,pe+24+optional+40*i+8)[1:] for i in range(count)]
    def exact(ins):
        rva=int(ins['va'],16)-base
        size=len(ins['bytes'])//2
        start,length,offset=next(s for s in sections if s[0]<=rva and rva+size<=s[0]+s[1])
        assert raw[offset+rva-start:offset+rva-start+size].hex()==ins['bytes'],ins
    for selected in contracts['selected']:
        for ins in selected['original_instructions']:
            exact(ins)
        assert selected['stack8_semantics'].startswith('Not read locally')
    for consumer in contracts['original_call_consumers']:
        for ins in consumer['instructions']:
            exact(ins)
    for row in summary['results']:
        va=row['va']
        after=load(EXPORT/f'after-storage-{va}.json')
        database=after['database']
        storages=[p['storage']['display'] for p in database['parameters']]
        assert storages==['ECX:4','Stack[0x4]:4','Stack[0x8]:4']
        assert all(p['type']=='/undefined4' and p['bytes']==4 for p in database['parameters'])
        assert database['return_storage']['display']=='EAX:4' and database['return_type']=='/undefined4'
        assert database['stack_purge_bytes']==8 and after['inferred']['extra_pop']==12
        assert not after['calls']
        assert row['compiled'] and row['compiler_exit_code']==0 and row['native_ret_bytes'] and set(row['native_ret_bytes'])=={8}
        symbols=coff.coff_symbols(ROOT/row['object'])
        assert symbols==row['symbols']
        assert symbols['defined']==row['defined_external_symbols'] and not symbols['undefined']
        assert not symbols['common'] and not symbols['weak']
        assert digest(ROOT/row['object'])==row['object_sha256']
        assert digest(ROOT/row['generated_source'])==row['generated_source_sha256']
        native=row['native_text_sections']
        assert len(native)==1 and native[0]['relocations']==0
        original=next(c for c in contracts['selected'] if c['va']==va)
        assert (native[0]['bytes']==original['original_body_hex'])==row['exact_original_body_byte_match']
        if va=='004930f0':
            witness=row['original_pointer_store_lowering']
            assert witness['instruction']['bytes']=='8910' and witness['instruction']['va']=='004930fa'
            assert witness['pcode']['opcode']=='STORE' and all(n['bytes']==4 for n in witness['pcode']['inputs'])
            assert [t['text'] for t in witness['tokens']]==['*','stack_4_bits','=','puVar1']
            assert row['exact_original_body_byte_match']
        else:
            assert row['cache_reused'] and row['original_pointer_store_lowering'] is None
    baseline=RUN.parent/'198-native-union/summary.json'
    prior=load(baseline)
    prior_vas={r['va'] for r in prior['results']}
    new_vas={r['va'] for r in summary['results']}
    assert len(prior_vas)==1070 and len(new_vas)==2 and not prior_vas.intersection(new_vas)
    assert len(prior_vas|new_vas)==1072
    paths=[RUN/'summary.json',RUN/'README.md',RUN/'README-blocked-checkpoint.md',RUN/'contracts-before-analysis.json',
           RUN/'checkpoint.json',RUN/'historical-artifacts.json',Path(__file__),*EXPORT.iterdir()]
    assert all(b'\r' not in p.read_bytes() for p in paths if p.is_file())
    result=dict(schema=1,summary_sha256=digest(RUN/'summary.json'),audit_source_sha256=digest(Path(__file__)),
                original_instructions_checked=44,original_CALL_snippets_checked=4,original_project_unchanged=True,
                corrected_storage_contracts=2,real_coff_objects=2,exact_original_body_byte_matches=1,
                unchanged_COFF_reused=1,changed_only_retry=1,actual_MP6_batches_total=2,
                historical_checkpoint_identities_preserved=True,input_guards_passed=True,new_text_LF_before_SHA=True,
                run198_summary_sha256=digest(baseline),disjoint_with_1070_run198=True,combined_unique_vas=1072,
                full_caller_native_execution_equivalence=False,union_relinked=False)
    (RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
