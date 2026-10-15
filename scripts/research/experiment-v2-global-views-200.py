"""Seven exact Run194 float4 aliases: extern-only native compile delta."""
import hashlib, importlib.util, json, re, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/200-global-float-views'
OUT=ROOT/'local/experiments/v2-global-float-views-200'
spec=importlib.util.spec_from_file_location('leaves187',ROOT/'scripts/research/experiment-v2-thiscall-leaves-187.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()
def write(p,s):p.write_text(s,encoding='utf8',newline='\n')
def dump(p,d):write(p,json.dumps(d,indent=2)+'\n')
def main():
 for p in (RUN,OUT,OUT/'objects'):p.mkdir(parents=True,exist_ok=True)
 evidence_path=ROOT/'iterations/v2/001-original-recovery/runs/194-global-aliases/summary.json'
 audit_path=ROOT/'local/experiments/v2-scalar-slices-189/full/audit.json'
 leaves_path=ROOT/'iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/summary.json'
 evidence=json.loads(evidence_path.read_text());audit=json.loads(audit_path.read_text());leaves=json.loads(leaves_path.read_text())
 pins={p:sha(p) for p in (Path(__file__),Path(spec.origin),evidence_path,audit_path,leaves_path,base.abi.COMPILER)}
 assert pins[base.abi.COMPILER]==leaves['compiler_sha256']
 groups={}
 for case in evidence['cases']:
  if not case['token_ram_width_agrees']:continue
  if not all(t['node_type']['name']=='float' and t['node_bytes']==4 for t in case['tokens']):continue
  assert case['original_direct_access_widths']==[4]
  assert all(i.get('direct_access_direction_agrees') for i in case['instructions'])
  groups.setdefault(case['va'],[]).append(case)
 assert sum(map(len,groups.values()))==7 and len(groups)==5
 oldrows={r['va']:r for r in audit['results']};leafrows={r['va']:r for r in leaves['results']}
 rows=[]
 for va,cases in sorted(groups.items()):
  old=leafrows[va] if va in leafrows else oldrows[va]
  source=Path(old['generated_source']);source=source if source.is_absolute() else ROOT/source
  assert sha(source)==old['generated_source_sha256']
  base.headers_closure([source],pins)
  for path,expected in old.get('dependency_sha256',{}).items():assert sha(ROOT/path)==expected;pins[ROOT/path]=expected
  header=OUT/(va+'-aliases.h');cpp=OUT/(va+'.cpp');obj=OUT/'objects'/(va+'.obj')
  assert not obj.exists(),'Fresh bounded native run required; refusing stale object acceptance'
  write(header,'#pragma once\nstatic_assert(sizeof(float)==4,"original RAM float4 width");\n'+''.join('extern float '+c['alias']+'; // Porsche.exe VA0x'+c['address']+' RAM4\n' for c in cases))
  write(cpp,'#include "'+header.as_posix()+'"\n#include "'+source.as_posix()+'"\n')
  rows.append({'va':va,'kind':'thiscall_leaf196' if va in leafrows else 'ordinary189','generated_source':rel(cpp),'generated_source_sha256':sha(cpp),'forced_headers':[],
   'original_generated_source':rel(source),'original_generated_source_sha256':sha(source),'body_unchanged':True,'alias_header':rel(header),'alias_header_sha256':sha(header),
   'aliases':[{'alias':c['alias'],'address':c['address'],'width':4,'high_type':'float','original_instructions':[{'pc':i['pc'],'bytes':i['bytes'],'capstone':i['capstone'],'sleigh':i['sleigh_direct_accesses']} for i in c['instructions']]} for c in cases],
   'object':rel(obj),'baseline_compiled':old.get('compiled',False),'baseline_syntax_passed':old.get('syntax_passed',old.get('compiled',False))})
 flags=leaves['compiler_flags'];assert '/MP6' in flags and '/c' in flags and '/O2' in flags
 rsp=OUT/'changed-5.rsp';log=OUT/'changed-5.log'
 rsp.write_text('\n'.join('"'+s+'"' for s in flags+['/Fo'+(OUT/'objects').as_posix()+'/']+[str(ROOT/r['generated_source']) for r in rows])+'\n',encoding='utf-8-sig',newline='\n')
 started=time.perf_counter();p=subprocess.run([str(base.abi.COMPILER),'@'+str(rsp)],cwd=OUT,env=base.abi.ENV,capture_output=True,encoding='utf8',errors='replace',timeout=180)
 raw=p.stdout+p.stderr;write(log,raw);diagnostics={r['va']:[] for r in rows};unattributed=[]
 for m in re.finditer(r'([^\r\n]+?)\((\d+),(\d+)\):\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)',raw):
  source,line,column,severity,code,message=m.groups();matches=[va for va in diagnostics if va in source]
  d={'source':source,'line':int(line),'column':int(column),'severity':severity,'code':code,'message':message}
  if len(matches)==1:diagnostics[matches[0]].append(d)
  else:unattributed.append(d)
 assert not unattributed,unattributed
 assert len(re.findall(r'\b(?:fatal error|error|warning) C\d+:',raw))==sum(map(len,diagnostics.values())),'Unparsed native diagnostics'
 for row in rows:
  obj=ROOT/row['object'];row['diagnostics']=diagnostics[row['va']];row['compiled']=obj.exists();row['syntax_passed']=obj.exists()
  assert row['compiled']==(not any('error' in d['severity'] for d in row['diagnostics']))
  row['dependency_sha256']={rel(k):v for k,v in pins.items() if k.suffix in ('.h','.cpp')}
  row['dependency_sha256'].update({row['alias_header']:row['alias_header_sha256'],row['generated_source']:row['generated_source_sha256']})
  if obj.exists():row.update(object_sha256=sha(obj),object_bytes=obj.stat().st_size,**base.coff_symbols(obj))
 for path,expected in pins.items():assert sha(path)==expected,('input mutation',path)
 report={'schema':1,'original_sha256':evidence['original_sha256'],'input_sha256':{rel(k):v for k,v in pins.items()},'compiler_sha256':sha(base.abi.COMPILER),'compiler_flags':flags,
  'alias_cases':7,'changed_tus':5,'actual_compiler_batches':1,'batch_exit_code':p.returncode,'compile_seconds':round(time.perf_counter()-started,3),
  'new_objects':sum(r['compiled'] for r in rows),'new_object_vas':[r['va'] for r in rows if r['compiled']],
  'unchanged_leaf_objects_reused':leaves['real_coff_objects'],'unchanged_ordinary_audit_rows':len(audit['results'])-1,
  'compiler_log':rel(log),'compiler_log_sha256':sha(log),'compiler_response':rel(rsp),'compiler_response_sha256':sha(rsp),'results':rows,
  'boundary':'Extern-only per-consumer views; no allocations/coalescing/formal-type replacement or body edits. Native compilation is not fidelity proof; x87/float-to-rawword warnings and shared-storage ownership remain open.'}
 dump(RUN/'summary.json',report);dump(OUT/'audit.json',report)
 dump(RUN/'validation.json',{'status':'PASS','all_input_sha_guards_before_after':True,'bodies_unchanged':True,'diagnostics_attributed':True,'summary_sha256':sha(RUN/'summary.json'),'native_compile_delta':report['new_objects']})
 print(json.dumps({k:report[k] for k in ('alias_cases','changed_tus','new_objects','new_object_vas','batch_exit_code','compile_seconds')}))
if __name__=='__main__':main()
