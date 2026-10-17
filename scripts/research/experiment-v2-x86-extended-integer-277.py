"""Native synthetic proof of bounded277 extensions; unchanged257 helpers reused."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/277-x86-extended-integer'
OUT=ROOT/'local/experiments/v2-x86-extended-integer-277'
BASE_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def fragments():
    specs=[('movsx-eax-ah','0fbec4c3','movsx eax,ah',8),('movzx-eax-ah','0fb6c4c3','movzx eax,ah',8),
      ('movsx-eax-dx','0fbfc2c3','movsx eax,dx',16),('movzx-eax-dx','0fb7c2c3','movzx eax,dx',16),
      ('movsx-ax-cl','660fbec1c3','movsx ax,cl',8),('movzx-ax-cl','660fb6c1c3','movzx ax,cl',8),
      ('movsx-ecx-memory8','0fbe0ac3','movsx ecx,byte ptr[edx]',8),('movzx-ecx-memory8','0fb60ac3','movzx ecx,byte ptr[edx]',8),
      ('movsx-cx-memory8','660fbe0ac3','movsx cx,byte ptr[edx]',8),('movzx-cx-memory8','660fb60ac3','movzx cx,byte ptr[edx]',8),
      ('movsx-ecx-memory16','0fbf0ac3','movsx ecx,word ptr[edx]',16),('movzx-ecx-memory16','0fb70ac3','movzx ecx,word ptr[edx]',16),
      ('movsx-eax-al','0fbec0c3','movsx eax,al',8),('movzx-eax-al','0fb6c0c3','movzx eax,al',8),
      ('or-ah-cl','0ae1c3','or ah,cl',8),('or-ax-cx','660bc1c3','or ax,cx',16),('or-eax-ecx','0bc1c3','or eax,ecx',32),
      ('not-ah','f6d4c3','not ah',8),('not-ax','66f7d0c3','not ax',16),('not-eax','f7d0c3','not eax',32)]
    rows=[dict(id=i,name=n,hex=h,asm=a+'\n ret',bits=b,entry=f'{0x11001000+i*0x100:08x}') for i,(n,h,a,b) in enumerate(specs)]
    for m,opcode in [('jg','7f'),('jle','7e'),('ja','77'),('jbe','76'),('jb','72'),('jae','73')]:
        i=len(rows);label='hit277_'+str(i)
        rows.append(dict(id=i,name=m,hex=opcode+'06b8df9b5713c3b821436587c3',asm=m+' '+label+'\n mov eax,0x13579bdf\n ret\n'+label+':\n mov eax,0x87654321\n ret',bits=0,entry=f'{0x11001000+i*0x100:08x}'))
    assert len(rows)==26 and sum(len(bytes.fromhex(r['hex'])) for r in rows)==164
    return rows


TAIL=r'''
// ORACLES277
void*targets277[26]={TARGETS277};
U edge277(U n,U bits){U mask=bits==8?0xffu:bits==16?0xffffu:0xffffffffu,sign=(mask>>1)+1u;
 switch(n){case 0:return 0;case 1:return 1;case 2:return mask;case 3:return sign-1u;case 4:return sign;case 5:return sign+1u;case 6:return mask-1u;default:return 2;}}
void seed_registers277(U seed){for(U i=0;i<8;++i)seed277[i]=(0x13579bdfu*(i+1u))^(0x80000001u*seed);}
void compare277(U id,U flags){
 U sp=reinterpret_cast<U>(stack277+128),capture=reinterpret_cast<U>(&capture277),entry=0x11001000u+id*0x100u;
 for(U i=0;i<256;++i)stack277[i]=static_cast<B>(i*31u+id*17u+flags*47u);
 write257(sp,4u,capture);for(U i=0;i<256;++i)before277[i]=stack277[i];
 for(U i=0;i<32;++i)before_mem277[i]=memory277[i];
 seed277[4]=sp;seed_flags277=0x202u|(flags&1u)|((flags&2u)<<5u)|((flags&4u)<<5u)|((flags&8u)<<8u);
 target277=reinterpret_cast<U>(targets277[id]);guest_sp277=sp;native_edge277();
 for(U i=0;i<256;++i)native_stack277[i]=stack277[i];
 U native_return=0;memcpy(&native_return,native_stack277+128,4u);require277(native_return==capture);
 memcpy(native_stack277+128,&halt277,4u);
 for(U i=0;i<32;++i)require277(memory277[i]==before_mem277[i]);
 for(U i=0;i<256;++i)stack277[i]=before277[i];write257(sp,4u,halt277);
 Machine257 state={};for(U i=0;i<8;++i)state.r[i]=seed277[i];state.flags=seed_flags277;state.pc=entry;state.stop=Stop257::Running;state.budget=64u;
 dispatch257(state,entry);
 for(U i=0;i<8;++i)require277(state.r[i]==seen277[i]);
 require277(((state.flags^seen_flags277)&0x8c1u)==0 && state.r[4]==sp+4u && state.pc==halt277 && state.stop==Stop257::Returned);
 if(id<14u || id>=17u)require277(((state.flags^seed_flags277)&0x8c1u)==0);
 else require277((state.flags&0x801u)==0);
 for(U i=0;i<32;++i)require277(memory277[i]==before_mem277[i]);
 for(U i=0;i<256;++i)require277(stack277[i]==native_stack277[i]);++cases277;
}
void text277(char*&p,const char*s){while(*s)*p++=*s++;}
void decimal277(char*&p,U v){char digits[10];U n=0;do{digits[n++]=static_cast<char>('0'+v%10u);v/=10u;}while(v);while(n)*p++=digits[--n];}
void result277(){
 char text[512];char*p=text;text277(p,"{\n  \"provenance\": \"syntheticCPUfixture\",\n  \"native_game_execution\": false,\n  \"cases\": ");decimal277(p,cases277);
 text277(p,",\n  \"failures\": ");decimal277(p,failures277);text277(p,",\n  \"extensions\": ");decimal277(p,extensions277);
 text277(p,",\n  \"logic\": ");decimal277(p,logic277);text277(p,",\n  \"conditions\": ");decimal277(p,conditions277);text277(p,"\n}\n");
 void*h=CreateFileA("fixture-result.json",0x40000000u,0,0,2,0x80u,0);U written=0;
 require277(h!=reinterpret_cast<void*>(0xffffffffu));if(h!=reinterpret_cast<void*>(0xffffffffu)){require277(WriteFile(h,text,static_cast<U>(p-text),&written,0)!=0);require277(written==static_cast<U>(p-text));require277(CloseHandle(h)!=0);}
}
extern "C" void __cdecl entry(){
 U bits[20]={8,8,16,16,8,8,8,8,8,8,16,16,8,8,8,16,32,8,16,32};
 for(U id=0;id<14;++id)for(U value=0;value<8;++value)for(U flags=0;flags<16;++flags)for(U seed=0;seed<4;++seed)
 for(U align=0;align<((id>=6u && id<=11u)?4u:1u);++align){
  seed_registers277(seed);U v=edge277(value,bits[id]);
  for(U i=0;i<32;++i)memory277[i]=static_cast<B>(i*59u+seed*31u);
  if(id<2u)seed277[0]=(seed277[0]&0xffff00ffu)|(v<<8u);
  else if(id<4u)seed277[2]=(seed277[2]&0xffff0000u)|v;
  else if(id<6u)seed277[1]=(seed277[1]&0xffffff00u)|v;
  else if(id<=11u){seed277[2]=reinterpret_cast<U>(memory277+align);write257(seed277[2],bits[id]/8u,v);}
  else seed277[0]=(seed277[0]&0xffffff00u)|v;
  compare277(id,flags);++extensions277;
 }
 for(U id=14;id<20;++id)for(U a=0;a<8;++a)for(U b=0;b<(id<17u?8u:1u);++b)
 for(U flags=0;flags<16;++flags)for(U seed=0;seed<4;++seed){
  seed_registers277(seed);U width=bits[id],shift=width==8u?8u:0u,mask=width==8u?0xffu:width==16u?0xffffu:0xffffffffu;
  seed277[0]=(seed277[0]&~(mask<<shift))|(edge277(a,width)<<shift);seed277[1]=(seed277[1]&~mask)|edge277(b,width);
  compare277(id,flags);++logic277;
 }
 for(U id=20;id<26;++id)for(U flags=0;flags<16;++flags)for(U seed=0;seed<8;++seed){seed_registers277(seed);compare277(id,flags);++conditions277;}
 require277(cases277==30976u && extensions277==16384u && logic277==13824u && conditions277==768u);
 result277();ExitProcess(failures277?1u:0u);
}
'''


def fixture(rows,base):
    head=base.FIXTURE.split('// SYNTHETIC_ORACLES')[0].replace('262','277')
    head=head.replace('U failures277,cases277,arithmetic277,views277,stack_cases277,indirect277,mapped_slots277;','U failures277,cases277,extensions277,logic277,conditions277;')
    head=head.replace('const U halt277=0x0badf00du,leaf_pc277=0x10002200u;','const U halt277=0x0badf00du;\nB memory277[32],before_mem277[32];')
    before='bool valid277(U a,U n){U base=reinterpret_cast<U>(stack277);return (n==1u||n==2u||n==4u)&&a>=base&&a-base<=256u-n;}'
    after='bool valid277(U a,U n){U base=reinterpret_cast<U>(stack277),mem=reinterpret_cast<U>(memory277);return (n==1u||n==2u||n==4u)&&((a>=base&&a-base<=256u-n)||(a>=mem&&a-mem<=32u-n));}'
    assert head.count(before)==1;head=head.replace(before,after)
    oracles='\n'.join('__declspec(naked) void oracle277_'+str(r['id'])+'(){__asm{\n '+r['asm']+'\n}}' for r in rows)
    targets=','.join('reinterpret_cast<void*>(&oracle277_'+str(r['id'])+')' for r in rows)
    return head+TAIL.replace('// ORACLES277',oracles).replace('TARGETS277',targets)


def main():
    args=argparse.ArgumentParser();args.add_argument('--prepare-only',action='store_true');args.add_argument('--finalize-existing',action='store_true');a=args.parse_args()
    assert not(RUN/'summary.json').exists(),'completed277 immutable'
    if a.finalize_existing:assert(OUT/'native-001.execution.json').exists(),'no rerun in metadata finalization'
    else:assert not(OUT/'compile-001.execution.json').exists(),'native batch cannot repeat'
    OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('pin',path);pins[relative(path)]=h;return path
    def materialize(path,text):
        data=text.encode('utf8')
        if path.exists():assert path.read_bytes()==data,('prepared source drift',path)
        else:path.write_bytes(data)
        pin(path)
    def guard():
        for n,h in pins.items():assert digest(ROOT/n)==h,('input drift',n)
    backend=module('backend277','scripts/research/x86-cpp-backend-277.py');base=module('fixture262','scripts/research/experiment-v2-x86-cpu-primitives-262.py')
    abi=module('abi277','scripts/research/experiment-v2-thiscall-186.py');oracle=module('oracle277','scripts/research/audit-v2-nested-calls-229.py')
    for p in [__file__,ROOT/'scripts/research/x86-cpp-backend-277.py',ROOT/'scripts/research/experiment-v2-x86-cpu-primitives-262.py',
              ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/audit-v2-nested-calls-229.py',abi.COMPILER,abi.DUMPBIN]:pin(p)
    pin(ROOT/'scripts/research/x86-cpp-backend-257.py',BASE_SHA);pin(Path(backend._base.capstone.__file__));pin(Path(backend._base.capstone.__file__).parent/'lib/capstone.dll')
    assert backend.HEADER==backend._base.HEADER
    rows=fragments();header=backend.HEADER+'\n'+''.join('void translated_'+r['entry']+'(Machine257&);\n' for r in rows)
    sources=[];witnesses={}
    for row in rows:
        src,wit=backend.translate(bytes.fromhex(row['hex']),int(row['entry'],16));sources.append(src);witnesses[row['name']]=wit
    dispatch='\nvoid dispatch257(Machine257&s,U target){s.pc=target;switch(target){\n'+''.join('case 0x'+r['entry']+'u:translated_'+r['entry']+'(s);return;\n' for r in rows)+'default:s.stop=Stop257::MissingEntry;return;}}\n'
    materialize(OUT/'machine257.h',header);materialize(OUT/'derived-backend277.py',backend.DERIVED_SOURCE)
    materialize(OUT/'extended277.cpp','\n'.join(sources)+dispatch);materialize(OUT/'state-fixture.cpp',fixture(rows,base))
    rejected=[]
    for raw,name in [(b'\xd1\xe0\xc3','SHL'),(b'\xd9\xe8\xc3','x87'),(b'\x0f\x94\xc0\xc3','SETcc'),(b'\x0f\xbe','truncatedMOVSX')]:
        try:backend.translate(raw,0x1000)
        except ValueError:rejected.append(name)
        else:raise AssertionError(('unsupported accepted',name))
    proof=dict(kind='synthetic-extended-integer-preflight',backend_sha256=digest(ROOT/'scripts/research/x86-cpp-backend-277.py'),baseline_backend_sha256=BASE_SHA,
               header_sha256=digest(OUT/'machine257.h'),baseline_header_sha256=hashlib.sha256(backend.HEADER.encode()).hexdigest(),fragments=rows,instruction_lowering=witnesses,
               unchanged_helper_header=True,lowering_patches=backend.PATCHES,planned_native_cases=30976,planned_tus=2,planned_compiler_batches=1,
               unsupported_rejected=rejected,original_game_functions=0,limits=['SyntheticCPUfixtures only; no gameentry/ABI/provider/acceptance orfullISA claim.',
               'DefinedCF/ZF/SF/OF only; PF/AF/undefinedflags/faults/segments/x87/shifts/SETcc unproved orunsupported.',
               'Selectedregister/memory widthcombinations and finiteedgevalues; validnative32stack/sourcearenas only.'])
    if(RUN/'proof-before-compile.json').exists():assert load(RUN/'proof-before-compile.json')==json.loads(json.dumps(proof))
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json');guard()
    if a.prepare_only:
        print(json.dumps({k:proof[k] for k in ['backend_sha256','header_sha256','baseline_header_sha256','planned_native_cases']}));return
    objects=OUT/'objects';objects.mkdir(exist_ok=a.finalize_existing);env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        receipt=OUT/(name+'.execution.json');log=OUT/(name+'.log');assert not receipt.exists() and not log.exists(),'unique attempt required'
        command=list(map(str,command));start=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);elapsed=time.perf_counter()-start
        write(receipt,dict(command=command,cwd=str(OUT),exit_code=p.returncode,elapsed_seconds=elapsed));log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'));return p,log,elapsed
    command=[abi.COMPILER,'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/MP6','/Fo'+str(objects)+os.sep,OUT/'extended277.cpp',OUT/'state-fixture.cpp']
    if a.finalize_existing:
        r=load(OUT/'compile-001.execution.json');assert r['exit_code']==0 and r['command']==list(map(str,command));seconds=r['elapsed_seconds'];clog=OUT/'compile-001.log'
    else:
        (OUT/'captured-compile-driver.py').write_bytes(Path(__file__).read_bytes());p,clog,seconds=run(command,'compile-001');assert p.returncode==0,clog.read_bytes()
    pin(OUT/'captured-compile-driver.py');assert not re.search(rb'(?:warning|error) [CD]\d+',clog.read_bytes()),clog.read_bytes()
    oracles=[]
    for r in rows:
        body,relocs=oracle.coff_function(objects/'state-fixture.obj','?oracle277_'+str(r['id'])+'@@YAXXZ');assert body.hex()==r['hex'] and relocs==[],(r['name'],body.hex(),r['hex'],relocs)
        oracles.append(dict(id=r['id'],name=r['name'],bytes=body.hex(),relocations=relocs))
    link=pin(abi.COMPILER.with_name('link.exe'));sdk=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0')
    libs=[pin(abi.COMPILER.parents[3]/'lib/x86'/n) for n in ['libcmt.lib','libvcruntime.lib']]+[pin(sdk/'ucrt/x86/libucrt.lib'),pin(sdk/'um/x86/kernel32.lib')];exe=OUT/'state-fixture.exe'
    if not a.finalize_existing:
        p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),objects/'extended277.obj',objects/'state-fixture.obj',*libs],'link-001');assert p.returncode==0,llog.read_bytes()
        p,_,native_seconds=run([exe],'native-001');assert p.returncode==0,('nativeprimitivecomparison',p.returncode)
    else:
        assert load(OUT/'link-001.execution.json')['exit_code']==0;r=load(OUT/'native-001.execution.json');assert r['exit_code']==0;native_seconds=r['elapsed_seconds']
    result=load(pin(OUT/'fixture-result.json'));assert result==dict(provenance='syntheticCPUfixture',native_game_execution=False,cases=30976,failures=0,extensions=16384,logic=13824,conditions=768)
    for p in [*objects.glob('*.obj'),exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(p)
    guard()
    summary=dict(schema=1,kind='synthetic-x86-extended-integer',backend_sha256=proof['backend_sha256'],header_sha256=proof['header_sha256'],
                 baseline_backend_sha256=BASE_SHA,unchanged257_header_helpers=True,synthetic_entries=26,synthetic_bytes=164,synthetic_instructions=sum(len(w) for w in witnesses.values()),
                 original_game_functions=0,new_accepted_functions=0,production_or_union_changed=False,native_game_execution_commands=0,actual_compiler_batches=1,compiled_tus=2,
                 compiler_exit_code=0,compile_seconds=seconds,compiler_warnings=0,native_fixture_exit_code=0,native_seconds=native_seconds,state_comparisons=30976,
                 case_groups=result,oracles=oracles,input_sha256=pins,before_after_guards=True,command=list(map(str,command)),resumed_existing_compile=a.finalize_existing,
                 unique_execution_receipts=['compile-001','link-001','native-001'],limits=proof['limits'])
    write(RUN/'summary.json',summary);print(json.dumps({k:summary[k] for k in ['synthetic_bytes','synthetic_instructions','state_comparisons','compile_seconds','native_seconds']}))


if __name__=='__main__':main()
