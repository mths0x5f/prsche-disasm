"""Audit the frame root cell and test the original neighboring copy cutpoint."""
import hashlib,json,re,struct,sys
from pathlib import Path
from v2_shared_manifests import externalize,ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/296-frame-root-state'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE=0x400000;CELL=0x628960
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EFLAGS,UC_X86_REG_EIP

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
def main():
 RUN.mkdir(parents=True,exist_ok=True)
 assert not (RUN/'summary.json').exists(),'Completed trace is immutable'
 original=ROOT/'local/game/Porsche.exe';raw=original.read_bytes();assert sha(original)==SHA
 pe=struct.unpack_from('<I',raw,60)[0];op=pe+24
 n=struct.unpack_from('<H',raw,pe+6)[0];oh=struct.unpack_from('<H',raw,pe+20)[0]
 sections=[]
 for i in range(n):
  p=op+oh+i*40;vs,va,rs,rp=struct.unpack_from('<IIII',raw,p+8)
  sections.append(dict(name=raw[p:p+8].split(b'\0')[0].decode(),virtual_size=vs,rva=va,raw_size=rs,raw_pointer=rp,flags=struct.unpack_from('<I',raw,p+36)[0]))
 def physical(va):
  s=next(s for s in sections if BASE+s['rva']<=va<BASE+s['rva']+max(s['virtual_size'],s['raw_size']))
  d=va-BASE-s['rva'];return s['raw_pointer']+d if d<s['raw_size'] else None
 def loaded(va,count):return bytes(raw[physical(v)] if physical(v) is not None else 0 for v in range(va,va+count))
 section=next(s for s in sections if BASE+s['rva']<=CELL<BASE+s['rva']+s['virtual_size'])
 assert section['flags']&0x80000000 and physical(CELL) is None
 assert loaded(CELL,4)==b'\0'*4
 rv,sz=struct.unpack_from('<II',raw,op+96+5*8);pos=physical(BASE+rv);end=pos+sz
 highlow=[]
 while pos<end:
  page,size=struct.unpack_from('<II',raw,pos);assert size>=8
  for q in range(pos+8,pos+size,2):
   token=struct.unpack_from('<H',raw,q)[0]
   if token>>12!=3:continue
   site=BASE+page+(token&4095);off=physical(site)
   value=struct.unpack_from('<I',raw,off)[0]
   if CELL-0x20<=value<=CELL+4:highlow.append(dict(site_va=f'{site:08x}',target_va=f'{value:08x}'))
  pos+=size
 asm_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm'
 instructions=[];owner=None
 for line in asm_path.read_text().splitlines():
  if line.startswith('; FUNCTION '):owner=line.split()[2]
  m=re.match(r'([0-9a-f]{8})  ([0-9a-f]+)  (.*)',line)
  if m:instructions.append(dict(va=m[1],hex=m[2],text=m[3],owner=owner))
 direct=[x for x in instructions if '0x00628960' in x['text']]
 for x in direct:
  assert 'dword ptr [0x00628960]' in x['text'] or '[0x00628960]' in x['text']
  va=int(x['va'],16);assert loaded(va,len(bytes.fromhex(x['hex'])))==bytes.fromhex(x['hex'])
 root_reloc=[x for x in highlow if x['target_va']=='00628960']
 for x in root_reloc:
  site=int(x['site_va'],16)
  x['indexed_instructions']=[i['va'] for i in direct if int(i['va'],16)<=site<int(i['va'],16)+len(bytes.fromhex(i['hex']))]
 assert len(root_reloc)==len(direct) and all(len(x['indexed_instructions'])==1 for x in root_reloc)
 raw_patterns=[];pattern=struct.pack('<I',CELL);offset=0
 while True:
  offset=raw.find(pattern,offset)
  if offset<0:break
  s=next((s for s in sections if s['raw_pointer']<=offset<s['raw_pointer']+s['raw_size']),None)
  raw_patterns.append(dict(file_offset=offset,va=f"{BASE+s['rva']+offset-s['raw_pointer']:08x}" if s else None));offset+=1
 assert {x['va'] for x in raw_patterns}=={x['site_va'] for x in root_reloc}
 registry=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'
 accepted=json.loads(registry.read_bytes())['functions']
 owners=[x for x in accepted if x['entry_va'] in ('00471b70','004874a0','00471c40')]
 copy_cases=[];image_size=struct.unpack_from('<I',raw,op+56)[0]
 for length in (0,31,32,35,40):
  uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,(image_size+4095)&~4095)
  for s in sections:
   if s['raw_size']:uc.mem_write(BASE+s['rva'],raw[s['raw_pointer']:s['raw_pointer']+s['raw_size']])
  uc.mem_map(0x2000000,0x10000);uc.reg_write(UC_X86_REG_ESP,0x200fff0);uc.reg_write(UC_X86_REG_EFLAGS,2)
  uc.mem_write(0x657444,b'X'*length+b'\0');before=b'\xa5'*48;uc.mem_write(0x628940,before)
  uc.emu_start(0x471b70,0x471b99,count=300)
  assert uc.reg_read(UC_X86_REG_EIP)==0x471b99
  after=bytes(uc.mem_read(0x628940,48));assert after[:length+1]==b'X'*length+b'\0' and after[length+1:]==before[length+1:]
  copy_cases.append(dict(source_length=length,cutpoint_va='00471b99',destination_va='00628940',before_hex=before.hex(),after_hex=after.hex(),root_bytes_after_hex=after[32:36].hex(),root_changed=after[32:36]!=before[32:36]))
 assert [x['root_changed'] for x in copy_cases]==[False,False,True,True,True]
 evidence=dict(section=section,root_initial=dict(hex='00000000',physical_file_bytes=False,reason='PE loader zero-filled writable virtual tail'),direct_consumers=direct,nearby_highlow=highlow,raw_byte_pattern_navigation=raw_patterns,accepted_function_owners=owners,copy_cutpoint_cases=copy_cases)
 write(RUN/'evidence.json',evidence)
 pins={}
 for p in [original,asm_path,registry,ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'scripts/research/v2_shared_manifests.py',ROOT/'scripts/research/v2_proof_cache.py',Path(__file__),RUN/'evidence.json',ROOT/'iterations/v2/001-original-recovery/runs/290-frame-service-cluster/frame_service_290.hpp']:
  pins[p.relative_to(ROOT).as_posix()]=sha(p)
 report=dict(schema=2,kind='frame-root-storage-trace',original_sha256=SHA,cell_va='00628960',direct_footprint_bytes=4,initial_hex='00000000',direct_consumer_count=len(direct),direct_HIGHLOW_count=len(root_reloc),interior_HIGHLOW_count=sum(CELL<int(x['target_va'],16)<CELL+4 for x in highlow),input_sha256=pins,storage_definition_added=False,storage_standalone_approved=False,native_commands=0,compiler_commands=0,original_copy_cutpoint_cases=len(copy_cases),init_chain=['00471b70:0059ef90(size=0x3c)','00471ba9:004874a0(this=allocation)','00471bae:00628960=EAX; failure00471bb5 stores0'],cleanup_chain=['00471c4b reads root','00471c5a calls00487590','00471c60 frees via0059f050','00471c6d clears root'],hold='Unbounded REP copy from mutable00657444 to00628940 can cross root32bytes later; no <=31 source-length invariant proven',next_target='Trace00657444 writers/005d2ac8 registration consumer; prove <=31 invariant or recover one shared original-layout storage owner covering00628940/root00628960/00628964',limits=['Cutpoints use controlled strings and prove possible memory effects, not real-game occurrence','HIGHLOW and raw byte patterns are navigation, not whole-program alias exclusion','No pointee allocation, initializer algorithm, or game behavior implemented'])
 report=externalize(ROOT,report,'input','raw');reader=ManifestReader(ROOT);reader.verify(report,expected_hash_mode='raw');write(RUN/'summary.json',report)
 write(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),reader_counts=reader.counts,root_direct_refs=len(direct),original_copy_cutpoints=5,standalone_storage='HOLD'))
 print(json.dumps(dict(direct=len(direct),root_highlow=len(root_reloc),copy_cases=5,storage='HOLD')))
if __name__=='__main__':main()
