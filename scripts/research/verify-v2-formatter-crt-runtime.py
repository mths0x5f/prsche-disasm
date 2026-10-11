"""Run157 exact heap wrappers, global locks, TLS lifecycle and error cells."""
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
BASE,MEM,ARENA,EXIT=0x400000,0x2200000,0x2210000,0x220f000
ENTRIES=dict(m=0x5a3be5,n=0x5a3bf7,r=0x5a3c23,f=0x5a3b9d,h=0x5ab4ab,i=0x5a4b7b,l=0x5a4ba4,u=0x5a4c05,
             t=0x5a53f5,d=0x5a5449,g=0x5a545c,x=0x5a54c3,e=0x5a669e,o=0x5a66a7,c=0x5a8ea9,q=0x5aa9aa,s=0x5abe90)
POINTER_OPS=set('mnrcqgeos')
STATIC=(0x6afd00,0x6afd18,0x6afd30,0x6afd48)
IMPORTS={0x5b207c:('init',1),0x5b2078:('enter',1),0x5b206c:('leave',1),0x5b21dc:('heapalloc',3),
         0x5b2098:('heapfree',3),0x5b212c:('tlsalloc',0),0x5b2128:('tlsget',1),0x5b2124:('tlsset',2),
         0x5b213c:('geterror',0),0x5b21a4:('seterror',1),0x5b2074:('threadid',0)}
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EFLAGS

def cases():
 rows=[]
 def add(op,a=0,b=0,threshold=1016,small=0,fail=0,mode=0,retries=0,tls=0,race=0,length=0):
  rows.append((op,a,b,threshold,small,fail,mode,retries,tls,race,length))
 for op,size,small,mode in itertools.product('mnr',(0,1,15,16,17,511,512,513,1016,1017,0xffffffe0,0xffffffe1,0xfffffff1,0xffffffff),(0,1),(0,1)):
  add(op,size,mode,small=small,fail=-1 if size>512 else 0,mode=mode,retries=1)
 for op in 'mnc':
  for retries,race in itertools.product((0,1,3),(0,4,5)):
   add(op,24,1,small=0,fail=2,mode=1,retries=retries,race=race)
 for (count,size),small,mode in itertools.product(((0,0),(0,3),(1,0),(1,1),(2,7),(3,17),(1,511),(1,512),(1,513),(0x80000000,2),(0xffffffff,0xffffffff),(0xfffffff0,1),(0xffffffe0,1),(0xffffffff,1),(0x40000001,4)),(0,1),(0,1)):
  add('c',count,size,small=small,fail=-1 if ((count*size)&0xffffffff)>512 else 0,mode=mode,retries=1)
 for mode,retries in itertools.product((0,1),(0,1,3)): add('h',0x1234,mode=mode,retries=retries)
 for threshold,pointer in itertools.product((0,4),(0xffffffff,0,0xfff,0x1000,0x1010,0x100fff,0x101000,0x201000,0x301000,0x401000)):
  add('f',pointer,threshold=threshold)
 for pointer,count in itertools.product((0,0xfff,0x1000,0x1001,0x100fff,0x101000,0x101001,0x201000,0x301000,0x400fff,0x401000,0xfffffff0),(0,1,2,4,0xffffffff)): add('q',pointer,threshold=count)
 for id,state in itertools.product((0,1,9,13,17,18,19,25),(0,1)):
  if id!=17 or state: add('l',id,state,threshold=0 if id==9 and not state else 1016)
 for id in (0,1,9,13,17,18,19,25): add('u',id,1)
 for race in (1,2,3): add('l',18,0,race=race)
 add('l',18,0,fail=-1)
 add('l',18,0,small=1)
 add('i'); add('i',race=9); add('d')
 for op,tls,small in itertools.product('tgeo',range(6),(0,1)): add(op,small=small,tls=tls)
 for op,race in itertools.product('tgeo',(10,11)): add(op,tls=1,race=race)
 for mask,explicit,tls in itertools.product((0,1,2,32,63,64,127),(0,1),(0,1,5)):
  add('x',mask,explicit,threshold=0,tls=tls)
 for race in (6,7): add('x',127,1,threshold=0,race=race)
 for op in 'rc': add(op,17,1,race=8)
 for offset,value,length in itertools.product(range(8),(0,0x80,0xff,0x1234),(0,1,2,3,4,5,7,8,15,16,17,31,32,63,64,127)):
  add('s',offset,value,length=length)
 return rows

