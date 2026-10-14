"""Run180: isolated exact integer p-code vocabulary; unchanged5772-body audit."""
from __future__ import annotations
import argparse
import collections
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'local/experiments/v2-pcode-compat-180'
RUN=ROOT/'iterations/v2/001-original-recovery/runs/180-pcode-compatibility'
GH=ROOT/'local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/src/decompile/cpp'
spec=importlib.util.spec_from_file_location('audit178',ROOT/'scripts/research/audit-v2-compile-corpus.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ty(n):return {1:'unsigned char',2:'unsigned short',4:'unsigned int',8:'unsigned __int64'}.get(n,'undefined'+str(n))
def mask(n):return (1<<(8*n))-1

def header():
 text='''/* Exact low-bit storage operations. Target: MSVC x86 little endian.
 Input/output sizes are the decimal BYTE suffixes emitted by typeop.cc.
 No floating arithmetic, storage definitions, ABI rewriting or game stubs. */
#pragma once
static_assert(sizeof(void*)==4,"Run180 requires x86");
typedef unsigned __int64 p180_u64;
template<int N,class T> static p180_u64 p180_read(const T& value) {
 static_assert(sizeof(T)>=N,"p-code input representation is too short");
 const unsigned char* p=reinterpret_cast<const unsigned char*>(&value);
 p180_u64 result=0;
 for(int i=0;i<N;++i) result|=p180_u64(p[i])<<(8*i);
 return result;
}
template<class T> static T p180_write(p180_u64 value) {
 T result; unsigned char* p=reinterpret_cast<unsigned char*>(&result);
 for(unsigned i=0;i<sizeof(T);++i) p[i]=static_cast<unsigned char>(value>>(8*i));
 return result;
}
'''
 names=[]
 for a in range(1,9):
  for b in range(1,9-a):
   name=f'CONCAT{a}{b}';names.append(name)
   text+=f'template<class A,class B> static {ty(a+b)} {name}(A a,B b) {{ return p180_write<{ty(a+b)}>((p180_read<{a}>(a)<<{8*b})|p180_read<{b}>(b)); }}\n'
 for a in range(1,9):
  for b in range(1,a+1):
   name=f'SUB{a}{b}';names.append(name)
   text+=f'template<class A> static {ty(b)} {name}(A a,unsigned int offset) {{ return p180_write<{ty(b)}>(offset>={a}?0:p180_read<{a}>(a)>>(offset*8)); }}\n'
  for b in range(a+1,9):
   for kind in ('ZEXT','SEXT'):
    name=f'{kind}{a}{b}';names.append(name)
    expr=f'p180_read<{a}>(a)'
    if kind=='SEXT':expr=f'({expr} ^ (p180_u64(1)<<{8*a-1}))-(p180_u64(1)<<{8*a-1})'
    text+=f'template<class A> static {ty(b)} {name}(A a) {{ return p180_write<{ty(b)}>({expr}); }}\n'
  for kind in ('CARRY','SCARRY','SBORROW'):
   name=f'{kind}{a}';names.append(name)
   if kind=='CARRY':expr=f'x>((x+y)&0x{mask(a):x}ULL)'
   elif kind=='SCARRY':expr=f'((~(x^y)&(x^(x+y)))>>{8*a-1})&1'
   else:expr=f'(((x^y)&(x^(x-y)))>>{8*a-1})&1'
   text+=f'template<class A,class B> static bool {name}(A a,B b) {{ p180_u64 x=p180_read<{a}>(a),y=p180_read<{a}>(b); return ({expr})!=0; }}\n'
 return text,names

def native_tests(compiler,helper):
 """Boundary vectors and exhaustive8-bit carry/overflow against Python integers."""
 source='#include "'+(OUT/'ghidra-scalars-syntax-only.h').as_posix()+'"\n#include "'+helper.as_posix()+'"\nint main(){\n'
 count=0
 def check(expr,n,want):
  nonlocal source,count
  count+=1;source+=f'if(p180_read<{n}>({expr})!=0x{want & mask(n):x}ULL) return {count%250+1};\n'
 values=lambda n:sorted({0,1,mask(n),mask(n)-1,1<<(8*n-1),(1<<(8*n-1))-1})
 val=lambda x,n:f'p180_write<{ty(n)}>(0x{x:x}ULL)'
 for a in range(1,9):
  for b in range(1,9-a):
   for x in values(a):
    for y in values(b):check(f'CONCAT{a}{b}({val(x,a)},{val(y,b)})',a+b,(x<<(8*b))|y)
  for b in range(1,a+1):
   for x in values(a):
    for off in (0,a-1,a,8,255):check(f'SUB{a}{b}({val(x,a)},{off})',b,x>>(off*8))
  for b in range(a+1,9):
   for x in values(a):
    check(f'ZEXT{a}{b}({val(x,a)})',b,x)
    check(f'SEXT{a}{b}({val(x,a)})',b,x if x<(1<<(8*a-1)) else x-(1<<(8*a)))
  for x in values(a):
   for y in values(a):
    sx=x if x<(1<<(8*a-1)) else x-(1<<(8*a));sy=y if y<(1<<(8*a-1)) else y-(1<<(8*a))
    for name,want in [('CARRY',x+y>mask(a)),('SCARRY',not -(1<<(8*a-1))<=sx+sy<(1<<(8*a-1))),('SBORROW',not -(1<<(8*a-1))<=sx-sy<(1<<(8*a-1)))]:check(f'{name}{a}({val(x,a)},{val(y,a)})',1,int(want))
 source+='''for(unsigned x=0;x<256;++x)for(unsigned y=0;y<256;++y){
 unsigned char a=(unsigned char)x,b=(unsigned char)y;
 int sx=x<128?x:int(x)-256,sy=y<128?y:int(y)-256;
 if(CARRY1(a,b)!=(x+y>255))return 251;
 if(SCARRY1(a,b)!=(sx+sy < -128 || sx+sy>127))return 252;
 if(SBORROW1(a,b)!=(sx-sy < -128 || sx-sy>127))return 253;
}return 0;}\n'''
 path=OUT/'helper-vectors.cpp';path.write_text(source,encoding='utf8')
 obj=OUT/'helper-vectors.obj';exe=OUT/'helper-vectors.exe'
 cmd=[str(compiler),'/nologo','/c','/TP','/O2','/GS-','/utf-8','/Fo'+str(obj),str(path)]
 p=subprocess.run(cmd,capture_output=True,text=True);log=p.stdout+p.stderr
 if p.returncode:raise RuntimeError(log)
 vc_lib=compiler.parents[3]/'lib/x86'
 cmd2=[str(compiler.with_name('link.exe')),'/nologo','/nodefaultlib','/entry:main','/subsystem:console','/machine:x86','/out:'+str(exe),str(obj),str(vc_lib/'libvcruntime.lib'),str(vc_lib/'libcmt.lib')]
 p=subprocess.run(cmd2,capture_output=True,text=True);log+=p.stdout+p.stderr
 if p.returncode:raise RuntimeError(log)
 p=subprocess.run([str(exe)],capture_output=True,text=True)
 (OUT/'helper-vectors.log').write_text(log,encoding='utf8')
 assert p.returncode==0, p.returncode
 return {'boundary_checks':count,'exhaustive8_bit_pairs':65536,'exhaustive8_bit_checks':196608,'exit_code':p.returncode,'source_sha256':sha(path),'exe_sha256':sha(exe),'commands':[cmd,cmd2]}

def delta_audit(compiler,helper,jobs):
 """Reuse byte-identical178 TUs; insert a header only in lexical helper users."""
 baseline_dir=ROOT/'local/experiments/v2-compile-corpus-178/prototypes-cpp-0000'
 baseline=json.loads((baseline_dir/'audit.json').read_text())
 assert baseline['selected_functions']==5772 and baseline['language']=='cpp' and baseline['phase']=='prototypes'
 assert str(compiler)==baseline['compiler']
 env={**os.environ,'VSLANG':'1033'}
 version=subprocess.run([str(compiler)],capture_output=True,text=True,encoding='utf8',errors='replace',env=env)
 assert (version.stdout+version.stderr).strip()==baseline['compiler_version']
 assert sha(baseline_dir.parent/'ghidra-scalars-syntax-only.h')==baseline['primitive_header_sha256']==hashlib.sha256(audit.PRIMITIVES.encode()).hexdigest()
 for name,pin in baseline['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==pin
 raw=(audit.CORPUS/'decompiled.c').read_bytes();assert hashlib.sha256(raw).hexdigest()==baseline['pseudo_c_sha256']
 bodymap={r['va']:r for r in audit.bodies(raw)}
 target=OUT/'prototypes-cpp-0000';target.mkdir(exist_ok=True)
 oldmap={r['va']:r for r in baseline['results']};results=[];pending=[]
 inputs={str(baseline_dir/'audit.json'):sha(baseline_dir/'audit.json'),str(helper):sha(helper),str(compiler):sha(compiler),str(audit.CORPUS/'decompiled.c'):sha(audit.CORPUS/'decompiled.c'),str(baseline_dir.parent/'ghidra-scalars-syntax-only.h'):sha(baseline_dir.parent/'ghidra-scalars-syntax-only.h')}
 begin=time.perf_counter()
 for va,old in oldmap.items():
  body=bodymap[va];assert old['source_body_sha256']==body['sha256']
  original=baseline_dir/(va+'.cpp');data=original.read_bytes();assert hashlib.sha256(data).hexdigest()==old['generated_source_sha256']
  changed=bool(re.search(r'\b(?:CONCAT|SUB|[SZ]EXT|CARRY|SCARRY|SBORROW)\d+\b',body['text']))
  # No header, scalar, prototype or source changes in a reused translation unit.
  if changed:
   first,rest=data.split(b'\n',1)
   data=first+b'\n#include "'+helper.as_posix().encode()+b'"\n'+rest
  dest=target/(va+'.cpp');dest.write_bytes(data)
  provenance={'generated_source':str(dest),'forced_headers':[],'compatibility_header':str(helper) if changed else None,'cache_reused':not changed,'baseline_generated_source':str(original),'baseline_generated_source_sha256':old['generated_source_sha256']}
  if changed:pending.append((body,dest,provenance))
  else:
   assert sha(dest)==old['generated_source_sha256']
   results.append({**old,**provenance})
 def one(item):
  row,path,provenance=item
  cmd=[str(compiler),'/nologo','/Zs','/TP','/diagnostics:column','/FC','/W3','/utf-8',str(path)]
  started=time.perf_counter();p=subprocess.run(cmd,cwd=target,capture_output=True,encoding='utf8',errors='replace',timeout=60,env=env);log=p.stdout+p.stderr
  (target/(row['va']+'.log')).write_text(log,encoding='utf8',newline='\n')
  diags=[]
  for match in re.finditer(r'(?m)^(.+?)\((\d+)(?:,(\d+))?\)\s*:\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)$',log):
   source,line,col,severity,code,message=match.groups();diags.append({'source':source,'line':int(line),'column':int(col or 0),'severity':severity,'code':code,'category':audit.category(code,message),'message':message})
  return {'va':row['va'],'name':row['name'],'source_body_sha256':row['sha256'],'generated_source_sha256':sha(path),'compiler_exit_code':p.returncode,'syntax_passed':p.returncode==0,'seconds':round(time.perf_counter()-started,4),'diagnostics':diags,'error_count':sum('error' in d['severity'] for d in diags),'log_sha256':hashlib.sha256(log.encode()).hexdigest(),**provenance,'compiler_command':cmd}
 print(json.dumps({'cache_reused':len(results),'recompiled':len(pending)}),flush=True)
 with ThreadPoolExecutor(max_workers=jobs) as pool:
  for i,f in enumerate(as_completed([pool.submit(one,item) for item in pending]),1):
   results.append(f.result())
   if i%50==0:print(json.dumps({'changed_completed':i,'changed_total':len(pending)}),flush=True)
 results.sort(key=lambda r:r['va']);errors=collections.Counter();functions=collections.Counter();codes=collections.Counter();examples={}
 for row in results:
  present=set()
  for d in row['diagnostics']:
   if 'error' not in d['severity']:continue
   errors[d['category']]+=1;codes[d['code']]+=1;present.add(d['category']);examples.setdefault(d['category'],[])
   if len(examples[d['category']])<8:examples[d['category']].append({'va':row['va'],**d})
  functions.update(present)
 merged={**baseline,'results':results,'syntax_passed':sum(r['syntax_passed'] for r in results),'syntax_failed':sum(not r['syntax_passed'] for r in results),'errors_by_category':dict(errors.most_common()),'functions_by_error_category':dict(functions.most_common()),'error_codes':dict(codes.most_common()),'examples':examples,'jobs':jobs,'elapsed_seconds':round(time.perf_counter()-begin,3),'headers_sha256':{str(helper):sha(helper)},'cache_reused':5772-len(pending),'recompiled':len(pending),'cache_inputs_sha256':inputs,'source_sha256':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},'limits':baseline['limits']+['Unchanged5515 translation units reuse frozen178 diagnostics after byte-identical generated-source/scalars/exporter checks. Changed257 translation units compile with an explicit include after scalars. Header metadata is not a global forced include.','Baseline pins compiler path/version, not historical compiler binary hash. The current compiler binary is pinned here; baseline historical byte identity is not independently established.']}
 for path,pin in inputs.items():assert sha(Path(path))==pin
 assert len(results)==5772
 (target/'audit.json').write_text(json.dumps(merged,indent=2)+'\n',encoding='utf8')
 return merged

def main():
 p=argparse.ArgumentParser();p.add_argument('--compiler',type=Path,default=audit.DEFAULT_COMPILER);p.add_argument('--jobs',type=int,default=6);p.add_argument('--skip-audit',action='store_true');args=p.parse_args()
 OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 h,names=header();helper=OUT/'ghidra-integer-pcode.h';helper.write_text(h,encoding='utf8',newline='\n');(OUT/'ghidra-scalars-syntax-only.h').write_text(audit.PRIMITIVES,encoding='utf8',newline='\n')
 pins={str((GH/f).relative_to(ROOT)):sha(GH/f) for f in ('opbehavior.cc','typeop.cc','printc.cc')}
 tests=native_tests(args.compiler.resolve(),helper);print(json.dumps({'native_helper_tests':tests['boundary_checks']+tests['exhaustive8_bit_checks']}),flush=True)
 raw=(audit.CORPUS/'decompiled.c').read_bytes();occ=collections.Counter(re.findall(r'\b(?:CONCAT|SUB|[SZ]EXT|CARRY|SCARRY|SBORROW)\d+\b',raw.decode()))
 if not args.skip_audit:
  delta_audit(args.compiler.resolve(),helper,args.jobs)
 baseline_path=ROOT/'local/experiments/v2-compile-corpus-178/prototypes-cpp-0000/audit.json';new_path=OUT/'prototypes-cpp-0000/audit.json'
 report={'schema':1,'module':'Porsche.exe','module_sha256':audit.SHA,'corpus_sha256':hashlib.sha256(raw).hexdigest(),'ghidra_source_sha256':pins,'helper_header_sha256':sha(helper),'implemented_helpers':names,'corpus_helpers':dict(occ),'unsupported_corpus_helpers':{k:v for k,v in occ.items() if k not in names},'native_helper_tests':tests,'script_sha256':sha(Path(__file__)),'limits':['Integer low-bit representations only, little-endian x86. Widths above8 bytes remain unresolved.','No float10 arithmetic, ABI replacement, fake globals, function bodies or corpus mutation.','Copied signatures are decompiler hypotheses. Compile results are syntax-only, not runtime or recovered-function acceptance.']}
 if new_path.exists():
  baseline=json.loads(baseline_path.read_text());new=json.loads(new_path.read_text());assert baseline['pseudo_c_sha256']==new['pseudo_c_sha256'] and baseline['selected_functions']==new['selected_functions']==5772
  for key in ('compiler','compiler_version','primitive_header_sha256','language','phase'):assert baseline[key]==new[key],key
  old={r['va']:r for r in baseline['results']};fresh={r['va']:r for r in new['results']};assert old.keys()==fresh.keys()
  assert all(old[va]['source_body_sha256']==r['source_body_sha256'] for va,r in fresh.items())
  brief=lambda data:{key:data[key] for key in ('syntax_passed','syntax_failed','errors_by_category','functions_by_error_category','error_codes','elapsed_seconds')}
  report.update({'baseline':brief(baseline),'helpers':brief(new),'cache_reused':new['cache_reused'],'recompiled':new['recompiled'],'baseline_audit_sha256':sha(baseline_path),'helper_audit_sha256':sha(new_path),'new_syntax_pass_vas':[va for va,r in fresh.items() if r['syntax_passed'] and not old[va]['syntax_passed']],'lost_syntax_pass_vas':[va for va,r in fresh.items() if not r['syntax_passed'] and old[va]['syntax_passed']],'error_limited_vas':[va for va,r in fresh.items() if any(d['code']=='C1003' for d in r['diagnostics'])]})
 (RUN/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({k:report[k] for k in ('unsupported_corpus_helpers','baseline','helpers','new_syntax_pass_vas','lost_syntax_pass_vas') if k in report}),flush=True)

if __name__=='__main__':main()
