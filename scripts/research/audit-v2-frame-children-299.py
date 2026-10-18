"""Independent captured-COFF and original-byte audit; no compile or native rerun."""
import hashlib,importlib.util,json,re
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/299-frame-action-children'
OUT=ROOT/'local/experiments/v2-frame-action-children-299'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 summary=load(RUN/'summary.json');reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw')
 assert sha(RUN/'summary.json')==load(RUN/'validation.json')['summary_sha256']
 for p,h in summary['tool_sha256'].items():assert sha(p)==h
 body=bytes.fromhex(summary['original_body_hex'])
 pe=mod('pe299',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 assert pe.pe_read((ROOT/'local/game/Porsche.exe').read_bytes(),0x476710,136)==body
 assert len(body)==136 and body[-3:]==bytes.fromhex('c20400')
 assert bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','))==body
 obj=ROOT/summary['game_objects'][0]['path'];assert sha(obj)==summary['game_objects'][0]['sha256']
 coff=mod('coff299',ROOT/'scripts/research/build-v2-compile-corpus.py');symbols=coff.coff_symbols(obj)
 assert symbols==summary['symbols'] and not symbols['undefined'] and not symbols['common'] and not symbols['weak']
 assert len(symbols['defined'])==1 and 'update_00476710' in symbols['defined'][0]
 assert body not in obj.read_bytes(),'Original machine code belongs only to test oracle'
 receipts={k:load(OUT/(k+'-001.receipt.json')) for k in ('compile','link','native')}
 for receipt in receipts.values():
  assert receipt['exit_code']==0 and sha(ROOT/receipt['log'])==receipt['log_sha256']
 compile=receipts['compile'];assert '/MP6' in compile['command'] and '/sourceDependencies' in compile['command']
 assert sum(x.endswith('.cpp') for x in compile['command'])==2
 assert not re.search(rb'(warning|error) [CD]\d+',(ROOT/compile['log']).read_bytes())
 assert load(ROOT/receipts['native']['log'])==dict(cases=648,failures=0)
 game_deps=load(OUT/'dependencies/00476710.cpp.json')['Data'];assert Path(game_deps['Source']).resolve()==(RUN/'00476710.cpp').resolve()
 assert not any('fixture' in p or 'original-body' in p for p in game_deps['Includes'])
 assert len(list(OUT.glob('compile-*.receipt.json')))==1
 reader.cache.check_stable()
 result=dict(passed=True,original_bytes=136,native_cases=648,compiler_batches=1,game_defined=1,game_undefined=0,input_counts=reader.counts)
 (RUN/'audit.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
if __name__=='__main__':main()
