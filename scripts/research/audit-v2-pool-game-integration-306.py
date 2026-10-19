"""Read-only audit of pool shutdown and its exact effect on the game link."""
import collections, hashlib, importlib.util, json, re
from pathlib import Path
from v2_shared_manifests import ManifestReader
ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'306-file-pool-game-integration'
BUILD=ROOT/'local/builds/v2/file-pool-game-integration-306'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 reader=ManifestReader(ROOT);packet=load(RUNS/'305-file-pool-shutdown/summary.json')
 reader.verify(packet,expected_hash_mode='raw')
 assert load(RUNS/'305-file-pool-shutdown/validation.json')['summary_sha256']==sha(RUNS/'305-file-pool-shutdown/summary.json')
 for p,h in packet.get('tool_sha256',{}).items():assert sha(p)==h
 assert packet['native_cases']==48 and packet['compiler_batches']==1
 pe=module('pe306',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 assert pe.pe_read((ROOT/'local/game/Porsche.exe').read_bytes(),0x5678f0,248).hex()==packet['original_body_hex']
 s=load(RUN/'build-001.json');mode,pins=reader.verify(s,'source',expected_hash_mode='crlf-to-lf')
 previous=load(RUNS/'298-frame-game-integration/build-002.json')
 assert s['source_manifest']==previous['source_manifest'] and s['source_delta'] and not s.get('source_removed')
 assert 'scripts/research/build-v2-game-entry-306.py' in pins and 'scripts/research/build-v2-game-entry-298.py' in pins
 assert s['source_count']==157 and len(s['project_paths'])==8 and s['input_unchanged']
 assert not s['compiler_errors'] and not s['other_linker_errors'] and not s['executable'] and not s['game_executed']
 assert s['exit_code']==1 and s['unresolved_names']==265 and s['unresolved_references']==301
 rp=ROOT/s['receipt'];receipt=load(rp);assert sha(rp)==s['receipt_sha256']
 assert receipt['exit_code']==1 and sha(ROOT/receipt['log'])==receipt['log_sha256']
 log=(ROOT/receipt['log']).read_text(encoding='utf8')
 printed=collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$',log))
 assert printed==collections.Counter(Path(p).name for p in s['compiled_source_roots'])
 assert not any('fixture.cpp' in p or 'original-body' in p for p in s['compiled_source_roots'])
 names={x['symbol'] for x in s['frontier']};old={x['symbol'] for x in previous['frontier']}
 closed=old-names
 assert closed=={'?application_pool_shutdown_005678f0@porsche@@YAXXZ'} and not names-old
 assert len([line for line in log.splitlines() if re.search(r'\berror LNK(?:2001|2019):',line)])==301
 objects=list(BUILD.glob('**/porsche_game_entry_bridges.dir/Release/005678f0.obj'));assert len(objects)==1
 coff=module('coff306',ROOT/'scripts/research/build-v2-compile-corpus.py');view=coff.coff_symbols(objects[0])
 assert '?application_pool_shutdown_005678f0@porsche@@YAXXZ' in view['defined']
 assert not any('reference' in x or 'capture' in x for x in view['defined'])
 assert set(view['undefined'])==set(packet['symbols']['undefined'])
 assert not list(BUILD.glob('**/porsche_original_game_link.exe'))
 warnings=[line for line in log.splitlines() if re.search(r'warning [CD]\d+',line)]
 assert len(warnings)==3 and all('C4005' in line and 'WIN32_LEAN_AND_MEAN' in line for line in warnings)
 reader.cache.check_stable()
 result=dict(schema=1,passed=True,build_report_sha256=sha(RUN/'build-001.json'),packet305_sha256=sha(RUNS/'305-file-pool-shutdown/summary.json'),native_comparisons=48,original_function_bytes=248,fresh_compiler_sources=157,source_pins=len(pins),shared_base_pins=len(reader.manifest(s['source_manifest'])[1]),source_delta_pins=len(s['source_delta']),closed_game_names=sorted(closed),new_game_names=[],unresolved_names=265,unresolved_references=301,fresh_object=dict(path=objects[0].relative_to(ROOT).as_posix(),sha256=sha(objects[0]),symbols=view),game_executed=False,reader_counts=reader.counts)
 output=RUN/'validation.json'
 if output.exists():assert load(output)==result,'Completed audit changed'
 else:output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({k:result[k] for k in ('passed','fresh_compiler_sources','source_pins','shared_base_pins','source_delta_pins','unresolved_names','unresolved_references')}))
if __name__=='__main__':main()
