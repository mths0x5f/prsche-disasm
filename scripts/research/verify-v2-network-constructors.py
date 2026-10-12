"""Complete network constructors/startup/address queries vs original x86."""
import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,STACK,EXIT=0x400000,0x2210000,0x223f000
B=0x23000000
S,C,W,W2,M,M2,N,K,V,T,D=[B+x for x in (0,0x1000,0x2000,0x2400,0x3000,0x3400,0x5000,0x5400,0x6000,0x8000,0x9000)]
FUNCTIONS={0:(0x48aa10,565),1:(0x48af80,566),2:(0x48b3c0,137),3:(0x48b450,149),4:(0x55d5a0,56),5:(0x55d5e0,101),6:(0x55d6e0,68),7:(0x55d730,20),8:(0x55d750,17),9:(0x580590,28),10:(0x5805b0,42),11:(0x5805e0,42)}
RANGES=((S,0x200),(C,0x20),(M,0x100),(M2,0x100),(N,0x40),(K,0x40),(V,0x50),(D,0x220))
def cases():
 result=[]
 def add(op,mode=4,query=1,settings=0,server=0,fail=0,empty=0,mutation=0,flags=3,present=0,allocfail=0,variant=1,callbacks=3):result.append([op,mode,query,settings,server,fail,empty,mutation,flags,present,allocfail,variant,callbacks])
 for op in range(12):add(op)
 for length in (1,38,45):add(0,server=length)
 for op in (5,10):
  for length in (1,2,19,20,21,32,53):
   for mode in (0,1,4):add(op,mode=mode,server=length)
 for op in (0,1):
  for fail in (0,1,2):
   for empty in (0,1):
    for variant in (0,1,2,3):
     for mutation in (0,1,2,3):add(op,fail=fail,empty=empty,variant=variant,mutation=mutation,query=0 if fail==2 else 1)
 for query in (0,1,0x80000000,0xffffffff):
  for settings in (0,1):
   for server in (0,1):
    for mutation in (0,4,8,16,28):add(1,query=query,settings=settings,server=server,mutation=mutation)
 for op in (2,3):
  for flags in range(4):
   for present in (0,1):
    for allocfail in range(4):
     for mutation in (0,1,2,3,32):add(op,flags=flags,present=present,allocfail=allocfail,mutation=mutation)
 for op in range(4,12):
  for mode in (0,1,2,3,4,5,0x80000000,0xffffffff):
   for callbacks in range(4):
    for variant in (0,1,2,3,4,5,0xffffffff):add(op,mode=mode,callbacks=callbacks,variant=variant)
 return result
