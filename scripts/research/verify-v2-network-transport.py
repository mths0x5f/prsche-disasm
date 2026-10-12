"""Exact lower network transport and route-list consumers vs original x86."""
import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,STACK,EXIT=0x400000,0x2210000,0x223f000
B=0x23000000
S,V,R,N,D,SRC=[B+x for x in (0,0x100,0x1000,0x2000,0x4000,0x10000)]
FUNCTIONS={0:(0x587000,176),1:(0x5870b0,89),2:(0x587110,94),3:(0x580b20,76),4:(0x580b70,28),5:(0x580a00,69),6:(0x580a50,57),7:(0x580ad0,72),8:(0x586ee0,102)}
RANGES=((B,0x200),(R,0x100),(N,0x100),(D,0x100),(SRC,0x8000))
def cases():
 result=[]
 def add(op,count=2,size=17,flags=0x80000000,routes=2,stage=1,head=2,mutation=0,returns=1,recurse=0,target=1,predicate=1):
  result.append([op,count,size,flags,routes,stage,head,mutation,returns,recurse,target,predicate])
 for op in range(9):add(op)
 for count in (0,1,2,3,4,0x80000000,0xffffffff):
  for size in (0,1,17,240,4095,5000):add(0,count,size)
 for count in (1,2,4):
  for routes in range(5):
   for recurse in (0,1):add(1,count,routes=routes,head=routes,recurse=recurse)
 for op in (2,3,4,8):
  for stage in (0,1,2,3,4,0x80000000,0xffffffff):
   for head in (0,1,2,4):add(op,stage=stage,head=head)
 for op in range(9):
  for mutation in (1,2,3,4,8,16,32,63):add(op,mutation=mutation)
  for returns in (0,1,0xffffffff):add(op,returns=returns)
 for op in (5,6,7):
  for target in range(5):
   for head in range(5):add(op,target=target,head=head)
 for flags in (0,0x01000000,0xff000000):
  for count in (1,2,4):add(0,count,flags=flags)
 for stage in (0,1,2,3):add(2,stage=stage,routes=4,head=4,recurse=1);add(8,stage=stage,routes=4,head=4,recurse=1)
 add(7,predicate=0)
 return result

