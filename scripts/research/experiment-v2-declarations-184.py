"""Run184: per-TU unambiguous179 externs, precise narrow x86 type vocabulary."""
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
OUT=ROOT/'local/experiments/v2-declaration-compat-184'
RUN=ROOT/'iterations/v2/001-original-recovery/runs/184-declaration-compatibility'
EXPORT=ROOT/'iterations/v2/001-original-recovery/runs/179-ghidra-declarations/export'
BASE=ROOT/'local/experiments/v2-pcode-types-183/prototypes-cpp-0000/audit.json'
spec=importlib.util.spec_from_file_location('a178',ROOT/'scripts/research/audit-v2-compile-corpus.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
PRIMITIVES={'void':(0,1),'undefined':(1,1),'undefined1':(1,1),'undefined2':(2,2),'undefined4':(4,4),'undefined8':(8,8),'byte':(1,1),'char':(1,1),'short':(2,2),'ushort':(2,2),'int':(4,4),'uint':(4,4),'long':(4,4),'ulong':(4,4),'longlong':(8,8),'ulonglong':(8,8),'float':(4,4),'double':(8,8)}
IDENT=re.compile(r'^[A-Za-z_$][\w$]*$')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines()]
def diagnostics(log):
 result=[]
 for m in re.finditer(r'(?m)^(.+?)\((\d+)(?:,(\d+))?\)\s*:\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)$',log):
  source,line,col,severity,code,message=m.groups();result.append({'source':source,'line':int(line),'column':int(col or 0),'severity':severity,'code':code,'category':audit.category(code,message),'message':message})
 return result
def diagnostic_owner(source):
 match=re.search(r'porsche_va_([0-9a-f]{8})',source,re.I) or re.search(r'([0-9a-f]{8})(?:-globals)?\.(?:cpp|h)$',source,re.I)
 return match.group(1).lower() if match else None

def resolve_type(path,types,trail=()):
 if path in trail:return None,'recursive_type'
 row=types.get(path)
 if not row:return None,'missing_type_metadata'
 name=row['name'];cls=row['class'];size=row['length'];align=row['alignment']
 if name in PRIMITIVES and 'Typedef' not in cls and 'Pointer' not in cls:
  if (size,align)!=PRIMITIVES[name]:return None,'primitive_layout_mismatch'
  return {'ctype':name,'bytes':size,'alignment':align,'typedefs':[],'type_paths':[path]},None
 if 'Pointer' in cls:
  if (size,align)!=(4,4):return None,'pointer_layout_mismatch'
  pointee=row.get('pointee')
  if not pointee:return None,'unknown_pointer_target'
  base,error=resolve_type(pointee,types,trail+(path,))
  if error:return None,error
  if '[' in base['ctype']:return None,'pointer_to_array_declarator'
  return {'ctype':base['ctype']+' *','bytes':4,'alignment':4,'typedefs':base['typedefs'],'type_paths':base['type_paths']+[path]},None
 if 'Typedef' in cls and IDENT.fullmatch(name):
  base,error=resolve_type(row['base'],types,trail+(path,))
  if error:return None,error
  if (size,align)!=(base['bytes'],base['alignment']):return None,'typedef_layout_mismatch'
  if '[' in base['ctype']:return None,'typedef_array_declarator'
  return {'ctype':name,'bytes':size,'alignment':align,'typedefs':base['typedefs']+[f'typedef {base["ctype"]} {name};'],'type_paths':base['type_paths']+[path]},None
 if 'Array' in cls:
  base,error=resolve_type(row['element_type'],types,trail+(path,))
  if error:return None,error
  if size!=base['bytes']*row['count'] or row['element_bytes']!=base['bytes'] or align!=base['alignment']:return None,'array_layout_mismatch'
  return {'ctype':base['ctype']+f'[{row["count"]}]','bytes':size,'alignment':align,'typedefs':base['typedefs'],'type_paths':base['type_paths']+[path]},None
 return None,'unsupported_'+cls.rsplit('.',1)[-1]