def mapped(image,module,va,size):
 rva=va-BASE
 s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+max(s['raw_size'],s['vsize']))
 rel=rva-s['rva']; n=max(0,min(size,s['raw_size']-rel)); off=s['raw_offset']+rel
 return image[off:off+n]+bytes(size-n)

def make_uc(image,module):
 uc=Uc(UC_ARCH_X86,UC_MODE_32); uc.mem_map(BASE,0x300000); uc.mem_map(MEM,0x30000)
 for s in module['sections']:
  if s['raw_size']: uc.mem_write(BASE+s['rva'],image[s['raw_offset']:s['raw_offset']+s['raw_size']])
 return uc

def original(uc,case,trace=False):
 op,a,b,threshold,small,fail,mode,retries,tls,race,length=case
 put=lambda p,v: uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 word=lambda p: struct.unpack('<I',uc.mem_read(p,4))[0]
 def signed(v): return struct.unpack('<i',struct.pack('<I',v&0xffffffff))[0]
 def loc(p):
  if not p: return -1
  if p==0x5e5ec8: return -2
  if p in STATIC: return -100-STATIC.index(p)*24
  return signed(p-ARENA)
 uc.mem_write(ARENA,bytes([0xa5])*0xc000)
 for p in STATIC: uc.mem_write(p,bytes([0xcc])*24)
 for i in range(26): put(0x5e57a8+i*4,ARENA+0x9000+i*32)
 for id,p in zip((1,17,9,13),STATIC): put(0x5e57a8+id*4,p)
 put(0x5e606c,threshold); put(0x6afec8,mode); put(0x6afecc,MEM+0x5000 if mode else 0)
 put(0x6c01d8,0x76543210); put(0x6c01d0,threshold if op in 'fq' else 4); put(0x6c01d4,ARENA+0xb000)
 for i in range(4): put(ARENA+0xb000+i*20+12,ARENA+0x1000+i*0x100000)
 put(0x5e58b4,0xffffffff if tls==5 else 7)
 tls_value=ARENA+0x7000 if tls==0 else 0
 last_error=77; heap_calls=handler_calls=0; heap_next=0x2000
 if op=='l' and not b: put(0x5e57a8+a*4,0)
 if op=='x':
  for i,off in enumerate((0x24,0x28,0x30,0x38,0x40,0x44)): put(ARENA+0x7000+off,ARENA+0x5000+i*0x100 if a&(1<<i) else 0)
  put(ARENA+0x7050,ARENA+0x6800 if a&64 else 0x5e5ec8)
 api={cell:MEM+0x1000+i*0x100 for i,cell in enumerate(IMPORTS)}
 for cell,p in api.items(): put(cell,p)
 api_names={p:IMPORTS[cell] for cell,p in api.items()}
 events=[]; fatal=False
 def hook(m,address,_size,_data):
  nonlocal last_error,heap_calls,heap_next,handler_calls,tls_value,fatal
  esp=m.reg_read(UC_X86_REG_ESP); arg=lambda i: word(esp+4+i*4)
  def finish(v=0,n=0):
   m.reg_write(UC_X86_REG_EAX,v&0xffffffff); m.reg_write(UC_X86_REG_EIP,word(esp)); m.reg_write(UC_X86_REG_ESP,esp+4+n*4)
  if address==EXIT: m.emu_stop(); return
  if address==0x5a2e22:
   events.append(f'fatal:{arg(0)}'); fatal=True; m.emu_stop(); return
  if address==0x5aad00:
   events.append(f'small:{arg(0)}'); last_error=0x32; finish(ARENA+0x1000 if small else 0); return
  if address==0x5aa9d5:
   events.append(f'smallfree:{loc(arg(0))}:{loc(arg(1))}'); last_error=0x33; finish(); return
  if address==MEM+0x5000:
   events.append(f'handler:{arg(0)}'); handler_calls+=1; last_error=0x39
   if race==4: put(0x6afec8,0)
   if race==5: put(0x6afecc,0)
   finish(-7 if handler_calls<=retries else 0); return
  if address not in api_names: return
  name,n=api_names[address]; value=0
  if name=='heapalloc':
   heap,flags,size=arg(0),arg(1),arg(2); events.append(f'heapalloc:{heap}:{flags}:{size}'); last_error=0x31; heap_calls+=1
   if fail>=0 and heap_calls>fail and tls!=2:
    assert size<=0x200 and heap_next+0x200<=0x7000
    value=ARENA+heap_next; heap_next+=0x200
    if flags&8: uc.mem_write(value,bytes(size))
  elif name=='heapfree':
   events.append(f'heapfree:{arg(0)}:{arg(1)}:{loc(arg(2))}'); last_error=0x34
   if race==6: put(ARENA+0x7028,ARENA+0x6000)
   if race==7: put(0x5e58b4,33)
  elif name in ('init','enter','leave'):
   p=arg(0); events.append(f'{name}:{loc(p)}'); last_error={'init':0x41,'enter':0x42,'leave':0x43}[name]
   if name=='init': uc.mem_write(p,bytes([0x5a])*24)
   if name=='init' and race==2: put(0x5e57a8+a*4,ARENA+0x9700)
   if name=='init' and race==9 and p==STATIC[1]:
    for id,off in ((13,0x9700),(9,0x9800),(1,0x9900)): put(0x5e57a8+id*4,ARENA+off)
   if name=='enter' and race==1 and p==STATIC[1]: put(0x5e57a8+a*4,ARENA+0x9700)
   if name=='leave' and race==3 and p==STATIC[1]: put(0x5e57a8+a*4,ARENA+0x9700)
   if name=='leave' and race==8: put(0x6c01d8,0x12345601)
  elif name=='tlsalloc': events.append(name); last_error=0x47; value=0xffffffff if tls==4 else 7
  elif name=='tlsget': events.append(f'tlsget:{arg(0)}'); last_error=0x44; value=tls_value
  elif name=='tlsset':
   events.append(f'tlsset:{arg(0)}:{loc(arg(1))}'); last_error=0x45
   if tls!=3:
    if race==10: put(0x5e58b4,33)
    tls_value=arg(1); value=1
  elif name=='geterror': events.append(name); value=last_error
  elif name=='seterror': events.append(f'seterror:{arg(0)}'); last_error=arg(0)
  elif name=='threadid':
   events.append(name); last_error=0x46; value=0x24681357
   if race==11: put(tls_value+4,0x1234); tls_value=ARENA+0x7200
  finish(value,n)
 args=[]
 if op in 'mrhlun': args=[a]
 if op=='n': args=[a,b]
 if op=='c': args=[a,b]
 if op in 'fq': args=[0 if op=='f' and a==0xffffffff else (ARENA+a)&0xffffffff]
 if op=='d': args=[ARENA+0x7000]
 if op=='x': args=[ARENA+0x7000 if b else 0]
 if op=='s': args=[ARENA+a,b,length]
 sp=MEM+0x8000; uc.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),EXIT,*args)); uc.reg_write(UC_X86_REG_ESP,sp)
 regs=(UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI)
 for r in regs: uc.reg_write(r,0x12345678)
 uc.reg_write(UC_X86_REG_EFLAGS,2)
 handle=uc.hook_add(UC_HOOK_CODE,hook)
 def memory_hook(m,_access,p,width,value,_data):
  if 0x5abe90<=m.reg_read(UC_X86_REG_EIP)<=0x5abee7 and ARENA<=p<ARENA+0xc000:
   events.append(f'store:{loc(p)}:{width}:{value&((1<<(width*8))-1)}')
 memory_handle=uc.hook_add(UC_HOOK_MEM_WRITE,memory_hook) if trace else None
 uc.emu_start(ENTRIES[op],0,count=200000)
 if not fatal:
  assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==sp+4,case
  assert all(uc.reg_read(r)==0x12345678 for r in regs),case
 value=0
 if not fatal and op in POINTER_OPS: value=loc(uc.reg_read(UC_X86_REG_EAX))
 elif not fatal and op in 'ht': value=signed(uc.reg_read(UC_X86_REG_EAX))
 data=bytearray(uc.mem_read(ARENA,0xc000))
 for i in range(4): struct.pack_into('<I',data,0xb000+i*20+12,0x1000+i*0x100000)
 result={'return':value,'fatal':fatal,'error':last_error,'tls_index':word(0x5e58b4),'tls':loc(tls_value),'heap':word(0x6c01d8),
         'mode':word(0x6afec8),'handler':bool(word(0x6afecc)),'locks':[loc(word(0x5e57a8+i*4)) for i in range(26)],
         'arena':data.hex(),'static':b''.join(bytes(uc.mem_read(p,24)) for p in STATIC).hex(),'events':events}
 uc.hook_del(handle)
 if memory_handle: uc.hook_del(memory_handle)
 return result

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--probe',required=True,type=Path); parser.add_argument('--report-dir',required=True,type=Path); args=parser.parse_args()
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe')
 image=(ROOT/'local/game'/module['path']).read_bytes(); assert hashlib.sha256(image).hexdigest()==SHA
 inputs=cases(); results=[]; traced=[]; initial_state=None
 for trace in (False,True):
  exe=args.probe.resolve() if not trace else args.probe.resolve().with_name('formatter_crt_runtime_trace_probe.exe')
  proc=subprocess.run([str(exe)],input='\n'.join(' '.join(map(str,c)) for c in inputs)+'\n',text=True,capture_output=True,check=True)
  native=[json.loads(x) for x in proc.stdout.splitlines()]; actual_initial=native.pop(0); assert len(native)==len(inputs)
  initial_word=lambda p:struct.unpack('<I',mapped(image,module,p,4))[0]
  def initial_loc(p):
   if not p:return -1
   assert p in STATIC
   return -100-STATIC.index(p)*24
  expected_initial={'initial':[initial_word(p) for p in (0x5e606c,0x6afec8,0x6c01d8,0x6c01d0,0x5e58b4,0x6afecc,0x6c01d4)],
                    'locks':[initial_loc(initial_word(0x5e57a8+i*4)) for i in range(26)],
                    'static':b''.join(mapped(image,module,p,24) for p in STATIC).hex()}
  assert actual_initial==expected_initial,(actual_initial,expected_initial); initial_state=actual_initial
  uc=make_uc(image,module)
  for c,row in zip(inputs,native):
   expected=original(uc,c,trace)
   assert row==expected,(c,trace,{k:v for k,v in row.items() if k!='arena'},{k:v for k,v in expected.items() if k!='arena'},'arena_equal',row['arena']==expected['arena'],
                        'first_difference',next((i//2 for i,(a,b) in enumerate(zip(row['arena'],expected['arena'])) if a!=b),None))
   if trace:
    traced.append({'input':c,'stores':[e for e in row['events'] if e.startswith('store:')]})
   else:
    summary={k:v for k,v in row.items() if k!='arena'}; summary['arena_sha256']=hashlib.sha256(bytes.fromhex(row['arena'])).hexdigest(); summary['arena_bytes']=0xc000
    results.append({'input':c,'output':summary})
 index=ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
 indexed={int(r['entry_va'],16):r for r in map(json.loads,(index/'functions.jsonl').read_text().splitlines())}
 functions={}
 for va in ENTRIES.values():
  f=indexed[va]; assert len(f['ranges'])==1; begin,end=map(lambda x:int(x,16),f['ranges'][0]); body=mapped(image,module,begin,end-begin+1); assert len(body)==f['body_bytes']
  functions[f'{va:08x}']={'ranges':f['ranges'],'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest()}
 prefix='iterations/v2/001-original-recovery/'
 paths=[prefix+'source/include/porsche/formatter_crt_runtime.hpp',prefix+'source/recovered/Porsche.exe/formatter_crt_runtime.cpp',prefix+'source/recovered/formatter_crt_runtime_probe.cpp',
        prefix+'runs/157-crt-runtime/CMakeLists.txt',prefix+'runs/157-crt-runtime/README.md','scripts/research/verify-v2-formatter-crt-runtime.py']
 calls=[r for r in map(json.loads,(index/'calls.jsonl').read_text().splitlines()) if r.get('from_function') in functions]
 names={'init':'InitializeCriticalSection','enter':'EnterCriticalSection','leave':'LeaveCriticalSection',
        'heapalloc':'HeapAlloc','heapfree':'HeapFree','tlsalloc':'TlsAlloc','tlsget':'TlsGetValue','tlsset':'TlsSetValue',
        'geterror':'GetLastError','seterror':'SetLastError','threadid':'GetCurrentThreadId'}
 indexed_imports={BASE+int(r['iat_rva'],16):r['symbol'] for r in map(json.loads,(ROOT/'research/binary-index/static/imports.jsonl').read_text().splitlines()) if r['path']==module['path']}
 for cell,(name,_) in IMPORTS.items(): assert indexed_imports[cell]==names[name]
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':list(functions),'full_function_vas':list(functions),'partial_function_vas':[],
         'functions':functions,'cases':len(results)+len(traced),'unique_inputs':len(inputs),'production_cases':len(results),'instrumented_cases':len(traced),
         'native_cpp_equal_original_x86':True,'case_results':results,'ordered_memset_stores':traced,'initial_storage':initial_state,'lock_table_prefix':{'va':'005e57a8','bytes':104,'sha256':hashlib.sha256(mapped(image,module,0x5e57a8,104)).hexdigest(),'reason':'Text consumer lock19 and locale setter lock25; prefix only, no total table extent claim'},'index_calls':calls,'source_sha256':source_hashes(paths),
         'iat_imports':{f'{cell:08x}':names[name] for cell,(name,_) in IMPORTS.items()},
         'unrecovered_dependencies':['005aad00','005aa9d5'],'unrecovered_data_dependencies':['005e5ec8'],
         'memory_trace':{'production_macro':False,'private_trace_macro':'PORSCHE_CRT_MEMORY_TRACE=1','stores':sum(len(r['stores']) for r in traced),
                         'scope':'Destination writes in 005abe90 only; excludes stack prologue and API fixture writes.'},
         'limits':['Win32 heap/TLS/critical-section APIs, small-block allocate/free and fatal dispatch are explicit recording boundaries.',
                   'The complete owned arena, 26 proven lock cells, 96 static lock bytes, TLS/error/global state and ordered boundary events are compared.',
                   'Native/oracle pointer fields are normalized by relocation identity; surrounding bytes remain exact.',
                   'No live native concurrency, OS heap allocator parity, game launch or visual acceptance.']}
 args.report_dir.mkdir(parents=True,exist_ok=True); (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({'ok':True,'full_functions':len(functions),'cases':len(results)+len(traced),'native_cpp_equal_original_x86':True}))

if __name__=='__main__': main()
