"""Complete network group removal and send functions: native C++ vs original x86."""
import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,STACK,EXIT=0x400000,0x2201000,0x222F000
B=0x23000000
G,P,S,M,M2,L,SENDER,SENDER2,VT,VT2,C=[B+x for x in (0,0x1000,0x2000,0x3000,0x3200,0x4000,0x6000,0x6020,0x6040,0x6050,0x6100)]
FUNCTIONS={0:(0x48BDA0,311,4),1:(0x48C220,135,12),2:(0x48C300,85,0),3:(0x490B70,50,4),4:(0x48A390,61,8),5:(0x48BAA0,134,4)}
RANGES=((G,0xD00),(P,0x1000),(S,0x200),(M,0x400),(L,0x1200),(C,4))
def cases():
 result=[]
 def add(op,count=3,idx=2,value=0xFFFFFFFE,mask=0xFF,ack=0,active=1,mutation=0,nonnull=1,counter=6,text=0):
  result.append([op,count,idx,value,mask,ack,active,mutation,nonnull,counter,text,0,0])
 for op in range(6):
  for count in (0,1,3,6):add(op,count)
 for idx in (0,7,8,31,32,63,127,128,255,0x12345680):
  for active in (0,1):add(0,3,idx,active=active);add(1,3,idx)
 for mask,ack in ((0,0),(1,1),(0xFF,0xFF),(3,1),(4,0)):
  add(0,3,2,mask=mask,ack=ack);add(1,3,2,mask=mask,ack=ack)
 for value in (0,1,0xFFFFFFFF,0x80000000):add(1,value=value)
 for count in (0,3,6):
  for text in (0,1,20,210):add(0,count,nonnull=1,text=text)
  add(0,count,nonnull=0)
 for counter in (0,1,0xFFFFFFFF,0x80000000):add(0,counter=counter);add(5,counter=counter)
 for op in range(6):
  for mutation in (1,2,4,8,16,32,64,96,128,256,512,1023):add(op,mutation=mutation)
 return result

