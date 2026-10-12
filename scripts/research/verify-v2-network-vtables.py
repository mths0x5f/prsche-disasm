"""Network relocated send slots, queues and transport dispatch: original vs native."""
import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,STACK,EXIT=0x400000,0x2201000,0x222f000
B=0x23000000
S,P,T,M,M2,L,N,N2,K,SRC,OUT,C=[B+x for x in (0,0x1000,0x2000,0x3000,0x3400,0x4000,0x5000,0x5200,0x5400,0x8000,0x9000,0x9100)]
FUNCTIONS={0:(0x48ad70,188,12),1:(0x48b340,122,12),2:(0x5a1056,9,0),3:(0x48a920,121,12),4:(0x48a8d0,72,8),5:(0x48a3d0,258,12),6:(0x55d4a0,41,0),7:(0x55c260,8,0),8:(0x55c270,55,0),9:(0x560420,57,0),10:(0x586fb0,66,0)}
def cases():
 result=[]
 def add(op,size=240,old=0,count=0,active=0,enabled=1,flag=1,route=0,mutation=0,empty=0,dest=1,returns=1):
  result.append([op,size,old,count,active,enabled,flag,route,mutation,empty,dest,returns])
 for op in range(11):add(op,old=int(op==4))
 for op in (0,1,5):
  for size in (0,1,4,17,239,240):
   for old in (0,1):
    for active in (0,1):add(op,size,old,active=active)
  for count in (0,1,2,0x7fffffff,0x80000000,0xffffffff):
   for active in (0,1):
    for returns in (0,1,0xffffffff):add(op,count=count,active=active,returns=returns)
  for enabled in (0,1):
   for flag in (0,1,2,255):
    for route in (0,0x12345678):add(op,active=1,enabled=enabled,flag=flag,route=route)
  for mutation in (1,2,3,4,8,16,32,63):
   for empty in (0,1):add(op,active=1,mutation=mutation,empty=empty)
  add(op,dest=0)
 for op in (3,4):
  for mutation in (0,1,2,3,8):
   for dest in range(8):add(op,old=int(op==4),mutation=mutation,dest=dest)
  if op==3:add(op,empty=1)
 for value in (1,2,3):add(3,size=value)
 for op in (6,8,9,10):
  for enabled in (0,1):
   for flag in (0,1,2,255):
    for route in (0,0x12345678):
     for returns in (0,1,0xffffffff):add(op,size=0xab000011,enabled=enabled,flag=flag,route=route,returns=returns)
 for value in (0,1,3,4,0xffffffff,0x80000000):add(7,size=value)
 return result

