"""Check305 captured input closure, original relocations and native receipts."""
import hashlib,importlib.util,json,re
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'iterations/v2/001-original-recovery/runs/305-file-pool-shutdown';OUT=ROOT/'local/experiments/v2-file-pool-shutdown-305'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 summary=load(RUN/'summary.json');reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw')
 assert sha(RUN/'summary.json')==load(RUN/'validation.json')['summary_sha256']
 for p,h in summary['tool_sha256'].items():assert sha(p)==h
 body=bytes.fromhex(summary['original_body_hex']);pe=mod('pe305',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 assert len(body)==248 and pe.pe_read((ROOT/'local/game/Porsche.exe').read_bytes(),0x5678f0,248)==body
 assert bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','))==body
 captured=[]
 for offset,nxt,target in re.findall(r'\{(\d+),(\d+),0x([0-9a-f]+)\}',(RUN/'relocations.inc').read_text()):
  offset,nxt,target=int(offset),int(nxt),int(target,16);captured.append(dict(offset=offset,next=nxt,target=target))
  value=int.from_bytes(body[offset:offset+4],'little',signed=bool(nxt))
  assert (0x5678f0+nxt+value if nxt else value)==target
 assert captured==summary['original_relocations'] and len(captured)==26
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
 assert set(summary['accepted_callee_vas'])<={x['entry_va'] for x in registry}
 assert len(summary['accepted_callee_vas'])==9 and not any(x['entry_va']=='005678f0' for x in registry)
 obj=ROOT/summary['game_objects'][0]['path'];coff=mod('coff305',ROOT/'scripts/research/build-v2-compile-corpus.py');symbols=coff.coff_symbols(obj)
 assert sha(obj)==summary['game_objects'][0]['sha256'] and symbols==summary['symbols']
 assert symbols['defined']==['?application_pool_shutdown_005678f0@porsche@@YAXXZ','__Avx2WmemEnabledWeakValue']
 assert len(symbols['undefined'])==15 and not symbols['common'] and not symbols['weak'] and body not in obj.read_bytes()
 receipts={x:load(OUT/(x+'-001.receipt.json')) for x in ('compile','link','native')}
 for receipt in receipts.values():assert receipt['exit_code']==0 and sha(ROOT/receipt['log'])==receipt['log_sha256']
 command=receipts['compile']['command'];assert '/MP6' in command and '/sourceDependencies' in command and sum(x.endswith('.cpp') for x in command)==2
 assert not re.search(rb'(warning|error) [CD]\d+',(ROOT/receipts['compile']['log']).read_bytes())
 assert load(ROOT/receipts['native']['log'])==dict(cases=48,failures=0)
 before=load(OUT/'before-001.json');oldproducer=OUT/'producer-before-finalization.py';assert before['input_sha256']['scripts/research/experiment-v2-pool-shutdown-305.py']==sha(oldproducer)
 for name,h in before['input_sha256'].items():
  if name!='scripts/research/experiment-v2-pool-shutdown-305.py':assert sha(ROOT/name)==h
 deps=load(OUT/'dependencies/005678f0.cpp.json')['Data'];assert Path(deps['Source']).resolve()==(RUN/'005678f0.cpp').resolve()
 assert not any('fixture' in x or 'original-body' in x for x in deps['Includes'])
 header=Path('C:/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0/ucrt/wchar.h')
 assert header.as_posix().lower() in {x.lower().replace('\\','/') for x in deps['Includes']}
 assert b'__declspec(selectany) int _Avx2WmemEnabledWeakValue = 0;' in header.read_bytes()
 assert len(list(OUT.glob('compile-*.receipt.json')))==1;reader.cache.check_stable()
 result=dict(passed=True,original_bytes=248,original_relocations=26,native_cases=48,compiler_batches=1,game_function_definitions=1,compiler_support_definitions=1,canonical_undefined=15,accepted_callees=9,reader_counts=reader.counts)
 (RUN/'audit.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
if __name__=='__main__':main()
