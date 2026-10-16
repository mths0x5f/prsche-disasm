"""Independent read-only PE/COFF audit of Run254's captured scalar object."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
RUN=Path(__file__).resolve().parent
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def module(path):
    spec=importlib.util.spec_from_file_location('coff_pe_254_audit',path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
def main():
    parser=module(ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py')
    summary=load(RUN/'summary.json');screen=load(RUN/'screening.json');validation=load(RUN/'validation.json')
    assert digest(RUN/'summary.json')==validation['summary_sha256']
    assert digest(RUN/'screening.json')==summary['screening_sha256']
    assert summary['kind']=='original-writable-data' and summary['functions_added']==0
    assert summary['physical_data_cells']==summary['data_symbols']==17
    assert screen['screened']==24 and len(screen['safe_vas'])==17 and len(screen['deferred_vas'])==7
    assert screen['before_after_guards'] and digest(ROOT/screen['owner_scan']['log'])==screen['owner_scan']['log_sha256']
    for name,sha in summary['input_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in screen['input_sha256'].items():assert digest(ROOT/name)==sha,name
    assert summary['compiled']['exit_code']==summary['fixture_link']['exit_code']==summary['native_fixture']['exit_code']==0
    for key in ('compiled','fixture_link','native_fixture'):
        receipt=summary[key]
        assert receipt['seconds']>=0 and digest(ROOT/receipt['log'])==receipt['log_sha256']
    assert len(summary['support_objects'])==1
    support=summary['support_objects'][0]
    assert digest(ROOT/support['generated_source'])==support['generated_source_sha256']
    assert digest(ROOT/support['object'])==support['object_sha256']
    obj=parser.coff(ROOT/support['object'])
    section=next(s for s in obj['sections'] if s['name']=='.ogw$zc')
    assert section['size']==68 and section['chars']&0xc0000000==0xc0000000 and not section['chars']&0x20000000
    assert obj['bytes'][section['raw']:section['raw']+68]==bytes(68)
    assert not any(s['reloc_count'] or (s['size'] and s['chars']&0x20000000) for s in obj['sections'])
    cells=support['storage_sections'][0]['cells']
    assert {c['va'] for c in cells}==set(screen['safe_vas'])
    assert sorted(c['native_offset'] for c in cells)==list(range(0,68,4))
    exports={s['name'] for s in obj['symbols'] if s['section']>0 and s['name'].startswith('?DAT_')}
    assert exports=={c['symbol'] for c in cells}
    for c in cells:
        assert c['initial_bytes']=='00000000'
        sym=[s for s in obj['symbols'] if s['name']==c['symbol']]
        assert len(sym)==1 and sym[0]['value']==c['native_offset']
        assert obj['sections'][sym[0]['section']-1]['name']=='.ogw$zc'
    original=parser.pe(ROOT/'local/game/Porsche.exe')
    assert original['sha256']==summary['original_sha256']
    refs=0
    for row in screen['rows']:
        if not row['safe']:continue
        va=int(row['va'],16);rva=va-original['image_base']
        sec=next(s for s in original['sections'] if s['va']<=rva< s['va']+s['vsize'])
        assert sec['name']=='.data' and sec['chars']&0xc0000000==0xc0000000
        assert rva>=sec['va']+sec['raw_size'] and rva+4<=sec['va']+sec['vsize']
        assert not any(rva-3<=r<rva+4 for r in original['reloc_rvas'])
        highlow_sites={f"{original['image_base']+r:08x}" for r in original['reloc_rvas']}
        assert set(row['complete_HIGHLOW_sites'])<=highlow_sites
        assert {r['HIGHLOW_site'] for r in row['direct_MEM4']}==set(row['complete_HIGHLOW_sites'])
        assert len(row['direct_MEM4'])==len(row['complete_HIGHLOW_sites'])
        refs+=len(row['direct_MEM4'])
    assert refs==summary['original_memory_instructions_verified']==68
    fixture=parser.pe(ROOT/summary['fixture_executable'])
    assert fixture['sha256']==summary['fixture_executable_sha256']
    sec=next(s for s in fixture['sections'] if s['name']=='.ogw')
    assert sec['chars']&0xc0000000==0xc0000000 and not sec['chars']&0x20000000
    assert fixture['bytes'][sec['raw']:sec['raw']+68]==bytes(68)
    assert not any(sec['va']<=r<sec['va']+68 for r in fixture['reloc_rvas'])
    print(json.dumps(dict(passed=True,cells=17,deferred=7,original_references=68,guarded_inputs=len(summary['input_sha256']),native_exit=0)))
if __name__=='__main__':main()
