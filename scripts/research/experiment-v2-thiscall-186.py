"""Isolated x86 native method ABI experiment; never mutates the source corpus."""
from __future__ import annotations
import argparse
import bisect
from collections import Counter
import hashlib,json,os,re,struct,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/186-thiscall-compatibility'
OUT=ROOT/'local/experiments/v2-thiscall-186'
CORPUS=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d'
DECL=ROOT/'iterations/v2/001-original-recovery/runs/179-ghidra-declarations/export/functions.jsonl'
TOOLS=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
COMPILER=TOOLS/'bin/Hostx64/x86/cl.exe'
DUMPBIN=TOOLS/'bin/Hostx64/x86/dumpbin.exe'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=lambda p:[json.loads(s) for s in p.read_text(encoding='utf-8-sig').splitlines() if s.strip()]
ENV={**os.environ,'VSLANG':'1033'}

FIXTURE=r'''// Synthetic ABI tests, no original game algorithms or runtime byte execution.
typedef unsigned int u32; typedef unsigned char u8; typedef unsigned short u16;
static_assert(sizeof(void*)==4,"x86 only");
extern "C" __declspec(dllimport) void __stdcall ExitProcess(u32);
extern "C" int _fltused=0;
volatile u32 seen_this,seen_a,seen_b,seen_edx,failures,checks;
struct Probe {
 __declspec(noinline) u32 __thiscall scalar(u32 a,u32 b);
 __declspec(noinline) u8 __thiscall narrow8(u32 a);
 __declspec(noinline) u16 __thiscall narrow16(u32 a);
 __declspec(noinline) double __thiscall real(double a);
 __declspec(noinline) void __thiscall store(u32 a);
 __declspec(noinline) u32 __thiscall noargs();
 __declspec(noinline) u32 __thiscall observe(u32 a,u32 b);
};
u32 Probe::scalar(u32 a,u32 b){seen_this=(u32)this;seen_a=a;seen_b=b;return a^b^0x6a3192e7u;}
u8 Probe::narrow8(u32 a){seen_this=(u32)this;seen_a=a;return (u8)(a^0xa5);}
u16 Probe::narrow16(u32 a){seen_this=(u32)this;seen_a=a;return (u16)(a^0x5aa5);}
double Probe::real(double a){seen_this=(u32)this;return a+1.25;}
void Probe::store(u32 a){seen_this=(u32)this;seen_a=a;}
u32 Probe::noargs(){seen_this=(u32)this;return 0x32b67e19u;}
u32 Probe::observe(u32 a,u32 b){__asm{
 mov seen_this,ecx
 mov seen_edx,edx
}seen_a=a;seen_b=b;return 0x7163a9e2u;}
// Restricted fixture: empty nonvirtual single-inheritance class only.
// This introspection does not define a portable/member-function-address lowering.
template<class T> void* raw_member(T member){
 static_assert(sizeof(T)==4,"fixture requires one-word native method pointer");
 u32 raw=0;const u8*p=(const u8*)&member;
 for(u32 i=0;i<4;i++)raw|=(u32)p[i]<<(i*8);
 return (void*)raw;
}
void require(bool ok){checks++;if(!ok)failures++;}
__declspec(noinline) u32 raw0(void*target,void*self){u32 before,after,out;__asm{
 mov before,esp
 mov ecx,self
 mov edx,0xd3b70965
 call target
 mov after,esp
 mov out,eax
 mov esp,before
}require(before==after);return out;}
__declspec(noinline) u32 raw1(void*target,void*self,u32 a){u32 before,after,out;__asm{
 mov before,esp
 push a
 mov ecx,self
 mov edx,0xd3b70965
 call target
 mov after,esp
 mov out,eax
 mov esp,before
}require(before==after);return out;}
__declspec(noinline) u32 raw2(void*target,void*self,u32 a,u32 b){u32 before,after,out;__asm{
 mov before,esp
 push b
 push a
 mov ecx,self
 mov edx,0xd3b70965
 call target
 mov after,esp
 mov out,eax
 mov esp,before
}require(before==after);return out;}
__declspec(noinline) double rawdouble(void*target,void*self,double a){u32 before,after;double out;__asm{
 mov before,esp
 push dword ptr a[4]
 push dword ptr a
 mov ecx,self
 mov edx,0xd3b70965
 call target
 fstp qword ptr out
 mov after,esp
 mov esp,before
}require(before==after);return out;}
__declspec(noinline) u32 direct_scalar(Probe*p,u32 a,u32 b){return p->scalar(a,b);}
__declspec(noinline) u32 direct_observer(Probe*p,u32 a,u32 b){return p->observe(a,b);}
extern "C" void __cdecl entry(){
 Probe object;Probe*p=&object;
 const u32 inputs[]={0,1,0x7fffffff,0x80000000,0xffffffff,0x13579bdf};
 for(u32 i=0;i<6;i++)for(u32 j=0;j<6;j++){
  u32 a=inputs[i],b=inputs[j],want=a^b^0x6a3192e7u;
  require(direct_scalar(p,a,b)==want);require(seen_this==(u32)p&&seen_a==a&&seen_b==b);
  require(raw2(raw_member(&Probe::scalar),p,a,b)==want);require(seen_this==(u32)p&&seen_a==a&&seen_b==b);
  require(raw2(raw_member(&Probe::observe),p,a,b)==0x7163a9e2u);
  require(seen_this==(u32)p&&seen_a==a&&seen_b==b&&seen_edx==0xd3b70965u);
  require(direct_observer(p,a,b)==0x7163a9e2u);require(seen_this==(u32)p&&seen_a==a&&seen_b==b);
 }
 for(u32 i=0;i<6;i++){
  u32 a=inputs[i];require((raw1(raw_member(&Probe::narrow8),p,a)&255)==((a^0xa5)&255));
  require((raw1(raw_member(&Probe::narrow16),p,a)&65535)==((a^0x5aa5)&65535));
  raw1(raw_member(&Probe::store),p,a);require(seen_this==(u32)p&&seen_a==a);
 }
 require(raw0(raw_member(&Probe::noargs),p)==0x32b67e19u);
 require(rawdouble(raw_member(&Probe::real),p,2.5)==3.75);
 require(rawdouble(raw_member(&Probe::real),p,-7.5)==-6.25);
 require(seen_this==(u32)p);
 ExitProcess(failures?failures:0);
}
'''

