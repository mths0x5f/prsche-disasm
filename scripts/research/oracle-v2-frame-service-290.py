"""Execute the two exact original PE bodies with controlled callee cutpoints."""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
PE=0x400000;ARENA=0x03000000;SERVICE=ARENA+0x1000;ROOTPTR=ARENA+0x1100
SENTINEL=ARENA+0x2000;ALT_SENTINEL=ARENA+0x2100;NODES=[ARENA+0x3000,ARENA+0x3100]
RESOLVERS=[ARENA+0x4000,ARENA+0x4100];ACTIONS=[ARENA+0x5000,ARENA+0x5100]
TAIL=ARENA+0x6000;STACK=0x02000000;EXIT=0x02200000
RUN=ROOT/'iterations/v2/001-original-recovery/runs/290-frame-service-cluster'
CASES=[dict(name='empty',count=0,actions=[],tail=False,switch=False),
       dict(name='empty_tail',count=0,actions=[],tail=True,switch=False),
       dict(name='single_null_action',count=1,actions=[False],tail=False,switch=False),
       dict(name='single_action_tail',count=1,actions=[True],tail=True,switch=False),
       dict(name='two_mixed',count=2,actions=[True,False],tail=True,switch=False),
       dict(name='sentinel_reloaded',count=1,actions=[True],tail=False,switch=True)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def u32(v):return struct.pack('<I',v)
def main():
 raw=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()=='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
 peoff=struct.unpack_from('<I',raw,0x3c)[0];n=struct.unpack_from('<H',raw,peoff+6)[0];opt=peoff+24;oh=struct.unpack_from('<H',raw,peoff+20)[0]
 image=struct.unpack_from('<I',raw,opt+28)[0];size=struct.unpack_from('<I',raw,opt+56)[0];assert image==PE
 sections=[]
 for i in range(n):
  p=opt+oh+i*40;vsize,rva,rsize,roff=struct.unpack_from('<IIII',raw,p+8)
  if rsize:sections.append((rva,roff,rsize))
 results=[]
 for case in CASES:
  uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(PE,(size+0xfff)&~0xfff);uc.mem_write(PE,raw[:0x1000])
  for rva,roff,rsize in sections:uc.mem_write(PE+rva,raw[roff:roff+rsize])
  uc.mem_map(ARENA,0x10000);uc.mem_map(STACK,0x20000);uc.mem_map(EXIT,0x1000)
  def put(a,v):uc.mem_write(a,u32(v))
  def get(a):return struct.unpack('<I',uc.mem_read(a,4))[0]
  put(0x628960,SERVICE);put(SERVICE+0x14,ROOTPTR);put(SERVICE+0x1c,TAIL if case['tail'] else 0)
  put(ROOTPTR,SENTINEL);put(SENTINEL+8,NODES[0] if case['count'] else SENTINEL)
  put(ALT_SENTINEL+8,ALT_SENTINEL)
  for i in range(case['count']):
   put(NODES[i]+0x14,RESOLVERS[i]);put(NODES[i]+4,NODES[i+1] if i+1<case['count'] else (ALT_SENTINEL if case['switch'] else SENTINEL))
   put(RESOLVERS[i]+0x14,ACTIONS[i] if case['actions'][i] else 0)
  sp=STACK+0x1fff0;put(sp,EXIT);uc.reg_write(UC_X86_REG_ESP,sp)
  events=[];temps=[]
  def hook(uc,address,size,user):
   if address==EXIT:uc.emu_stop();return
   if address==0x4898f0:
    ecx=uc.reg_read(UC_X86_REG_ECX);sp=uc.reg_read(UC_X86_REG_ESP);temp=get(sp+4)
    assert ecx in RESOLVERS and get(sp+8)==0
    events.append(['resolve',RESOLVERS.index(ecx)]);temps.append(temp);return
   if address in (0x476170,0x423840,0x482e50):
    ecx=uc.reg_read(UC_X86_REG_ECX);sp=uc.reg_read(UC_X86_REG_ESP)
    if address==0x476170:
     assert ecx in ACTIONS;events.append(['action',ACTIONS.index(ecx)])
    elif address==0x423840:
     current=get(ecx);assert current in NODES
     events.append(['advance',NODES.index(current)]);put(ecx,get(current+4))
     if case['switch']:put(ROOTPTR,ALT_SENTINEL)
    else:
     assert ecx==TAIL;events.append(['tail',0])
    uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
  uc.hook_add(UC_HOOK_CODE,hook)
  uc.emu_start(0x471b60,EXIT,count=300)
  assert uc.reg_read(UC_X86_REG_EIP)==EXIT
  assert uc.reg_read(UC_X86_REG_ESP)==sp+4
  assert len(temps)==case['count'] and len(set(temps))<=1
  results.append({**case,'events':events,'esp_delta':4,'original_entry':'00471b60'})
 RUN.mkdir(parents=True,exist_ok=True)
 path=RUN/'original-oracles.json';path.write_text(json.dumps({'schema':1,'original_sha256':sha(ROOT/'local/game/Porsche.exe'),'cases':results},indent=2)+'\n',encoding='utf8')
 print(f'{len(results)} original PE oracle cases')
if __name__=='__main__':main()
