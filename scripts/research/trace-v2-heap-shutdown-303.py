"""Original shutdown binding/state audit, with controlled original-call cutpoints."""
import hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
from v2_shared_manifests import externalize,ManifestReader
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'iterations/v2/001-original-recovery/runs/303-heap-shutdown-bridge'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
def main():
 RUN.mkdir(parents=True,exist_ok=True);assert not (RUN/'summary.json').exists()
 image=ROOT/'local/game/Porsche.exe';raw=image.read_bytes();assert sha(image)==SHA
 spec=importlib.util.spec_from_file_location('pe303',ROOT/'scripts/research/audit-v2-frame-service-290.py');pe_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(pe_module);read=pe_module.pe_read
 wrapper=read(raw,0x4a54e0,5);body=read(raw,0x59eb20,159);assert wrapper[0]==0xe9 and (0x4a54e5+int.from_bytes(wrapper[1:],'little',signed=True))==0x59eb20 and body[-1:]==b'\xc3'
 targets=['004a54e0','0059eb20','005678f0','0055ec30','0059ee30','005699f0']
 registry_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json';registry=json.loads(registry_path.read_bytes())['functions']
 index_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl';index=[json.loads(x) for x in index_path.read_text().splitlines()]
 accepted={x['entry_va'] for x in registry};assert not any(t in accepted for t in targets)
 assert not any(int(a,16)<=int(t,16)<=int(b,16) for t in targets for x in index if x['entry_va'] in accepted for a,b in x['ranges'])
 imports_path=ROOT/'research/binary-index/static/imports.jsonl';imports=[json.loads(x) for x in imports_path.read_text().splitlines()]
 imp=[x for x in imports if x['path']=='Porsche.exe' and x['symbol']=='VirtualFree'];assert len(imp)==1 and int(imp[0]['iat_rva'],16)+0x400000==0x5b2148
 asm_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm';asm=asm_path.read_text();block=asm.split('; FUNCTION 0059eb20 ',1)[1].split('; FUNCTION ',1)[0]
 assert b''.join(bytes.fromhex(x) for x in re.findall(r'(?m)^[0-9a-f]{8}\s+([0-9a-f]+)\s+',block))==body
 union_path=RUN.parent/'274-shared-heap-union/summary.json';union=json.loads(union_path.read_bytes());providers=[x for x in union['results'] if x['va'] in targets]
 assert [x['va'] for x in providers]==['0055ec30']
 provider=providers[0];assert sha(ROOT/provider['object'])==provider['object_sha256'] and sha(ROOT/provider['generated_source'])==provider['generated_source_sha256']
 c=importlib.util.spec_from_file_location('coff303',ROOT/'scripts/research/build-v2-compile-corpus.py');coff=importlib.util.module_from_spec(c);c.loader.exec_module(coff)
 assert coff.coff_symbols(ROOT/provider['object'])==provider['symbols']
 resources={f'{a:08x}':read(raw,a,n).hex() for a,n in [(0x5e4fe8,4),(0x5e4fec,4),(0x5e3e18,16)]}
 assert resources['005e4fe8']=='183e5e00' and resources['005e4fec']=='74f36a00'
 pe=struct.unpack_from('<I',raw,60)[0];op=pe+24;n=struct.unpack_from('<H',raw,pe+6)[0];oh=struct.unpack_from('<H',raw,pe+20)[0];size=struct.unpack_from('<I',raw,op+56)[0]
 sections=[struct.unpack_from('<IIII',raw,op+oh+i*40+8) for i in range(n)]
 cases=[]
 configs=[('disabled',0,3,-1,0),('absent',1,3,-1,0),('found_zero',1,3,0,0),('found_last',1,3,15,0),('queue_swaps_selector',1,3,5,1),('free_changes_object_id',1,3,4,2),('pool_changes_object_id',1,3,2,3),('index16_aliases_guard',0x91,16,-1,0)]
 for name,flag,object_id,found,mutation in configs:
  uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(0x400000,(size+4095)&~4095)
  for vs,va,rs,rp in sections:
   if rs:uc.mem_write(0x400000+va,raw[rp:rp+rs])
  uc.mem_map(0x2000000,0x10000);uc.mem_map(0x2200000,0x1000);uc.mem_map(0x3000000,0x10000)
  def get(a):return struct.unpack('<I',uc.mem_read(a,4))[0]
  def put(a,v):uc.mem_write(a,struct.pack('<I',v&0xffffffff))
  base=0x6af3b4;selector=0x3001000;alternate=0x3002000;events=[]
  for i in range(18):put(base+i*4,0x10000000+i*0x1000)
  put(0x6af3fc,object_id);uc.mem_write(0x6af3f4,bytes([flag]));put(0x5e4fec,selector);put(0x5e4fe8,0x3003000)
  effective=5 if mutation==3 else object_id
  for i in range(16):put(selector+i*4,0x70000000+i);put(alternate+i*4,0x80000000+i)
  if found>=0:put(selector+found*4,effective)
  put(0x5b2148,0x2200100)
  sp=0x200fff0;put(sp,0x2200000);uc.reg_write(UC_X86_REG_ESP,sp)
  nonvol={UC_X86_REG_EBX:0x12345678,UC_X86_REG_EBP:0x87654321,UC_X86_REG_ESI:0x89abcdef,UC_X86_REG_EDI:0xfedcba98}
  for reg,value in nonvol.items():uc.reg_write(reg,value)
  def hook(machine,address,length,user):
   if address not in (0x5678f0,0x55ec30,0x59ee30,0x5699f0,0x2200100):return
   stack=machine.reg_read(UC_X86_REG_ESP);argc=3 if address==0x2200100 else (1 if address in (0x59ee30,0x5699f0) else 0)
   args=[get(stack+4+i*4) for i in range(argc)];events.append(dict(target=f'{address:08x}',args=args))
   if address==0x5678f0 and mutation==3:put(0x6af3fc,5)
   if address==0x59ee30 and mutation==1:put(0x5e4fec,alternate)
   if address==0x2200100 and mutation==2:put(0x6af3fc,7)
   machine.reg_write(UC_X86_REG_EAX,1);machine.reg_write(UC_X86_REG_ESP,stack+4+(12 if address==0x2200100 else 0));machine.reg_write(UC_X86_REG_EIP,get(stack))
  uc.hook_add(UC_HOOK_CODE,hook)
  before_slots=bytes(uc.mem_read(base,72));before_selector=bytes(uc.mem_read(selector,64));before_alternate=bytes(uc.mem_read(alternate,64))
  uc.emu_start(0x4a54e0,0x2200000,count=500)
  assert uc.reg_read(UC_X86_REG_EIP)==0x2200000 and uc.reg_read(UC_X86_REG_ESP)==sp+4 and all(uc.reg_read(reg)==value for reg,value in nonvol.items())
  if not flag:
   assert events==[] and bytes(uc.mem_read(base,72))==before_slots and get(0x5e4fe8)==0x3003000
  else:
   expected=['005678f0','0055ec30']+(['0059ee30'] if found>=0 else [])+['005699f0','02200100'];assert [x['target'] for x in events]==expected
   if found>=0:
    assert events[2]['args']==[(-found)&0xffffffff]
    assert get((alternate if mutation==1 else selector)+found*4)==0
    if mutation==1:assert get(selector+found*4)==effective
   assert events[-2]['args']==[effective] and events[-1]['args'][1:]==[0,0x8000]
   assert get(base)==0 and get(base+effective*4)==0 and get(base+(7 if mutation==2 else effective)*4)==0
   assert get(0x5e4fe8)==0x5e3e18
   assert bytes(uc.mem_read(0x6af3f4,1))==(b'\0' if object_id==16 else bytes([flag]))
  cases.append(dict(name=name,events=events,original_object_id=object_id,effective_cached_id=effective,selector_match=found,mutation=mutation,before_slots_hex=before_slots.hex(),after_slots_hex=bytes(uc.mem_read(base,72)).hex(),before_selector_hex=before_selector.hex(),after_selector_hex=bytes(uc.mem_read(selector,64)).hex(),before_alternate_hex=before_alternate.hex(),after_alternate_hex=bytes(uc.mem_read(alternate,64)).hex(),final_context_pointer=f'{get(0x5e4fe8):08x}',esp_delta=4,nonvolatiles_preserved=True))
 evidence=dict(original_sha256=SHA,wrapper_hex=wrapper.hex(),body_hex=body.hex(),indexed_ranges=[x for x in index if x['entry_va'] in targets],original_import=imp[0],physical_pointer_initializers=resources,existing_raw_provider=provider,cutpoint_cases=cases,limits=['External callees and VirtualFree are controlled cutpoints, not algorithm/OS acceptance','Index16 case proves original unmasked address aliasing for controlled input, not actual startup occurrence'])
 save(RUN/'evidence.json',evidence)
 names=['application_heap.cpp','application_heap_init.cpp','application_pool.cpp','application_context_base.cpp','context_effects.cpp']
 inputs=[image,asm_path,index_path,registry_path,imports_path,union_path,ROOT/provider['object'],ROOT/provider['generated_source'],RUN/'evidence.json',Path(__file__),ROOT/'scripts/research/audit-v2-frame-service-290.py',ROOT/'scripts/research/build-v2-compile-corpus.py',ROOT/'scripts/research/v2_shared_manifests.py',ROOT/'scripts/research/v2_proof_cache.py']
 inputs += [ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'/x for x in names]
 inputs += [ROOT/'iterations/v2/001-original-recovery/source/include/porsche'/x for x in ['application_heap.hpp','application_heap_init.hpp','application_pool.hpp','application_context_base.hpp','context_effects.hpp']]
 summary=dict(schema=2,kind='heap-shutdown-binding-state-preflight',original_sha256=SHA,input_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},wrapper='004a54e0',body='0059eb20',original_bytes=164,original_cutpoint_cases=8,canonical_accepted_owners=0,actual_274_provider_vas=['0055ec30'],provider_abi={'005678f0':'cdecl noargs RET0; canonical declaration only','0055ec30':'cdecl noargs RET0; actual rawCOFF provider, returns oldglobalEAX but caller ignores','0059ee30':'cdecl oneDWORD RET0; caller pushes modular NEG selectorindex','005699f0':'cdecl oneDWORD RET0; caller ignores EAX; child masks IDlow4 but parent arenaindex is unmasked','005b2148':'VirtualFree stdcall3DWORD RET12; canonical application_virtual_free has equivalent argument/return boundary but provider remains external'},state_hold=['006af3b4 indexed base is split across canonical primary scalar and other15array; original unmasked index16 overlaps guardDWORD006af3f4','005e4fe8 is writable context pointer reset to address005e3e18; existing canonical getter has no writable owner/setter','005e4fec is writable selector-table pointer initially006af374, read again after queuecallee; existing getter boundaries do not own this pointer cell','005e3e18 default context firstDWORD also holds006af374; original alias between defaultcontext andselector must be retained'],implementation_added=False,storage_added=False,compiler_commands=0,native_commands=0,next_targets=['Recover one canonical selector/context owner for005e4fe8/005e4fec/default005e3e18 using original writers','Reconcile006af3b4 arena indexing with existing scalar/array owners and guard/page/id neighbors before binding parent','005699f0 is72B bounded child over existing16slot heaps;0059ee30 is124B queuecleanup over context state;005678f0 is248B pool shutdown'])
 summary=externalize(ROOT,summary,'input','raw');reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw');save(RUN/'summary.json',summary);save(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),original_bytes=164,cutpoint_cases=8,reader_counts=reader.counts))
 print(json.dumps(dict(passed=True,original_bytes=164,cutpoint_cases=8,implementation='HOLD',compiler_commands=0)))
if __name__=='__main__':main()