def declarations(types,globals_):
 accepted=[];excluded=[]
 for record in globals_:
  if record['conflict']:excluded.append({'identity':record['identity'],'reason':'conflicting_global_identity'});continue
  assert len(record['variants'])==1
  variant=record['variants'][0];symbol=variant['symbol'];name=symbol.get('name');storage=symbol['storage_detail']
  reason=None;resolved=None
  if symbol.get('namespace')!='Global':reason='non_global_scope_requires_class_or_namespace_model'
  elif not name or not IDENT.fullmatch(name):reason='non_cpp_symbol_spelling'
  elif not storage['memory'] or storage['compound'] or len(storage['varnodes'])!=1:reason='not_single_memory_global'
  elif symbol['type']['class'].endswith('StringDataType'):
   if not re.fullmatch(r'char\s+'+re.escape(name)+r'\['+str(symbol['bytes'])+r'\]',symbol['declaration']):reason='string_native_declarator_mismatch'
   else:resolved={'ctype':f'char[{symbol["bytes"]}]','bytes':symbol['bytes'],'alignment':1,'typedefs':[],'type_paths':[symbol['type']['path']]}
  else:resolved,reason=resolve_type(symbol['type']['path'],types)
  if not reason and (not resolved or resolved['bytes']!=symbol['bytes'] or resolved['bytes']<=0):reason='symbol_type_storage_size_mismatch'
  if reason:excluded.append({'identity':record['identity'],'reason':reason,'symbol':symbol});continue
  accepted.append({'identity':record['identity'],'symbol':symbol,'consumer_vas':variant['consumer_vas'],'resolved':resolved})
 return accepted,excluded

