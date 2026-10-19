"""Independently check307 original operands, canonical contracts and captured run."""
import hashlib,importlib.util,json,re
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'iterations/v2/001-original-recovery/runs/307-disk-slot-shutdown';OUT=ROOT/'local/experiments/v2-disk-slot-shutdown-307'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 summary=load(RUN/'summary.json');reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw')
 assert sha(RUN/'summary.json')==load(RUN/'validation.json')['summary_sha256']
 for p,h in summary['tool_sha256'].items():assert sha(p)==h
 body=bytes.fromhex(summary['original_body_hex']);pe=mod('pe307',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 assert len(body)==181 and pe.pe_read((ROOT/'local/game/Porsche.exe').read_bytes(),0x5918c0,181)==body
 assert bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','))==body
 captured=[]
 for offset,nxt,target in re.findall(r'\{(\d+),(\d+),0x([0-9a-f]+)\}',(RUN/'relocations.inc').read_text()):
  offset,nxt,target=int(offset),int(nxt),int(target,16);captured.append(dict(offset=offset,next=nxt,target=target));value=int.from_bytes(body[offset:offset+4],'little',signed=bool(nxt))
  assert (0x5918c0+nxt+value if nxt else value)==target
 assert captured==summary['original_relocations'] and len(captured)==18
 # The end value is used only by the internal CMP. Original loop starts at the
 # array, advances4 and exits at +128; no dereference or escape uses this end.
 assert body[105:110]==bytes.fromhex('befcef6a00')
 assert body[131:142]==bytes.fromhex('83c60481fe7cf06a007ce0')
 assert 0x6af07c-0x6aeffc==32*4 and summary['endpoint_relocation']['offset']==136
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions'];assert set(summary['accepted_callee_vas'])<={x['entry_va'] for x in registry}
 obj=ROOT/summary['game_objects'][0]['path'];coff=mod('coff307',ROOT/'scripts/research/build-v2-compile-corpus.py');symbols=coff.coff_symbols(obj)
 assert sha(obj)==summary['game_objects'][0]['sha256'] and symbols==summary['symbols']
 assert symbols['defined']==['?application_pool_disk_slots_release_005918c0@porsche@@YAXXZ']
 assert len(symbols['undefined'])==9 and not symbols['common'] and not symbols['weak'] and body not in obj.read_bytes()
 receipts={x:load(OUT/(x+'-001.receipt.json')) for x in ('compile','native')}
 receipts['link']=load(OUT/'link-004.receipt.json')
 for receipt in receipts.values():assert receipt['exit_code']==0 and sha(ROOT/receipt['log'])==receipt['log_sha256']
 for name in ('001','002'):
  failed=load(OUT/('link-'+name+'.receipt.json'));assert failed['exit_code']!=0 and b'_memset' in (ROOT/failed['log']).read_bytes() and sha(ROOT/failed['log'])==failed['log_sha256']
 failed=load(OUT/'link-003.receipt.json');assert failed['exit_code']!=0 and b'___isa_available' in (ROOT/failed['log']).read_bytes() and sha(ROOT/failed['log'])==failed['log_sha256']
 origin=summary['fixture_runtime_support'];library=ROOT/origin['library'];member=ROOT/origin['object']
 assert sha(library)==origin['library_sha256'] and sha(member)==origin['object_sha256']
 start=origin['member_offset'];data=library.read_bytes();assert data[start:start+60].hex()==origin['member_header_hex']
 assert member.read_bytes()==data[start+60:start+60+origin['member_bytes']]
 member_symbols=coff.coff_symbols(member);assert member_symbols['undefined']==['__imp__IsProcessorFeaturePresent@4']
 assert all(x in member_symbols['defined'] for x in ('___isa_available','___isa_enabled','___favor'))
 assert str(member) in receipts['link']['command'] and str(library) not in receipts['link']['command']
 assert not any('memset' in x or 'isa_' in x or 'favor' in x for x in symbols['defined']+symbols['undefined'])
 command=receipts['compile']['command'];assert '/MP6' in command and '/sourceDependencies' in command and sum(x.endswith('.cpp') for x in command)==2
 assert not re.search(rb'(warning|error) [CD]\d+',(ROOT/receipts['compile']['log']).read_bytes())
 assert load(ROOT/receipts['native']['log'])==dict(cases=48,failures=0)
 before=load(OUT/'before-001.json');assert before['input_sha256']['scripts/research/experiment-v2-disk-shutdown-307.py']==sha(OUT/'producer-before-finalization.py')
 for name,h in before['input_sha256'].items():
  if name!='scripts/research/experiment-v2-disk-shutdown-307.py':assert sha(ROOT/name)==h
 deps=load(OUT/'dependencies/005918c0.cpp.json')['Data'];assert Path(deps['Source']).resolve()==(RUN/'005918c0.cpp').resolve();assert not any('fixture' in x or 'original-body' in x for x in deps['Includes'])
 assert len(list(OUT.glob('compile-*.receipt.json')))==1;reader.cache.check_stable()
 result=dict(passed=True,original_bytes=181,original_relocations=18,native_cases=48,compiler_batches=1,game_defined=1,canonical_undefined=9,accepted_callees=5,end_literal_is_internal_bound=True,failed_link_receipts_preserved=3,fixture_runtime_member_origin_verified=True,reader_counts=reader.counts)
 (RUN/'audit.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
if __name__=='__main__':main()
