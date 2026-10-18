"""Read-only audit of exact original bytes, COFF boundaries and native receipts."""
import hashlib, importlib.util, json, re
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/297-frame-action'
OUT=ROOT/'local/experiments/v2-frame-action-297'
def load(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 s=load(RUN/'summary.json');v=load(RUN/'validation.json');r=ManifestReader(ROOT)
 r.verify(s,expected_hash_mode='raw')
 assert all(sha(p)==h for p,h in s['tool_sha256'].items())
 assert v['summary_sha256']==sha(RUN/'summary.json') and v['passed']
 pe=module('pe297audit',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 body=pe.pe_read((ROOT/'local/game/Porsche.exe').read_bytes(),0x476170,169)
 assert body.hex()==s['original_body_hex'] and len(body)==169
 recorded=bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','));assert recorded==body
 assert body[43]==0xe8 and int.from_bytes(body[44:48],'little')+0x4761a0==0x476710
 asm=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text()
 callee=asm.split('; FUNCTION 00476710 ',1)[1].split('; FUNCTION ',1)[0]
 assert 'MOV EAX,dword ptr [ESP + 0x4]' in callee and callee.count('RET 0x4')==2
 # The native oracle copies all169 bytes verbatim and rewrites only the one
 # REL32 operand to the private provider; no oracle implementation is in game.
 fixture=(RUN/'fixture.cpp').read_text()
 assert 'copyBytes(reference,original,sizeof(original))' in fixture
 assert 'copyBytes(reference+44,&displacement,4)' in fixture
 assert 'boundary-reinterpret_cast<U>(reference+48)' in fixture
 cof=module('coff297audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 obj=ROOT/s['game_objects'][0]['path'];assert sha(obj)==s['game_objects'][0]['sha256']
 symbols=cof.coff_symbols(obj);assert symbols==s['symbols'] and len(symbols['defined'])==len(symbols['undefined'])==1
 assert 'invoke_00476170' in symbols['defined'][0] and 'update_00476710' in symbols['undefined'][0]
 for name,code in [('compile-001',0),('link-001',1120),('compile-002',0),('link-002',0),('native-002',0)]:
  receipt=load(OUT/(name+'.receipt.json'))
  assert receipt['exit_code']==code and sha(ROOT/receipt['log'])==receipt['log_sha256'],name
  assert receipt['seconds']>=0
 assert load(OUT/'native-002.log')==dict(cases=480,failures=0)
 r.cache.check_stable()
 print(json.dumps(dict(passed=True,original_body_bytes=169,native_comparisons=480,game_bodies=1,external_callee='00476710',failed_link_preserved=True)))
if __name__=='__main__': main()
