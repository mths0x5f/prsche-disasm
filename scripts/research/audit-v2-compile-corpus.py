"""Isolated MSVC syntax audit; never link, execute or mutate the pseudo-C corpus."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
CORPUS=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
DEFAULT_COMPILER=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86/cl.exe'
PRIMITIVES=r'''/* Syntax-only scalar vocabulary; no algorithms, storage or implementations. */
typedef unsigned char byte;
typedef signed char sbyte;
typedef unsigned short ushort;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef __int64 longlong;
typedef unsigned __int64 ulonglong;
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short undefined2;
typedef struct { unsigned char bytes[3]; } undefined3;
typedef unsigned int undefined4;
typedef struct { unsigned char bytes[5]; } undefined5;
typedef struct { unsigned char bytes[6]; } undefined6;
typedef struct { unsigned char bytes[7]; } undefined7;
typedef unsigned __int64 undefined8;
typedef float float4;
typedef double float8;
/* MSVC long double is not80-bit. Preserve width with an opaque storage type;
   arithmetic/cast errors remain explicit blockers instead of guessing semantics. */
typedef struct { unsigned char bytes[10]; } float10;
typedef struct { unsigned char bytes[16]; } float16;
typedef void code(void);
#ifndef __cplusplus
typedef unsigned char bool;
typedef unsigned short wchar_t;
#endif
'''

def digest(data):return hashlib.sha256(data).hexdigest()

def bodies(raw):
 markers=list(re.finditer(rb'/\* VA ([0-9a-fA-F]+) \*/',raw));result=[]
 for i,m in enumerate(markers):
  data=raw[m.start():markers[i+1].start() if i+1<len(markers) else len(raw)]
  text=data.decode('utf8');plain=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S).strip()
  signature=plain.split('{',1)[0].strip()
  match=re.search(r'\b([A-Za-z_$][\w$]*)\s*\(',signature)
  result.append({'va':m.group(1).decode().lower(),'start':m.start(),'end':m.start()+len(data),'bytes':len(data),'sha256':digest(data),'text':text,'signature':signature,'name':match.group(1) if match else None})
 assert len({r['va'] for r in result})==len(result)
 return result

def category(code,message):
 if 'float10' in message or 'float16' in message:return 'extended_float_representation'
 if re.search(r'CONCAT\d|SUB\d|[SZ]EXT\d|[SC]?CARRY\d|SBORROW\d|[RL]ROTATE|FLOAT_[A-Z]',message):return 'pcode_intrinsic'
 if code=='C3865' or re.search(r'\bthis\b|__thiscall',message):return 'cpp_this_keyword_or_calling_convention'
 if re.search(r'\b_?(?:DAT|PTR|LAB|IMAGE|JUMPTABLE|switchdataD|switchD|s_|u_)_[0-9a-f]',message):return 'missing_global_or_address_symbol'
 if re.search(r'\b(?:in_|unaff_|extraout_|in_stack_)',message):return 'unrecovered_register_or_stack_value'
 if re.search(r'_\d+_\d+_',message):return 'partial_scalar_field_access'
 if re.search(r'FUN_[0-9a-f]+',message) and code in ('C2065','C3861','C4013'):return 'missing_function_declaration'
 if code in ('C2197','C2198','C2660','C2664','C2733','C2371','C2084'):return 'prototype_or_call_type_conflict'
 if code in ('C2061','C2143','C2146','C4430','C3646'):return 'missing_type_or_declaration_syntax'
 if code in ('C2440','C2446','C2106','C2109','C2039','C2227','C2228'):return 'incompatible_type_or_field'
 if code=='C1003':return 'compiler_error_limit'
 if code in ('C2065','C3861','C4013'):return 'missing_declaration_other'
 return 'other_'+code

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--compiler',type=Path,default=DEFAULT_COMPILER);parser.add_argument('--output',type=Path,default=ROOT/'local/experiments/v2-compile-corpus-178');parser.add_argument('--phase',choices=('raw','primitives','prototypes','header'),required=True);parser.add_argument('--language',choices=('c','cpp'),default='c');parser.add_argument('--header',action='append',type=Path,default=[]);parser.add_argument('--jobs',type=int,default=min(6,os.cpu_count() or 1));parser.add_argument('--limit',type=int);parser.add_argument('--start',type=int,default=0);args=parser.parse_args()
 assert args.jobs>0 and args.start>=0
 assert args.phase!='header' or args.header
 raw=(CORPUS/'decompiled.c').read_bytes();all_bodies=bodies(raw);assert len(all_bodies)==5772
 binary=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');binary_path=ROOT/'local/game'/binary['path'];assert digest(binary_path.read_bytes())==SHA
 metadata=json.loads((CORPUS/'decompilation.json').read_text());assert metadata['sha256']==SHA and metadata['pseudo_c_functions']==len(all_bodies)
 selected=all_bodies[args.start:args.start+args.limit if args.limit else None]
 output=args.output.resolve();output.mkdir(parents=True,exist_ok=True);run=output/(args.phase+'-'+args.language+f'-{args.start:04d}'+('-'+str(args.limit) if args.limit else ''));run.mkdir(exist_ok=True)
 primitive_path=output/'ghidra-scalars-syntax-only.h';primitive_path.write_text(PRIMITIVES,encoding='utf8',newline='\n')
 signatures={r['name']:r['signature'] for r in all_bodies if r['name']}
 headers=[p.resolve() for p in args.header];header_pins={str(p):digest(p.read_bytes()) for p in headers}
 source_files=[]
 for row in selected:
  path=run/(row['va']+('.c' if args.language=='c' else '.cpp'));parts=[]
  if args.phase in ('primitives','prototypes'):parts.append('#include "'+primitive_path.as_posix()+'"\n')
  if args.phase=='prototypes':
   names=set(re.findall(r'\b[A-Za-z_$][\w$]*\b',row['text']))&signatures.keys();names.discard(row['name'])
   parts.append('/* Forward declarations copied verbatim from other exported bodies. */\n'+'\n'.join(signatures[name]+';' for name in sorted(names))+'\n')
  parts.append('#line 1 "porsche_va_'+row['va']+'"\n'+row['text']);path.write_text(''.join(parts),encoding='utf8',newline='\n');source_files.append((row,path))
 compiler_env={**os.environ,'VSLANG':'1033'}
 version=subprocess.run([str(args.compiler)],capture_output=True,text=True,encoding='utf8',errors='replace',env=compiler_env);compiler_version=(version.stdout+version.stderr).strip()
 begin=time.perf_counter()
 def compile_one(item):
  row,path=item;command=[str(args.compiler.resolve()),'/nologo','/Zs','/TC' if args.language=='c' else '/TP','/diagnostics:column','/FC','/W3','/utf-8']
  for header in headers:command.append('/FI'+str(header))
  command.append(str(path));before=time.perf_counter();p=subprocess.run(command,cwd=run,capture_output=True,encoding='utf8',errors='replace',timeout=60,env=compiler_env);log=p.stdout+p.stderr
  (run/(row['va']+'.log')).write_text(log,encoding='utf8',newline='\n')
  diagnostics=[]
  for match in re.finditer(r'(?m)^(.+?)\((\d+)(?:,(\d+))?\)\s*:\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)$',log):
   source,line,column,severity,code,message=match.groups();diagnostics.append({'source':source,'line':int(line),'column':int(column or 0),'severity':severity,'code':code,'category':category(code,message),'message':message})
  errors=[d for d in diagnostics if 'error' in d['severity']]
  return {'va':row['va'],'name':row['name'],'source_body_sha256':row['sha256'],'generated_source_sha256':digest(path.read_bytes()),'compiler_exit_code':p.returncode,'syntax_passed':p.returncode==0,'seconds':round(time.perf_counter()-before,4),'diagnostics':diagnostics,'error_count':len(errors),'log_sha256':digest(log.encode())}
 results=[]
 with ThreadPoolExecutor(max_workers=args.jobs) as pool:
  futures={pool.submit(compile_one,item):item[0]['va'] for item in source_files}
  for future in as_completed(futures):
   result=future.result();results.append(result)
   if len(results)%250==0:print(json.dumps({'completed':len(results),'total':len(selected),'phase':args.phase,'language':args.language}),flush=True)
 results.sort(key=lambda r:r['va']);errors=Counter();error_functions=Counter();codes=Counter();examples={}
 for row in results:
  present=set()
  for d in row['diagnostics']:
   if 'error' not in d['severity']:continue
   errors[d['category']]+=1;codes[d['code']]+=1;present.add(d['category']);examples.setdefault(d['category'],[])
   if len(examples[d['category']])<8:examples[d['category']].append({'va':row['va'],**d})
  error_functions.update(present)
 lexical={}
 for name,pattern in {'decompiler_warning':r'WARNING:','overlapping_globals':r'Globals starting with', 'unrecovered_register_or_stack_value':r'\b(?:in_|unaff_|extraout_|in_stack_)\w+', 'partial_scalar_field':r'\._\d+_\d+_', 'pcode_intrinsic':r'\b(?:CONCAT|SUB|[SZ]EXT|CARRY|SCARRY|SBORROW)\d+\b', 'extended_float':r'\bfloat(?:10|16)\b', 'this_parameter_or_value':r'\bthis\b'}.items():
  hits=[{'va':r['va'],'matches':len(re.findall(pattern,r['text']))} for r in all_bodies if re.search(pattern,r['text'])];lexical[name]={'functions':len(hits),'matches':sum(x['matches'] for x in hits),'example_vas':[x['va'] for x in hits[:12]]}
 summary={'schema':1,'module':'Porsche.exe','original_sha256':SHA,'pseudo_c_sha256':digest(raw),'pseudo_c_bytes':len(raw),'total_exported_functions':len(all_bodies),'phase':args.phase,'language':args.language,'selected_functions':len(selected),'syntax_passed':sum(r['syntax_passed'] for r in results),'syntax_failed':sum(not r['syntax_passed'] for r in results),'jobs':args.jobs,'elapsed_seconds':round(time.perf_counter()-begin,3),'compiler':str(args.compiler.resolve()),'compiler_version':compiler_version,'headers_sha256':header_pins,'primitive_header_sha256':digest(PRIMITIVES.encode()),'errors_by_category':dict(errors.most_common()),'functions_by_error_category':dict(error_functions.most_common()),'error_codes':dict(codes.most_common()),'examples':examples,'lexical_full_corpus':lexical,'results':results,'limits':['Syntax-only experiment: no linked executable, generated algorithms, storage definitions, function stubs or corpus edits.','Forward prototypes are copied from decompiler output, not treated as recovered ABI facts. Primitive vocabulary is syntax scaffolding; extended floats retain opaque10/16-byte storage and arithmetic remains an explicit error.','Syntax success does not prove runtime behavior, original ABI, overlapping-data identity, initialization, imports, x87 or hidden register semantics. Error-limited functions are listed individually.'],'source_sha256':{str(Path(__file__).relative_to(ROOT)):digest(Path(__file__).read_bytes().replace(b'\r\n',b'\n')),'scripts/research/ghidra/ExportRecoveryCorpus.java':digest((ROOT/'scripts/research/ghidra/ExportRecoveryCorpus.java').read_bytes().replace(b'\r\n',b'\n'))}}
 assert digest((CORPUS/'decompiled.c').read_bytes())==summary['pseudo_c_sha256']
 for path,sha in header_pins.items():assert digest(Path(path).read_bytes())==sha
 (run/'audit.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8');print(json.dumps({key:summary[key] for key in ('phase','language','selected_functions','syntax_passed','syntax_failed','elapsed_seconds','errors_by_category')}))
if __name__=='__main__':main()
