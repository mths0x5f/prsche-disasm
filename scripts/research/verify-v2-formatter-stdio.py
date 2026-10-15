"""Run175: original stdio buffer/lock/printf callers at typed canonical boundaries."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,ARENA,STACK,IOB,EXIT=0x400000,0x24000000,0x22000000,0x5e54e8,0x2200f000
VAS=(0x5a177b,0x5a36ea,0x5a3719,0x5a373c,0x5a376b,0x5a533e,0x5a53cb,0x5a76a1)
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EFLAGS

def cases():
 out=[]
 def add(op,selector=0,index=1,flags=2,delta=4,remaining=16,size=4096,character=1,malloc=0,write=0,variant=0,counter=0,temporary=0):out.append((op,selector,index&0xffffffff,flags&0xffffffff,delta&0xffffffff,remaining&0xffffffff,size&0xffffffff,character&0xffffffff,malloc,write,variant,counter,temporary))
 for op,selector,index in itertools.product((1,2,3,4),range(9),(-0x80000000,-29,-28,-1,0,1,19,20,21,0x7fffffff)):add(op,selector=selector,index=index)
 flags=(0,1,2,3,4,8,0x80,0x82,0x100,0x102,0x10a,0x1002,0x1102,0x1182,0x10000,0x10002,0xa5001102,0xffffffff)
 for selector,flag,character,malloc,temp in itertools.product(range(3),flags,(0,1,0x80000000),(0,1),(0,1,2,3)):
  add(5,selector=selector,flags=flag,character=character,malloc=malloc,temporary=temp,counter=0xffffffff)
 for installed,selector,flag,delta,write in itertools.product((0,1,0xffffffff),range(3),(2,0x102,0x1002,0x1102,0x1182,0xffffffff),(0,1,4,17,-1),(0,1,2,3)):
  add(6,index=installed,selector=selector,flags=flag,delta=delta,write=write)
 for flag,delta,write,variant in itertools.product(flags,(-0x80000000,-17,-1,0,1,4,17),(0,1,2,3),(0,4)):
  add(7,selector=2,flags=flag,delta=delta,write=write,variant=variant)
 for flag,malloc,character,temp,variant in itertools.product((2,0x102,0x1002,0x1102,0x1182),(0,1),(0,1),(0,1),(0,1,2,4,8,16,32)):
  add(0,flags=flag,malloc=malloc,character=character,temporary=temp,variant=variant,index=0xabcdef01)
 for op,variant in itertools.product((0,5,6,7),(1,2,4,8,16,32,63)):
  add(op,flags=0x1102 if op in (6,7) else 2,variant=variant,temporary=0,counter=0xffffffff)
 rng=random.Random(175)
 for _ in range(100):add(rng.choice((5,6,7)),selector=rng.randrange(3),flags=rng.getrandbits(32),delta=rng.randrange(-32,33),index=rng.getrandbits(32),remaining=rng.getrandbits(32),size=rng.getrandbits(32),character=rng.getrandbits(32),malloc=rng.randrange(2),write=rng.randrange(4),variant=rng.randrange(64),counter=rng.getrandbits(32),temporary=rng.randrange(4))
 return out

def mapped(image,module,va,n):
 rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+max(s['raw_size'],s['vsize']))
 within=rva-s['rva'];available=min(n,max(0,s['raw_size']-within));offset=s['raw_offset']+within
 return image[offset:offset+available]+bytes(n-available)

def make_uc(image,module):
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000);uc.mem_map(ARENA,0x10000);uc.mem_map(STACK,0x10000)
 for s in module['sections']:
  if s['raw_size']:uc.mem_write(BASE+s['rva'],image[s['raw_offset']:s['raw_offset']+s['raw_size']])
 for iat,target in ((0x5b2078,STACK+0xe000),(0x5b206c,STACK+0xe010)):uc.mem_write(iat,struct.pack('<I',target))
 return uc

def original(uc,row,seq,payload,coverage):
 op,selector,index,flags,delta,remaining,size,character,malloc,write,variant,counter,temporary=row
 put=lambda p,v:uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 get=lambda p:struct.unpack('<I',uc.mem_read(p,4))[0]
 def loc(p):return 0x25000000+p-IOB if IOB-32<=p<IOB+672 else p
 def normal(p,n):
  data=bytearray(uc.mem_read(p,n))
  for i in range(0,n-3,4):struct.pack_into('<I',data,i,loc(struct.unpack_from('<I',data,i)[0]))
  return data.hex()
 uc.mem_write(ARENA,bytes((i*13+seq*7+0x21)&255 for i in range(0x4000)));uc.mem_write(IOB,bytes((i*17+seq+0x31)&255 for i in range(640)));uc.mem_write(ARENA+0x500,payload)
 put(0x6afcf8,counter);put(0x6afd60,ARENA+0x3000 if temporary&1 else 0);put(0x6afd64,ARENA+0x3100 if temporary&2 else 0)
 d=IOB+32 if op==0 or selector==0 else IOB+64 if selector==1 else ARENA+0x100 if selector==2 else (IOB+(0,608,609,-1,1,607)[(selector-3)%6])&0xffffffff
 if selector<=2 or op==0:
  for offset,value in ((0,ARENA+0x1000+delta),(4,remaining),(8,ARENA+0x1000),(12,flags),(16,0x11223344),(24,size)):put(d+offset,value)
 if op==0:args=[ARENA+0x500]+[get(ARENA+0x600+i*4) for i in range(8)]
 elif op in (2,4,6):args=[index,d]
 else:args=[d]
 events='';stage_events=0
 def state():return normal(IOB,96)+':'+normal(ARENA+0x100,32)+':'+f'{get(0x6afcf8):08x}:{loc(get(0x6afd60)):08x}:{loc(get(0x6afd64)):08x}'
 def mutate(bit):
  if not variant&bit or selector>2 and op!=0:return
  for offset,value in ((12,0xa5000082),(8,ARENA+0x1100),(0,ARENA+0x1120),(4,0x87654321)):put(d+offset,value)
  put(0x6afd60,ARENA+0x3000);put(0x6afcf8,get(0x6afcf8)+1)
 def hook(m,va,_size,_data):
  nonlocal events,stage_events
  if va==EXIT:m.emu_stop();return
  coverage[va]=coverage.get(va,0)+1;sp=m.reg_read(UC_X86_REG_ESP);arg=lambda n:get(sp+4+n*4);result=0;clean=0
  if va in (0x5a4ba4,0x5a4c05):
   tag='L' if va==0x5a4ba4 else 'U';events+=f'{tag}:{arg(0):08x}:'+state()+';'
   if tag=='L':mutate(32)
  elif va in (STACK+0xe000,STACK+0xe010):
   tag='E' if va==STACK+0xe000 else 'V';events+=f'{tag}:{loc(arg(0)):08x}:'+state()+';';clean=4
   if tag=='E':mutate(32)
  elif va==0x5abf35:events+=f'C:{arg(0):08x}:{character:08x}:'+state()+';';mutate(1);result=character
  elif va==0x5a3be5:
   result=0 if malloc else ARENA+0x2000;events+=f'M:{arg(0):08x}:{result:08x}:'+state()+';';mutate(2)
  elif va==0x5a9e49:
   length=arg(2);result=length if write==0 else (length-1)&0xffffffff if write==1 else 0xffffffff if write==2 else 0
   events+=f'W:{arg(0):08x}:{loc(arg(1)):08x}:{length:08x}:{result:08x}:'+bytes(m.mem_read(arg(1),length)).hex()+':'+state()+';';mutate(4)
  elif va==0x5a4371:
   fmt=bytearray()
   while True:
    x=m.mem_read(arg(1)+len(fmt),1)[0];fmt.append(x)
    if not x:break
   events+=f'P:{loc(arg(0)):08x}:'+fmt.hex()+':'+''.join(f'{get(arg(2)+i*4):08x}' for i in range(8))+':'+state()+';'
   raw=arg(0);base=get(raw+8)
   if ARENA<=base and base+4<ARENA+0x4000 or IOB<=base and base+4<IOB+640:m.mem_write(base,b'ABCD');put(raw,base+4);put(raw+4,get(raw+4)-4)
   mutate(8)
   if variant&16:put(raw+12,get(raw+12)&~0x1000)
   result=index
  else:return
  stage_events+=1;m.reg_write(UC_X86_REG_EAX,result);m.reg_write(UC_X86_REG_EIP,get(sp));m.reg_write(UC_X86_REG_ESP,sp+4+clean)
 handle=uc.hook_add(UC_HOOK_CODE,hook);sp=STACK+0x8000;uc.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),EXIT,*args));uc.reg_write(UC_X86_REG_ESP,sp)
 for reg in (UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI):uc.reg_write(reg,0x12345678)
 uc.reg_write(UC_X86_REG_EFLAGS,2);uc.emu_start(VAS[op],0,count=200000);uc.hook_del(handle)
 assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==sp+4,(seq,'completion/stack')
 assert all(uc.reg_read(reg)==0x12345678 for reg in (UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI)) and not uc.reg_read(UC_X86_REG_EFLAGS)&0x400
 result=uc.reg_read(UC_X86_REG_EAX) if op in (0,5,7) else 0
 return {'case':seq,'result':f'{result:08x}','events':events,'iob':normal(IOB,640),'memory':normal(ARENA,0x4000),'counter':f'{get(0x6afcf8):08x}','buffers':[f'{loc(get(0x6afd60)):08x}',f'{loc(get(0x6afd64)):08x}']},stage_events

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--probe',required=True,type=Path);parser.add_argument('--report-dir',required=True,type=Path);parser.add_argument('--limit',type=int);parser.add_argument('--require-canonical-lock-prefix',action='store_true');args=parser.parse_args()
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 rows=cases();rows=rows[:args.limit] if args.limit else rows
 payload=b'diagnostic %d %s\0'+bytes(0x100-17)+struct.pack('<8I',0x12345678,0x87654321,0,0xffffffff,0x80000000,1,2,3)
 assert len(b'diagnostic %d %s\0')==17
 inputs=''.join(str(i)+' '+str(row[0])+' '+' '.join(f'{v:x}' for v in row[1:])+' '+payload.hex()+'\n' for i,row in enumerate(rows))
 process=subprocess.run([str(args.probe.resolve())],input=inputs,text=True,capture_output=True,timeout=120);assert process.returncode==0,(process.returncode,process.stderr,len(process.stdout.splitlines()))
 native=[json.loads(line) for line in process.stdout.splitlines()];assert len(native)==len(rows)
 uc=make_uc(image,module);coverage={};results=[];stages=0
 for i,(row,actual) in enumerate(zip(rows,native)):
  expected,count=original(uc,row,i,payload,coverage);stages+=count
  if actual!=expected:
   fields=[key for key in actual if actual[key]!=expected[key]]
   raise AssertionError((i,row,fields,{key:(actual[key],expected[key]) for key in fields if key not in ('memory','iob')},[(key,next((j//2 for j,(a,b) in enumerate(zip(actual[key],expected[key])) if a!=b),None)) for key in fields if key in ('memory','iob')]))
  results.append({'op':row[0],'input':list(row[1:]),'state_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True).encode()).hexdigest(),'boundary_events':count})
 entries={int(r['entry_va'],16):r for r in map(json.loads,(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
 def pin(va):
  f=entries[va];body=b''.join(mapped(image,module,int(a,16),int(b,16)-int(a,16)+1) for a,b in f['ranges']);assert len(body)==f['body_bytes'];return {'ranges':f['ranges'],'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest()}
 functions={f'{va:08x}':pin(va) for va in VAS};lock_data=mapped(image,module,0x5e57a8,192)
 lock_expected=[0]*48
 for i,value in ((1,0x6afd00),(9,0x6afd30),(13,0x6afd48),(17,0x6afd18)):lock_expected[i]=value
 assert lock_data==struct.pack('<48I',*lock_expected)
 assert mapped(image,module,0x6afd60,8)==bytes(8) and mapped(image,module,0x6afcf8,4)==bytes(4)
 reloc=next(s for s in module['sections'] if s['name']=='.reloc');data=image[reloc['raw_offset']:reloc['raw_offset']+reloc['raw_size']];position=0;relocs=[]
 while position+8<=len(data):
  page,size=struct.unpack_from('<II',data,position)
  if not size:break
  assert size>=8 and position+size<=len(data)
  for offset in range(position+8,position+size,2):
   entry=struct.unpack_from('<H',data,offset)[0];assert entry>>12 in (0,3)
   va=BASE+page+(entry&4095)
   if entry>>12==3 and 0x5e57a8<=va<0x5e5868:relocs.append(va)
  position+=size
 assert relocs==[0x5e57ac,0x5e57cc,0x5e57dc,0x5e57ec]
 references=[r for r in map(json.loads,(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl').read_text().splitlines()) if re.fullmatch('[0-9a-fA-F]{8}',r.get('to_va','')) and 0x5e57a8<=int(r['to_va'],16)<0x5e5868]
 aliases={}
 for path in (ROOT/'iterations/v2/001-original-recovery/source/include/porsche').glob('*.hpp'):
  for name in re.findall(r'\b(\w+_005e5[78][0-9a-f]{2})\b',path.read_text(encoding='utf8')):
   if 0x5e57a8<=int(name[-8:],16)<0x5e5868:aliases.setdefault(name,[]).append(path.relative_to(ROOT).as_posix())
 assert set(aliases)=={'formatter_crt_locks_005e57a8'}
 owner=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_crt_runtime.cpp';header=ROOT/'iterations/v2/001-original-recovery/source/include/porsche/formatter_crt_runtime.hpp'
 owner_count=int(re.search(r'formatter_crt_locks_005e57a8\[(\d+)\]',owner.read_text()).group(1));header_count=int(re.search(r'formatter_crt_locks_005e57a8\[(\d+)\]',header.read_text()).group(1));assert owner_count==header_count
 if args.require_canonical_lock_prefix:assert owner_count>=48
 prefix='iterations/v2/001-original-recovery/'
 compiled=[prefix+'source/recovered/'+name for name in ('formatter_stdio_probe.cpp','Porsche.exe/formatter_stdio.cpp','Porsche.exe/formatter_runtime_storage.cpp')]
 paths=[prefix+'runs/175-formatter-stdio/README.md',prefix+'runs/175-formatter-stdio/CMakeLists.txt',str(owner),str(header),'scripts/research/verify-v2-formatter-stdio.py','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl','research/binary-index/static/binaries.jsonl']
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':list(functions),'full_function_vas':list(functions) if not args.limit else [],'partial_function_vas':[],'functions':functions,'cases':len(rows),'native_cpp_equal_original_x86':True,'unrecovered_dependencies':[],'case_results':results,'boundary_stage_events':stages,'original_x86_coverage':{f'{va:08x}':coverage.get(va,0) for va in VAS},'source_sha256':source_hashes(paths,compiled_sources=compiled),'probe_sha256':hashlib.sha256(args.probe.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(inputs.encode()).hexdigest(),'canonical_lock_prefix':{'va':'005e57a8','bytes':192,'sha256':hashlib.sha256(lock_data).hexdigest(),'initial_values':[f'{v:08x}' for v in lock_expected],'required_ids':[28,47],'reason':'20 FILE entries and inclusive pointer bounds, then index+28; prefix only, no total extent claim'},'canonical_callees':{f'{va:08x}':pin(va) for va in (0x5a4b7b,0x5a4ba4,0x5a4c05,0x5a3be5,0x5a4371,0x5a9e49)},'limits':['Canonical lock/malloc/character-device/write/parser callees are typed scripted boundaries here; no new implementation or whole formatted-output composition claim. The printf body receives eight actual native x86 varargs, compared at the canonical raw-va parser boundary.', 'Complete640-byte FILE20 array,16384-byte poisoned arena, two buffer cells, counter and ordered boundary snapshots compare; only native canonical FILE pointer identities are normalized. cdecl stack/nonvolatile registers/DF checked. Invalid inaccessible memory excluded.', 'Original8 bodies have no SEH or floating-point operations. No host printf conversion substitute. Root must expand canonical157 lock prefix48 before production use; no duplicate table owner in175.', 'No live game or visual acceptance.']}
 report['canonical_lock_prefix'].update(highlow_sites=[f'{va:08x}' for va in relocs],initialization='005a4b7b initializes17/13/9/1;005a4ba4 lazily allocates selected null cells under17; no selector bound in genericlock',index_references=references,canonical_aliases=aliases,published_owner_prefix=owner_count,production_ready=owner_count>=48)
 report['initial_zero_storage']={'006afd60':{'bytes':8,'sha256':hashlib.sha256(bytes(8)).hexdigest()},'006afcf8':{'bytes':4,'sha256':hashlib.sha256(bytes(4)).hexdigest()}}
 assert all(report['original_x86_coverage'][f'{va:08x}'] for va in VAS) or args.limit
 args.report_dir.mkdir(parents=True,exist_ok=True);(args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'ok':True,'functions':len(functions),'bytes':sum(f['body_bytes'] for f in functions.values()),'cases':len(rows),'boundary_events':stages,'canonical_lock_prefix':owner_count}))
if __name__=='__main__':main()
