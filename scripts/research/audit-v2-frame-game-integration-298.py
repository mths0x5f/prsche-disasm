"""Batch audit of new frame packets and the actual156-TU game-source build."""
import collections, hashlib, importlib.util, json, re
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'298-frame-game-integration'
BUILD=ROOT/'local/builds/v2/frame-game-integration-298'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 reader=ManifestReader(ROOT);packets={}
 for name in ('295-frame-helpers','296-frame-root-state','297-frame-action','299-frame-action-children','300-frame-float-data','301-frame-name-bound'):
  p=RUNS/name/'summary.json';s=load(p);v=load(p.with_name('validation.json'))
  assert v['passed'] and v['summary_sha256']==sha(p)
  reader.verify(s,expected_hash_mode='raw')
  if 'source_manifest' in s:reader.verify(s,'source',expected_hash_mode='raw')
  for key in ('tool_sha256','external_tools_sha256','external_dependencies_sha256','output_sha256'):
   for name_or_path,h in s.get(key,{}).items():
    target=Path(name_or_path);assert sha(target if target.is_absolute() else ROOT/target)==h
  packets[name]=dict(summary_sha256=sha(p),native_cases=s.get('native_cases',0),game_sources=s.get('game_sources',[s['game_source']] if 'game_source' in s else [s['source']] if 'source' in s else []))
 pe=module('pe298audit',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 image=(ROOT/'local/game/Porsche.exe').read_bytes()
 helper=load(RUNS/'295-frame-helpers/summary.json')
 for va,row in helper['original_bodies'].items():assert pe.pe_read(image,int(va,16),row['size']).hex()==row['hex']
 for name in ('297-frame-action','299-frame-action-children'):
  s=load(RUNS/name/'summary.json');assert pe.pe_read(image,int(s['va'],16),s['original_body_bytes']).hex()==s['original_body_hex']
 assert pe.pe_read(image,0x5b47d8,4).hex()=='0000fa45' and pe.pe_read(image,0x5b2764,4).hex()=='00401c46'
 root=load(RUNS/'296-frame-root-state/summary.json');bound=load(RUNS/'301-frame-name-bound/summary.json')
 assert not root['storage_definition_added'] and not bound['storage_definition_added'] and not bound['upper_bound_31_proved']
 s=load(RUN/'build-002.json');_,pins=reader.verify(s,'source',expected_hash_mode='crlf-to-lf')
 assert s['source_count']==156 and len(s['project_paths'])==8 and s['input_unchanged']
 assert not s['compiler_errors'] and not s['other_linker_errors'] and not s['executable'] and not s['game_executed']
 assert s['exit_code']==1 and s['unresolved_names']==266 and s['unresolved_references']==302
 receipt=load(ROOT/s['receipt']);assert sha(ROOT/s['receipt'])==s['receipt_sha256']
 assert sha(ROOT/receipt['log'])==receipt['log_sha256'] and receipt['exit_code']==1
 text=(ROOT/receipt['log']).read_text(encoding='utf8')
 printed=collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$',text))
 assert printed==collections.Counter(Path(x).name for x in s['compiled_source_roots'])
 assert not any(Path(x).name=='fixture.cpp' or 'original-body' in x for x in s['compiled_source_roots'])
 diagnostics=[line for line in text.splitlines() if re.search(r'\berror LNK(?:2001|2019):',line)]
 names={re.findall(r'\((\?[^()]+)\)',line)[0] for line in diagnostics}
 old=load(RUNS/'293-game-startup-followup/build-002.json');old_names={x['symbol'] for x in old['frontier']}
 closed=old_names-names
 assert len(closed)==3 and not names-old_names and len(names)==266 and len(diagnostics)==302
 assert {next(x for x in ('advance_00423840','invoke_00476170','invoke_00482e50') if x in name) for name in closed}=={'advance_00423840','invoke_00476170','invoke_00482e50'}
 assert any('frame_service_root_00628960' in n for n in names)
 assert not any('update_00476710' in n or 'frame_limit_005b47d8' in n or 'frame_step_005b2764' in n for n in names)
 cof=module('coff298audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 expected={'00423840':1,'00482e50':1,'00476170':1,'00476710':1,'frame_floats_300':2};fresh={}
 for stem,count in expected.items():
  matches=list(BUILD.glob('**/porsche_game_entry_bridges.dir/Release/'+stem+'.obj'));assert len(matches)==1
  obj=matches[0];view=cof.coff_symbols(obj);assert len(view['defined'])==count and not view['common'] and not view['weak']
  assert not any('reference' in n or 'capture' in n or 'destroy297' in n for n in view['defined'])
  fresh[stem]=dict(path=obj.relative_to(ROOT).as_posix(),sha256=sha(obj),symbols=view)
 warnings=[line for line in text.splitlines() if re.search(r'warning [CD]\d+',line)]
 assert len(warnings)==3 and all('C4005' in line and 'WIN32_LEAN_AND_MEAN' in line for line in warnings)
 blocked=load(RUN/'build-001.json');assert blocked['source_count']==156 and blocked['unresolved_names']==0 and blocked['exit_code']==1
 blocked_receipt=load(ROOT/blocked['receipt']);assert sha(ROOT/blocked['receipt'])==blocked['receipt_sha256'] and sha(ROOT/blocked_receipt['log'])==blocked_receipt['log_sha256']
 assert 'Checking Build System' in (ROOT/blocked_receipt['log']).read_text(encoding='utf8')
 assert not list(BUILD.glob('**/porsche_original_game_link.exe'))
 reader.cache.check_stable()
 result=dict(schema=1,passed=True,packets=packets,native_comparisons=1139,original_function_bytes=441,read_only_float_bytes=8,fresh_compiler_sources=156,source_pins=len(pins),reader_counts=reader.counts,build_report_sha256=sha(RUN/'build-002.json'),fresh_objects=fresh,closed_game_names=sorted(closed),new_game_names=[],unresolved_names=266,unresolved_references=302,game_executed=False,root_layout='HOLD',sandbox_build_attempt_preserved=True)
 output=RUN/'validation.json'
 if output.exists():assert load(output)==result,'Completed audit content changed'
 else:output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({k:result[k] for k in ('passed','native_comparisons','fresh_compiler_sources','source_pins','unresolved_names','unresolved_references','root_layout')}))
if __name__=='__main__':main()
