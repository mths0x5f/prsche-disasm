"""Typed original RTTI graph, destructor effects and complete cast helpers."""
import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'iterations/v2/001-original-recovery/runs/174-network-rtti'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,STACK,EXIT=0x400000,0x2210000,0x223f000;B=0x23000000
O,L,H,A,D,T,P,V,VB,STR=[B+x for x in (0,0x1000,0x1100,0x1200,0x2000,0x3000,0x4000,0x5000,0x6000,0x7000)]
FUNCTIONS={0:(0x5a1011,41),1:(0x5a103a,28),2:(0x5a14b3,26),3:(0x5a14cd,90),4:(0x5a1527,249),5:(0x5a1620,312),6:(0x5a1758,35),7:(0x5a4c20,129)}
CANON_COLS=(0x5c5190,0x5c51d8,0x5c5228);CANON_TYPES=(0x5d0630,0x5d0650,0x5d0690)
def cases():
 result=[]
 def add(op,count=4,target=0,source=1,offset=4,attrs=0,contained=3,virtual=0,cached=1,flags=1,mutation=0,length=9,align=0):result.append([op,count,target,source,offset,attrs,contained,virtual,cached,flags,mutation,length,align])
 for op in range(13):add(op)
 for op in (0,1,8):
  for cached in (0,1):
   for flags in (0,1,2,3,0x80000000,0xffffffff):
    for mutation in range(4):add(op,cached=cached,flags=flags,mutation=mutation)
 for offset in (0,4,16,0xfffffff0):
  for source in (0,16,0xfffffff0):
   for virtual in (0,4):add(2,offset=offset,source=source,virtual=virtual)
 for op in (3,4,5):
  for count in range(9):
   for target in range(4):
    for source in range(4):
     for contained in (0,1,3):add(op,count=count,target=target,source=source,contained=contained,offset=(source%4)*4)
  for attrs in (1,2,3,0x5555,0xaaaa,0xffff):
   for target in range(4):
    for virtual in range(4):
     for offset in (0,4,12,36):add(op,count=8,attrs=attrs,target=target,virtual=virtual,offset=offset)
 for source in range(8):
  for offset in (0,4,0x80000000,0xffffffff):
   for virtual in range(4):add(6,source=source,offset=offset,virtual=virtual)
 for align in range(16):
  for length in range(18):
   for mutation in (0,4,8):add(7,align=align,length=length,mutation=mutation)
 for target in (0,3):
  for attrs in (0,0xffff):
   for virtual,offset in ((0,20),(1,92),(2,0),(3,72)):add(5,count=8,target=target,source=1,offset=offset,attrs=attrs,contained=3,virtual=virtual)
 for op in (9,10,11,12):
  for target in range(3):
   for source in range(3):
    for length in range(3):add(op,target=target,source=source,length=length)
 return result
