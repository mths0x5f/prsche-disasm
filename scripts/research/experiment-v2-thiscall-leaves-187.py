"""Batch real COFF for ABI-gated, call-free thiscall leaves; no production edits."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib,importlib.util,json,os,re,struct,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/187-thiscall-leaf-candidates'
OUT=ROOT/'local/experiments/v2-thiscall-leaves-187'
BASE=ROOT/'local/experiments/v2-pcode-types-183/prototypes-cpp-0000/audit.json'
PROOF=ROOT/'iterations/v2/001-original-recovery/runs/186-thiscall-compatibility/summary.json'
spec=importlib.util.spec_from_file_location('thiscall186',ROOT/'scripts/research/experiment-v2-thiscall-186.py');abi=importlib.util.module_from_spec(spec);spec.loader.exec_module(abi)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()

def write_json(path,value):
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8');temp.replace(path)

def strip_comments(text):return re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)

def headers_closure(paths,pins):
 todo=list(paths);seen=set()
 while todo:
  path=Path(todo.pop()).resolve()
  if path in seen:continue
  seen.add(path);pins[path]=sha(path)
  for name in re.findall(r'^\s*#include\s+"([^"]+)"',path.read_text(encoding='utf8'),flags=re.M):
   include=Path(name);todo.append(include if include.is_absolute() else path.parent/include)
 return {relative(p):pins[p] for p in seen}

def eligibility(decl,text,entry,index,known_names,numeric_helpers):
 contract=abi.original_contract(decl,entry,index)
 if not contract['ret_agrees']:return 'original RET mismatch or no local RET',contract
 instructions=abi.function_instructions(entry,index)
 if any(i['instruction'].split(' ',1)[0].upper().startswith('CALL') for i in instructions):return 'original machine call',contract
 ranges=[(int(a,16),int(b,16)) for a,b in entry['ranges']]
 for i in instructions:
  mnemonic=i['instruction'].split(' ',1)[0].upper()
  if mnemonic.startswith('J'):
   target=re.fullmatch(r'J\w*\s+0x([0-9a-f]+)',i['instruction'],flags=re.I)
   if not target:return 'indirect or unclassified branch',contract
   if not any(a<=int(target[1],16)<=b for a,b in ranges):return 'external branch or tail-call seam',contract
 body=strip_comments(text).split('{',1)[-1]
 if re.search(r'\b(?:in_|unaff_|extraout_|in_stack_)\w*',body):return 'unknown incoming register or stack value',contract
 if set(re.findall(r'\b[A-Za-z_$][\w$]*\b',body))&known_names:return 'function or import address/name in body',contract
 if re.search(r'\bcode\b|\b__thiscall\b|\b__fastcall\b|\b__stdcall\b',body):return 'function-pointer or callback ABI in body',contract
 if re.search(r'\(\s*\*[^;{}\n]*\)\s*\(',body):return 'possible indirect call syntax',contract
 allowed=numeric_helpers|{'if','while','for','switch','return','sizeof','alignof','bool','char','short','int','long','float','double','byte','uint','ushort','ulong','undefined','undefined1','undefined2','undefined4','undefined8'}
 unknown=set(re.findall(r'\b([A-Za-z_$][\w$]*)\s*\(',body))-allowed
 if unknown:return 'unproven source helper/call: '+','.join(sorted(unknown)),contract
 try:abi.lower(decl,text)
 except ValueError as e:return str(e),contract
 return None,contract

def coff_symbols(path):
 data=path.read_bytes();machine,count,_,offset,nsyms,optional,_=struct.unpack_from('<HHIIIHH',data,0);assert machine==0x14c
 strings=data[offset+nsyms*18:];undefined=[];defined=[];i=0
 while i<nsyms:
  item=offset+i*18;name=data[item:item+8]
  if name[:4]==b'\0'*4:
   pos=struct.unpack_from('<I',name,4)[0];end=strings.find(b'\0',pos);text=strings[pos:end].decode('ascii',errors='replace')
  else:text=name.rstrip(b'\0').decode('ascii',errors='replace')
  value,section,typ,storage,aux=struct.unpack_from('<IhHBB',data,item+8)
  if storage==2:
   if section==0 and value==0:undefined.append(text)
   elif section>0:defined.append(text)
  i+=1+aux
 return {'machine':'i386','defined_external_symbols':defined,'undefined_external_symbols':undefined}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--audit',type=Path,default=BASE);parser.add_argument('--jobs',type=int,default=6);parser.add_argument('--batch-size',type=int,default=64);parser.add_argument('--limit',type=int);args=parser.parse_args()
 assert 1<=args.jobs<=6 and args.batch_size>0
 start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 sources=OUT/'sources';objects=OUT/'objects';logs=OUT/'logs'
 for p in (sources,objects,logs):p.mkdir(exist_ok=True)
 audit=json.loads(args.audit.read_bytes());proof=json.loads(PROOF.read_bytes());assert audit['original_sha256']==proof['original_sha256']==abi.SHA
 assert all(r['native_exit']==0 for r in proof['native_fixtures'])
 pins={Path(__file__).resolve():sha(Path(__file__)),args.audit.resolve():sha(args.audit),PROOF:sha(PROOF),Path(spec.origin):sha(Path(spec.origin)),abi.DECL:sha(abi.DECL),abi.CORPUS/'decompiled.c':sha(abi.CORPUS/'decompiled.c'),abi.CORPUS/'functions.jsonl':sha(abi.CORPUS/'functions.jsonl'),abi.CORPUS/'disassembly.asm':sha(abi.CORPUS/'disassembly.asm'),abi.COMPILER:sha(abi.COMPILER)}
 # Reuse the frozen native ABI proof only when its complete recorded inputs agree.
 for name,expected in proof['source_pins'].items():
  p=ROOT/name;assert sha(p)==expected,('186 input changed',name);pins[p]=expected
 for name,expected in audit.get('headers_sha256',{}).items():
  p=Path(name);assert sha(p)==expected,('baseline header changed',name);pins[p.resolve()]=expected
 original_binary=next(r for r in abi.rows(ROOT/'research/binary-index/static/binaries.jsonl') if r['file']=='Porsche.exe');assert sha(ROOT/'local/game'/original_binary['path'])==abi.SHA
 all_bodies=abi.bodies();decls=abi.rows(abi.DECL);base_rows={r['va']:r for r in audit['results']};catalog={r['entry_va']:r for r in abi.rows(abi.CORPUS/'functions.jsonl')};index=abi.instruction_index()
 accepted_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json';pins[accepted_path]=sha(accepted_path)
 accepted={r['entry_va'] for r in json.loads(accepted_path.read_bytes())['functions'] if r['module']=='Porsche.exe'}
 known_names={r['name'] for r in decls}
 helper=ROOT/'local/experiments/v2-pcode-compat-180/ghidra-integer-pcode.h'
 numeric=set(re.findall(r'\b((?:CONCAT|SUB|ZEXT|SEXT|CARRY|SCARRY|SBORROW)\d+)\s*\(',helper.read_text()))|{'p180_write','p180_read'}
 pins[helper]=sha(helper)
 selected=[];skipped=[];counts=Counter();all_eligible=0
 for d in decls:
  if d['inferred_calling_convention']!='__thiscall':continue
  va=d['entry_va']
  if va in accepted:skipped.append({'va':va,'reason':'canonical accepted owner excluded'});counts['canonical accepted owner excluded']+=1;continue
  row=base_rows[va];baseline=Path(row['generated_source']);assert sha(baseline)==row['generated_source_sha256'],('baseline source changed',va)
  pins[baseline.resolve()]=sha(baseline);text=baseline.read_text(encoding='utf8');marker='/* VA '+va+' */';assert text.count(marker)==1;body=text.split(marker,1)[1]
  reason,contract=eligibility(d,body,catalog[va],index,known_names,numeric)
  if reason:skipped.append({'va':va,'reason':reason,'original_contract':contract});counts[reason]+=1;continue
  all_eligible+=1
  if args.limit is not None and len(selected)>=args.limit:continue
  lowered,method=abi.lower(d,body)
  includes=re.findall(r'^\s*#include\s+"([^"]+)"',text.split(marker,1)[0],flags=re.M)
  if row.get('declaration_header') and row['declaration_header'] not in includes:includes.append(row['declaration_header'])
  forced=[str(Path(p).resolve()) for p in row.get('forced_headers',[])]
  dependency_pins=headers_closure([Path(p) for p in includes+forced],pins)
  prefix=''.join('#include "'+Path(p).as_posix()+'"\n' for p in includes)
  source=sources/(va+'.cpp');source.write_text(prefix+'#line 1 "porsche_method_'+va+'"\n'+lowered,encoding='utf8')
  obj=objects/(va+'.obj')
  if obj.exists():obj.unlink() # Exact known output path only; avoid stale successes.
  instructions=abi.function_instructions(catalog[va],index);original_bytes=bytes.fromhex(''.join(i['bytes'] for i in instructions))
  original_ranges=catalog[va]['ranges'];expected_bytes=catalog[va]['body_bytes']
  assert len(original_bytes)==expected_bytes,('catalog byte coverage mismatch',va,len(original_bytes),expected_bytes)
  selected.append({'va':va,'source':source,'object':obj,'generated_source_sha256':sha(source),'baseline_generated_source':relative(baseline),'baseline_generated_source_sha256':row['generated_source_sha256'],'baseline_source_body_sha256':row['source_body_sha256'],'source_body_preserved_from_baseline':True,'forced_headers':forced,'dependency_sha256':dependency_pins,'original_body_ranges':original_ranges,'original_body_bytes':expected_bytes,'original_instruction_bytes_sha256':hashlib.sha256(original_bytes).hexdigest(),'original_instruction_bytes_hex':original_bytes.hex(),'original_contract':contract,'method_contract':method})
 write_json(RUN/'progress.json',{'phase':'selected','thiscall_functions':1301,'eligible':all_eligible,'selected':len(selected),'skipped':dict(counts),'complete':False})
 print(json.dumps({'eligible':all_eligible,'selected':len(selected),'skip_counts':dict(counts)}),flush=True)
 batches={}
 # Actual MSVC /MP6 batches; no duplicate syntax pass before real code generation.
 # Separate forced-include contracts are never silently merged across TUs.
 groups={}
 for row in selected:groups.setdefault(tuple(row['forced_headers']),[]).append(row)
 batch_id=0
 for forced,group in groups.items():
  for offset in range(0,len(group),args.batch_size):
   batch=group[offset:offset+args.batch_size];rsp=logs/(f'batch-{batch_id:03}.rsp');log=logs/(f'batch-{batch_id:03}.log')
   options=['/nologo','/c','/std:c++17','/O2','/GS-','/GR-','/W4','/utf-8','/diagnostics:column','/FC','/MP'+str(args.jobs),'/Fo'+objects.as_posix()+'/']+['/FI'+p for p in forced]
   rsp.write_text('\n'.join('"'+s+'"' for s in options+[str(r['source']) for r in batch]),encoding='utf-8-sig')
   before=time.perf_counter();p=subprocess.run([str(abi.COMPILER),'@'+str(rsp)],cwd=OUT,capture_output=True,encoding='utf8',errors='replace',env=abi.ENV,timeout=240)
   log.write_text(p.stdout+p.stderr,encoding='utf8');info={'compiler_exit_code':p.returncode,'seconds':round(time.perf_counter()-before,3),'response_file':relative(rsp),'response_file_sha256':sha(rsp),'log':relative(log),'log_sha256':sha(log),'vas':[r['va'] for r in batch]};batches[str(batch_id)]=info
   for row in batch:row['batch_id']=batch_id
   batch_id+=1;print(json.dumps({'compiled':sum(len(b['vas']) for b in batches.values()),'total':len(selected),'batch_exit':p.returncode}),flush=True)
   write_json(RUN/'progress.json',{'phase':'compiling','selected':len(selected),'attempted':sum(len(b['vas']) for b in batches.values()),'complete':False})
 results=[]
 for row in selected:
  source=row.pop('source');obj=row.pop('object');assert sha(source)==row['generated_source_sha256']
  row['generated_source']=relative(source);row['compiled']=obj.exists();row['object']=relative(obj);row['compiler_exit_code']=0 if obj.exists() else None
  if obj.exists():
   row['object_sha256']=sha(obj);row['object_bytes']=obj.stat().st_size;row.update(coff_symbols(obj));sections=abi.text_sections(obj);row['native_text_sections']=sections
   row['exact_original_body_bytes_match']=any(s['relocations']==0 and s['bytes']==row['original_instruction_bytes_hex'] for s in sections)
   assert any('Thiscall_'+row['va'] in s for s in row['defined_external_symbols']),('missing native method symbol',row['va'])
  else:row['failure']='Compiler produced no COFF; exact diagnostics in pinned batch log. No replacement types, casts or stubs added.'
  results.append(row)
 # Detect input mutation once at the batch boundary, not once per function.
 for path,expected in pins.items():assert sha(path)==expected,('input changed during batch',path)
 symbols=Counter(s for r in results if r['compiled'] for s in r['undefined_external_symbols'])
 summary={'schema':1,'module':'Porsche.exe','original_sha256':abi.SHA,'baseline_audit':relative(args.audit),'baseline_audit_sha256':sha(args.audit),'abi_proof':relative(PROOF),'abi_proof_sha256':sha(PROOF),'input_sha256':{relative(p):h for p,h in sorted(pins.items(),key=lambda x:str(x[0]))},'compiler_sha256':sha(abi.COMPILER),'jobs':args.jobs,'batch_size':args.batch_size,'actual_compiler_batches':len(batches),'thiscall_functions':1301,'eligible_callfree_functions':all_eligible,'selected_functions':len(results),'real_coff_objects':sum(r['compiled'] for r in results),'compiler_failures':sum(not r['compiled'] for r in results),'exact_original_body_byte_matches':sum(r.get('exact_original_body_bytes_match',False) for r in results),'undefined_unique_symbols':len(symbols),'undefined_references':sum(symbols.values()),'undefined_symbols':dict(symbols),'skipped_by_reason':dict(counts),'skipped':skipped,'batches':batches,'results':results,'elapsed_seconds':round(time.perf_counter()-start,3),'boundary':'Isolated class-method compile candidates only. Original call-free/RET/type-width gates; no caller adapters, registry/production binding, original runtime bytes or guessed algorithms. Native ABI proof reused from frozen186; compiler-inserted/runtime/global dependencies stay unresolved.'}
 write_json(RUN/'summary.json',summary);write_json(RUN/'progress.json',{'complete':True,'selected':len(results),'real_coff_objects':summary['real_coff_objects'],'compiler_failures':summary['compiler_failures']})
 print(json.dumps({k:summary[k] for k in ('eligible_callfree_functions','selected_functions','real_coff_objects','compiler_failures','exact_original_body_byte_matches','undefined_unique_symbols','undefined_references','elapsed_seconds')},indent=2))

if __name__=='__main__':main()