def run(command,log,timeout=90):
 p=subprocess.run([str(x) for x in command],cwd=OUT,capture_output=True,encoding='utf8',errors='replace',env=ENV,timeout=timeout)
 log.write_text(p.stdout+p.stderr,encoding='utf8');return p

def text_sections(obj):
 raw=obj.read_bytes();machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,0);assert machine==0x14c
 result=[]
 for i in range(count):
  off=20+optional+40*i;name=raw[off:off+8].rstrip(b'\0').decode('ascii');size,start,relocations=struct.unpack_from('<III',raw,off+16);nreloc=struct.unpack_from('<H',raw,off+32)[0]
  if name.startswith('.text'):result.append({'name':name,'bytes':raw[start:start+size].hex(),'relocations':nreloc,'sha256':hashlib.sha256(raw[start:start+size]).hexdigest()})
 return result

def fixture():
 source=OUT/'abi_fixture.cpp';source.write_text(re.sub(r'\bout\b','answer',FIXTURE),encoding='utf8')
 sdk=ROOT/'local/tools/Windows Kits/10/Lib'
 if not sdk.exists():sdk=Path(os.environ.get('ProgramFiles(x86)','C:/Program Files (x86)'))/'Windows Kits/10/Lib'
 kernel=sorted(sdk.glob('*/um/x86/kernel32.lib'))[-1]
 result=[]
 for opt in ('Od','O2'):
  obj=OUT/('abi_fixture_'+opt+'.obj');exe=OUT/('abi_fixture_'+opt+'.exe');log=OUT/('abi_fixture_'+opt+'.log')
  command=[COMPILER,'/nologo','/c','/std:c++17','/'+opt,'/Oy-','/GS-','/GR-','/EHs-c-','/W4','/Fo'+str(obj),source]
  p=run(command,log);assert p.returncode==0,log
  link=TOOLS/'bin/Hostx64/x86/link.exe'
  p=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,kernel],OUT/('abi_fixture_'+opt+'_link.log'));assert p.returncode==0,p.stdout+p.stderr
  native=run([exe],OUT/('abi_fixture_'+opt+'_native.log'));assert native.returncode==0,('Native ABI fixture failed',opt,native.returncode)
  dis=OUT/('abi_fixture_'+opt+'_disassembly.txt');symbols=OUT/('abi_fixture_'+opt+'_symbols.txt')
  assert run([DUMPBIN,'/disasm',obj],dis).returncode==0
  assert run([DUMPBIN,'/symbols',obj],symbols).returncode==0
  result.append({'optimization':opt,'compiler_exit':0,'native_exit':native.returncode,'source_sha256':sha(source),'object_sha256':sha(obj),'exe_sha256':sha(exe),'disassembly_sha256':sha(dis),'symbols_sha256':sha(symbols),'method_invocations':165,'checked_conditions':403,'boundary':'Synthetic native compiler/caller ABI tests; no original algorithm acceptance; high EAX bits of AL/AX returns ignored as ABI-unspecified'})
 return result

