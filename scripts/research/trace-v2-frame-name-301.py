"""Bounded original trace of TRACK_NAME registration and its string writer."""
import hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
from v2_shared_manifests import externalize,ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/301-frame-name-bound'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EFLAGS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
def main():
 RUN.mkdir(parents=True,exist_ok=True);assert not (RUN/'summary.json').exists(),'Completed packet immutable'
 original=ROOT/'local/game/Porsche.exe';raw=original.read_bytes();assert sha(original)==SHA
 asmfile=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm'
 instructions=[];owner=None
 for line in asmfile.read_text().splitlines():
  if line.startswith('; FUNCTION '):owner=line.split()[2]
  m=re.match(r'([0-9a-f]{8})  ([0-9a-f]+)  (.*)',line)
  if m:instructions.append(dict(va=m[1],hex=m[2],text=m[3],indexed_owner=owner))
 spans=[(0x439e53,0x439e72),(0x4fbf30,0x4fbf6b),(0x4b29a1,0x4b29bf),(0x4b4b80,0x4b4cca),(0x5a0fbf,0x5a1010),(0x471b70,0x471b97),(0x4155d1,0x4155ed),(0x48f998,0x48f9cb)]
 selected=[x for x in instructions if any(a<=int(x['va'],16)<=b for a,b in spans)]
 spec=importlib.util.spec_from_file_location('pe301',ROOT/'scripts/research/audit-v2-frame-service-290.py');pe_read=importlib.util.module_from_spec(spec);spec.loader.exec_module(pe_read)
 for x in selected:assert pe_read.pe_read(raw,int(x['va'],16),len(bytes.fromhex(x['hex'])))==bytes.fromhex(x['hex'])
 pe=struct.unpack_from('<I',raw,60)[0];op=pe+24;n=struct.unpack_from('<H',raw,pe+6)[0];oh=struct.unpack_from('<H',raw,pe+20)[0];image_size=struct.unpack_from('<I',raw,op+56)[0]
 sections=[struct.unpack_from('<IIII',raw,op+oh+i*40+8) for i in range(n)]
 def fresh():
  uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(0x400000,(image_size+4095)&~4095)
  for vs,va,rs,rp in sections:
   if rs:uc.mem_write(0x400000+va,raw[rp:rp+rs])
  uc.mem_map(0x2000000,0x10000);uc.mem_map(0x2200000,0x1000);uc.mem_map(0x3000000,0x10000)
  uc.reg_write(UC_X86_REG_ESP,0x200fff0);uc.reg_write(UC_X86_REG_EFLAGS,2);return uc
 initialization=[x for x in instructions if 0x4b0ff0<=int(x['va'],16)<=0x4b4b75]
 assert len(initialization)==1637 and all(x['text'].split()[0] in ('MOV','XOR','RET') for x in initialization)
 init_bytes=pe_read.pe_read(raw,0x4b0ff0,0x4b4b76-0x4b0ff0)
 # No function-entry acceptance is inferred: this straight-line store span is
 # navigated under the index's broad004b0fa0 range and executed as a cutpoint.
 cases=[]
 for length in (31,32,40,63):
  uc=fresh();uc.emu_start(0x4b0ff0,0x4b4b75,count=2000)
  assert uc.reg_read(UC_X86_REG_EIP)==0x4b4b75
  registration=bytes(uc.mem_read(0x5d2ac4,12));assert struct.unpack('<III',registration)==(0x10f,0x657444,0x5d5274)
  cursor=0x5d1e40;matches=[]
  while True:
   key,ptr,label=struct.unpack('<III',uc.mem_read(cursor,12))
   if not key:break
   if key==0x10f:matches.append((cursor,ptr,label))
   cursor+=12;assert cursor<0x5d3a00
  assert matches==[(0x5d2ac4,0x657444,0x5d5274)]
  payload=struct.pack('<I',0x10f)+b'Q'*length+b'\0';uc.mem_write(0x3000000,payload)
  uc.mem_write(0x657444,b'\xa5'*64);sp=0x200fff0
  uc.mem_write(sp,struct.pack('<II',0x2200000,0x3000000));uc.reg_write(UC_X86_REG_ESP,sp)
  uc.emu_start(0x4b4b80,0x2200000,count=12000)
  assert uc.reg_read(UC_X86_REG_EIP)==0x2200000 and uc.reg_read(UC_X86_REG_ESP)==sp+4
  written=bytes(uc.mem_read(0x657444,64));assert written==b'Q'*length+b'\0'+b'\xa5'*(63-length)
  before=b'\xa5'*80;uc.mem_write(0x628940,before);uc.reg_write(UC_X86_REG_ESP,sp)
  uc.emu_start(0x471b70,0x471b99,count=500)
  after=bytes(uc.mem_read(0x628940,80));assert after==b'Q'*length+b'\0'+before[length+1:]
  cases.append(dict(source_length=length,packet_hex=payload.hex(),registration_hex=registration.hex(),source_after_hex=written.hex(),destination_after_hex=after.hex(),root_after_hex=after[32:36].hex(),root_changed=after[32:36]!=before[32:36],following_buffer_changed=after[36:]!=before[36:]))
 assert [x['root_changed'] for x in cases]==[False,True,True,True]
 uc=fresh();sp=0x200fff0;uc.mem_write(sp,struct.pack('<IIII',0x2200000,0x657444,0x5d5274,0));uc.reg_write(UC_X86_REG_ESP,sp)
 uc.emu_start(0x5a0fbf,0x5a0fe8,count=30);assert uc.reg_read(UC_X86_REG_EIP)==0x5a0fe8
 format_sp=uc.reg_read(UC_X86_REG_ESP);stream,fmt,args=struct.unpack('<III',uc.mem_read(format_sp,12))
 stream_bytes=bytes(uc.mem_read(stream,32));assert struct.unpack_from('<I',stream_bytes,4)[0]==0x7fffffff
 label=pe_read.pe_read(raw,0x5d5274,11);assert label==b'TRACK_NAME\0'
 evidence=dict(original_sha256=SHA,instructions=selected,registration=dict(record_va='005d2ac4',id='0000010f',pointer_cell='005d2ac8',destination='00657444',label_va='005d5274',label_hex=label.hex()),initializer_cutpoint=dict(start='004b0ff0',stop='004b4b75',instruction_count=1637,span_sha256=hashlib.sha256(init_bytes).hexdigest(),entry_proved=False),consumer_cases=cases,format_wrapper_cutpoint=dict(start='005a0fbf',stop='005a0fe8',stream_hex=stream_bytes.hex(),remaining_capacity=0x7fffffff,format_va=f'{fmt:08x}',format_core='005a4371'),format_writer=dict(site='00439e68',owner='00439bd0',destination='00657444',format_source='004fbf30 result+8',lookup='signed16 item identifier through pointer vector00691d00; no length check in60Blookup'),limits=['Controlled valid packets prove writer/copy effects, not that shipped data or a full game session supplies these lengths','No bound on every upstream packet constructor or resource string is claimed'])
 save(RUN/'evidence.json',evidence)
 pins={}
 for p in (original,asmfile,Path(__file__),ROOT/'scripts/research/audit-v2-frame-service-290.py',ROOT/'scripts/research/v2_shared_manifests.py',ROOT/'scripts/research/v2_proof_cache.py',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',RUN/'evidence.json',RUN.parent/'296-frame-root-state/summary.json'):
  pins[p.relative_to(ROOT).as_posix()]=sha(p)
 summary=dict(schema=2,kind='frame-name-bound-trace',original_sha256=SHA,input_sha256=pins,upper_bound_31_proved=False,storage_definition_added=False,compiler_commands=0,native_commands=0,original_packet_copy_cases=4,original_formatter_cutpoints=1,hold='Registered TRACK_NAME consumer copies inlineNUL string without a31byte bound; lengths32/40/63 survive into00657444 then cross root in original initialization copy',shared_layout_requirements=['00628940 destination must retain root00628960 at offset32 and following00628964 at offset36 for any allowed crossing write','Final storage extent still requires an upstream allowed-length bound; no arbitrary allocation or entire-data-section owner is justified','Original root constructor/store and cleanup remain separate algorithms; shared layout does not implement them'],next_target='If continuing length proof: inspect payload producers for004155da/0048f9b8 and resources underlying00691d00 item+8; do not infer bounds from consumer or formatting wrapper')
 summary=externalize(ROOT,summary,'input','raw');reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw');save(RUN/'summary.json',summary)
 save(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),packet_cases=4,formatter_cutpoints=1,repo_inputs=len(pins),reader_counts=reader.counts))
 print(json.dumps(dict(passed=True,packet_cases=4,formatter_capacity=0x7fffffff,bound31=False,storage='HOLD')))
if __name__=='__main__':main()