def original(module,image,case,records,reads):
 sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_READ
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
 for sec in module['sections']:
  if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
 uc.mem_map(0x2200000,0x40000);uc.mem_map(B,0x10000)
 def get(p):return struct.unpack('<I',uc.mem_read(p,4))[0]
 def put(p,v):uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 op,*a=case;trace=[];object_=0x5d0630 if op==8 else O
 uc.mem_write(B,b'\xcc'*0x10000);put(object_,0x12345678);put(object_+4,0x26000000 if a[7] else 0);put(O+0x20,VB);put(V,L);put(V+4,0);put(O,V+4)
 if op==8:put(object_,0x5c18f8)
 for i in range(5):put(L+i*4,0)
 put(L+4,a[3]);put(L+8,0x10 if a[6]&4 else 0);put(O+0x30,a[2]);put(O+0x40,V+4);put(L+0x10,H);put(H+8,a[0]);put(H+0xc,A)
 for i in range(8):
  put(A+i*4,D+i*0x40);put(D+i*0x40,T+(i%4)*0x100);remain=max(0,a[0]-i-1);put(D+i*0x40+4,0 if a[5]==0 else min(remain,1) if a[5]==1 else min(remain,3) if a[5]==2 else remain);put(D+i*0x40+8,0 if a[6]&2 else i*4);put(D+i*0x40+12,0x20 if a[6]&1 else 0xffffffff);put(D+i*0x40+16,i*4);put(D+i*0x40+20,(a[4]>>(i*2))&3);put(VB+i*4,i*8)
 for i,name in enumerate((b'.?AVA@@\0',b'.?AVB@@\0',b'.?AVC@@\0',b'.?AVA@@\0')):put(T+i*0x100,0);put(T+i*0x100+4,0);uc.mem_write(T+i*0x100+8,name)
 put(P,a[3]);put(P+4,0x20 if a[6]&1 else 0xffffffff);put(P+8,a[2]*4)
 uc.mem_write(STR,b'a'*64);uc.mem_write(STR+0x100,b'a'*64);uc.mem_write(STR+(a[11]&3)+a[10],b'\0');uc.mem_write(STR+0x100+((a[11]>>2)&3)+a[10],b'\0')
 if a[9]&4:uc.mem_write(STR+0x100+((a[11]>>2)&3)+max(0,a[10]-1),b'\xff')
 if a[9]&8:uc.mem_write(STR+0x100+((a[11]>>2)&3)+max(0,a[10]-1),b'\0')
 if op==9:put(V,CANON_COLS[a[1]%3])
 argmap={0:[],1:[a[8]],2:[O+0x40],3:[O,L,T+(a[2]%4)*0x100,a[3],T+(a[1]%4)*0x100],4:[O,L,T+(a[2]%4)*0x100,a[3],T+(a[1]%4)*0x100],5:[O,L,T+(a[2]%4)*0x100,a[3],T+(a[1]%4)*0x100],6:[O,P],7:[STR+(a[11]&3),STR+0x100+((a[11]>>2)&3)],8:[a[8]],9:[O],10:[O,CANON_COLS[a[1]%3],CANON_TYPES[a[2]%3],0,CANON_TYPES[a[10]%3]],11:[O,CANON_COLS[a[1]%3],CANON_TYPES[a[2]%3],0,CANON_TYPES[a[10]%3]],12:[O,CANON_COLS[a[1]%3],CANON_TYPES[a[2]%3],0,CANON_TYPES[a[10]%3]]}
 put(STACK,EXIT)
 for i,value in enumerate(argmap[op]):put(STACK+4+i*4,value)
 uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,object_)
 saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
 for reg,value in saved.items():uc.reg_write(reg,value)
 def hook(machine,address,size,data):
  if address==EXIT:machine.emu_stop();return
  if address not in (0x5a4ba4,0x5a4c05,0x5a3b9d,0x59f050):return
  sp=machine.reg_read(UC_X86_REG_ESP);arg=get(sp+4);trace.append([address,arg,get(object_),get(object_+4)])
  if address==0x5a4ba4 and a[9]&1:put(object_+4,0x26000010)
  if address==0x5a3b9d and a[9]&2:put(object_+4,0x26000020)
  machine.reg_write(UC_X86_REG_EAX,0x87654321 if address==0x59f050 else 0);machine.reg_write(UC_X86_REG_ESP,sp+4);machine.reg_write(UC_X86_REG_EIP,get(sp))
 def read_hook(machine,access,address,size,value,data):
  if op<8:return
  owner=next((r for r in records if int(r['va'],16)<=address<int(r['va'],16)+(r['bytes']+3)//4*4),None)
  if owner:reads.add((machine.reg_read(UC_X86_REG_EIP),address,size,owner['va']))
 uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ,read_hook)
 index=op if op<8 else {8:1,9:2,10:3,11:4,12:5}[op]
 uc.emu_start(FUNCTIONS[index][0],EXIT+1,count=100000)
 assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4+(4 if op in (1,8) else 0)
 assert all(uc.reg_read(reg)==value for reg,value in saved.items())
 state=[]
 for va,n in ((O,0x100),(D,0x200),(P,12)):state+=list(struct.unpack('<'+'I'*(n//4),uc.mem_read(va,n)))
 graph=[]
 for r in sorted(records,key=lambda r:r['va']):graph+=list(uc.mem_read(int(r['va'],16),r['bytes']))
 return {'return':0 if op==0 else uc.reg_read(UC_X86_REG_EAX),'trace':trace,'state':state,'graph':graph}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-rtti-174/bin/Release/rtti_probe.exe');ap.add_argument('--report-dir',type=Path,required=True);args=ap.parse_args();args.report_dir.mkdir(parents=True,exist_ok=True)
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 def raw(va,n):
  rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+s['raw_size']);o=s['raw_offset']+rva-s['rva'];return image[o:o+n]
 records=json.loads((RUN/'graph-inventory.json').read_text());records.append({'va':'005c18f4','kind':'VTABLE','bytes':8,'hex':raw(0x5c18f4,8).hex()})
 highlow=set();section=next(s for s in module['sections'] if s['name']=='.reloc');reloc=raw(BASE+section['rva'],section['raw_size']);offset=0
 while offset+8<=len(reloc):
  page,size=struct.unpack_from('<II',reloc,offset)
  if size<8:break
  for item in struct.unpack_from('<'+'H'*((size-8)//2),reloc,offset+8):
   if item>>12==3:highlow.add(BASE+page+(item&4095))
  offset+=size
 for r in records:
  va,n=int(r['va'],16),r['bytes'];data=raw(va,n);assert data.hex()==r['hex'];r['sha256']=hashlib.sha256(data).hexdigest()
  kind=r['kind'];pointer_offsets={'COL':[12,16],'CHD':[12],'BCD':[0],'TD':[0],'VTABLE':[0,4]}.get(kind,list(range(0,n,4)))
  r['relocations']=[]
  for i in pointer_offsets:
   assert va+i in highlow,(r['va'],i);r['relocations'].append({'offset':i,'target':f'{struct.unpack_from("<I",data,i)[0]:08x}','type':'HIGHLOW'})
 cs=cases();run=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,c))+'\n' for c in cs),text=True,capture_output=True,check=True);actuals=[json.loads(s) for s in run.stdout.splitlines()];assert len(actuals)==len(cs);reads=set()
 for i,(case,actual) in enumerate(zip(cs,actuals)):
  expected=original(module,image,case,records,reads)
  for key in expected:
   if actual[key]!=expected[key]:
    diff=[(j,x,y) for j,(x,y) in enumerate(zip(expected[key],actual[key])) if x!=y][:4] if isinstance(expected[key],list) else (expected[key],actual[key])
    raise AssertionError(f'case{i} {case} {key} {diff}; traces{expected["trace"]}/{actual["trace"]}')
 evidence={'module':'Porsche.exe','sha256':SHA,'records':sorted(records,key=lambda r:r['va']),'consumer_reads':[{'instruction_va':f'{pc:08x}','address':f'{va:08x}','size':n,'record':owner} for pc,va,n,owner in sorted(reads)],'bounds':'COL20,CHD16,BCD24 and count-sized pointer arrays from original consumers. Type descriptor prefix8 plus exact NUL name; original strcmp may fetch aligned DWORD containing terminator, so native C++ alignment provides readable padding but no original padding extent/value is asserted. type_info vtable has COL[-1] and one actual deleting destructor slot, before next original error text. Mutable cached name+4 remains a single canonical owner; destructor reads it after lock27 and frees without clearing.'}
 (args.report_dir/'rtti-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 index={r['entry_va']:r for r in map(json.loads,(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
 originals=[]
 for va,n in FUNCTIONS.values():
  row=index[f'{va:08x}'];assert row['body_bytes']==n;ranges=row['ranges'];data=b''.join(raw(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in ranges);assert len(data)==n
  originals.append({'va':f'{va:08x}','body_bytes':n,'ranges':ranges,'body_sha256':hashlib.sha256(data).hexdigest()})
 base='iterations/v2/001-original-recovery/';compiled=[base+'source/recovered/'+s for s in ('rtti_probe.cpp','Porsche.exe/rtti.cpp')];paths=compiled+[base+'runs/174-network-rtti/'+s for s in ('README.md','CMakeLists.txt','extract-rtti.py','graph-inventory.json','rtti-evidence.json')]+['scripts/research/verify-v2-network-rtti.py','research/binary-index/static/binaries.jsonl','research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']+['research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/'+s+'.jsonl' for s in ('functions','calls','references','symbols','unresolved-calls')]
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'full_function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'partial_function_vas':[],'cases':len(cs),'native_cpp_equal_original_x86':True,'index_query':'164 native table RTTI predecessors5c5190/5c51d8/5c5228 and168rtti-evidence; recurse type_info vtable5c18f8/COL5c98d0, destructors5a1011/5a103a and cast helpers5a14b3/14cd/1527/1620/1758/4c20. Registry checked all8 absent.',
 'comparison_boundary':'Eight complete bodies, exact returns/nonvolatile registers/ESP cleanup and private scripted existing lock/free/release effects. Synthetic hierarchy cases exercise repeated names, pointer identity, attributes, contained bases, virtual displacement/ambiguity, all byte alignments and NUL lengths. Real native typed graphs match original bytes after exact native pointer normalization at proven relocation fields; original functions traverse all three network graphs and actual native type_info destructor dispatch. No raw original VA callback calls.',
 'unresolved_effects':['dynamic_cast entry5a1366 SEH/throw path','type_info demangled-name cache population','shared networking providers/workers and text5e8e50 identity5b4980 extents'],
 'original_functions':originals,'compiled_source_files':compiled,'source_sha256':source_hashes(paths,compiled_sources=compiled)}
 (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS {len(cs)} original-x86 comparisons /8 bodies /{len(records)} typed graph records /{len(reads)} original field reads')
if __name__=='__main__':main()
