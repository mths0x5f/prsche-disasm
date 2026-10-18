"""Direct original PE oracle for the 25-byte 004898f0 resolver body."""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/291-frame-resolver'
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ECX,UC_X86_REG_EDI,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
PE=0x400000;ARENA=0x03000000;SELF=ARENA+0x1000;OUTPUT=ARENA+0x2008;STACK=0x02000000;EXIT=0x02200000
CASES=[('zero_zero',0,0),('highbit_fullword',0x81234567,0xabcd1234),('all_ones',0xffffffff,0xffffffff),('low_tag_zero',0xfedcba98,0xaaaa0000),('low_tag_high',0x00000001,0x12348000)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 path=ROOT/'local/game/Porsche.exe';raw=path.read_bytes();assert sha(path)=='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
 pe=struct.unpack_from('<I',raw,0x3c)[0];opt=pe+24;n=struct.unpack_from('<H',raw,pe+6)[0];oh=struct.unpack_from('<H',raw,pe+20)[0]
 image,size=struct.unpack_from('<I',raw,opt+28)[0],struct.unpack_from('<I',raw,opt+56)[0];assert image==PE
 sections=[]
 for i in range(n):
  p=opt+oh+i*40;vsize,rva,rsize,roff=struct.unpack_from('<IIII',raw,p+8)
  if rsize:sections.append((rva,roff,rsize))
 results=[]
 for name,word,tag in CASES:
  uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(PE,(size+0xfff)&~0xfff);uc.mem_write(PE,raw[:0x1000])
  for rva,roff,rsize in sections:uc.mem_write(PE+rva,raw[roff:roff+rsize])
  uc.mem_map(ARENA,0x10000);uc.mem_map(STACK,0x20000);uc.mem_map(EXIT,0x1000)
  before=bytes([0xa5]*32);uc.mem_write(OUTPUT-8,before)
  uc.mem_write(SELF+0x14,struct.pack('<I',word))
  sp=STACK+0x1ffe0;uc.mem_write(sp,struct.pack('<III',EXIT,OUTPUT,tag));uc.reg_write(UC_X86_REG_ESP,sp);uc.reg_write(UC_X86_REG_ECX,SELF)
  nonvol={UC_X86_REG_EBX:0x12345678,UC_X86_REG_EBP:0x87654321,UC_X86_REG_ESI:0xfedcba98,UC_X86_REG_EDI:0x89abcdef}
  for reg,value in nonvol.items():uc.reg_write(reg,value)
  uc.emu_start(0x4898f0,EXIT,count=20)
  assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==sp+12
  assert all(uc.reg_read(reg)==value for reg,value in nonvol.items())
  after=bytes(uc.mem_read(OUTPUT-8,32))
  assert after[:8]==before[:8] and after[16:]==before[16:]
  assert after[8:12]==struct.pack('<I',word) and after[12]==0 and after[13]==0xa5 and after[14:16]==struct.pack('<H',tag&0xffff)
  assert uc.reg_read(UC_X86_REG_EAX)==OUTPUT
  results.append(dict(name=name,self_word=word,tag_dword=tag,before_hex=before.hex(),after_hex=after.hex(),eax=OUTPUT,esp_delta=12,nonvolatile_preserved=True))
 RUN.mkdir(parents=True,exist_ok=True)
 (RUN/'original-oracles.json').write_bytes((json.dumps(dict(schema=1,original_sha256=sha(path),body_va='004898f0',cases=results),indent=2)+'\n').encode())
 print(f'{len(results)} original PE resolver cases')
if __name__=='__main__':main()
