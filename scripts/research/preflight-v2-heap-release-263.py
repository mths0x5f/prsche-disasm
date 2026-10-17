"""Read-only exact-owner and native-consumer preflight for canonical heap free."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release'
CORPUS=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VA='00531f90';START=0x531f90;END=0x5320a6
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p):return json.loads(Path(p).read_bytes())
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 RUN.mkdir(parents=True,exist_ok=True)
 image=ROOT/'local/game/Porsche.exe';data=image.read_bytes();assert sha(image)==SHA
 catalog=[json.loads(x) for x in (CORPUS/'functions.jsonl').read_text().splitlines()]
 row=next(x for x in catalog if x['entry_va']==VA)
 assert row['ranges']==[[VA,'005320a5']] and row['body_bytes']==278
 off=struct.unpack_from('<I',data,0x3c)[0];assert data[off:off+4]==b'PE\0\0'
 n,oh=struct.unpack_from('<HH',data,off+6)[0],struct.unpack_from('<H',data,off+20)[0]
 secs=[]
 for i in range(n):
  p=off+24+oh+i*40;rs,rv,sz,rp=struct.unpack_from('<IIII',data,p+8);secs.append((rv,rp,sz))
 rva=START-0x400000;sec=next((v,p,z) for v,p,z in secs if v<=rva and rva+278<=v+z)
 raw=data[sec[1]+rva-sec[0]:sec[1]+rva-sec[0]+278]
 assert len(raw)==278 and raw[:3]==bytes.fromhex('515556') and raw[-9:]==bytes.fromhex('5eb8010000005d59c3')
 code=[]
 for line in (CORPUS/'disassembly.asm').read_text().splitlines():
  if len(line)<12:continue
  try:pc=int(line[:8],16)
  except ValueError:continue
  if START<=pc<END:
   parts=line.split(None,2);assert data[sec[1]+pc-START+rva-sec[0]:sec[1]+pc-START+rva-sec[0]+len(bytes.fromhex(parts[1]))]==bytes.fromhex(parts[1]);code.append(line)
 assert code and code[0].startswith(VA) and code[-1].startswith('005320a5')
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
 owner=[x for x in registry if x['module']=='Porsche.exe' and x['entry_va']==VA]
 assert len(owner)==1 and owner[0]['source'].endswith('/heap.cpp')
 union=load(ROOT/'iterations/v2/001-original-recovery/runs/261-canonical-reuse-union/summary.json')
 assert union['overlapping_vas']==0 and not any(x.get('va')==VA for x in union['results'])
 indexed_overlap=[]
 for x in union['results']:
  q=next((c for c in catalog if c['entry_va']==x.get('va')),None)
  if q and any(int(a,16)<END and START<int(b,16)+1 for a,b in q['ranges']):indexed_overlap.append(x['va'])
 assert not indexed_overlap
 symbol='?free_00531f90@porsche@@YAIPAX@Z'
 frontier=[x for x in union['frontier'] if x['symbol']==symbol]
 assert len(frontier)==1 and frontier[0]['referring_object_vas']==['0059f050']
 caller=next(x for x in union['results'] if x['va']=='0059f050');obj=ROOT/caller['object'];assert sha(obj)==caller['object_sha256']
 coff=module('coff263',ROOT/'scripts/research/build-v2-compile-corpus.py')
 assert symbol in coff.coff_symbols(obj)['undefined']
 src=ROOT/owner[0]['source'];header=ROOT/'iterations/v2/001-original-recovery/source/include/porsche/heap.hpp'
 old=ROOT/'iterations/v2/001-original-recovery/runs/078-shared-runtime-integration/heap/verification.json';verified=load(old)
 assert verified['cases']==551 and verified['native_cpp_equal_original_x86'] and VA in verified['function_vas']
 assert sha(src)==verified['source_sha256'][rel(src)] and sha(header)==verified['source_sha256'][rel(header)]
 lock_src=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/heap_locks.cpp'
 lock_ver=ROOT/'iterations/v2/001-original-recovery/runs/078-shared-runtime-integration/heap-locks/verification.json';lock_old=load(lock_ver)
 assert sha(lock_src)==lock_old['source_sha256'][rel(lock_src)] and lock_old['cases']==31
 imports=[json.loads(x) for x in (ROOT/'research/binary-index/static/imports.jsonl').read_text().splitlines()]
 locks=[]
 for lock_va,iat,sdk in [('005322b0','0x1b2078','EnterCriticalSection'),('005322c0','0x1b206c','LeaveCriticalSection')]:
  item=next(x for x in catalog if x['entry_va']==lock_va);assert item['body_bytes']==12
  own=[x for x in registry if x['module']=='Porsche.exe' and x['entry_va']==lock_va]
  assert len(own)==1 and own[0]['source']==rel(lock_src) and lock_va not in {x.get('va') for x in union['results']}
  a=int(lock_va,16);z=a+12
  assert not any(any(int(p,16)<z and a<int(q,16)+1 for p,q in next((y['ranges'] for y in catalog if y['entry_va']==x.get('va')),[])) for x in union['results'])
  assert any(x['path']=='Porsche.exe' and x['iat_rva']==iat and x['symbol']==sdk and x['dll']=='KERNEL32.dll' for x in imports)
  locks.append(dict(va=lock_va,bytes=12,owner=own[0],source=rel(lock_src),source_sha256=sha(lock_src),original_iat_va=f'{0x400000+int(iat,16):08x}',sdk='KERNEL32.dll!'+sdk,union_collision=False))
 report=dict(schema=1,kind='precompile-heap-release-connected-preflight',module='Porsche.exe',original_sha256=SHA,original_va=VA,original_bytes=278,original_bytes_sha256=hashlib.sha256(raw).hexdigest(),indexed_instructions=len(code),registry_owner=owner[0],union_exact_owner=False,union_interior_overlap=False,actual_consumer=dict(va='0059f050',object=caller['object'],object_sha256=sha(obj),undefined=symbol),canonical_source=rel(src),canonical_source_sha256=sha(src),header=rel(header),header_sha256=sha(header),prior_differential=dict(path=rel(old),sha256=sha(old),cases=551,limits=['whole heap native differential; binary_matched false','controlled lock endpoints','no game launch']),lock_wrappers=locks,lock_prior_differential=dict(path=rel(lock_ver),sha256=sha(lock_ver),cases=31),original_contracts=dict(return_value=1,ret_pop_bytes=0,heap_table_va='006b4f20',lock_enter_va='005322b0',lock_leave_va='005322c0'),proposed_fragment=['heap.cpp include prefix','exact static address/at/links/unlink/insert helpers','exact free_00531f90 definition','two exact heap_locks.cpp wrappers'],predicted_new_undefined=['heaps_006b4f20 table','platform_enter_critical_section','platform_leave_critical_section'],compilation_performed=False,native_performed=False)
 (RUN/'preflight.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({k:report[k] for k in ('original_va','original_bytes','indexed_instructions','union_exact_owner','union_interior_overlap','compilation_performed')}))
if __name__=='__main__':main()