def original(module,image,case):
 sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
 for sec in module['sections']:
  if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
 uc.mem_map(0x2200000,0x30000);uc.mem_map(B,0x10000)
 def get(p):return struct.unpack('<I',uc.mem_read(p,4))[0]
 def put(p,v):uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 def byte(p):return uc.mem_read(p,1)[0]
 def pb(p,v):uc.mem_write(p,bytes([v&255]))
 op,*a=case;trace=[];locks=0;fatal=False
 uc.mem_write(B,b'\xcc'*0x10000)
 put(S+4,T);put(S+8,0x26000001);put(S+0xc,L);pb(S+0x10,a[3]);pb(S+0x16,a[4]);put(S+0x18,L+0x100)
 put(P,P+0x400);put(P+0xb4,a[2]);pb(P+0xbe,a[3]);put(P+0xc4,L);put(P+0x3fc+0xdc,a[5])
 for h in (L,L+0x100):put(h,h);put(h+4,h)
 if a[1]:
  put(L,L+0x200);put(L+4,L+0x200);put(L+0x200,L);put(L+0x204,L);put(L+0x208,17)
  for i in range(240):pb(L+0x20c+i,0x50+i)
 for m in (M,M2):put(m+0x28,0x26000002+(m==M2));put(m+0xb0,0 if a[8] else N);put(m+0x38,K)
 put(N+4,N2);put(N2+4,0);put(K+4,0);put(C,M);put(0x5e4fe8,M)
 for i in range(244):pb(SRC+i,0x21+i)
 pb(T+0x2c8,a[4]);put(T+0x254+0x28,a[5]);put(T+0x254+0x34,a[6]);put(P+0x3fc+0x68+0x28,a[5]);put(P+0x3fc+0x68+0x34,a[6]);put(T+0x28,a[5]);put(T+0x34,a[6])
 if not a[9]:put(P,0)
 put(STACK,EXIT)
 desc=OUT+0x200;put(desc,a[0]&0xff000000);put(desc+4,a[0]&0xffffff);put(desc+8,SRC)
 receivers={0:S,1:S,2:S,3:S,4:S,5:P}
 outputs=[OUT,OUT+4,L,L+4,L+0x200,L+0x204,N+4,M+0xb0];sources=[SRC,N+4,N+12,N+8]
 argmap={0:[P,SRC,a[0]],1:[P,SRC,a[0]],2:[P,SRC,a[0]],3:[outputs[a[9]],L,sources[a[0] if a[0]<4 else 0]],4:[outputs[a[9]],L+0x200],5:[SRC,a[0],T if a[4] else 0],6:[T,SRC,a[0]],7:[a[0]],8:[T,P+0x400,SRC,a[0]],9:[T,SRC,a[0]],10:[T if a[4] else 0,1,desc]}
 for i,v in enumerate(argmap[op]):put(STACK+4+i*4,v)
 uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,receivers.get(op,0))
 saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
 for reg,value in saved.items():uc.reg_write(reg,value)
 def event(va,values=()):trace.append([va,*values,get(P+0xb4),byte(P+0xbe),byte(S+0x10),byte(S+0x16),get(S+8),get(M+0xb0),get(M2+0xb0),get(C),get(L),get(L+4)])
 def hook(machine,address,size,data):
  nonlocal locks,fatal
  if address==EXIT:machine.emu_stop();return
  if address not in (0x5322b0,0x5322c0,0x59eeb0,0x5323e0,0x587000,0x5870b0,0x5a2e22):return
  sp=machine.reg_read(UC_X86_REG_ESP);result=0
  if address==0x5322b0:
   event(address,[get(sp+4)]);locks+=1;captured=get(C)
   if a[7]&1:put(C,M2 if captured==M else M);put(0x5e4fe8,get(C))
   if a[7]&2:put(captured+0x28,0x26002000+locks)
   if a[7]&4:pb(S+0x16,0);pb(P+0xbe,1)
  elif address==0x5322c0:
   event(address,[get(sp+4)])
   if a[7]&8:put(P+0xb4,0xffffffff)
  elif address==0x59eeb0:
   event(address,[get(sp+4),get(sp+8)]);put(M+0xb0,N);put(M2+0xb0,N);put(M+0x38,K);put(M2+0x38,K)
  elif address==0x5323e0:
   dst,src,n=[get(sp+4+i*4) for i in range(3)];event(address,[src,n]);uc.mem_write(dst,bytes(uc.mem_read(src,n)))
  elif address==0x5a2e22:
   event(address,[get(sp+4)]);fatal=True;machine.emu_stop();return
  else:
   t,n,d=[get(sp+4+i*4) for i in range(3)];route=get(sp+16) if address==0x5870b0 else 0;row=[address,t,n,route]
   for i in range(n):
    ds=[get(d+i*12+j*4) for j in range(3)];row+=ds
    if ds[1]&0xffffff<=240 and ds[2]:row+=list(uc.mem_read(ds[2],ds[1]&0xffffff))
   trace.append(row);event(0x24000000)
   if a[7]&16:put(P+0xb4,0);pb(P+0xbe,7)
   if a[7]&32:put(S+8,0x26001000);put(L,N)
   result=a[10]
  machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4);machine.reg_write(UC_X86_REG_EIP,get(sp))
 uc.hook_add(UC_HOOK_CODE,hook)
 if op<3:put(S,(0x5b4968,0x5b4978,0x5b4970)[op])
 entry=get(get(S)) if op<3 else FUNCTIONS[op][0];assert entry==FUNCTIONS[op][0]
 try:uc.emu_start(entry,EXIT+1,count=200000)
 except Exception as exc:raise RuntimeError(f'case {case} EIP={uc.reg_read(UC_X86_REG_EIP):08x}, trace={trace[-3:]}') from exc
 if not fatal:
  assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4+FUNCTIONS[op][2]
  assert all(uc.reg_read(reg)==v for reg,v in saved.items())
 if op in (0,1,5):
  for n in (N,N2):
   for i in range(4+a[0],244):pb(n+8+i,0)
 # This descriptor was harness storage, not original state.
 uc.mem_write(desc,b'\xcc'*12)
 if op<3:put(S,0xcccccccc)
 return {'return':uc.reg_read(UC_X86_REG_EAX) if op not in (0,1,2) else 0,'fatal':fatal,'trace':trace,'state':list(struct.unpack('<16384I',uc.mem_read(B,0x10000)))}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-vtables-164/bin/Release/network_vtables_probe.exe');ap.add_argument('--report-dir',type=Path,required=True);args=ap.parse_args();args.report_dir.mkdir(parents=True,exist_ok=True)
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 all_cases=cases();run=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,c))+'\n' for c in all_cases),text=True,capture_output=True,check=True);actuals=[json.loads(x) for x in run.stdout.splitlines()];assert len(actuals)==len(all_cases)
 summaries=[]
 for i,(case,actual) in enumerate(zip(all_cases,actuals)):
  expected=original(module,image,case)
  for key in expected:
   if expected[key]!=actual[key]:
    if isinstance(expected[key],list):diff=[(j,x,y) for j,(x,y) in enumerate(zip(expected[key],actual[key])) if x!=y][:3]
    else:diff=(expected[key],actual[key])
    raise AssertionError(f'case{i} {case}, {key}: {diff}; expectedtrace={expected["trace"][-3:]}, actualtrace={actual["trace"][-3:]}')
  summaries.append({'index':i,'function_va':f'{FUNCTIONS[case[0]][0]:08x}','input':case,'boundary_calls':len(expected['trace'])})
 def raw(va,n):
  rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+s['raw_size']);o=s['raw_offset']+rva-s['rva'];return image[o:o+n]
 original_functions=[{'va':f'{va:08x}','body_bytes':n,'body_sha256':hashlib.sha256(raw(va,n)).hexdigest()} for va,n,_ in FUNCTIONS.values()]
 asm={}
 for line in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines():
  parts=line.split()
  if len(parts)>2 and len(parts[0])==8:
   try:asm[int(parts[0],16)]=(bytes.fromhex(parts[1]),line)
   except ValueError:pass
 for va,n,pop in FUNCTIONS.values():
  body=b'';cursor=va
  while len(body)<n:
   code,_=asm[cursor];body+=code;cursor+=len(code)
  assert body==raw(va,n)
  assert body.endswith(b'\xc2'+struct.pack('<H',pop) if pop else b'\xc3')
 reloc_section=next(s for s in module['sections'] if s['name']=='.reloc')
 reloc=image[reloc_section['raw_offset']:reloc_section['raw_offset']+reloc_section['vsize']];highlow=set();offset=0
 while offset<len(reloc):
  page,size=struct.unpack_from('<II',reloc,offset)
  if not size:break
  for item in struct.unpack_from('<'+'H'*((size-8)//2),reloc,offset+8):
   if item>>12==3:highlow.add(BASE+page+(item&4095))
  offset+=size
 words=[(0x5b4964,0x5c5190),(0x5b4968,0x48ad70),(0x5b496c,0x5c51d8),(0x5b4970,0x5a1056),(0x5b4974,0x5c5228),(0x5b4978,0x48b340)]
 for va,value in words:assert raw(va,4)==struct.pack('<I',value) and va in highlow
 refs=[json.loads(line) for line in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl').read_text().splitlines()]
 assignments=[r for r in refs if r.get('to_va') in ('005b4968','005b4970','005b4978')]
 for r in assignments:
  va=int(r['from_va'],16);code,_=asm[va];immediate=code.index(struct.pack('<I',int(r['to_va'],16)));assert va+immediate in highlow
  r['immediate_relocation_va']=f'{va+immediate:08x}'
 functions=[json.loads(line) for line in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
 manual=[json.loads(line) for line in (ROOT/'research/binary-index/manual-functions.jsonl').read_text().splitlines()]
 omitted=[]
 for va,n,pop in (FUNCTIONS[i] for i in (0,1,2)):
  assert not any(any(int(a,16)<=va<=int(b,16) for a,b in f['ranges']) for f in functions)
  omitted.append({'va':f'{va:08x}','last_byte_va':f'{va+n-1:08x}','body_bytes':n,'body_sha256':hashlib.sha256(raw(va,n)).hexdigest(),'ret_pop':pop,'automatic_index_coverage':'absent','supplementary_entries':[f for f in manual if f.get('entry_va')==f'{va:08x}']})
 evidence={'module':'Porsche.exe','module_sha256':SHA,'omitted_complete_bodies':omitted,'words':[{'va':f'{va:08x}','value':f'{value:08x}','relocation':'HIGHLOW'} for va,value in words],'assignments':assignments,'slot0_consumers':[{'va':f'{va:08x}','instruction':asm[va][1]} for va in (0x48a3b8,0x48bb1c,0x48c946,0x48c96e)],'purecall_fatal_instruction':asm[0x5a1058][1]}
 (args.report_dir/'vtable-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 base='iterations/v2/001-original-recovery/'
 compiled=[base+'source/recovered/'+x for x in ('network_vtables_probe.cpp','Porsche.exe/network_vtables.cpp','Porsche.exe/network_workers_members.cpp','Porsche.exe/network_cleanup.cpp')]
 paths=compiled+[base+'runs/164-network-vtables/'+x for x in ('README.md','CMakeLists.txt','extract-helpers.py','vtable-evidence.json')]+['scripts/research/verify-v2-network-vtables.py','research/binary-index/static/binaries.jsonl','research/binary-index/manual-functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl','research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],'full_function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],'partial_function_vas':[],'cases':len(all_cases),'native_cpp_equal_original_x86':True,
 'index_query':'Run163 relocated slot0 words5b4968/70/78; exact complete targets and caller/callee closure through packet queues,55c260/55c270/55d4a0/560420/586fb0.',
 'comparison_boundary':'Eleven complete bodies plus exact canonical529050/50e140/4937f0/4c3150 helper extraction. Full64KiB fixture backing, boundary arguments/order/state and returns, ESP/nonvolatile ABI on returning original bodies; actual native one-slot table dispatch. Fatal25 stops at existing noreturn service. Short-packet uninitialized queue-record tail excluded identically; initialized prefix exact. External effects are scripted lock/refill/copy and lower transport587000/5870b0.',
 'unresolved_effects':['00587000/005870b0 lower transport bodies','005c5190/005c51d8/005c5228 RTTI owners remain unsized unresolved data'],
 'deferred':['Integrate native table assignments/identity comparisons instead of frozen151/155 literal VAs; constructors/destructors unchanged here','RTTI consumer/layout recovery','005e8e50 remains untouched unsized unresolved data','short packet indeterminate244-byte queue-record tail has no byte parity claim'],
 'original_functions':original_functions,'native_vtable_proposal':{'table_type':'NetworkSendTable { const void* rtti; NetworkSendSlot send; }','vptr':'address of owner.send; preceding native word references the exact original COL dependency','owners':['network_vtable_owner_005b4968','network_vtable_owner_005b4970','network_vtable_owner_005b4978'],'rtti':'three unsized external symbols intentionally unresolved in production','integration':'replace constructor/destructor assignments and original identity comparisons together, with original VA-to-native-table mapping in the new integration packet; frozen151/155 remain unchanged'},'compiled_source_files':compiled,'source_sha256':source_hashes(paths,compiled_sources=compiled),'case_results':summaries}
 (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS {len(all_cases)} original-x86 comparisons /11 bodies')
if __name__=='__main__':main()