def original(module,image,case):
 sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
 for sec in module['sections']:
  if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
 uc.mem_map(0x2200000,0x40000);uc.mem_map(B,0x20000);uc.mem_map(0x24000000,0x1000)
 def get(p):return struct.unpack('<I',uc.mem_read(p,4))[0]
 def put(p,v):uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 def norm(p):return p if B<=p<B+0x20000 else 0
 op,*a=case;trace=[];copies=0
 uc.mem_write(B,b'\xcc'*0x20000);put(S+8,V);put(V+8,0x24000000);put(S+0x24,0x24000000)
 put(R,a[3]);put(R+8,N if a[5] else 0);put(R+0x18,0x26000000);put(R+0x1c,0x12345678);put(R+0x10,0x24000030);put(R+0x14,N+a[9]*0x40 if a[9]<4 else 0)
 for i in range(4):n=N+i*0x40;put(n,n+0x40 if i+1<a[5] else 0);put(n+4,0x24000010);put(n+8,0x24000020);put(n+0xc,0x81000000+i)
 for i in range(12):put(D+i*12,a[2]^(i<<24));put(D+i*12+4,a[1]+i);put(D+i*12+8,SRC+(i%4)*0x2000)
 uc.mem_write(SRC,bytes((0x21+i*7)&255 for i in range(0x8000)))
 count,stage=a[0],a[4];target=N+a[9]*0x40 if a[9]<4 else 0
 argmap={0:[S,count,D],1:[S,count,D,R],2:[S,stage,count,D,R],3:[R,stage],4:[N,stage],5:[R,target],6:[R],7:[R,0x24000030 if a[10] else 0,target],8:[S,stage,count,D,R]}
 put(STACK,EXIT)
 for i,v in enumerate(argmap[op]):put(STACK+4+i*4,v)
 uc.reg_write(UC_X86_REG_ESP,STACK)
 saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
 for reg,value in saved.items():uc.reg_write(reg,value)
 def event(va,values=()):trace.append([va,*values,get(R),get(R+8),get(R+0x18),get(R+0x1c),get(D+4),get(D+16)])
 def hook(machine,address,size,data):
  nonlocal copies
  if address==EXIT:machine.emu_stop();return
  if address not in (0x5322b0,0x5322c0,0x5323e0,0x24000000,0x24000010,0x24000020,0x24000030):return
  sp=machine.reg_read(UC_X86_REG_ESP);result=0
  if address==0x5322b0:
   event(address,[get(sp+4)])
   if a[6]&1:put(R+8,get(N))
   if a[6]&2:put(R+0x18,0x26001000)
  elif address==0x5322c0:
   event(address,[get(sp+4)])
   if a[6]&4:put(R+8,0)
  elif address==0x5323e0:
   dst,src,n=[get(sp+4+i*4) for i in range(3)];event(address,[norm(dst),norm(src),n]);uc.mem_write(dst,bytes(uc.mem_read(src,n)))
   if not copies and a[6]&8:put(D+20,SRC+0x6000)
   copies+=1
  elif address==0x24000000:
   context,bytes_,packed=[get(sp+4+i*4) for i in range(3)];trace.append([address,context,norm(bytes_),packed,*uc.mem_read(bytes_,packed&0xffffff)]);event(0x24000001)
   if a[6]&16:put(R+0x18,0x26001111)
   result=a[7]
  elif address in (0x24000010,0x24000020):
   context,provider,count,desc,routes=[get(sp+4+i*4) for i in range(5)]
   trace.append([address,context,provider,count,routes,*struct.unpack('<'+str(count*3)+'I',uc.mem_read(desc,count*12))]);event(0x24000001)
   if a[6]&16:put(R+0x18,0x26001111)
   if a[8]:
    stage=get(R+0x1c)
    if address==0x24000010:put(desc+count*12,0x40000000);put(desc+count*12+4,3);put(desc+count*12+8,SRC+0x7000);put(sp+8,stage-1);put(sp+12,count+1);entry=0x587110
    else:put(sp+8,stage+1);entry=0x586ee0
    machine.reg_write(UC_X86_REG_EIP,entry);return
   result=a[7]
  else:
   node,target=get(sp+4),get(sp+8);event(address,[node,target])
   if a[6]&32:put(node,0)
   result=a[7] if node==target else 0
  machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4);machine.reg_write(UC_X86_REG_EIP,get(sp))
 uc.hook_add(UC_HOOK_CODE,hook)
 try:uc.emu_start(FUNCTIONS[op][0],EXIT+1,count=600000)
 except Exception as exc:raise RuntimeError(f'case{case} EIP={uc.reg_read(UC_X86_REG_EIP):08x} trace={trace[-3:]}') from exc
 assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4
 assert all(uc.reg_read(reg)==value for reg,value in saved.items())
 state=[]
 for va,n in RANGES:state+=list(struct.unpack('<'+str(n//4)+'I',uc.mem_read(va,n)))
 return {'return':uc.reg_read(UC_X86_REG_EAX),'trace':trace,'state':state}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-transport-168/bin/Release/network_transport_probe.exe');ap.add_argument('--report-dir',type=Path,required=True);args=ap.parse_args();args.report_dir.mkdir(parents=True,exist_ok=True)
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 cs=cases();run=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,c))+'\n' for c in cs),text=True,capture_output=True,check=True);actuals=[json.loads(s) for s in run.stdout.splitlines()];assert len(actuals)==len(cs)
 summaries=[]
 for i,(c,actual) in enumerate(zip(cs,actuals)):
  expected=original(module,image,c)
  for key in expected:
   if actual[key]!=expected[key]:
    diff=[(n,x,y) for n,(x,y) in enumerate(zip(expected[key],actual[key])) if x!=y][:3] if isinstance(expected[key],list) else (expected[key],actual[key])
    raise AssertionError(f'case{i} {c} {key}: {diff}; expectedtail={expected["trace"][-3:]}, actualtail={actual["trace"][-3:]}')
  summaries.append({'index':i,'function_va':f'{FUNCTIONS[c[0]][0]:08x}','input':c,'boundary_calls':len(expected['trace'])})
 def raw(va,n):
  rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+s['raw_size']);o=s['raw_offset']+rva-s['rva'];return image[o:o+n]
 asm={}
 for line in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines():
  parts=line.split()
  if len(parts)>2 and len(parts[0])==8:
   try:asm[int(parts[0],16)]=(bytes.fromhex(parts[1]),line)
   except ValueError:pass
 for va,n in FUNCTIONS.values():
  body=b'';cursor=va
  while len(body)<n:code,_=asm[cursor];body+=code;cursor+=len(code)
  assert body==raw(va,n) and body.endswith(b'\xc3')
 # RTTI observations remain an evidence packet, not production storage.
 reloc_sec=next(s for s in module['sections'] if s['name']=='.reloc');reloc=image[reloc_sec['raw_offset']:reloc_sec['raw_offset']+reloc_sec['vsize']];highlow=set();offset=0
 while offset<len(reloc):
  page,size=struct.unpack_from('<II',reloc,offset)
  if not size:break
  for item in struct.unpack_from('<'+'H'*((size-8)//2),reloc,offset+8):
   if item>>12==3:highlow.add(BASE+page+(item&4095))
  offset+=size
 def record(va,n,meaning):
  data=raw(va,n);return {'va':f'{va:08x}','bytes':n,'sha256':hashlib.sha256(data).hexdigest(),'hex':data.hex(),'meaning':meaning,'relocations':[{'offset':i,'value':f'{struct.unpack_from("<I",data,i)[0]:08x}','type':'HIGHLOW'} for i in range(0,n-3,4) if va+i in highlow]}
 records=[]
 for col in (0x5c5190,0x5c51d8,0x5c5228):
  words=struct.unpack('<5I',raw(col,20));records.append(record(col,20,'COL accessed prefix; no declaration/storage emitted'))
  assert col+12 in highlow and col+16 in highlow
  td,chd=words[3:];header=struct.unpack('<4I',raw(chd,16));records.append(record(chd,16,'hierarchy accessed prefix'))
  assert chd+12 in highlow and td in highlow
  count,array=header[2:];assert count in (1,2);records.append(record(array,count*4,'base array length from original hierarchy count'))
  for i,base_va in enumerate(struct.unpack('<'+str(count)+'I',raw(array,count*4))):
   assert array+i*4 in highlow and base_va in highlow
   records.append(record(base_va,24,'base descriptor accessed prefix incl PMD and attribute byte'))
  name=raw(td+8,64).split(b'\0',1)[0];records.append(record(td,8+len(name)+1,'type descriptor prefix and exact NUL-terminated name'));records[-1]['name']=name.decode('ascii')
 records=list({r['va']:r for r in records}.values());records.append(record(0x5c18f4,8,'type_info preceding RTTI pointer and destructor slot; next word begins error text'))
 consumer_vas=(0x5a1399,0x5a139b,0x5a13ac,0x5a14b9,0x5a14be,0x5a14c1,0x5a14db,0x5a14de,0x5a14e2,0x5a14ec,0x5a14f2,0x5a14f5,0x5a1505,0x5a13eb,0x5a175e,0x5a176c,0x5a1776,0x5a1016,0x5a1021,0x5a102a)
 evidence={'module':'Porsche.exe','sha256':SHA,'records':records,'consumer_instructions':[asm[va][1] for va in consumer_vas],'confirmed':'Original consumers use vptr[-1],COL+4/+8/+16, hierarchy+4/+8/+12, base+0/+8/+0c/+10/+14, type descriptor NUL name at+8. Mutable type descriptor cache+4 is read after lock27 then CRT-freed by5a1011. Imported type names identify CConClient/CConnection/CConHost, not transport algorithms.',
  'remaining':'No native owners emitted. Need full native RTTI graph incl type_info COL5c98d0 and its hierarchy/type descriptor, relocation-sensitive ownership/type_info vtable5c18f8 and real destructor5a103a/5a1011.5a103a automatic range includes trailing bytes beyond RET4; preserve exact index evidence before counting its recovery. Do not replace RTTI by dummy arrays.'}
 (args.report_dir/'rtti-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 base='iterations/v2/001-original-recovery/'
 compiled=[base+'source/recovered/'+s for s in ('network_transport_probe.cpp','Porsche.exe/network_transport.cpp','Porsche.exe/network_workers_members.cpp','Porsche.exe/io_lists.cpp')]
 paths=compiled+[base+'runs/168-network-transport/'+s for s in ('README.md','CMakeLists.txt','extract-count.py','rtti-evidence.json')]+['scripts/research/verify-v2-network-transport.py','research/binary-index/static/binaries.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/symbols.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/unresolved-calls.jsonl','research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'full_function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'partial_function_vas':[],'cases':len(cs),'native_cpp_equal_original_x86':True,
 'index_query':'164 missing587000/5870b0; directcallee587110/580b20/580b70 and connected route-list consumers580a00/580a50/580ad0/586ee0.',
 'comparison_boundary':'Nine complete bodies plus canonical159 count5809f0 verbatim extraction. Exact initialized descriptor/packet data, concatenation/flags, returns/order/state and original ESP/nonvolatile ABI. Provider-table+8/+24 and route-node+4/+8 plus predicates are scripted private effects; recursive callback scripts execute real original/native traversal. Existing lock/copy boundaries mutate head/lock/source/next at call points. Native _alloca implements original chkstk platform seam. Unused spare descriptor tail excluded because original leaves it uninitialized.',
 'unresolved_effects':['actual context provider-table+8/+24 backends','actual route-node transform callbacks+4/+8','RTTI owners5c5190/5c51d8/5c5228'],
 'deferred':['trace provider table and route-node writers before claiming actual OS transport implementation','RTTI consumer layout and bounds; COL-shaped raw data alone does not prove native owners'],
 'original_functions':[{'va':f'{va:08x}','body_bytes':n,'body_sha256':hashlib.sha256(raw(va,n)).hexdigest()} for va,n in FUNCTIONS.values()],
 'compiled_source_files':compiled,'source_sha256':source_hashes(paths,compiled_sources=compiled),'cases_summary':summaries}
 (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS {len(cs)} original-x86 comparisons /9 bodies')
if __name__=='__main__':main()