def header(selected):
 aliases=list(dict.fromkeys(x for r in selected for x in r['resolved']['typedefs']))
 text='#pragma once\n/* Exact179 memory externs only; no storage/aliases/function prototypes. */\nstatic_assert(sizeof(void*)==4,"x86 required");\n'+'\n'.join(aliases)+'\n'
 for record in selected:
  s=record['symbol'];t=record['resolved'];name=s['name']
  text+=f'/* {record["identity"]} {s["storage"]} {s["type"]["path"]} */\nextern {s["declaration"]};\nstatic_assert(sizeof(decltype({name}))=={t["bytes"]},"179 global byte width");\nstatic_assert(alignof(decltype({name}))=={t["alignment"]},"179 global alignment");\n'
 return text

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');parser.add_argument('--jobs',type=int,default=6);args=parser.parse_args()
 OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 baseline=json.loads(BASE.read_text());types={r['path']:r for r in rows(EXPORT/'types.jsonl')};globals_=rows(EXPORT/'globals.jsonl')
 # DataTypeManager iteration omits DefaultDataType /undefined. Exported global
 # metadata still supplies its exact canonical class/length/alignment. Seed
 # only missing primitive paths, demanding agreement across all occurrences.
 seeded={}
 for record in globals_:
  for variant in record['variants']:
   t=variant['symbol']['type']
   if t['path'] in types or t['name'] not in PRIMITIVES or (t['length'],t['alignment'])!=PRIMITIVES[t['name']] or 'Typedef' in t['class']:continue
   if t['path'] in seeded:assert seeded[t['path']]['type']==t
   else:seeded[t['path']]={'type':t,'source':'179 globals[].type canonical primitive metadata','identities':[]}
   seeded[t['path']]['identities'].append(record['identity'])
 types.update({path:entry['type'] for path,entry in seeded.items()})
 accepted,excluded=declarations(types,globals_)
 compiler=Path(baseline['compiler']);env={**os.environ,'VSLANG':'1033'}
 pins={str(BASE):sha(BASE),str(EXPORT/'types.jsonl'):sha(EXPORT/'types.jsonl'),str(EXPORT/'globals.jsonl'):sha(EXPORT/'globals.jsonl'),str(EXPORT/'functions.jsonl'):sha(EXPORT/'functions.jsonl'),str(compiler):sha(compiler)}
 for name,pin in baseline['source_sha256'].items():assert sha(ROOT/name)==pin;pins[str(ROOT/name)]=pin
 v=subprocess.run([str(compiler)],capture_output=True,text=True,encoding='utf8',errors='replace',env=env);assert (v.stdout+v.stderr).strip()==baseline['compiler_version']
 assert all(r['module_sha256']==audit.SHA for r in globals_)
 primitive=ROOT/'local/experiments/v2-pcode-compat-180/ghidra-scalars-syntax-only.h';assert sha(primitive)==baseline['primitive_header_sha256'];pins[str(primitive)]=sha(primitive)
 for path,pin in baseline['headers_sha256'].items():assert sha(Path(path))==pin;pins[path]=pin
 # One batch validates all selected declarators and every byte/alignment claim.
 validation=OUT/'all-supported-declarations.h';validation.write_text(header(accepted),encoding='utf8');probe=OUT/'type-layout-probe.cpp';probe.write_text('#include "'+primitive.as_posix()+'"\n#include "'+validation.as_posix()+'"\n',encoding='utf8')
 cmd=[str(compiler),'/nologo','/Zs','/TP','/diagnostics:column','/W3','/utf-8',str(probe)]
 p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace',env=env);(OUT/'type-layout-probe.log').write_text(p.stdout+p.stderr,encoding='utf8');assert p.returncode==0,'type layout probe failed; inspect local log before broadening'
 by_va={}
 for record in accepted:
  for va in record['consumer_vas']:by_va.setdefault(va,[]).append(record)
 candidates=[];oldmap={r['va']:r for r in baseline['results']};source_pins={}
 for va,old in oldmap.items():
  path=Path(old['generated_source']);data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==old['generated_source_sha256'];source_pins[str(path)]=old['generated_source_sha256']
  tokens=set(re.findall(rb'\b[A-Za-z_$][\w$]*\b',data));selected=[r for r in by_va.get(va,[]) if r['symbol']['name'].encode() in tokens]
  if selected:candidates.append((va,old,data,selected))
 if args.full:
  pilot=RUN/'pilot.json';assert pilot.exists(),'run12-body pilot first';pilot_data=json.loads(pilot.read_text());assert pilot_data['type_probe_passed'] and pilot_data['source_pins']==pins and not pilot_data['lost_syntax_pass_vas'] and pilot_data['type_probe_header_sha256']==sha(validation),'pilot provenance mismatch'
  selected_candidates=candidates
 else:
  easy=[r for r in candidates if set(d['category'] for d in r[1]['diagnostics'] if 'error' in d['severity'])=={'missing_global_or_address_symbol'}]
  chosen=easy[:6]+sorted(candidates,key=lambda r:len(r[3]),reverse=True)[:3]
  chosen+= [r for r in candidates if any(d['code']=='C2672' for d in r[1]['diagnostics'])][:3]
  selected_candidates=list({r[0]:r for r in chosen}.values())
 target=OUT/('full' if args.full else 'pilot');target.mkdir(exist_ok=True);started=time.perf_counter();pending=[];changed=set();selection=[];pilot_reused=[]
 pilot_results={r['va']:r for r in json.loads((OUT/'pilot/results.json').read_text())} if args.full else {}
 for va,old,data,records in selected_candidates:
  old_pilot=pilot_results.get(va)
  if old_pilot and old_pilot['baseline_generated_source_sha256']==old['generated_source_sha256'] and Path(old_pilot['declaration_header']).read_text(encoding='utf8')==header(records):
   assert sha(Path(old_pilot['generated_source']))==old_pilot['generated_source_sha256'] and sha(Path(old_pilot['declaration_header']))==old_pilot['declaration_header_sha256']
   pilot_reused.append({**old_pilot,'pilot_cache_reused':True});changed.add(va);selection.append({'va':va,'header':old_pilot['declaration_header'],'header_sha256':old_pilot['declaration_header_sha256'],'identities':[r['identity'] for r in records]});continue
  h=target/(va+'-globals.h');h.write_text(header(records),encoding='utf8');first,rest=data.split(b'\n',1);new=first+b'\n#include "'+h.as_posix().encode()+b'"\n'+rest;path=target/(va+'.cpp');path.write_bytes(new)
  selection.append({'va':va,'header':str(h),'header_sha256':sha(h),'identities':[r['identity'] for r in records]});pending.append((va,old,path,h));changed.add(va)
 print(json.dumps({'phase':'full' if args.full else 'pilot','supported_global_identities':len(accepted),'excluded':dict(Counter(r['reason'] for r in excluded)),'changed_total_candidates':len(candidates),'selected':len(pending)}),flush=True)
 def one(item):
  va,old,path,h=item;command=[str(compiler),'/nologo','/Zs','/TP','/diagnostics:column','/FC','/W3','/utf-8',str(path)];before=time.perf_counter();p=subprocess.run(command,cwd=target,capture_output=True,encoding='utf8',errors='replace',timeout=60,env=env);log=p.stdout+p.stderr;(target/(va+'.log')).write_text(log,encoding='utf8');diags=[]
  for m in re.finditer(r'(?m)^(.+?)\((\d+)(?:,(\d+))?\)\s*:\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)$',log):
   source,line,col,severity,code,message=m.groups();diags.append({'source':source,'line':int(line),'column':int(col or 0),'severity':severity,'code':code,'category':audit.category(code,message),'message':message})
  return {**old,'generated_source':str(path),'generated_source_sha256':sha(path),'baseline_generated_source':old['generated_source'],'baseline_generated_source_sha256':old['generated_source_sha256'],'cache_reused':False,'forced_headers':[],'declaration_header':str(h),'declaration_header_sha256':sha(h),'compiler_exit_code':p.returncode,'syntax_passed':p.returncode==0,'seconds':round(time.perf_counter()-before,4),'diagnostics':diags,'error_count':sum('error' in d['severity'] for d in diags),'log_sha256':hashlib.sha256(log.encode()).hexdigest(),'compiler_command':command}
 fresh=list(pilot_reused);batch_commands=[];batch_fallbacks=[];recovered_failures=0;batch_pilot=None;actual_invocations=0
 def attributed(item,diags,log,syntax_passed,exitcode,seconds,command,**extra):
  va,old,path,h=item
  return {**old,'generated_source':str(path),'generated_source_sha256':sha(path),'baseline_generated_source':old['generated_source'],'baseline_generated_source_sha256':old['generated_source_sha256'],'cache_reused':False,'forced_headers':[],'declaration_header':str(h),'declaration_header_sha256':sha(h),'compiler_exit_code':exitcode,'syntax_passed':syntax_passed,'seconds':seconds,'diagnostics':diags,'error_count':sum('error' in d['severity'] for d in diags),'log_sha256':hashlib.sha256(log.encode()).hexdigest(),'compiler_command':command,**extra}
 def batch(items,label):
  nonlocal actual_invocations
  command=[str(compiler),'/nologo','/Zs',f'/MP{args.jobs}','/TP','/diagnostics:column','/FC','/W3','/utf-8']+[str(item[2]) for item in items]
  before=time.perf_counter();p=subprocess.run(command,cwd=target,capture_output=True,encoding='utf8',errors='replace',timeout=180,env=env);seconds=round(time.perf_counter()-before,3);log=p.stdout+p.stderr;logpath=target/(label+'.log');logpath.write_text(log,encoding='utf8');actual_invocations+=1
  ds=diagnostics(log);vas={item[0] for item in items};markers=re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$',log,re.I)
  unknown=[d for d in ds if diagnostic_owner(d['source']) not in vas]
  all_severities=re.findall(r'(?m)^.*?:\s*(?:fatal error|error|warning)\s+[CD]\d+:',log)
  ambiguous=unknown or len(all_severities)!=len(ds) or set(markers)!=vas or len(markers)!=len(vas) or (p.returncode!=0 and not any('error' in d['severity'] for d in ds))
  batch_commands.append({'label':label,'command':command,'exit_code':p.returncode,'seconds':seconds,'log':str(logpath),'log_sha256':sha(logpath),'files':len(items),'ambiguous':bool(ambiguous)})
  if ambiguous:return None
  by={va:[] for va in vas}
  for d in ds:by[diagnostic_owner(d['source'])].append(d)
  return [attributed(item,by[item[0]],log,not any('error' in d['severity'] for d in by[item[0]]),None,seconds,command,batch_compiler_exit_code=p.returncode,batch_log=str(logpath),batch_files=len(items),batch_attribution='All filenames emitted exactly once; all diagnostics uniquely owned; process completed without unattributable diagnostics.') for item in items]
 if args.full:
  # A failing+passing mixed batch must reproduce completed individual logs.
  completed=[item for item in pending if (target/(item[0]+'.log')).exists()]
  failing=[item for item in completed if any('error' in d['severity'] for d in diagnostics((target/(item[0]+'.log')).read_text(encoding='utf8')))]
  passing_candidates=[item for item in completed if item not in failing]
  pilot_items=failing[:8]+passing_candidates[:4]
  if pilot_items:
   prior={item[0]:diagnostics((target/(item[0]+'.log')).read_text(encoding='utf8')) for item in pilot_items};pilot_rows=batch(pilot_items,'batch-attribution-pilot')
   # /MP appends a localized "compiling source file ...VA.cpp" suffix.
   # Strip only that generated-file annotation for the equivalence comparison;
   # actual messages and raw batch output remain verbatim in the artifacts.
   norm=lambda ds:Counter((d['source'],d['line'],d['column'],d['severity'],d['code'],re.sub(r' \([^()\r\n]*[\\/][0-9a-f]{8}\.cpp\)$','',d['message'],flags=re.I)) for d in ds)
   assert pilot_rows is not None and all(norm(r['diagnostics'])==norm(prior[r['va']]) for r in pilot_rows),'mixed batch attribution pilot mismatch; stop and inspect before mass compile'
   batch_pilot={'files':len(pilot_items),'identical_to_individual_diagnostics':True,'command':batch_commands[-1]};fresh.extend(pilot_rows)
  done={r['va'] for r in fresh};remaining=[]
  for item in pending:
   if item[0] in done:continue
   oldlog=target/(item[0]+'.log')
   if oldlog.exists():
    log=oldlog.read_text(encoding='utf8');ds=diagnostics(log)
    if any('error' in d['severity'] for d in ds) and all(diagnostic_owner(d['source'])==item[0] for d in ds):
     fresh.append(attributed(item,ds,log,False,None,0,None,recovered_individual_failure=True,individual_log=str(oldlog),exit_code_unavailable='Interrupted driver retained complete error-bearing logs, not per-process exit-code sidecars. Failure is proven by actual owned compiler errors; success is never inferred.'));recovered_failures+=1;continue
   remaining.append(item)
  for index in range(0,len(remaining),64):
   items=remaining[index:index+64];result=batch(items,f'batch-{index//64:03d}')
   if result is None:
    batch_fallbacks.append([item[0] for item in items])
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
     for f in as_completed([pool.submit(one,item) for item in items]):fresh.append(f.result());actual_invocations+=1
   else:fresh.extend(result)
   print(json.dumps({'completed_changed':len(fresh),'total_changed':len(selected_candidates),'batch_invocations':actual_invocations,'recovered_individual_failures':recovered_failures}),flush=True)
 else:
  with ThreadPoolExecutor(max_workers=args.jobs) as pool:
   for f in as_completed([pool.submit(one,item) for item in pending]):fresh.append(f.result());actual_invocations+=1
 report={'schema':1,'phase':'full' if args.full else 'pilot','original_sha256':audit.SHA,'source_pins':pins,'script_sha256':sha(Path(__file__)),'seeded_canonical_primitive_metadata':seeded,'type_probe_passed':True,'type_probe_command':cmd,'type_probe_header_sha256':sha(validation),'supported_globals':len(accepted),'excluded_counts':dict(Counter(r['reason'] for r in excluded)),'excluded_globals':excluded,'selected_functions':len(fresh),'actual_compiler_invocations':actual_invocations,'recovered_individual_failures':recovered_failures,'batch_attribution_pilot':batch_pilot,'batch_commands':batch_commands,'batch_fallback_vas':batch_fallbacks,'pilot_cache_reused':len(pilot_reused),'eligible_functions':len(candidates),'selection':selection,'syntax_before':sum(oldmap[r['va']]['syntax_passed'] for r in fresh),'syntax_after':sum(r['syntax_passed'] for r in fresh),'new_syntax_pass_vas':[r['va'] for r in fresh if r['syntax_passed'] and not oldmap[r['va']]['syntax_passed']],'lost_syntax_pass_vas':[r['va'] for r in fresh if not r['syntax_passed'] and oldmap[r['va']]['syntax_passed']],'missing_global_errors_before':sum(d['category']=='missing_global_or_address_symbol' and 'error' in d['severity'] for r in fresh for d in oldmap[r['va']]['diagnostics']),'missing_global_errors_after':sum(d['category']=='missing_global_or_address_symbol' and 'error' in d['severity'] for r in fresh for d in r['diagnostics']),'elapsed_seconds':round(time.perf_counter()-started,3)}
 if args.full:
  merged_rows=sorted(fresh+[{**r,'cache_reused':True} for va,r in oldmap.items() if va not in changed],key=lambda r:r['va']);errors=Counter();functions=Counter();codes=Counter()
  for row in merged_rows:
   present=set()
   for d in row['diagnostics']:
    if 'error' in d['severity']:errors[d['category']]+=1;codes[d['code']]+=1;present.add(d['category'])
   functions.update(present)
  header_pins={r['header']:r['header_sha256'] for r in selection}
  for path,pin in header_pins.items():assert sha(Path(path))==pin
  merged={**baseline,'results':merged_rows,'syntax_passed':sum(r['syntax_passed'] for r in merged_rows),'syntax_failed':sum(not r['syntax_passed'] for r in merged_rows),'errors_by_category':dict(errors.most_common()),'functions_by_error_category':dict(functions.most_common()),'error_codes':dict(codes.most_common()),'cache_reused':5772-len(fresh),'recompiled':len(pending)-recovered_failures,'actual_compiler_invocations':actual_invocations,'recovered_individual_failures':recovered_failures,'pilot_cache_reused':len(pilot_reused),'elapsed_seconds':report['elapsed_seconds'],'source_sha256':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},'headers_sha256':{**baseline['headers_sha256'],**header_pins},'cache_inputs_sha256':{**pins,**header_pins},'declaration_headers_sha256':header_pins,'limits':baseline['limits']+['Run184 adds only exported nonconflicting memory extern declarations with per-TU type/size/alignment checks. No global definitions, address aliases, storage coalescing, function prototypes or ABI lowering. Overlap/initialization behavior is not proven.','Batched /MP syntax results require exactly one emitted filename per TU and uniquely attributed diagnostics. Aggregate exit codes are retained; per-TU exit codes are null. Unattributable batches fall back to individual invocations. Interrupted individual error logs prove failures only, never passes.']}
  assert len(merged_rows)==5772
  (target/'audit.json').write_text(json.dumps(merged,indent=2)+'\n',encoding='utf8');report.update({'cache_reused':merged['cache_reused'],'syntax_total_before':baseline['syntax_passed'],'syntax_total_after':merged['syntax_passed'],'error_limited_vas':[r['va'] for r in merged_rows if any(d['code']=='C1003' for d in r['diagnostics'])]})
 for path,pin in {**pins,**source_pins}.items():assert sha(Path(path))==pin
 (target/'results.json').write_text(json.dumps(fresh,indent=2)+'\n',encoding='utf8');(RUN/('summary.json' if args.full else 'pilot.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:report[k] for k in ('phase','selected_functions','syntax_before','syntax_after','new_syntax_pass_vas','lost_syntax_pass_vas','missing_global_errors_before','missing_global_errors_after','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
