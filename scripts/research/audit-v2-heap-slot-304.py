"""Independently check304 captured COFF, dependencies, receipts and PE oracle."""
import hashlib,importlib.util,json,re
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'iterations/v2/001-original-recovery/runs/304-heap-slot-release';OUT=ROOT/'local/experiments/v2-heap-slot-release-304'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 summary=load(RUN/'summary.json');reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw')
 assert sha(RUN/'summary.json')==load(RUN/'validation.json')['summary_sha256']
 for p,h in summary['tool_sha256'].items():assert sha(p)==h
 body=bytes.fromhex(summary['original_body_hex']);pe=mod('pe304',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 assert len(body)==72 and pe.pe_read((ROOT/'local/game/Porsche.exe').read_bytes(),0x5699f0,72)==body
 assert body[14:18]==body[21:25]==bytes.fromhex('204f6b00')
 for offset,nxt,target in [(38,42,0x5322d0),(51,55,0x53c290)]:assert 0x5699f0+nxt+int.from_bytes(body[offset:offset+4],'little',signed=True)==target
 assert bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','))==body
 coff=mod('coff304',ROOT/'scripts/research/build-v2-compile-corpus.py');obj=ROOT/summary['game_objects'][0]['path'];symbols=coff.coff_symbols(obj)
 assert sha(obj)==summary['game_objects'][0]['sha256'] and symbols==summary['symbols']
 assert len(symbols['defined'])==1 and 'heap_slot_release_005699f0' in symbols['defined'][0]
 assert len(symbols['undefined'])==3 and not symbols['common'] and not symbols['weak'] and body not in obj.read_bytes()
 owner=load(RUN.parent/'272-shared-heap-table/summary.json')['support_objects'][0];table=ROOT/summary['reused_table_object']['path']
 assert sha(table)==summary['reused_table_object']['sha256']==owner['object_sha256']
 assert not any('heaps_006b4f20' in x for x in symbols['defined'])
 assert any('heaps_006b4f20' in x for x in coff.coff_symbols(table)['defined'])
 receipts={x:load(OUT/(x+'-001.receipt.json')) for x in ('compile','link','native')}
 for receipt in receipts.values():assert receipt['exit_code']==0 and sha(ROOT/receipt['log'])==receipt['log_sha256']
 command=receipts['compile']['command'];assert '/MP6' in command and '/sourceDependencies' in command and sum(x.endswith('.cpp') for x in command)==2
 assert str(table) in receipts['link']['command']
 assert not re.search(rb'(warning|error) [CD]\d+',(ROOT/receipts['compile']['log']).read_bytes())
 assert load(ROOT/receipts['native']['log'])==dict(cases=960,failures=0)
 deps=load(OUT/'dependencies/005699f0.cpp.json')['Data'];assert Path(deps['Source']).resolve()==(RUN/'005699f0.cpp').resolve()
 assert not any('fixture' in x or 'original-body' in x for x in deps['Includes'])
 assert len(list(OUT.glob('compile-*.receipt.json')))==1;reader.cache.check_stable()
 result=dict(passed=True,original_bytes=72,native_cases=960,compiler_batches=1,game_objects=1,reused_table_owner=272,game_defined=1,game_undefined=3,reader_counts=reader.counts)
 (RUN/'audit.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
if __name__=='__main__':main()
