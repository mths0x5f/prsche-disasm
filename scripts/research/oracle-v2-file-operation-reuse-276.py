"""Original PE x86 cutpoints for the two accepted file-operation bodies."""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/276-file-operation-reuse'
OUT=ROOT/'local/experiments/v2-file-operation-reuse-276'
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
PE=0x400000;ARENA=0x03000000;DEV=ARENA+0x1000;OP=ARENA+0x2000;CONTEXT=ARENA+0x3000;EVENT=ARENA+0x4000;STACK=0x02000000;EXIT=0x02200000
TARGET={'queue':0x568200,'allocate':0x5682a0}
DEPEND={'pop':0x580790,'sorted':0x580850,'event':0x55fb30,'start':0x568390,'lock':0x580ea0,'unlock':0x580ec0,'diagnostic':EXIT+0x100}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 pre=json.loads((RUN/'preflight.json').read_bytes());raw=(ROOT/'local/game/Porsche.exe').read_bytes()
 assert sha(ROOT/'local/game/Porsche.exe')==pre['original_sha256']
 peoff=struct.unpack_from('<I',raw,0x3c)[0];num=struct.unpack_from('<H',raw,peoff+6)[0];oh=struct.unpack_from('<H',raw,peoff+20)[0]
 sections=[]
 for i in range(num):
  p=peoff+24+oh+i*40;vsize,rva,rsize,roff=struct.unpack_from('<IIII',raw,p+8)
  if rsize:sections.append((rva,roff,rsize))
 cases=[dict(name='queue_high_id',kind='queue',index=1,serial=3,initialized=1,op_id=0xdeadbee1,pop=True),dict(name='allocate_wrap',kind='allocate',index=1,serial=0xffffff,initialized=1,op_id=0xcccccccc,pop=True),dict(name='allocate_start',kind='allocate',index=0,serial=2,initialized=0,op_id=0xcccccccc,pop=True),dict(name='allocate_empty',kind='allocate',index=1,serial=9,initialized=1,op_id=0xcccccccc,pop=False)]
 outputs=[]
 for case in cases:
  uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(PE,0x300000)
  for rva,roff,size in sections:uc.mem_write(PE+rva,raw[roff:roff+size])
  for addr,size in ((ARENA,0x10000),(STACK,0x10000),(EXIT,0x1000)):uc.mem_map(addr,size)
  uc.mem_write(DEV,b'\xcc'*(2*0x70));uc.mem_write(OP,b'\xcc'*48)
  def put(addr,value):uc.mem_write(addr,struct.pack('<I',value&0xffffffff))
  def get(addr):return struct.unpack('<I',uc.mem_read(addr,4))[0]
  put(0x6a5c7c,DEV);put(0x5debf0,DEPEND['diagnostic'])
  d=DEV+case['index']*0x70
  put(d,case['initialized']);put(d+0x68,case['serial']);put(d+0x5c,EVENT);put(OP+4,case['op_id'])
  before=dict(op=bytes(uc.mem_read(OP,48)).hex(),device=bytes(uc.mem_read(d,0x70)).hex())
  events=[]
  def hook(machine,address,size,user):
   if address==EXIT:uc.emu_stop();return
   name=next((k for k,v in DEPEND.items() if v==address),None)
   if name is None:
    assert PE<=address<PE+0x300000,('unexpected code',hex(address));return
   esp=uc.reg_read(UC_X86_REG_ESP)
   ret=get(esp);a=get(esp+4);value=0
   if name=='pop':assert a==0x6a5c58;value=OP if case['pop'] else 0;events.append(['pop'])
   elif name=='sorted':assert a==d+0x24 and get(esp+8)==OP;events.append(['sorted',a,OP])
   elif name=='event':assert a==EVENT;events.append(['event',a]);value=1
   elif name=='start':assert a==case['index'];put(d,1);events.append(['start',a])
   elif name=='lock':assert a==d+0x24;value=0x1234abcd;events.append(['lock',a])
   elif name=='unlock':assert a==d+0x24 and get(esp+8)==0x1234abcd;events.append(['unlock',a,0x1234abcd])
   elif name=='diagnostic':
    msg=a;buf=bytearray()
    while (ch:=uc.mem_read(msg+len(buf),1)[0])!=0:buf.append(ch)
    events.append(['diagnostic',buf.decode('ascii')])
   uc.reg_write(UC_X86_REG_EAX,value);uc.reg_write(UC_X86_REG_ESP,esp+4);uc.reg_write(UC_X86_REG_EIP,ret)
  uc.hook_add(UC_HOOK_CODE,hook)
  esp=STACK+0xff00
  args=[OP] if case['kind']=='queue' else [7,0x000000d7,CONTEXT,case['index']]
  uc.mem_write(esp,struct.pack('<'+'I'*(len(args)+1),EXIT,*args))
  uc.reg_write(UC_X86_REG_ESP,esp)
  uc.emu_start(TARGET[case['kind']],EXIT,count=10000)
  assert uc.reg_read(UC_X86_REG_EIP)==EXIT
  after=dict(op=bytes(uc.mem_read(OP,48)).hex(),device=bytes(uc.mem_read(d,0x70)).hex())
  outputs.append(dict(**case,before=before,after=after,eax=uc.reg_read(UC_X86_REG_EAX),events=events,diagnostic_file=struct.unpack('<I',uc.mem_read(0x5deb74,4))[0],diagnostic_line=get(0x5deb78)))
 OUT.mkdir(parents=True,exist_ok=True)
 report=dict(schema=1,kind='original-x86-file-operation-cutpoints',original_sha256=pre['original_sha256'],preflight_sha256=sha(RUN/'preflight.json'),oracle_script_sha256=sha(__file__),cases=outputs,boundaries=list(DEPEND),limits=['Controlled original dependency endpoints, not OS scheduling or file I/O','No original caller execution'])
 (OUT/'original-oracles.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(cases=len(outputs),entrypoints=2,events=[len(x['events']) for x in outputs])))
if __name__=='__main__':main()
