"""Run183: exact24-bit cast arguments to PIECE; no global type/ABI guesses."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'local/experiments/v2-pcode-types-183'
RUN=ROOT/'iterations/v2/001-original-recovery/runs/183-pcode-typing'
BASE=ROOT/'local/experiments/v2-pcode-compat-180/prototypes-cpp-0000/audit.json'
spec=importlib.util.spec_from_file_location('compat180',ROOT/'scripts/research/experiment-v2-pcode-compat.py');compat=importlib.util.module_from_spec(spec);spec.loader.exec_module(compat)
audit=compat.audit
INT_TYPES='bool byte sbyte char short ushort int uint long ulong longlong ulonglong undefined undefined1 undefined2 undefined4 undefined8'.split()
HELPER=OUT.parent/'v2-pcode-compat-180/ghidra-integer-pcode.h'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def closing(text,start):
 depth=0;quote=None;i=start
 while i<len(text):
  c=text[i]
  if quote:
   if c=='\\':i+=2;continue
   if c==quote:quote=None
  elif c in ('"',"'"):quote=c
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return i
  i+=1
 return None

def args_at(text,start,end):
 parts=[];depth=0;quote=None;begin=start+1;i=begin
 while i<end:
  c=text[i]
  if quote:
   if c=='\\':i+=2;continue
   if c==quote:quote=None
  elif c in ('"',"'"):quote=c
  elif c=='(':depth+=1
  elif c==')':depth-=1
  elif c==',' and depth==0:parts.append((begin,i));begin=i+1
  i+=1
 parts.append((begin,end));return parts

def strip_outer(text):
 text=text.strip()
 while text.startswith('(') and closing(text,0)==len(text)-1:text=text[1:-1].strip()
 return text

def rewrite(body):
 # Only scalar DECLARATIONS, not name prefixes or guessed variable meanings.
 pattern=r'\b('+ '|'.join(INT_TYPES)+r')\s+([A-Za-z_]\w*)\s*(?=[,;)=])'
 scalar={m.group(2):m.group(1) for m in re.finditer(pattern,body)}
 replacements=[]
 for call in re.finditer(r'\bCONCAT([1-8])([1-8])\s*\(',body):
  widths=list(map(int,call.groups()))
  if sum(widths)>8:continue
  start=body.find('(',call.start());end=closing(body,start)
  if end is None:continue
  spans=args_at(body,start,end)
  if len(spans)!=2:continue
  for width,(a,b) in zip(widths,spans):
   if width!=3:continue
   arg=body[a:b];value=strip_outer(arg);cast=re.match(r'^\((int3|uint3|undefined3)\)\s*',value)
   if not cast:continue
   expr=value[cast.end():].strip()
   if expr.startswith('('):
    end_expr=closing(expr,0)
    if end_expr!=len(expr)-1:continue
    expr=expr[1:-1]
   elif not re.fullmatch(r'[A-Za-z_]\w*',expr):continue
   # A conservative integer-expression proof: every variable is explicitly
   # declared scalar integer. Known CONCAT results may only be2/4/8-byte scalar.
   tokens=set(re.findall(r'\b[A-Za-z_]\w*\b',expr))
   constants=set(re.findall(r'\b(?:0x[0-9a-fA-F]+|\d+)(?:ULL|LL|UL|U|L)?\b',expr))
   permitted=set(INT_TYPES)|set(scalar)|{'true','false'}
   permitted|={name for name in tokens if re.fullmatch(r'CONCAT[1-8][1-8]',name) and sum(map(int,name[6:])) in (2,4,8)}
   unknown=tokens-permitted-constants
   if unknown or re.search(r'\._\d+_\d+_|\bfloat|\bdouble|\b(?:in_|unaff_|extraout_)',expr):continue
   replacement='p180_write<undefined3>('+expr+')'
   replacements.append({'start':a,'end':b,'old':arg,'new':replacement,'cast':cast.group(1),'helper':call.group().split('(')[0].strip(),'integer_variables':{name:scalar[name] for name in sorted(tokens&scalar.keys())},'proof':'Whole3-byte PIECE argument: low24 bits of an explicitly integer expression; signedness cannot change copied bits.'})
 # Nested call arguments may overlap; accept innermost nonoverlapping spans.
 chosen=[]
 for r in sorted(replacements,key=lambda r:(r['end']-r['start'],r['start'])):
  if not any(r['start']<c['end'] and c['start']<r['end'] for c in chosen):chosen.append(r)
 rewritten=body
 for r in sorted(chosen,key=lambda r:r['start'],reverse=True):rewritten=rewritten[:r['start']]+r['new']+rewritten[r['end']:]
 return rewritten,sorted(chosen,key=lambda r:r['start'])

def native_tests(compiler):
 # Real signed/unsigned scalar argument types, including carriers wider than
 # the p-code operand. Expected results use Python unlimited-width integers.
 scalar=lambda n,s:({1:'signed char',2:'short',4:'int',8:'__int64'}[next(w for w in (1,2,4,8) if w>=n)] if s else {1:'unsigned char',2:'unsigned short',4:'unsigned int',8:'unsigned __int64'}[next(w for w in (1,2,4,8) if w>=n)])
 value=lambda x,n,s:f'({scalar(n,s)})0x{x:x}ULL'
 source='#include "'+(HELPER.parent/'ghidra-scalars-syntax-only.h').as_posix()+'"\n#include "'+HELPER.as_posix()+'"\nint main(){\n';checks=0
 def check(expr,n,want):
  nonlocal source,checks
  checks+=1;source+=f'if(p180_read<{n}>({expr})!=0x{want&compat.mask(n):x}ULL)return {checks%250+1};\n'
 for a in range(1,9):
  for b in range(1,9-a):
   for sa in (False,True):
    for sb in (False,True):
     for x in (0,1,compat.mask(a),1<<(8*a-1)):
      for y in (0,1,compat.mask(b),1<<(8*b-1)):check(f'CONCAT{a}{b}({value(x,a,sa)},{value(y,b,sb)})',a+b,(x<<(8*b))|y)
 for x in (0,1,0x7fffff,0x800000,0xffffff,0x12345678,0xffffffff):
  for signed in (False,True):
   v=value(x,4,signed)
   for lo in (0,1,255):
    check(f'CONCAT31(p180_write<undefined3>({v}),{lo})',4,((x&0xffffff)<<8)|lo)
    check(f'CONCAT13({lo},p180_write<undefined3>({v}))',4,(lo<<24)|(x&0xffffff))
 source+='return 0;}\n';path=OUT/'mixed-scalar-vectors.cpp';path.write_text(source,encoding='utf8')
 obj=OUT/'mixed-scalar-vectors.obj';exe=OUT/'mixed-scalar-vectors.exe';libs=compiler.parents[3]/'lib/x86'
 commands=[[str(compiler),'/nologo','/c','/TP','/O2','/GS-','/utf-8','/Fo'+str(obj),str(path)],[str(compiler.with_name('link.exe')),'/nologo','/nodefaultlib','/entry:main','/subsystem:console','/machine:x86','/out:'+str(exe),str(obj),str(libs/'libvcruntime.lib'),str(libs/'libcmt.lib')]]
 log=''
 for command in commands:
  p=subprocess.run(command,capture_output=True,text=True);log+=p.stdout+p.stderr
  assert p.returncode==0,log
 p=subprocess.run([str(exe)],capture_output=True,text=True);assert p.returncode==0,p.returncode
 (OUT/'mixed-scalar-vectors.log').write_text(log,encoding='utf8')
 return {'checks':checks,'exit_code':p.returncode,'commands':commands,'source_sha256':sha(path),'exe_sha256':sha(exe)}

def main():
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=6);args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 baseline=json.loads(BASE.read_text());compiler=Path(baseline['compiler']);raw=(audit.CORPUS/'decompiled.c').read_bytes();assert hashlib.sha256(raw).hexdigest()==baseline['pseudo_c_sha256']
 bodymap={r['va']:r for r in audit.bodies(raw)};oldmap={r['va']:r for r in baseline['results']};assert len(oldmap)==5772
 pins={str(BASE):sha(BASE),str(HELPER):sha(HELPER),str(compiler):sha(compiler),str(HELPER.parent/'ghidra-scalars-syntax-only.h'):sha(HELPER.parent/'ghidra-scalars-syntax-only.h'),str(audit.CORPUS/'decompiled.c'):sha(audit.CORPUS/'decompiled.c')}
 assert pins[str(HELPER)]==baseline['headers_sha256'][str(HELPER)] and pins[str(HELPER.parent/'ghidra-scalars-syntax-only.h')]==baseline['primitive_header_sha256']
 env={**os.environ,'VSLANG':'1033'};v=subprocess.run([str(compiler)],capture_output=True,text=True,encoding='utf8',errors='replace',env=env);assert (v.stdout+v.stderr).strip()==baseline['compiler_version']
 tests=native_tests(compiler);target=OUT/'prototypes-cpp-0000';target.mkdir(exist_ok=True);results=[];pending=[];rewrites=[];deduction=[]
 started=time.perf_counter()
 for va,old in oldmap.items():
  body=bodymap[va];assert old['source_body_sha256']==body['sha256'];src=Path(old['generated_source']);data=src.read_bytes();assert hashlib.sha256(data).hexdigest()==old['generated_source_sha256']
  revised,changes=rewrite(body['text'])
  for d in old['diagnostics']:
   if d['code']=='C2672' and d['category']=='pcode_intrinsic':
    lines=body['text'].splitlines();context='\n'.join(lines[d['line']-1:d['line']+5]);causes=[]
    if re.search(r'\._\d+_\d+_',context):causes.append('partial_scalar_field')
    if re.search(r'\b_?(?:DAT|PTR|s|u)_\w+',context):causes.append('undeclared_original_global')
    if re.search(r'\b(?:NAN|float10|in_ST\d|extraout_)',context):causes.append('extended_float_or_hidden_state')
    if re.search(r'\((?:int3|uint3|undefined3)\)',context):causes.append('nonstandard24_bit_cast')
    deduction.append({'va':va,'line':d['line'],'context':context,'observed_dependencies':causes or ['requires_specific_argument_trace']})
  provenance={'baseline_generated_source':str(src),'baseline_generated_source_sha256':old['generated_source_sha256'],'forced_headers':old['forced_headers'],'compatibility_header':old['compatibility_header'],'cache_reused':not changes}
  if changes:
   assert data.count(body['text'].encode())==1
   data=data.replace(body['text'].encode(),revised.encode());path=target/(va+'.cpp');path.write_bytes(data)
   rewrites.append({'va':va,'changes':changes});pending.append((body,path,provenance))
  else:results.append({**old,**provenance,'generated_source':str(src)})
 print(json.dumps({'native_checks':tests['checks'],'changed_functions':len(pending),'rewrites':sum(len(r['changes']) for r in rewrites),'cache_reused':len(results)}),flush=True)
 def one(item):
  row,path,provenance=item;cmd=[str(compiler),'/nologo','/Zs','/TP','/diagnostics:column','/FC','/W3','/utf-8',str(path)];before=time.perf_counter();p=subprocess.run(cmd,cwd=target,capture_output=True,encoding='utf8',errors='replace',timeout=60,env=env);log=p.stdout+p.stderr;(target/(row['va']+'.log')).write_text(log,encoding='utf8');diags=[]
  for m in re.finditer(r'(?m)^(.+?)\((\d+)(?:,(\d+))?\)\s*:\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)$',log):
   source,line,col,severity,code,message=m.groups();diags.append({'source':source,'line':int(line),'column':int(col or 0),'severity':severity,'code':code,'category':audit.category(code,message),'message':message})
  return {'va':row['va'],'name':row['name'],'source_body_sha256':row['sha256'],'generated_source':str(path),'generated_source_sha256':sha(path),'compiler_exit_code':p.returncode,'syntax_passed':p.returncode==0,'seconds':round(time.perf_counter()-before,4),'diagnostics':diags,'error_count':sum('error' in d['severity'] for d in diags),'log_sha256':hashlib.sha256(log.encode()).hexdigest(),'compiler_command':cmd,**provenance}
 with ThreadPoolExecutor(max_workers=args.jobs) as pool:
  for f in as_completed([pool.submit(one,item) for item in pending]):results.append(f.result())
 results.sort(key=lambda r:r['va']);errors=Counter();functions=Counter();codes=Counter()
 for row in results:
  present=set()
  for d in row['diagnostics']:
   if 'error' in d['severity']:errors[d['category']]+=1;codes[d['code']]+=1;present.add(d['category'])
  functions.update(present)
 merged={**baseline,'results':results,'syntax_passed':sum(r['syntax_passed'] for r in results),'syntax_failed':sum(not r['syntax_passed'] for r in results),'errors_by_category':dict(errors.most_common()),'functions_by_error_category':dict(functions.most_common()),'error_codes':dict(codes.most_common()),'cache_reused':5772-len(pending),'recompiled':len(pending),'cache_inputs_sha256':pins,'source_sha256':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},'elapsed_seconds':round(time.perf_counter()-started,3),'limits':baseline['limits']+['Run183 rewrites only whole3-byte CONCAT argument casts of syntactically proven integer expressions into exact24-bit representation packing. Other int3 arithmetic, globals, partial fields, floats and ABI remain unresolved.']}
 for path,pin in pins.items():assert sha(Path(path))==pin
 for row in results:assert sha(Path(row['generated_source']))==row['generated_source_sha256']
 (target/'audit.json').write_text(json.dumps(merged,indent=2)+'\n',encoding='utf8')
 report={'schema':1,'original_sha256':audit.SHA,'corpus_sha256':baseline['pseudo_c_sha256'],'source_sha256':merged['source_sha256'],'input_sha256':pins,'native_tests':tests,'total_functions':5772,'cache_reused':merged['cache_reused'],'recompiled':len(pending),'rewrites':rewrites,'deduction_diagnostics':deduction,'syntax_baseline':baseline['syntax_passed'],'syntax_after':merged['syntax_passed'],'new_syntax_pass_vas':[r['va'] for r in results if r['syntax_passed'] and not oldmap[r['va']]['syntax_passed']],'lost_syntax_pass_vas':[r['va'] for r in results if not r['syntax_passed'] and oldmap[r['va']]['syntax_passed']],'pcode_errors_before':baseline['errors_by_category']['pcode_intrinsic'],'pcode_errors_after':errors['pcode_intrinsic'],'error_limited_vas':[r['va'] for r in results if any(d['code']=='C1003' for d in r['diagnostics'])],'elapsed_seconds':merged['elapsed_seconds'],'limits':merged['limits']}
 (RUN/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({k:report[k] for k in ('cache_reused','recompiled','syntax_baseline','syntax_after','new_syntax_pass_vas','lost_syntax_pass_vas','pcode_errors_before','pcode_errors_after','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
