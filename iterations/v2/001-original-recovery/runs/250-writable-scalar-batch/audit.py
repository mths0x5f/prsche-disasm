"""Independent read-only PE/COFF check of Run250's captured data packet."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
RUN=Path(__file__).resolve().parent
EXPECTED={'00690848','00656864','00656ac0','006a6450','00699c84','00699fe0'}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    spec=importlib.util.spec_from_file_location('independent250',path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
def main():
    parser=load(ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py')
    summary=json.loads((RUN/'summary.json').read_bytes())
    validation=json.loads((RUN/'validation.json').read_bytes())
    pre=json.loads((RUN/'preflight.json').read_bytes())
    assert sha(RUN/'summary.json')==validation['summary_sha256']
    assert summary['kind']=='original-writable-data' and summary['functions_added']==0
    assert summary['physical_data_cells']==summary['data_symbols']==6
    assert set(pre['selected_vas'])==EXPECTED and pre['safe_for_bounded_storage']
    assert set(summary['deferred'])=={'0065b928','006c0508'}
    for name,expected in summary['input_sha256'].items():
        assert sha(ROOT/name)==expected,name
    for name,expected in pre['input_sha256'].items():
        assert sha(ROOT/name)==expected,name
    assert summary['compiled']['exit_code']==summary['fixture_link']['exit_code']==summary['native_fixture']['exit_code']==0
    for key in ('compiled','fixture_link','native_fixture'):
        receipt=summary[key]
        assert receipt['seconds']>=0 and sha(ROOT/receipt['log'])==receipt['log_sha256']
    support=summary['support_objects']
    assert len(support)==1
    row=support[0]
    assert sha(ROOT/row['object'])==row['object_sha256']
    assert sha(ROOT/row['generated_source'])==row['generated_source_sha256']
    obj=parser.coff(ROOT/row['object'])
    section=next(s for s in obj['sections'] if s['name']=='.ogw$zb')
    assert section['size']==24 and section['chars']&0xc0000000==0xc0000000
    assert not section['chars']&0x20000000 and section['reloc_count']==0
    assert obj['bytes'][section['raw']:section['raw']+24]==bytes(24)
    assert not any(s['reloc_count'] or (s['size'] and s['chars']&0x20000000) for s in obj['sections'])
    cells=row['storage_sections'][0]['cells']
    assert {c['va'] for c in cells}==EXPECTED
    assert sorted(c['native_offset'] for c in cells)==list(range(0,24,4))
    assert all(c['initial_bytes']=='00000000' for c in cells)
    for cell in cells:
        matches=[s for s in obj['symbols'] if s['name']==cell['symbol']]
        assert len(matches)==1 and matches[0]['value']==cell['native_offset']
        assert obj['sections'][matches[0]['section']-1]['name']=='.ogw$zb'
    pe=parser.pe(ROOT/'local/game/Porsche.exe')
    assert pe['sha256']==summary['original_sha256']
    for va in EXPECTED:
        n=int(va,16)
        sec=next(s for s in pe['sections'] if s['va']<=n-pe['image_base']<s['va']+s['vsize'])
        assert sec['name']=='.data' and sec['chars']&0xc0000000==0xc0000000
        assert n-pe['image_base']>=sec['va']+sec['raw_size']
        assert not any(n-pe['image_base']-3<=r<n-pe['image_base']+4 for r in pe['reloc_rvas'])
        assert len(pre['original_MEM4'][va])==len(pre['complete_HIGHLOW_sites'][va])
    fixture=parser.pe(ROOT/summary['fixture_executable'])
    assert fixture['sha256']==summary['fixture_executable_sha256']
    fsec=next(s for s in fixture['sections'] if s['name']=='.ogw')
    assert fsec['chars']&0xc0000000==0xc0000000 and not fsec['chars']&0x20000000
    assert fixture['bytes'][fsec['raw']:fsec['raw']+24]==bytes(24)
    assert not any(fsec['va']<=r<fsec['va']+24 for r in fixture['reloc_rvas'])
    print(json.dumps(dict(passed=True,cells=6,refs=sum(map(len,pre['original_MEM4'].values())),deferred=2,pins=len(summary['input_sha256']))))
if __name__=='__main__': main()
