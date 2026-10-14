"""Run189: byte-exact local scalar slices in narrow proven bitvector contexts."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'local/experiments/v2-scalar-slices-189';RUN=ROOT/'iterations/v2/001-original-recovery/runs/189-scalar-slices'
BASE=ROOT/'local/experiments/v2-declaration-compat-184/full/audit.json'
GH=ROOT/'local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/src/decompile/cpp'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=module('decl184',ROOT/'scripts/research/experiment-v2-declarations-184.py')
parser183=module('types183',ROOT/'scripts/research/experiment-v2-pcode-types-183.py')
SIZES={'byte':1,'sbyte':1,'char':1,'short':2,'ushort':2,'int':4,'uint':4,'long':4,'ulong':4,'longlong':8,'ulonglong':8,'undefined':1,'undefined1':1,'undefined2':2,'undefined4':4,'undefined8':8,'float':4,'float4':4,'double':8,'float8':8}
FLOATS={'float','float4','double','float8'}
FIELD=re.compile(r'\b([A-Za-z_]\w*)\._(\d+)_(\d+)_')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,text):path.write_text(text,encoding='utf8',newline='\n')
def dump(path,value):write(path,json.dumps(value,indent=2)+'\n')

def helper():
 text='''#pragma once
#ifndef _M_IX86
#error Run189 requires little-endian MSVC x86
#endif
template<class T> struct p189_integer { enum { value=0 }; };
'''
 for t in ('char','signed char','unsigned char','short','unsigned short','int','unsigned int','long','unsigned long','__int64','unsigned __int64'):text+=f'template<> struct p189_integer<{t}> {{ enum {{ value=1 }}; }};\n'
 text+='template<int N> struct p189_result;\n'
 for n,t in ((1,'unsigned char'),(2,'unsigned short'),(3,'undefined3'),(4,'unsigned int'),(5,'undefined5'),(6,'undefined6'),(7,'undefined7'),(8,'unsigned __int64')):text+=f'template<> struct p189_result<{n}> {{ typedef {t} type; }};\n'
 text+='''template<int O,int N,class T> static typename p189_result<N>::type p189_read(const T& value) {
 static_assert(O>=0 && N>0 && O+N<=sizeof(T),"scalar slice bounds");
 typename p189_result<N>::type result={};
 unsigned char* out=reinterpret_cast<unsigned char*>(&result);
 const unsigned char* in=reinterpret_cast<const unsigned char*>(&value);
 for(int i=0;i<N;++i)out[i]=in[O+i];
 return result;
}
template<int O,class T> static bool p189_nonzero(const T& value) {
 static_assert(p189_integer<T>::value && O>=0 && O+1<=sizeof(T),"integer byte zero test only");
 return reinterpret_cast<const unsigned char*>(&value)[O]!=0;
}
template<int D,int S,int N,class T,class U> static void p189_copy(T& dst,const U& src) {
 static_assert(p189_integer<T>::value && p189_integer<U>::value,"integer representation copies only");
 static_assert(D>=0 && S>=0 && N>0 && D+N<=sizeof(T) && S+N<=sizeof(U),"integer slice copy bounds");
 unsigned char snapshot[N];
 const unsigned char* in=reinterpret_cast<const unsigned char*>(&src);
 unsigned char* out=reinterpret_cast<unsigned char*>(&dst);
 for(int i=0;i<N;++i)snapshot[i]=in[S+i];
 for(int i=0;i<N;++i)out[D+i]=snapshot[i];
}
template<int D,int N,class T,class U> static void p189_store(T& dst,const U& value) { p189_copy<D,0,N>(dst,value); }
'''
 return text

def lower(body):
 decls={}
 for m in re.finditer(r'\b('+ '|'.join(sorted(SIZES,key=len,reverse=True))+r')\s+([A-Za-z_]\w*)\s*(?=[,;)=])',body):
  if re.search(r'(?:const|volatile)\s*$',body[max(0,m.start()-24):m.start()]):continue
  name=m.group(2)
  if name.startswith(('DAT_','PTR_','in_','unaff_','extraout_')):continue
  if name in decls:decls[name]=None
  else:decls[name]={'type':m.group(1),'bytes':SIZES[m.group(1)],'integer':m.group(1) not in FLOATS}
 fields=list(FIELD.finditer(body));edits=[]
 def valid(name,o,n,integer=False):
  d=decls.get(name);return bool(d and 0<=o and 0<n<=8 and o+n<=d['bytes'] and (d['integer'] or not integer))
 def add(a,b,new,kind):
  if not any(a<e['end'] and e['start']<b for e in edits):edits.append({'start':a,'end':b,'old':body[a:b],'new':new,'kind':kind})
 def place(token):
  m=FIELD.fullmatch(token)
  if m:
   name=m.group(1);o,n=map(int,m.groups()[1:]);return (name,o,n) if valid(name,o,n,True) else None
  d=decls.get(token);return (token,0,d['bytes']) if d and d['integer'] else None
 # Whole, standalone integer statements only. A snapshot also handles overlap.
 for m in re.finditer(r'(?m)^([ \t]*)([A-Za-z_]\w*(?:\._\d+_\d+_)?)[ \t]*=[ \t]*([^;\n]+);',body):
  left,right=m.group(2),parser183.strip_outer(m.group(3));dst=place(left);src=place(right)
  if not dst or not (FIELD.fullmatch(left) or FIELD.fullmatch(right)):continue
  if src:
   dn,do,dw=dst;sn,so,sw=src
   if FIELD.fullmatch(left):
    if sw<dw:continue
   elif sw!=dw:continue
   add(m.start(),m.end(),f'{m.group(1)}p189_copy<{do},{so},{dw}>({dn},{sn});','standalone_integer_copy')
  elif FIELD.fullmatch(left) and re.fullmatch(r'-?(?:0x[0-9a-fA-F]+|\d+)[uUlL]*|\'\\0\'',right):
   dn,do,dw=dst;minimum=1 if right=="'\\0'" else 8 if 'll' in right.lower() else 4
   if dw<=minimum:add(m.start(),m.end(),f'{m.group(1)}p189_store<{do},{dw}>({dn},{right});','standalone_integer_constant_store')
 # Exact CONCAT arguments are byte vectors, so no signedness inference is used.
 for call in re.finditer(r'\bCONCAT([1-8])([1-8])\s*\(',body):
  widths=list(map(int,call.groups()));start=body.find('(',call.start());end=parser183.closing(body,start)
  if end is None or sum(widths)>8:continue
  spans=parser183.args_at(body,start,end)
  if len(spans)!=2:continue
  for n,(a,b) in zip(widths,spans):
   f=FIELD.fullmatch(parser183.strip_outer(body[a:b]))
   if not f:continue
   name=f.group(1);o,w=map(int,f.groups()[1:])
   if n==w and valid(name,o,w):add(a,b,f'p189_read<{o},{w}>({name})','exact_concat_bitvector_read')
 # One-byte integer zero tests; larger widths could hide a floating field type.
 for f in fields:
  name=f.group(1);o,w=map(int,f.groups()[1:])
  if w!=1 or not valid(name,o,w,True):continue
  before=body[:f.start()].rstrip()
  if not (before.endswith('(') or before.endswith('&&') or before.endswith('||')):continue
  tail=re.match(r'\s*(==|!=)\s*(0(?![\w.])|\'\\0\')',body[f.end():])
  if not tail:continue
  end=f.end()+tail.end();after=body[end:].lstrip()
  if not (not after or after.startswith((')','&&','||',';',',','?'))):continue
  expr=f'p189_nonzero<{o}>({name})'
  add(f.start(),end,'(!'+expr+')' if tail.group(1)=='==' else '('+expr+')','integer_byte_zero_test')
 excluded=[]
 for f in fields:
  if any(e['start']<=f.start() and f.end()<=e['end'] for e in edits):continue
  name=f.group(1);o,n=map(int,f.groups()[1:]);d=decls.get(name)
  reason='unsupported_context_or_signedness'
  if not d:reason='not_unique_supported_local_or_param'
  elif n<=0 or n>8 or o+n>d['bytes']:reason='unproven_extent'
  excluded.append({'object':name,'offset':o,'bytes':n,'declaration':d,'reason':reason,'line':body.count('\n',0,f.start())+1})
 result=body
 for e in sorted(edits,key=lambda e:e['start'],reverse=True):result=result[:e['start']]+e['new']+result[e['end']:]
 return result,edits,excluded

def native(compiler,header,primitive):
 source='#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'
 source+='template<class T> void init(T& x,unsigned __int64 v){unsigned char* p=reinterpret_cast<unsigned char*>(&x);for(unsigned i=0;i<sizeof(T);++i)p[i]=(unsigned char)(v>>(i*8));}\nint main(){\n';checks=0
 def bytes_check(var,n,want):
  nonlocal source,checks
  for i in range(n):checks+=1;source+=f'if(reinterpret_cast<const unsigned char*>(&{var})[{i}]!={want>>(8*i)&255})return {checks%250+1};\n'
 for t,size,integer in [('unsigned int',4,True),('int',4,True),('unsigned __int64',8,True),('__int64',8,True),('float',4,False),('double',8,False)]:
  for value in (0,(1<<(8*size))-1,0x0123456789abcdef&((1<<(8*size))-1),0x7f800001 if size==4 else 0x7ff0000000000001):
   for n in range(1,size+1):
    for o in sorted({0,size-n}):
     source+=f'{{{t} x;init(x,0x{value:x}ULL);auto y=p189_read<{o},{n}>(x);\n';bytes_check('y',n,value>>(8*o));source+='}\n'
   if integer:
    for n in (1,2,size):
     for d in sorted({0,size-n}):
      for s in sorted({0,size-n}):
       wanted=(value&~(((1<<(8*n))-1)<<(8*d)))|(((value>>(8*s))&((1<<(8*n))-1))<<(8*d))
       source+=f'{{{t} x;init(x,0x{value:x}ULL);p189_copy<{d},{s},{n}>(x,x);\n';bytes_check('x',size,wanted);source+='}\n'
    for o in range(size):
     source+=f'{{{t} x;init(x,0x{value:x}ULL);if(p189_nonzero<{o}>(x)!={int(bool((value>>(8*o))&255))})return 251;}}\n';checks+=1
 source+='return 0;}\n';path=OUT/'slice-oracle.cpp';write(path,source);obj=OUT/'slice-oracle.obj';exe=OUT/'slice-oracle.exe';libs=compiler.parents[3]/'lib/x86'
 commands=[[str(compiler),'/nologo','/c','/TP','/O2','/GS-','/utf-8','/Fo'+str(obj),str(path)],[str(compiler.with_name('link.exe')),'/nologo','/nodefaultlib','/entry:main','/subsystem:console','/machine:x86','/out:'+str(exe),str(obj),str(libs/'libvcruntime.lib'),str(libs/'libcmt.lib')]]
 log=''
 for cmd in commands:
  p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace');log+=p.stdout+p.stderr;assert p.returncode==0,log
 p=subprocess.run([str(exe)]);assert p.returncode==0,p.returncode;write(OUT/'slice-oracle.log',log)
 return {'checks':checks,'exit_code':p.returncode,'commands':commands,'source_sha256':sha(path),'exe_sha256':sha(exe)}

def main():
 p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--jobs',type=int,default=6);args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 base=json.loads(BASE.read_text());compiler=Path(base['compiler']);primitive=ROOT/'local/experiments/v2-pcode-compat-180/ghidra-scalars-syntax-only.h';header=OUT/'scalar-slices.h';write(header,helper())
 pins={str(BASE):sha(BASE),str(compiler):sha(compiler),str(primitive):sha(primitive),str(header):sha(header)}
 for path,pin in base['headers_sha256'].items():assert sha(Path(path))==pin;pins[path]=pin
 for path,pin in base['source_sha256'].items():assert sha(ROOT/path)==pin;pins[str(ROOT/path)]=pin
 for f in ('printc.cc','printlanguage.cc','opbehavior.cc'):pins[str(GH/f)]=sha(GH/f)
 env={**os.environ,'VSLANG':'1033'};v=subprocess.run([str(compiler)],capture_output=True,text=True,encoding='utf8',errors='replace',env=env);assert (v.stdout+v.stderr).strip()==base['compiler_version']
 candidates=[];inventory=[];oldmap={r['va']:r for r in base['results']};source_pins={}
 for va,old in oldmap.items():
  path=Path(old['generated_source']);data=path.read_bytes();assert sha(path)==old['generated_source_sha256'];source_pins[str(path)]=old['generated_source_sha256']
  marker=re.search(rb'#line 1 "porsche_va_'+va.encode()+rb'"\r?\n',data);assert marker
  body=data[marker.end():].decode();changed,edits,excluded=lower(body)
  if edits:candidates.append((va,old,data[:marker.end()]+changed.encode(),edits))
  if edits or excluded:inventory.append({'va':va,'rewrites':edits,'excluded':excluded})
 print(json.dumps({'eligible_functions':len(candidates),'rewrites':sum(len(r[3]) for r in candidates),'exclusions':dict(Counter(x['reason'] for r in inventory for x in r['excluded']))}),flush=True)
 if args.full:
  pilot=json.loads((RUN/'pilot.json').read_text());assert pilot['input_pins']==pins and pilot['native_tests']['exit_code']==0 and not pilot['lost_syntax_pass_vas'];tests=pilot['native_tests']
 else:tests=native(compiler,header,primitive)
 selected=candidates if args.full else candidates[:12];target=OUT/('full' if args.full else 'pilot');target.mkdir(exist_ok=True);items=[]
 for va,old,data,edits in selected:
  first,rest=data.split(b'\n',1);path=target/(va+'.cpp');path.write_bytes(first+b'\n#include "'+header.as_posix().encode()+b'"\n'+rest);items.append((va,old,path))
 started=time.perf_counter();fresh=[];batch_reports=[];fallbacks=[];pilot_cached=0
 if args.full:
  old_pilot={r['va']:r for r in json.loads((OUT/'pilot/results.json').read_text())};todo=[]
  for item in items:
   cached=old_pilot.get(item[0])
   if cached and cached['generated_source_sha256']==sha(item[2]) and cached['scalar_slice_header_sha256']==sha(header):
    assert sha(Path(cached['generated_source']))==cached['generated_source_sha256'];fresh.append({**cached,'pilot_cache_reused':True});pilot_cached+=1
   else:todo.append(item)
  items=todo
 def row(item,ds,log,passed,exitcode,command,**extra):
  va,old,path=item;return {**old,'generated_source':str(path),'generated_source_sha256':sha(path),'baseline_generated_source':old['generated_source'],'baseline_generated_source_sha256':old['generated_source_sha256'],'cache_reused':False,'forced_headers':[],'scalar_slice_header':str(header),'scalar_slice_header_sha256':sha(header),'syntax_passed':passed,'compiler_exit_code':exitcode,'diagnostics':ds,'error_count':sum('error' in d['severity'] for d in ds),'log_sha256':hashlib.sha256(log.encode()).hexdigest(),'compiler_command':command,**extra}
 for start in range(0,len(items),64):
  chunk=items[start:start+64];cmd=[str(compiler),'/nologo','/Zs',f'/MP{args.jobs}','/TP','/diagnostics:column','/FC','/W3','/utf-8']+[str(i[2]) for i in chunk];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace',env=env,timeout=180);log=p.stdout+p.stderr;logpath=target/f'batch-{start//64:03d}.log';write(logpath,log);ds=prior.diagnostics(log);vas={i[0] for i in chunk};markers=re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$',log,re.I);ambiguous=set(markers)!=vas or len(markers)!=len(vas) or any(prior.diagnostic_owner(d['source']) not in vas for d in ds) or len(re.findall(r'(?m)^.*?:\s*(?:fatal error|error|warning)\s+[CD]\d+:',log))!=len(ds) or(p.returncode!=0 and not any('error' in d['severity'] for d in ds))
  batch_reports.append({'command':cmd,'exit_code':p.returncode,'log':str(logpath),'log_sha256':sha(logpath),'ambiguous':bool(ambiguous)})
  if ambiguous:
   fallbacks.append(sorted(vas))
   for item in chunk:
    command=[str(compiler),'/nologo','/Zs','/TP','/diagnostics:column','/FC','/W3','/utf-8',str(item[2])];q=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',env=env,timeout=60);text=q.stdout+q.stderr;write(target/(item[0]+'.log'),text);fresh.append(row(item,prior.diagnostics(text),text,q.returncode==0,q.returncode,command))
  else:
   for item in chunk:
    own=[d for d in ds if prior.diagnostic_owner(d['source'])==item[0]];fresh.append(row(item,own,log,not any('error' in d['severity'] for d in own),None,cmd,batch_compiler_exit_code=p.returncode,batch_log=str(logpath)))
 newpasses=[r['va'] for r in fresh if r['syntax_passed'] and not oldmap[r['va']]['syntax_passed']];lost=[r['va'] for r in fresh if not r['syntax_passed'] and oldmap[r['va']]['syntax_passed']]
 invocations=len(batch_reports)+sum(len(chunk) for chunk in fallbacks)
 report={'schema':1,'phase':'full' if args.full else 'pilot','input_pins':pins,'script_sha256':sha(Path(__file__)),'native_tests':tests,'eligible_functions':len(candidates),'rewrites':sum(len(r[3]) for r in candidates),'inventory':inventory,'selected_functions':len(fresh),'actual_changed_checks':len(items),'actual_compiler_invocations':invocations,'pilot_cache_reused':pilot_cached,'new_syntax_pass_vas':newpasses,'lost_syntax_pass_vas':lost,'batch_reports':batch_reports,'fallback_vas':fallbacks,'elapsed_seconds':round(time.perf_counter()-started,3)}
 if args.full:
  by={r['va']:r for r in fresh};merged_rows=[by.get(va,{**old,'cache_reused':True}) for va,old in oldmap.items()];errors=Counter();functions=Counter();codes=Counter()
  for r in merged_rows:
   present=set()
   for d in r['diagnostics']:
    if 'error' in d['severity']:errors[d['category']]+=1;present.add(d['category']);codes[d['code']]+=1
   functions.update(present)
  merged={**base,'results':merged_rows,'syntax_passed':sum(r['syntax_passed'] for r in merged_rows),'syntax_failed':sum(not r['syntax_passed'] for r in merged_rows),'errors_by_category':dict(errors.most_common()),'functions_by_error_category':dict(functions.most_common()),'error_codes':dict(codes.most_common()),'cache_reused':5772-len(fresh),'recompiled':len(items),'actual_compiler_invocations':invocations,'recovered_individual_failures':0,'pilot_cache_reused':pilot_cached,'headers_sha256':{**base['headers_sha256'],str(header):sha(header)},'cache_inputs_sha256':pins,'source_sha256':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},'limits':base['limits']+['Run189 lowers only bounded simple local/param slices in exact CONCAT bitvector inputs, integer byte zero tests, and standalone integer representation stores/copies. No general field signedness, FP assignments, globals, aliases, side effects, or ABI inference.']}
  report.update({'syntax_before':base['syntax_passed'],'syntax_after':merged['syntax_passed'],'cache_reused':merged['cache_reused'],'error_limited_vas':[r['va'] for r in merged_rows if any(d['code']=='C1003' for d in r['diagnostics'])]});dump(target/'audit.json',merged)
 for path,pin in {**pins,**source_pins}.items():assert sha(Path(path))==pin
 for r in fresh:assert sha(Path(r['generated_source']))==r['generated_source_sha256']
 dump(target/'results.json',fresh);dump(RUN/('summary.json' if args.full else 'pilot.json'),report);print(json.dumps({k:report[k] for k in ('phase','eligible_functions','rewrites','selected_functions','new_syntax_pass_vas','lost_syntax_pass_vas','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