def original(module,image,case):
 sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
 for sec in module['sections']:
  if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
 uc.mem_map(0x2200000,0x40000);uc.mem_map(B,0x10000);uc.mem_map(0x24000000,0x1000)
 def get(p):return struct.unpack('<I',uc.mem_read(p,4))[0]
 def put(p,v):uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 def byte(p,v):uc.mem_write(p,bytes([v&255]))
 def pointer(p):return p if B<=p<B+0x10000 else 0
 def text(p):
  result=bytearray()
  while True:
   b=uc.mem_read(p+len(result),1)[0];result.append(b)
   if not b:return bytes(result)
 op,*a=case;trace=[];manager=M;calls=0
 uc.mem_write(B,b'\xcc'*0x10000);put(0x5e4fe8,M)
 for base in (M,M2):put(base+0x28,base+0x80);put(base+0x38,0 if a[5] else K);put(base+0xb0,0 if a[5] else N)
 put(N+4,N+0x20);put(K+4,K+0x20);put(N+0x24,0);put(K+0x24,0)
 for w in (W,W2):put(w+0xbc,a[0]);put(w+0x14,V);put(w+0x18,0x87650000+w-W)
 put(V+0x40,0x24000000);put(V+0x38,0x24000010 if a[11]&1 else 0);put(V+0x3c,0x24000020 if a[11]&2 else 0)
 put(S+4,W);put(S+0xc,C if a[8] else 0);put(S+0x10,D+0x200);put(S+0x1c,22);put(S+0x20,11);put(S+0x24,33);byte(S+0x14,a[7]&1);byte(S+0x15,(a[7]>>1)&1);uc.mem_write(S+0x28,b'host-key\0');uc.mem_write(S+0x128,b'host.example\0')
 for i,s in enumerate((b'left\0',b'right\0',b'suffix\0',b'extra\0',b'server.example\0')):uc.mem_write(T+i*0x100,s)
 if a[10]&2:
  for i in range(4):byte(T+i*0x100,0)
 if op==0 and a[3]:uc.mem_write(T,b'L'*a[3]+b'\0');uc.mem_write(T+0x100,b'R'*8+b'\0')
 if op in (5,10) and a[3]:uc.mem_write(T,b'A'*(a[3]-1)+b'\0')
 uc.mem_write(T+0x500,bytes([65+i if i<10 else 0 for i in range(52)]));uc.mem_write(0x5e8e50,b'\0')
 for i in range(5):put(D+i*4,0x11110000+i);put(D+0x40+i*4,0x11110000+i)
 if a[10]<5:put(D+0x40+a[10]*4,0xeeeeeeee)
 args={0:[11,22,33,T,T+0x100,T+0x200,T+0x300,44],1:[11,22,a[1],33,T+0x500 if a[2] else 0,T+0x400 if a[3] else 0,1234],2:[],3:[],4:[W,D+0x80,D+0xa0,D+0xc0],5:[W,T,1234,D+0x80],6:[W,D,D+0x40],7:[W],8:[W],9:[W+8,D,D+0x40],10:[W+8,T,1234,D+0x80],11:[W+8,D+0x80,D+0xa0,D+0xc0]}[op]
 put(STACK,EXIT)
 for i,value in enumerate(args):put(STACK+4+i*4,value)
 uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,S)
 saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
 for reg,value in saved.items():uc.reg_write(reg,value)
 def event(va,args=()):trace.append([va,*args,*[get(p) for p in (S,S+4,S+0xc,S+0x10,S+0x14,C,C+4,M+0x28,M+0x38,M+0xb0,M2+0x38,M2+0xb0)],manager])
 def bytes_event(va,p,n):trace.append([va,*uc.mem_read(p,n)])
 def text_event(va,p):trace.append([va,*text(p)])
 boundaries=(0x5321f0,0x5322b0,0x5322c0,0x59eeb0,0x53c290,0x5323e0,0x55c370,0x55aaa0,0x55d650,0x5a28a0,0x5a0fbf,0x59ef90,0x48ac90,0x24000000,0x24000010,0x24000020)
 def hook(machine,address,size,data):
  nonlocal manager,calls
  if address==EXIT:machine.emu_stop();return
  if address not in boundaries:return
  sp=machine.reg_read(UC_X86_REG_ESP);values=lambda n:[get(sp+4+i*4) for i in range(n)];result=0;pop=0
  if address==0x5321f0:event(address);result=0x26000000
  elif address==0x5322b0:
   event(address,values(1))
   if a[6]&1:manager=M2;put(0x5e4fe8,M2)
   if a[6]&2:put(M+0x28,0x26000010)
  elif address==0x5322c0:event(address,values(1))
  elif address==0x59eeb0:
   kind,zero=values(2);event(address,[kind,zero]);put(M+0x28+(0x88 if kind==31 else 0x10),N if kind==31 else K)
  elif address==0x53c290:
   dst,v,n=values(3);event(address,[pointer(dst),v,n]);uc.mem_write(dst,bytes([v&255])*n)
  elif address==0x5323e0:
   dst,src,n=values(3);event(address,[pointer(dst),pointer(src),n]);uc.mem_write(dst,bytes(uc.mem_read(src,n)))
  elif address in (0x55c370,0x55aaa0):
   args_=values(6 if address==0x55c370 else 7);event(address,args_[:3]+args_[4:]);bytes_event(4 if address==0x55c370 else 5,args_[3],92 if address==0x55c370 else 52)
   if address==0x55c370:result=0 if a[4]==2 else W
   else:
    result=0 if a[4] and (calls==0 or a[4]==2) else W
    if a[4]:calls+=1
  elif address==0x55d650:
   worker,out=values(2);event(address,[worker,pointer(out)])
   for i in range(5):put(out+i*4,0x11110000+i)
   if a[6]&4:put(S+4,W2)
   result=1
  elif address==0x5a28a0:
   out,src,n=values(3);event(address,[pointer(out),pointer(src),n]);s=text(src)[:-1][:n];uc.mem_write(out,s+bytes(n-len(s)));result=out
  elif address==0x5a0fbf:
   out,fmt,ch,addr,port,settings=values(6);event(address,[pointer(out),ch,port]);text_event(6,fmt);text_event(7,addr);bytes_event(8,settings,52)
   signed=port if port<0x80000000 else port-0x100000000;s=bytes([ch])+text(addr)[:-1]+b'.'+str(signed).encode()+b'.'+text(settings)[:-1];uc.mem_write(out,s+b'\0');result=len(s)
  elif address==0x59ef90:
   n=values(1)[0];event(address,[n])
   if n==8 and a[6]&32:put(S+0xc,D+0x100)
   result=0 if (n==20 and a[9]&1) or (n==8 and a[9]&2) else C if n==20 else D+0x200
  elif address==0x48ac90:
   server,port=values(2);event(address,[machine.reg_read(UC_X86_REG_ECX),pointer(server),port]);text_event(9,server);result=7;pop=8
  elif address==0x24000000:
   state,first,second=values(3);event(address,[state]);bytes_event(1,first,20);bytes_event(2,second,20);result=a[10]
  elif address==0x24000010:
   state,src,port,out=values(4);event(address,[state,pointer(src),port,pointer(out)]);text_event(3,src)
   for i in range(5):put(out+i*4,0x11110000+i+(0 if a[10] else 1))
   if a[6]&16:put(S+4,W)
   result=0x87654321
  else:
   state,first,second,third=values(4);event(address,[state,pointer(first),pointer(second),pointer(third)]);put(first,0x99887766);uc.mem_write(second,b'192.168.0.42\0');put(third,30000+a[10])
   if a[6]&8:put(S+4,W2)
   result=0xabcdef01
  machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4+pop);machine.reg_write(UC_X86_REG_EIP,get(sp))
 uc.hook_add(UC_HOOK_CODE,hook)
 try:uc.emu_start(FUNCTIONS[op][0],EXIT+1,count=50000)
 except Exception as exc:raise RuntimeError(f'{case} EIP={uc.reg_read(UC_X86_REG_EIP):08x} trace={trace[-3:]}') from exc
 assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4+(32 if op==0 else 28 if op==1 else 0)
 assert all(uc.reg_read(reg)==value for reg,value in saved.items())
 state=[]
 for va,n in RANGES:state+=list(struct.unpack('<'+str(n//4)+'I',uc.mem_read(va,n)))
 return {'return':0 if op in (2,3) else uc.reg_read(UC_X86_REG_EAX),'trace':trace,'state':state}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-constructors-171/bin/Release/network_constructors_probe.exe');ap.add_argument('--report-dir',type=Path,required=True);args=ap.parse_args();args.report_dir.mkdir(parents=True,exist_ok=True)
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 cs=cases();run=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,c))+'\n' for c in cs),text=True,capture_output=True,check=True);actuals=[json.loads(s) for s in run.stdout.splitlines()];assert len(actuals)==len(cs)
 for i,(c,actual) in enumerate(zip(cs,actuals)):
  expected=original(module,image,c)
  for key in expected:
   if actual[key]!=expected[key]:
    diff=[(n,x,y) for n,(x,y) in enumerate(zip(expected[key],actual[key])) if x!=y][:3] if isinstance(expected[key],list) else (expected[key],actual[key])
    raise AssertionError(f'case{i} {c} {key}: {diff}; expectedtail={expected["trace"][-3:]}, actualtail={actual["trace"][-3:]}')
 def raw(va,n):
  rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+s['raw_size']);o=s['raw_offset']+rva-s['rva'];return image[o:o+n]
 base='iterations/v2/001-original-recovery/';compiled=[base+'source/recovered/'+s for s in ('network_constructors_probe.cpp','Porsche.exe/network_constructors.cpp')]
 paths=compiled+[base+'runs/171-network-constructors/'+s for s in ('README.md','CMakeLists.txt')]+['scripts/research/verify-v2-network-constructors.py','research/binary-index/static/binaries.jsonl']
 # Index records and exact disassembly are part of the reproducible evidence closure.
 paths+=['research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/'+s+'.jsonl' for s in ('functions','calls','references','symbols','unresolved-calls')]+['research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'full_function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'partial_function_vas':[],'cases':len(cs),'native_cpp_equal_original_x86':True,'index_query':'Remaining raw-vptr assignments48aa21/48aa84/48af92/48b015; parent functions48aa10/48af80 and direct startup48b3c0/48b450; address consumers55d5a0/55d5e0/55d6e0 and protocol/provider callees. All12 bodies indexed.',
 'comparison_boundary':'Complete12 bodies, original ESP/nonvolatile ABI, returns except void startup EAX, entire object/list/pool backing and all initialized52/92-byte worker packets. Exact effects/order with captured manager versus reloaded lock, changed worker pointers after current/get/parse, allocation failures and retry. Private native vptr identity normalized to original words only; actual callback functions remain native. Provider and unrecovered worker/allocator/CRT/lock effects are scripted. Query constructors use initialized provider outputs; unsupported query mode remains original undefined local data and is excluded.',
 'unresolved_effects':['worker constructors55c370/55aaa0','current address55d650','connect48ac90','actual provider callbacks','RTTI graph ownership','identity5b4980 full extent','text5e8e50 full extent'],
 'deferred':['Trace actual worker creation/provider startup and connect before claiming OS transport. Original copies are unbounded; input strings must fit original packet fields. Allocation20 failure still calls connect with null; scripted boundary observes this and does not establish actual null handling.'],
 'original_functions':[{'va':f'{va:08x}','body_bytes':n,'body_sha256':hashlib.sha256(raw(va,n)).hexdigest()} for va,n in FUNCTIONS.values()],
 'compiled_source_files':compiled,'source_sha256':source_hashes(paths,compiled_sources=compiled)}
 (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS {len(cs)} original-x86 comparisons /12 bodies')
if __name__=='__main__':main()