def bodies():
 raw=(CORPUS/'decompiled.c').read_bytes();ms=list(re.finditer(rb'/\* VA ([0-9a-f]+) \*/',raw));out={}
 for i,m in enumerate(ms):out[m[1].decode()]=raw[m.end():ms[i+1].start() if i+1<len(ms) else len(raw)].decode()
 assert len(out)==5772;return out

def instruction_index():
 result=[]
 for line in (CORPUS/'disassembly.asm').read_text().splitlines():
  m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
  if m:result.append((int(m[1],16),{'va':m[1],'bytes':m[2],'instruction':m[3]}))
 return [r[0] for r in result],[r[1] for r in result]

def function_instructions(entry,index):
 addresses,instructions=index;result=[]
 for a,b in entry['ranges']:result.extend(instructions[bisect.bisect_left(addresses,int(a,16)):bisect.bisect_right(addresses,int(b,16))])
 return result

def original_contract(d,entry,index):
 instructions=function_instructions(entry,index);rets=[i for i in instructions if i['instruction'].startswith('RET')]
 expected=sum((p['type']['length']+3)//4*4 for p in d['parameters'] if not p['this'])
 actual=sorted({int(r['instruction'].split(' ',1)[1],16) if ' ' in r['instruction'] else 0 for r in rets})
 return {'expected_stack_bytes':expected,'original_ret_bytes':actual,'ret_agrees':bool(actual) and actual==[expected],'original_ret_sites':rets,'ghidra_extra_pop':d['extra_pop'],'extra_pop_is_ret_plus_return_address':d['extra_pop']==expected+4}

def contract_census(decls,catalog,index):
 result=[]
 for d in decls:
  if d['inferred_calling_convention']=='__thiscall':result.append({'va':d['entry_va'],**original_contract(d,catalog[d['entry_va']],index)})
 return {'functions':len(result),'matching_ret':sum(r['ret_agrees'] for r in result),'ret_mismatch':sum(bool(r['original_ret_bytes']) and not r['ret_agrees'] for r in result),'no_ret_body':sum(not r['original_ret_bytes'] for r in result),'extra_pop_matches_parameter_extent_plus_return_address':sum(r['extra_pop_is_ret_plus_return_address'] for r in result),'rows':result}

def split_parameters(text):
 result=[];start=0;depth=0
 for i,c in enumerate(text):
  if c in '([':depth+=1
  elif c in ')]':depth-=1
  elif c==',' and depth==0:result.append(text[start:i].strip());start=i+1
 result.append(text[start:].strip());return result

def lower(decl,text):
 va=decl['entry_va'];name=decl['name'];parameters=decl['parameters'];thisparams=[(i,p) for i,p in enumerate(parameters) if p['this']]
 if len(thisparams)!=1 or thisparams[0][0]!=0:raise ValueError('not one leading this parameter')
 if decl['varargs'] or any(p['hidden_return'] for p in parameters):raise ValueError('vararg/hidden return unresolved')
 thisparam=thisparams[0][1]
 if thisparam['storage_detail']['serialization']!='register:00000004:4':raise ValueError('this storage is not ECX4')
 if re.search(r'\b(?:in_|unaff_|extraout_|in_stack_)\w*',text):raise ValueError('unrecovered register/stack value')
 clean=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S).strip();sig,body=clean.split('{',1)
 match=re.fullmatch(r'\s*(.*?)\s+__thiscall\s+'+re.escape(name)+r'\s*\((.*)\)\s*',sig,flags=re.S)
 if not match or not re.fullmatch(r'FUN_[0-9a-f]+',name):raise ValueError('qualified/decorated signature requires explicit naming plan')
 ret=match[1].strip();args=split_parameters(match[2]);first=args[0];param=thisparam['name'];paramtype=first[:first.rfind(param)].strip()
 if not first.endswith(param) or len(args)!=len(parameters):raise ValueError('signature/metadata parameter mismatch')
 if param=='this':raise ValueError('literal this requires identifier-only body substitution')
 if decl['return_storage']=='ST0:10' and ret not in ('float','double'):raise ValueError('extended x87 return has no native scalar representation')
 expected_offset=4
 for p in parameters[1:]:
  if not p['storage_detail']['stack'] or p['storage_detail']['compound']:raise ValueError('nonstandard parameter storage')
  if len(p['storage_detail']['varnodes'])!=1 or int(p['storage_detail']['varnodes'][0]['offset'])!=expected_offset:raise ValueError('parameter extent/gap requires explicit ABI recovery')
  expected_offset+=(p['type']['length']+3)//4*4
 klass='Thiscall_'+va
 method='invoke'
 assertions=['static_assert(sizeof('+paramtype+') == 4, "original ECX width");']
 for i,p in enumerate(parameters[1:],1):
  ptype=args[i][:args[i].rfind(p['name'])].strip();assertions.append('static_assert(sizeof('+ptype+') == '+str(p['type']['length'])+', "original parameter width");')
 if ret!='void':assertions.append('static_assert(sizeof('+ret+') == '+str(decl['return_type']['length'])+', "original return width");')
 lowered='\n'.join(assertions)+'\nstruct '+klass+' {\n __declspec(noinline) '+ret+' __thiscall '+method+'('+','.join(args[1:])+');\n};\n'
 lowered+=ret+' '+klass+'::'+method+'('+','.join(args[1:])+')\n{\n '+paramtype+' '+param+' = reinterpret_cast<'+paramtype+'>(this);\n'+body
 return lowered,{'class':klass,'method':method,'explicit_this':param,'explicit_this_type':paramtype,'original_signature':sig.strip(),'native_stack_bytes':sum((p['type']['length']+3)//4*4 for p in parameters[1:]),'this_storage':thisparam['storage'],'return_storage':decl['return_storage']}

def pilot(limit):
 bs=bodies();decls=rows(DECL);catalog={r['entry_va']:r for r in rows(CORPUS/'functions.jsonl')}
 accepted={r['entry_va'] for r in json.loads((ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_text())['functions'] if r['module']=='Porsche.exe'}
 index=instruction_index();calls=rows(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl')
 census=contract_census(decls,catalog,index)
 candidates=[r for r in decls if r['inferred_calling_convention']=='__thiscall' and not r['globals'] and r['entry_va'] not in accepted and not re.search(r'\bFUN_[0-9a-f]+\s*\(',bs[r['entry_va']].split('{',1)[-1])]
 candidates.sort(key=lambda r:(len(bs[r['entry_va']]),r['entry_va']));results=[];rejected=Counter()
 primitives=ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h'
 for d in candidates:
  if len(results)>=limit:break
  try:lowered,contract=lower(d,bs[d['entry_va']])
  except ValueError as e:rejected[str(e)]+=1;continue
  original=original_contract(d,catalog[d['entry_va']],index)
  if not original['ret_agrees']:rejected['original RET disagrees or absent']+=1;continue
  va=d['entry_va'];source=OUT/(va+'.cpp');obj=OUT/(va+'.obj');log=OUT/(va+'.log')
  source.write_text('#include "'+primitives.as_posix()+'"\n'+lowered,encoding='utf8')
  p=run([COMPILER,'/nologo','/c','/std:c++17','/O2','/GS-','/GR-','/W4','/Fo'+str(obj),source],log)
  instructions=function_instructions(catalog[va],index)
  contract['original_ret_sites']=original['original_ret_sites'];contract['original_ret_agrees']=original['ret_agrees']
  contract['ghidra_extra_pop']=d['extra_pop'];contract['extra_pop_is_ret_plus_return_address']=d['extra_pop']==contract['native_stack_bytes']+4
  evidence=OUT/(va+'_disassembly.txt');symbols=OUT/(va+'_symbols.txt')
  if p.returncode==0:
   run([DUMPBIN,'/disasm',obj],evidence);run([DUMPBIN,'/symbols',obj],symbols)
  sections=text_sections(obj) if p.returncode==0 else [];original_bytes=''.join(i['bytes'] for i in instructions)
  results.append({'va':va,'compiler_exit':p.returncode,'source_body_sha256':hashlib.sha256(bs[va].encode()).hexdigest(),'generated_source_sha256':sha(source),'object_sha256':sha(obj) if obj.exists() else None,'native_text_sections':sections,'exact_original_body_bytes_match':any(s['relocations']==0 and s['bytes']==original_bytes for s in sections),'log_sha256':sha(log),'contract':contract,'original_instructions':instructions,'indexed_callers':[c for c in calls if c['to_function']==va][:4],'boundary':'Original body preserved; native method/this binding only. Compile/ABI candidate, not original behavior acceptance or recovered class layout.'})
 # One explicitly traced receiver reconstruction, rather than guessing printed arg0.
 by_va={r['entry_va']:r for r in decls};caller_va='00466e60';callee_va='00466e80'
 caller,caller_contract=lower(by_va[caller_va],bs[caller_va]);callee,callee_contract=lower(by_va[callee_va],bs[callee_va])
 call_text='FUN_00466e80(param_2)'
 receiver='reinterpret_cast<Thiscall_00466e80 *>(*(unsigned int *)(param_1 + 0xc) + 0xb8)'
 assert caller.count(call_text)==1
 # Validate the exact original binding instructions/bytes before emitting it.
 binding={'00466e6a':'8902','00466e6c':'8b490c','00466e6f':'81c1b8000000','00466e75':'e806000000'}
 original_caller=function_instructions(catalog[caller_va],index)
 assert all(any(i['va']==va and i['bytes']==code for i in original_caller) for va,code in binding.items())
 caller=caller.replace(call_text,receiver+'->invoke(param_2)')
 source=OUT/'original_caller_00466e60.cpp';obj=OUT/'original_caller_00466e60.obj';log=OUT/'original_caller_00466e60.log'
 source.write_text('#include "'+primitives.as_posix()+'"\n'+callee+'\n'+caller,encoding='utf8')
 p=run([COMPILER,'/nologo','/c','/std:c++17','/O2','/GS-','/GR-','/W4','/Fo'+str(obj),source],log)
 if p.returncode==0:run([DUMPBIN,'/disasm',obj],OUT/'original_caller_00466e60_disassembly.txt');run([DUMPBIN,'/symbols',obj],OUT/'original_caller_00466e60_symbols.txt')
 rewrite={'caller_va':caller_va,'callee_va':callee_va,'compiler_exit':p.returncode,'original_call_text':call_text,'rewritten_call':receiver+'->invoke(param_2)','receiver_equation':'ECX_call = DWORD[ECX_entry + 0x0c] + 0xb8; stack_arg0 = DWORD[ESP_entry+4]','binding_instruction_bytes':binding,'caller_contract':original_contract(by_va[caller_va],catalog[caller_va],index),'callee_contract':original_contract(by_va[callee_va],catalog[callee_va],index),'original_caller_instructions':original_caller,'generated_source_sha256':sha(source),'object_sha256':sha(obj) if obj.exists() else None,'log_sha256':sha(log),'boundary':'Single original consumer traced explicitly. Printed call omits ECX; no automatic first-argument-as-this inference is allowed.'}
 return results,dict(rejected),census,rewrite

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--pilot',type=int,default=12);args=parser.parse_args();assert 0<=args.pilot<=32
 OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 binary=next(r for r in rows(ROOT/'research/binary-index/static/binaries.jsonl') if r['file']=='Porsche.exe');assert sha(ROOT/'local/game'/binary['path'])==SHA
 native=fixture();candidates,rejected,census,rewrite=pilot(args.pilot)
 pins=(Path(__file__),DECL,CORPUS/'decompiled.c',CORPUS/'disassembly.asm',CORPUS/'functions.jsonl',ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json',ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h',COMPILER,DUMPBIN,TOOLS/'bin/Hostx64/x86/link.exe')
 report={'schema':1,'original_sha256':SHA,'source_pins':{str(p.relative_to(ROOT)):sha(p) for p in pins},'native_fixtures':native,'pilot':candidates,'pilot_attempted':len(candidates),'pilot_compiled':sum(r['compiler_exit']==0 for r in candidates),'rejected':rejected,'original_contract_census':census,'traced_original_caller':rewrite,'method':'Nonvirtual class method, native ECX this; explicit original ECX parameter becomes typed local this view, stack parameters unchanged. No cdecl/fastcall replacement.','remaining_seams':['true class/object lifetime/layout not recovered','getC calls can omit ECX receiver and signatures can omit actual stack arguments; original consumers required','direct caller expression evaluation order must match original','literal this and decorated/qualified names require token-safe mapping','function addresses/member-pointer representation not portable','virtual/indirect call contracts unresolved','unknown incoming registers/hidden returns/varargs rejected','extended x87 float10 and storage aliases unchanged'],'boundary':'Synthetic ABI fixtures plus isolated compile pilot only; no gameplay algorithms guessed, no original bytes executed, no production integration or verified-function count change'}
 (RUN/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'native_fixture_exit_codes':[r['native_exit'] for r in native],'pilot_attempted':len(candidates),'pilot_compiled':report['pilot_compiled'],'original_ret_agreements':sum(r['contract']['original_ret_agrees'] for r in candidates),'remaining_seams':report['remaining_seams']},indent=2))

if __name__=='__main__':main()
