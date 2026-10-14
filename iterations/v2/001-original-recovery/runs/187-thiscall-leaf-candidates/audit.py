"""Independent input/body/PE/COFF audit; no compilation or original execution."""
from collections import Counter
import hashlib,importlib.util,json,re,struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
RUN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('leaves187',ROOT/'scripts/research/experiment-v2-thiscall-leaves-187.py');experiment=importlib.util.module_from_spec(spec);spec.loader.exec_module(experiment)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
summary_path=RUN/'summary.json';report=json.loads(summary_path.read_bytes())
assert report['thiscall_functions']==1301 and report['selected_functions']==report['eligible_callfree_functions']==159
for name,expected in report['input_sha256'].items():assert sha(ROOT/name)==expected,('input changed',name)
binary=next(r for r in experiment.abi.rows(ROOT/'research/binary-index/static/binaries.jsonl') if r['file']=='Porsche.exe')
image=(ROOT/'local/game'/binary['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==report['original_sha256']
pe=struct.unpack_from('<I',image,0x3c)[0];sections_count=struct.unpack_from('<H',image,pe+6)[0];optional_size=struct.unpack_from('<H',image,pe+20)[0];base=struct.unpack_from('<I',image,pe+24+28)[0]
sections=[]
for i in range(sections_count):
 off=pe+24+optional_size+i*40;virtual_size,rva,raw_size,raw=struct.unpack_from('<IIII',image,off+8);sections.append((base+rva,base+rva+raw_size,raw))
def original_bytes(ranges):
 chunks=[]
 for low,high in ranges:
  a,b=int(low,16),int(high,16)
  match=[(start,end,raw) for start,end,raw in sections if start<=a<=b<end];assert len(match)==1,(low,high)
  start,_,raw=match[0];chunks.append(image[raw+a-start:raw+b-start+1])
 return b''.join(chunks)

decls={r['entry_va']:r for r in experiment.abi.rows(experiment.abi.DECL)}
index=experiment.abi.instruction_index();catalog={r['entry_va']:r for r in experiment.abi.rows(experiment.abi.CORPUS/'functions.jsonl')}
known_names={r['name'] for r in decls.values()};helper=ROOT/'local/experiments/v2-pcode-compat-180/ghidra-integer-pcode.h'
numeric=set(re.findall(r'\b((?:CONCAT|SUB|ZEXT|SEXT|CARRY|SCARRY|SBORROW)\d+)\s*\(',helper.read_text()))|{'p180_write','p180_read'}
diagnostics={};codes=Counter();failure_details=[]
for batch in report['batches'].values():
 assert sha(ROOT/batch['log'])==batch['log_sha256'] and sha(ROOT/batch['response_file'])==batch['response_file_sha256']
 text=(ROOT/batch['log']).read_text()
 for m in re.finditer(r'porsche_method_([0-9a-f]{8})\((\d+),(\d+)\):\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)',text):
  va,line,column,severity,code,message=m.groups();diagnostics.setdefault(va,[]).append({'line':int(line),'column':int(column),'severity':severity,'code':code,'message':message});codes[code]+=1

objects=0;matches=0;undefined=Counter();byte_count=0
assert len({r['va'] for r in report['results']})==159
for r in report['results']:
 va=r['va'];source=ROOT/r['generated_source'];baseline=ROOT/r['baseline_generated_source']
 assert sha(source)==r['generated_source_sha256'] and sha(baseline)==r['baseline_generated_source_sha256']
 body=baseline.read_text().split('/* VA '+va+' */',1)[1];lowered,contract=experiment.abi.lower(decls[va],body)
 assert source.read_text().endswith(lowered),('original typed body/lowering changed',va)
 reason,machine_contract=experiment.eligibility(decls[va],body,catalog[va],index,known_names,numeric)
 assert reason is None and machine_contract['ret_agrees'],(va,reason)
 actual=original_bytes(r['original_body_ranges']);assert actual.hex()==r['original_instruction_bytes_hex']
 assert len(actual)==r['original_body_bytes'] and hashlib.sha256(actual).hexdigest()==r['original_instruction_bytes_sha256'];byte_count+=len(actual)
 for name,expected in r['dependency_sha256'].items():assert sha(ROOT/name)==expected
 obj=ROOT/r['object']
 if r['compiled']:
  assert obj.exists() and sha(obj)==r['object_sha256'];symbols=experiment.coff_symbols(obj);assert symbols['undefined_external_symbols']==r['undefined_external_symbols']
  assert symbols['defined_external_symbols']==r['defined_external_symbols'];text_sections=experiment.abi.text_sections(obj);assert text_sections==r['native_text_sections']
  exact=any(s['relocations']==0 and s['bytes']==actual.hex() for s in text_sections);assert exact==r['exact_original_body_bytes_match']
  objects+=1;matches+=exact;undefined.update(symbols['undefined_external_symbols'])
 else:
  assert not obj.exists();failure_details.append({'va':va,'diagnostics':diagnostics.get(va,[]),'batch_id':r['batch_id']})
assert objects==report['real_coff_objects']==127
assert matches==report['exact_original_body_byte_matches']==27
assert dict(undefined)==report['undefined_symbols']
validation={'schema':1,'summary_sha256':sha(summary_path),'audit_source_sha256':sha(Path(__file__)),'input_pins_pass':True,'selected_bodies_pass':True,'actual_original_pe_bytes_pass':True,'original_leaf_ret_gates_pass':True,'objects_pass':True,'selected':159,'real_coff_objects':objects,'compiler_failures':len(failure_details),'exact_body_byte_matches':matches,'original_instruction_bytes_checked':byte_count,'undefined_symbols':dict(undefined),'diagnostic_codes':dict(codes),'failure_details':failure_details,'boundary':'Read-only audit of frozen compiler results/actual original PE bytes; no repeated native ABI tests or original execution, no semantic acceptance.'}
(RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in validation.items() if k!='failure_details'},indent=2))
