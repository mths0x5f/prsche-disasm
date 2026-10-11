"""Run161: connected original CRT small-block heap and realloc differential proof."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,MEM,START=0x400000,0x22000000,0x23000000
HEAD,META,OTHER,REGION=START,START+0x10000,START+0x200000,START+0x400000
EXIT=MEM+0xf000
VAS=(0x5aa96c,0x5aa9d5,0x5aad00,0x5ab009,0x5ab0ba,0x5ab1b5,0x5a8029,0x5a8161,0x5a96fa,0x5a7ad0)
IAT={0x5b21dc:('ha',3),0x5b2098:('hf',3),0x5b2104:('hr',4),0x5b2100:('hs',3),0x5b20d8:('hc',3),
     0x5b20dc:('hd',1),0x5b2144:('va',4),0x5b2148:('vf',3),0x5b2078:('enter',1),0x5b206c:('leave',1)}
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EFLAGS
POISON=bytes([0xa5])*0x400000

def cases():
 out=[]
 def add(k,a=0,b=0,c=0,seed=0,fail=0,call=1,mode=0):out.append((k,fail,call,mode,a,b,c,seed))
 for entry in range(10):add('V',a=entry)
 for k in 'IS':
  for fail,mode in itertools.product((0,1,5),(0,1)):add(k,a=mode,fail=fail)
 for capacity,fail in itertools.product((0,1,16),(0,1,2,3)):add('H',a=capacity,fail=fail)
 for size in sorted({n*16+delta for n in range(1,65) for delta in (-8,-7) if n*16+delta<=1016}):
  add('A',a=1,b=size)
  for order in (0,1,2):add('F',a=4,b=size,c=order)
 for group,fail in itertools.product((0,1,15,31),(0,4)):add('C',a=group,fail=fail)
 for count,size in itertools.product((1,2,3,8,40,100),(0,1,15,16,17,495,496,497,511,512,513,1000,1016)):add('A',a=count,b=size)
 for count,size,order in itertools.product((1,2,3,8,40,100),(1,17,496,512,1016),(0,1,2)):add('F',a=count,b=size,c=order)
 for count,reverse,fail in itertools.product((2,3),(0,1),(0,6,7)):add('D',a=count,b=reverse,fail=fail,call=0)
 for size in (0,16,496,512,1016):add('B',a=1,b=size)
 for seed in (17,499):add('F',a=100,b=13,c=2,seed=seed)
 for op,size,mask in itertools.product('Rr',(16,32,64,496,512,1016),(0,1,2,3)):
  requests=(0,1,15,16,31,32,63,64,127,495,512,1016) if op=='R' else (0,1,32,512,1016,1017,4096,0xffffffe1)
  for request in requests:add(op,a=size,b=mask,c=request)
 for op,fail,mode in itertools.product('APr',(1,3,4),(0,1,2)):
  add(op,a=64 if op=='r' else 2,b=0 if op=='r' else 32,c=4096 if op=='r' else 0,fail=fail,mode=mode)
 for size in (1,17,496,512,1016):add('Z',a=3,b=size)
 for size,op,fail in itertools.product((0,1,17,512,4096,0xffffffe1),(0,1),(0,2,8)):add('E',b=size,c=op,fail=fail)
 for size,fail in itertools.product((4096,0xffffffe1),(0,1,2)):add('E',b=size,fail=fail,mode=2)
 for src,dst,length in itertools.product(range(8),range(8),(0,1,2,3,4,5,7,8,15,16,17,31,32,63,64,127)):add('M',a=32+src,b=32+dst,c=length,seed=13)
 return out

def mapped(image,module,va,n):
 rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+max(s['raw_size'],s['vsize']))
 rel=rva-s['rva'];amount=max(0,min(n,s['raw_size']-rel));off=s['raw_offset']+rel
 return image[off:off+amount]+bytes(n-amount)

def make_uc(image,module):
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000);uc.mem_map(MEM,0x10000);uc.mem_map(START,0x1000000)
 for s in module['sections']:
  if s['raw_size']:uc.mem_write(BASE+s['rva'],image[s['raw_offset']:s['raw_offset']+s['raw_size']])
 return uc

def original(uc,case):
 kind,fail_api,fail_call,mode,a,b,c,seed=case
 put=lambda p,v:uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 word=lambda p:struct.unpack('<I',uc.mem_read(p,4))[0]
 uc.mem_write(START,POISON)
 for p,v in ((0x6c01d8,0xabcdef01),(0x6c01d0,0),(0x6c01d4,0),(0x6c01c0,0),(0x6c01c4,87),(0x6c01c8,0),(0x6c01cc,0),(0x5e606c,1016),(0x6afec8,mode),(0x6afecc,MEM+0x5000 if mode else 0)):put(p,v)
 events=[];returns=[];states=[];boundary_states=[];ranges={};sizes={};counters=[0]*10;enabled=False
 metadata_next=region_next=other_next=0;header_size=0;header_target=HEAD+0x1000;fatal=False;handler_calls=0
 api={cell:MEM+0x1000+i*0x100 for i,cell in enumerate(IAT)}
 for cell,p in api.items():put(cell,p)
 names={p:IAT[cell] for cell,p in api.items()}
 def fail(id):
  counters[id]+=1
  return enabled and id==fail_api and (not fail_call or counters[id]==fail_call)
 def track(p,n):
  if p:ranges[p]=max(ranges.get(p,0),n);sizes[p]=n
 def configure():
  nonlocal enabled
  counters[:]=[0]*10;enabled=True
 def snapshot():
  digest=hashlib.sha256(struct.pack('<7I',*(word(p) for p in (0x6c01d8,0x6c01c0,0x6c01d0,0x6c01d4,0x6c01c8,0x6c01cc,0x6c01c4))))
  for p,n in sorted(ranges.items()):digest.update(struct.pack('<II',p,n));digest.update(uc.mem_read(p,n))
  return digest.hexdigest()
 def hook(m,address,_size,_data):
  nonlocal metadata_next,region_next,other_next,header_size,header_target,fatal,handler_calls
  esp=m.reg_read(UC_X86_REG_ESP);arg=lambda i:word(esp+4+i*4)
  def finish(v=0,n=0):
   m.reg_write(UC_X86_REG_EAX,v&0xffffffff);m.reg_write(UC_X86_REG_EIP,word(esp));m.reg_write(UC_X86_REG_ESP,esp+4+n*4)
  if address==EXIT:m.emu_stop();return
  if address==0x5a2e22:boundary_states.append(snapshot());events.append(f'fatal:{arg(0)}');fatal=True;m.emu_stop();return
  if address==MEM+0x5000:
   boundary_states.append(snapshot());events.append(f'handler:{arg(0)}');handler_calls+=1;finish(int(mode==2 and handler_calls==1));return
  if address not in names:return
  boundary_states.append(snapshot())
  name,n=names[address];args=[arg(i) for i in range(n)];value=0
  if name in ('enter','leave'):
   assert args[0] in (0x6afd30,0x6afd18);events.append(name+('9' if args[0]==0x6afd30 else '17'));finish(0,n);return
  events.append(name+':'+':'.join(map(str,args)))
  if name=='ha':
   heap,flags,size=args
   if not fail(1):
    if size==0x140 and not word(0x6c01d4):value=HEAD;header_size=size
    elif size==0x41c4:assert metadata_next<32;value=META+metadata_next*0x10000;metadata_next+=1
    else:assert size<=0x10000 and other_next<16;value=OTHER+other_next*0x10000;other_next+=1
    if flags&8:uc.mem_write(value,bytes(size))
    track(value,size)
  elif name=='hf':value=0 if fail(7) else 1
  elif name=='hr':
   heap,flags,p,size=args
   if not fail(2):
    if HEAD<=p<HEAD+0x10000:value=header_target;header_target+=0x1000;amount=min(header_size,size);header_size=size
    else:value=OTHER+other_next*0x10000;other_next+=1;amount=min(sizes.get(p,0),size)
    assert size<=0x10000
    uc.mem_write(value,bytes(uc.mem_read(p,amount)));track(value,size)
  elif name=='hs':value=0xffffffff if fail(8) else sizes.get(args[2],0xffffffff)
  elif name=='hc':value=0 if fail(5) else 0xabcdef01
  elif name=='hd':value=0 if fail(9) else 1
  elif name=='va':
   p,size,flags,protect=args
   if not fail(3 if flags==0x2000 else 4):
    if flags==0x2000:assert region_next<12;value=REGION+region_next*0x100000;region_next+=1
    else:uc.mem_write(p,bytes(size));track(p,size);value=p
  elif name=='vf':value=0 if fail(6) else 1
  finish(value,n)
 handle=uc.hook_add(UC_HOOK_CODE,hook)
 def run(va,*args):
  sp=MEM+0x8000;uc.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),EXIT,*args));uc.reg_write(UC_X86_REG_ESP,sp)
  regs=(UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI)
  for r in regs:uc.reg_write(r,0x12345678)
  uc.reg_write(UC_X86_REG_EFLAGS,2);uc.emu_start(va,0,count=1000000)
  if fatal:raise RuntimeError('fatal')
  assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==sp+4,(case,hex(va))
  assert all(uc.reg_read(r)==0x12345678 for r in regs),(case,hex(va))
  assert not (uc.reg_read(UC_X86_REG_EFLAGS)&0x400),(case,'DF')
  return uc.reg_read(UC_X86_REG_EAX)
 def record(va,*args):
  value=run(va,*args);returns.append(value);states.append(snapshot());return value
 def get(size,direct=True):
  p=record(0x5aad00 if direct else 0x5a3be5,size)
  if p:uc.mem_write(p,bytes((j*17+size+seed)&255 for j in range(size)))
  return p
 def release(p):run(0x5a3b9d,p);returns.append(0);states.append(snapshot())
 try:
  if kind=='V':
   counts=(0,2,1,0,1,3,2,1,1,3);args=[0,0,0]
   if a not in (0,8):record(0x5aa96c)
   if a in (1,5,6,7):
    p=get(64);args[:2]=p,96
    if a in (1,5):args[:]=run(0x5aa9aa,p),p,96
   if a==2:args[0]=32
   if a==4:args[0]=record(0x5ab009)
   if a==9:
    uc.mem_write(OTHER,bytes((j*13+seed)&255 for j in range(1024)));track(OTHER,1024);args[:]=OTHER+35,OTHER+32,127
   if a==1:run(VAS[a],*args[:counts[a]]);returns.append(0);states.append(snapshot())
   else:record(VAS[a],*args[:counts[a]])
  elif kind=='I':configure();record(0x5a96fa,a)
  elif kind=='S':configure();record(0x5aa96c)
  elif kind=='M':
   uc.mem_write(OTHER,bytes((j*13+seed)&255 for j in range(1024)));track(OTHER,1024);record(0x5a7ad0,OTHER+b,OTHER+a,c)
  else:
   record(0x5aa96c)
   if kind=='H':
    if a:record(0x5ab009);put(0x6c01c0,a)
    configure();record(0x5ab009)
   elif kind=='C':
    h=record(0x5ab009);put(h+8,0x80000000>>(a&31));configure();record(0x5ab0ba,h)
   elif kind=='D':
    values=[]
    for i in range(a):
     if i:h=record(0x5ab009);record(0x5ab0ba,h);put(0x6c01c8,h)
     values.append(get(1016))
    configure()
    if b:values.reverse()
    for p in values:release(p)
   elif kind=='E':
    # Call the same explicit fixture boundary used by the native input constructor.
    p=OTHER+other_next*0x10000;other_next+=1;boundary_states.append(snapshot());events.append(f'ha:{word(0x6c01d8)}:0:128');fail(1);track(p,128)
    uc.mem_write(p,bytes((j+seed)&255 for j in range(128)));configure();record(0x5a8161,p) if c else record(0x5a8029,p,b)
   elif kind in 'Rr':
    values=[get(a) for _ in range(3)]
    if b&1:release(values[0])
    if b&2:release(values[2])
    configure()
    if kind=='R':record(0x5ab1b5,run(0x5aa9aa,values[1]),values[1],c)
    else:record(0x5a8029,values[1],c)
   else:
    configure();values=[]
    for i in range(a):
     size=(b+i*seed)%1017 if seed else b;p=get(size,kind!='P')
     if not p:break
     values.append(p)
    if kind=='F':
     order=list(reversed(values)) if c==1 else values[::2]+values[1::2] if c==2 else values
     for p in order:release(p)
    elif kind=='Z':
     for p in values:record(0x5a8161,p)
    elif kind=='B' and values:release(values[-1]);get(b)
 except RuntimeError:
  assert fatal
 result={'fatal':fatal,'heap':word(0x6c01d8),'capacity':word(0x6c01c0),'count':word(0x6c01d0),'base':word(0x6c01d4),
         'cursor':word(0x6c01c8),'pending':word(0x6c01cc),'group':word(0x6c01c4),'returns':returns,'events':events,'states':states,'boundary_states':boundary_states,
         'memory':[{'p':p,'data':bytes(uc.mem_read(p,n)).hex()} for p,n in sorted(ranges.items())]}
 uc.hook_del(handle);return result

def alias_evidence(image,module):
 # All differing DWORDs are original HIGHLOW relocations into the two complete spans.
 a,b=0x5a1a40,0x5a7ad0;n=0x335;left=bytearray(mapped(image,module,a,n));right=mapped(image,module,b,n)
 reloc_section=next(s for s in module['sections'] if s['name']=='.reloc')
 data=image[reloc_section['raw_offset']:reloc_section['raw_offset']+reloc_section['raw_size']];sites=set();off=0
 while off+8<=len(data):
  page,size=struct.unpack_from('<II',data,off)
  if not size:break
  assert size>=8 and off+size<=len(data)
  for i in range(off+8,off+size,2):
   entry=struct.unpack_from('<H',data,i)[0]
   if entry>>12==3:sites.add(BASE+page+(entry&0xfff))
  off+=size
 patches=[];i=0
 while i<n:
  if left[i]==right[i]:i+=1;continue
  x=struct.unpack_from('<I',left,i)[0];y=struct.unpack_from('<I',right,i)[0]
  assert a<=x<a+n and y-x==b-a and a+i in sites and b+i in sites,(i,x,y)
  struct.pack_into('<I',left,i,y);patches.append({'offset':i,'from':f'{x:08x}','to':f'{y:08x}'});i+=4
 assert bytes(left)==right
 parent_path='iterations/v2/001-original-recovery/runs/154-context-move/verification.json'
 parent=json.loads((ROOT/parent_path).read_text(encoding='utf8'))
 assert parent['sha256']==SHA and parent['native_cpp_equal_original_x86'] and parent['memory_access_events']==130440
 inherited=source_hashes(['iterations/v2/001-original-recovery/source/recovered/Porsche.exe/context_move.cpp'])
 for path,sha in inherited.items():assert parent['source_sha256'][path]==sha,(path,'stale154proof')
 return {'source_va':f'{a:08x}','alias_va':f'{b:08x}','contiguous_bytes':n,'source_span_sha256':hashlib.sha256(mapped(image,module,a,n)).hexdigest(),
         'alias_span_sha256':hashlib.sha256(right).hexdigest(),'highlow_rebases':patches,'normalized_spans_equal':True,
         'inherited_order_proof':parent_path,'inherited_report_sha256':hashlib.sha256((ROOT/parent_path).read_bytes()).hexdigest(),
         'inherited_exact_ordered_memory_accesses':parent['memory_access_events'],'inherited_compiled_sources_current':True}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--probe',required=True,type=Path);parser.add_argument('--report-dir',required=True,type=Path);args=parser.parse_args()
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe')
 image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 inputs=cases();process=subprocess.run([str(args.probe.resolve())],input='\n'.join(' '.join(map(str,c)) for c in inputs)+'\n',text=True,capture_output=True,check=True)
 native=[json.loads(x) for x in process.stdout.splitlines()];assert len(native)==len(inputs)
 uc=make_uc(image,module);results=[]
 for case,row in zip(inputs,native):
  expected=original(uc,case)
  assert row==expected,(case,{k:v for k,v in row.items() if k!='memory'},{k:v for k,v in expected.items() if k!='memory'},
                        [(r['p'],r['data']==e['data'],next((i//2 for i,(a,b) in enumerate(zip(r['data'],e['data'])) if a!=b),None)) for r,e in zip(row['memory'],expected['memory'])])
  summary={k:v for k,v in row.items() if k!='memory'};summary['memory']=[{'p':m['p'],'bytes':len(m['data'])//2,'sha256':hashlib.sha256(bytes.fromhex(m['data'])).hexdigest()} for m in row['memory']]
  results.append({'input':case,'output':summary})
 index=ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
 entries={int(r['entry_va'],16):r for r in map(json.loads,(index/'functions.jsonl').read_text().splitlines())};functions={}
 for va in VAS:
  f=entries[va];body=b''.join(mapped(image,module,int(a,16),int(b,16)-int(a,16)+1) for a,b in f['ranges']);assert len(body)==f['body_bytes']
  functions[f'{va:08x}']={'ranges':f['ranges'],'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest()}
 prefix='iterations/v2/001-original-recovery/'
 paths=[prefix+'source/include/porsche/formatter_small_heap.hpp',prefix+'source/recovered/Porsche.exe/formatter_small_heap.cpp',prefix+'source/recovered/formatter_small_heap_probe.cpp',prefix+'runs/161-small-heap/CMakeLists.txt',prefix+'runs/161-small-heap/README.md',prefix+'runs/154-context-move/verification.json','scripts/research/verify-v2-formatter-small-heap.py']
 compiled=[prefix+'source/recovered/Porsche.exe/formatter_crt_runtime.cpp',prefix+'source/recovered/Porsche.exe/context_move.cpp']
 paths.extend(['research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/static/binaries.jsonl'])
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':list(functions),'full_function_vas':list(functions),'partial_function_vas':[],
         'functions':functions,'cases':len(results),'native_cpp_equal_original_x86':True,'case_results':results,'copy_alias':alias_evidence(image,module),
         'probe_sha256':hashlib.sha256(args.probe.read_bytes()).hexdigest(),
         'intermediate_snapshots':sum(len(r['output']['states']) for r in results),'boundary_snapshots':sum(len(r['output']['boundary_states']) for r in results),
         'snapshot_format':'SHA256 of seven LE32 allocator globals followed by sorted LE32 address,length and exact buffer bytes; captured after each recorded return and immediately before every external boundary.',
         'abi':'All original calls assert cdecl stack/nonvolatile registers/cleared DF; ten native V cases directly call each production entry through an inline-assembly sentinel bridge and check ESP, EBP, EBX, ESI, EDI and DF.',
         'source_sha256':source_hashes(paths,compiled_sources=compiled),'unrecovered_dependencies':[],
         'limits':['Heap/virtual-memory Win32 imports are deterministic recording boundaries; production contains no host allocator replacement.',
                   'Private Win32 fixed-address memory provides identical pointer values to original x86; all allocated metadata/header/OS buffers and committed groups are compared.',
                   'Decommit/release fixture records original calls and preserves readable private snapshots; it does not claim live VM protection or allocator parity.',
                   'Real recovered157 malloc/free/locks/headerlookup and154 memmove are compiled in the connected native probe.',
                   'Raw small-block allocation/resize/free inputs are valid initialized metadata and allocated blocks; no invented invalid-pointer handling.',
                   'No game launch or visual acceptance.']}
 args.report_dir.mkdir(parents=True,exist_ok=True);(args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({'ok':True,'full_functions':len(functions),'cases':len(results),'native_cpp_equal_original_x86':True}))
if __name__=='__main__':main()