def original(module,image,case):
 sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
 for sec in module['sections']:
  if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
 assert uc.mem_read(0x5E8E50,1)==b'\0'
 uc.mem_map(0x2200000,0x30000);uc.mem_map(B,0x10000);uc.mem_map(0x24000000,0x1000)
 def get(v):return struct.unpack('<I',uc.mem_read(v,4))[0]
 def put(v,n):uc.mem_write(v,struct.pack('<I',n&0xFFFFFFFF))
 def byte(v):return uc.mem_read(v,1)[0]
 def pb(v,n):uc.mem_write(v,bytes([n&255]))
 def head(g):return L+g*0x200
 def node(g,i):return head(g)+0x20+i*0x30
 def peer(i):return P+0x200+i*0x100 if i%2 else P
 def init_list(g,count):
  h=head(g);put(h,node(g,0) if count else h);put(h+4,node(g,count-1) if count else h)
  for i in range(count):
   n=node(g,i);put(n,node(g,i+1) if i+1<count else h);put(n+4,node(g,i-1) if i else h)
   put(n+8,peer(i) if g==0 else 0x12340000+i if g==1 else 3+i)
   for j in range(16):pb(n+12+j,0x40+g+i+j)
 op,*a=case;uc.mem_write(B,b'\xCC'*0x10000);send_count=lock_count=0
 for g in range(9):init_list(g,a[0])
 put(G+0x60,S);put(G+0x64,SENDER);put(G+0x68,0);put(G+0x70,0x89ABCDEF);put(G+0xA8,head(0));put(G+0xAC,a[8])
 for i in range(52):pb(G+0x74+i,0x21+i)
 pb(G+0xCC0,a[3]);pb(G+0xCC2,a[4]);pb(G+0xCC3,a[5]);put(S+0x164,head(1))
 for i in range(6):
  p=peer(i);put(p,a[7]);put(p+0xA4,G);put(p+0xAC,0x12340000+i);put(p+0xC8,head(2+i))
 put(P+0xAC,a[1]);put(P+0xC8,head(2));put(SENDER,VT);put(SENDER2,VT2);put(VT,0x24000000);put(VT2,0x24000010);put(C,M);put(0x5E4FE8,M)
 for m in (M,M2):put(m+0x28,0x27000000 if m==M else 0x27000001);put(m+0x38,0x26000000);put(m+0xB0,0x26001000)
 uc.mem_write(0x5E8E50,bytes(256))
 for i in range(a[9]):pb(0x5E8E50+i,0x41+i%26)
 receiver,args={0:(G,[P]),1:(G,[P,a[2],0x11223344]),2:(P+0xC8,[]),3:(S,[G]),4:(P,[G+0x64,P]),5:(G,[P])}[op]
 put(STACK,EXIT)
 for i,v in enumerate(args):put(STACK+4+i*4,v)
 uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,receiver)
 saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
 for reg,value in saved.items():uc.reg_write(reg,value)
 trace=[]
 def event(va,values=()):
  trace.append([va,*values,get(P+0xAC),get(P+0xA4),get(G+0xAC),byte(G+0xCC0),byte(G+0xCC2),byte(G+0xCC3),get(M+0x38),get(M+0xB0),get(M2+0x38),get(M2+0xB0),get(C)])
 def hook(machine,address,size,data):
  nonlocal send_count,lock_count
  if address==EXIT:machine.emu_stop();return
  if address not in (0x24000000,0x24000010,0x5322B0,0x5322C0,0x53C290,0x5323E0):return
  sp=machine.reg_read(UC_X86_REG_ESP);pop=0
  if address in (0x24000000,0x24000010):
   dest,packet,n=[get(sp+4+i*4) for i in range(3)];sender=machine.reg_read(UC_X86_REG_ECX)
   trace.append([address,sender,dest,n,*uc.mem_read(packet,n)]);event(0x24000020);send_count+=1;pop=12
   if send_count==1:
    if a[6]&1:put(P+0xAC,0x89ABCDEF)
    if a[6]&2:pb(G+0xCC0,0xA5);pb(G+0xCC2,5)
    if a[6]&4:put(node(0,0),head(0))
    if a[6]&8:put(G+0x64,SENDER2)
    if a[6]&16:put(node(1,0),head(1))
    if a[6]&256:put(G+0xAC,0x76543210)
  elif address==0x5322B0:
   handle=get(sp+4);event(address,[handle]);lock_count+=1;captured=get(C)
   if a[6]&32:put(C,M2 if captured==M else M);put(0x5E4FE8,get(C))
   if a[6]&64:put(captured+0x28,0x27001000+lock_count);put(captured+0x38,0x26010000+lock_count);put(captured+0xB0,0x26011000+lock_count)
  elif address==0x5322C0:event(address,[get(sp+4)])
  elif address==0x53C290:
   dst,pattern,n=[get(sp+4+i*4) for i in range(3)];event(address,[pattern,n]);assert pattern==0
   uc.mem_write(dst,bytes(n))
   if a[6]&128:put(G+0xAC,0xABCDEF01)
  else:
   dst,src,n=[get(sp+4+i*4) for i in range(3)];event(address,[src,n]);uc.mem_write(dst,bytes(uc.mem_read(src,n)))
   if a[6]&512:put(G+0x64,SENDER2)
  machine.reg_write(UC_X86_REG_EAX,0);machine.reg_write(UC_X86_REG_ESP,sp+4+pop);machine.reg_write(UC_X86_REG_EIP,get(sp))
 uc.hook_add(UC_HOOK_CODE,hook)
 try:uc.emu_start(FUNCTIONS[op][0],EXIT+1,count=400000)
 except Exception as e:raise RuntimeError(f'case {case} EIP={uc.reg_read(UC_X86_REG_EIP):08x}, trace={trace[-3:]}') from e
 assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4+FUNCTIONS[op][2]
 assert all(uc.reg_read(reg)==value for reg,value in saved.items())
 state=[]
 for va,size in RANGES:state+=list(struct.unpack(f'<{size//4}I',uc.mem_read(va,size)))
 return {'trace':trace,'state':state}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-groups-163/bin/Release/network_groups_probe.exe');parser.add_argument('--report-dir',type=Path,required=True);args=parser.parse_args();args.report_dir.mkdir(parents=True,exist_ok=True)
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 all_cases=cases();run=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,c))+'\n' for c in all_cases),text=True,capture_output=True,check=True);actuals=[json.loads(s) for s in run.stdout.splitlines()];assert len(actuals)==len(all_cases)
 summaries=[]
 for i,(case,actual) in enumerate(zip(all_cases,actuals)):
  expected=original(module,image,case)
  for key in ('trace','state'):
   if expected[key]!=actual[key]:
    diffs=[(n,x,y) for n,(x,y) in enumerate(zip(expected[key],actual[key])) if x!=y]
    raise AssertionError(f'case {i} {case} {key}: {diffs[:4]}; expected trace {expected["trace"][:10]}; native trace {actual["trace"][:10]}')
  summaries.append({'index':i,'function_va':f'{FUNCTIONS[case[0]][0]:08x}','input':case,'boundary_calls':len(expected['trace'])})
 def raw(va,n):
  rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+s['raw_size']);o=s['raw_offset']+rva-s['rva'];return image[o:o+n]
 # Independently verify relocation and target evidence, without installing tables.
 reloc_section=next(s for s in module['sections'] if s['name']=='.reloc')
 reloc=image[reloc_section['raw_offset']:reloc_section['raw_offset']+reloc_section['vsize']]
 highlow=set();offset=0
 while offset<len(reloc):
  page,size=struct.unpack_from('<II',reloc,offset)
  if not size:break
  for item in struct.unpack_from('<'+'H'*((size-8)//2),reloc,offset+8):
   if item>>12==3:highlow.add(BASE+page+(item&4095))
  offset+=size
 words=[(0x5B4964,0x5C5190),(0x5B4968,0x48AD70),(0x5B496C,0x5C51D8),(0x5B4970,0x5A1056),(0x5B4974,0x5C5228),(0x5B4978,0x48B340)]
 for va,value in words:assert raw(va,4)==struct.pack('<I',value) and va in highlow
 refs=[json.loads(line) for line in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl').read_text().splitlines()]
 writes=[r for r in refs if r.get('to_va') in ('005b4968','005b4970','005b4978')]
 asm={}
 for line in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines():
  parts=line.split()
  if len(parts)>2 and len(parts[0])==8:
   try:asm[int(parts[0],16)]=(bytes.fromhex(parts[1]),line)
   except ValueError:pass
 for r in writes:
  va=int(r['from_va'],16);code,_=asm[va];immediate=code.index(struct.pack('<I',int(r['to_va'],16)));assert va+immediate in highlow
  r['immediate_relocation_va']=f'{va+immediate:08x}'
 targets=[(0x48AD70,188,12),(0x48B340,122,12),(0x5A1056,9,0)]
 functions=[json.loads(line) for line in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
 missing=[]
 for va,size,pop in targets:
  assert not any(any(int(a,16)<=va<=int(b,16) for a,b in f['ranges']) for f in functions)
  assert raw(va+size-(3 if pop else 1),3 if pop else 1)==(b'\xc2'+struct.pack('<H',pop) if pop else b'\xc3')
  missing.append({'va':f'{va:08x}','body_bytes':size,'body_sha256':hashlib.sha256(raw(va,size)).hexdigest(),'index_coverage':'absent','ret_pop':pop})
 table_evidence={'words':[{'va':f'{va:08x}','value':f'{value:08x}','relocation':'HIGHLOW'} for va,value in words],
  'assignments':writes,'slot0_consumers':[{'va':f'{va:08x}','instruction':asm[va][1]} for va in (0x48A3B8,0x48BB1C,0x48C946,0x48C96E)],
  'target_coverage_gaps':missing,
  'confirmed':'Each slot0 pointer and preceding RTTI pointer is HIGHLOW relocated. Native thiscall send ABI has three stack arguments and RET12.48ad70 ignores destination and queues packet;48b340 dereferences destination then calls48a3d0 and conditionally inserts it.5a1056 calls CRT fatal service5a2e22 with code25.',
  'next_step':'Supplement omitted target index coverage, recover targets48ad70/48b340 and full list/send callees48a920/48a8d0/48a3d0/55d4a0, trace RTTI consumers, then install one canonical native table owner and replace frozen151/155 literal identities in a new integration packet. No table size/RTTI layout or fatal-return behavior is guessed here.'}
 base='iterations/v2/001-original-recovery/'
 compiled=[base+'source/recovered/network_groups_probe.cpp',base+'source/recovered/Porsche.exe/network_groups.cpp',base+'source/recovered/Porsche.exe/network_services.cpp']
 paths=compiled+[base+'runs/163-network-groups/'+p for p in ('README.md','CMakeLists.txt')]+['scripts/research/verify-v2-network-groups.py','research/binary-index/static/binaries.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl','research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],'full_function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],'partial_function_vas':[],'cases':len(all_cases),'native_cpp_equal_original_x86':True,
 'comparison_boundary':'Six complete bodies; actual recovered 48c870 and48b660. Exact packets, call order/arguments and boundary state, all group/member/session/list/manager backing bytes, original ESP/nonvolatile registers and RET4/8/12. Private lock/fill/copy/virtual-send fixtures mutate index/masks/receiver/links/manager/pool/count at call boundaries. Text storage is a private fixture, production remains unsized unresolved.',
 'index_query':'48bda0 unresolved from complete492770, then all callers/callees48c220/48c300/490b70/48a390/48baa0; references to5b4968/70/78, original table words and PE HIGHLOW relocations.',
 'unresolved_effects':['005e8e50 unsized char data; owner and aliases remain unresolved','existing canonical heap lock/fill/copy and virtual-slot0 providers'],
 'deferred':['native vtable relocation for5b4968/70/78 and exact targets48ad70/5a1056/48b340','005e8bfc table owner/extent','0048dcb0 poll/0048e1a0 wait'],
 'original_functions':[{'va':f'{va:08x}','body_bytes':size,'body_sha256':hashlib.sha256(raw(va,size)).hexdigest()} for va,size,_ in FUNCTIONS.values()],
 'vtable_relocation_evidence':table_evidence,'cases_summary':summaries,'source_sha256':source_hashes([ROOT/p for p in paths],compiled_sources=[ROOT/p for p in compiled])}
 (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps({k:report[k] for k in ('function_vas','cases','native_cpp_equal_original_x86')}))
if __name__=='__main__':main()
