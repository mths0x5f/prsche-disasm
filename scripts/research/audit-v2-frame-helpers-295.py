"""Independent read-only acceptance of frame helper packet295."""
import hashlib, importlib.util, json
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/295-frame-helpers'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 s=load(RUN/'summary.json');r=ManifestReader(ROOT)
 r.verify(s,expected_hash_mode='raw');r.verify(s,'source',expected_hash_mode='raw')
 for key in ('output_sha256','external_tools_sha256','external_dependencies_sha256'):
  for path,h in s[key].items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==h,path
 assert sha(RUN/'summary.json')==load(RUN/'validation.json')['summary_sha256']
 pe=module('pe295audit',ROOT/'scripts/research/audit-v2-frame-service-290.py');image=(ROOT/'local/game/Porsche.exe').read_bytes()
 assert sha(ROOT/'local/game/Porsche.exe')==s['original_sha256']
 for va,row in s['original_bodies'].items(): assert pe.pe_read(image,int(va,16),row['size']).hex()==row['hex']
 cof=module('coff295audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 for row,symbols in zip(s['game_objects'],s['symbols']):
  assert sha(ROOT/row['path'])==row['sha256'] and cof.coff_symbols(ROOT/row['path'])==symbols
  assert len(symbols['defined'])==1 and not symbols['common'] and not symbols['weak']
 assert not s['symbols'][0]['undefined'] and len(s['symbols'][1]['undefined'])==2
 out=ROOT/'local/experiments/v2-frame-helpers-295'/s['attempt']
 for name in ('compile','link','native'):
  receipt=load(out/(name+'.receipt.json'));assert receipt['exit_code']==0 and sha(ROOT/receipt['log'])==receipt['log_sha256']
 assert load(out/'native.log')==dict(cases=11,failures=0)
 assert 'const volatile std::uint32_t*>(self + 0x18)' in (RUN/'00482e50.cpp').read_text()
 r.cache.check_stable()
 print(json.dumps(dict(passed=True,original_bytes=136,native_cases=11,game_bodies=2,external_float_cells=2)))
if __name__=='__main__': main()
