"""Recheck291/292 artifacts and the fresh293 game build, without native reruns."""
import collections,hashlib,importlib.util,json,re,struct,subprocess
from pathlib import Path
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 packet_checks={}
 for name in ('291-frame-resolver','292-stdio-lock-prefix'):
  p=RUNS/name/'summary.json';s=load(p);v=load(p.with_name('validation.json'));assert sha(p)==v['summary_sha256']
  for path,h in s['input_sha256'].items():assert sha(ROOT/path if not Path(path).is_absolute() else path)==h,path
  packet_checks[name]=dict(summary_sha256=sha(p),input_pins=len(s['input_sha256']),native_cases=s['native_cases'])
 oracle=module('coffOracle293',ROOT/'scripts/research/audit-v2-direct-callee-223.py')
 getter=load(RUNS/'291-frame-resolver/summary.json');native,relocs=oracle.coff_function(ROOT/'local/experiments/v2-frame-resolver-291/objects/fixture.obj','@reference291@16')
 assert native.hex()==getter['original_body_hex'] and len(native)==25 and not relocs
 assert getter['native_cases']==512 and getter['new_distinct_function_VAs']==0 and not getter['undefined_symbols']
 assert getter['old_void_candidate']['method_contract']['return_storage']=='<VOID>'
 pre=load(RUNS/'292-stdio-lock-prefix/preflight.json')
 for patch in pre['patches']:
  before=subprocess.check_output(['git','show',pre['parent_commit']+':'+patch['path']])
  assert hashlib.sha256(before).hexdigest()==patch['before_sha256']
  assert before.count(patch['old'].encode())==1
  assert (ROOT/patch['path']).read_bytes()==before.replace(patch['old'].encode(),patch['new'].encode())
 image=(ROOT/'local/game/Porsche.exe').read_bytes();pe=struct.unpack_from('<I',image,0x3c)[0];n=struct.unpack_from('<H',image,pe+6)[0];opt=struct.unpack_from('<H',image,pe+20)[0]
 reloc=None
 for i in range(n):
  p=pe+24+opt+i*40
  if image[p:p+8].rstrip(b'\0')==b'.reloc':size,off=struct.unpack_from('<II',image,p+16);reloc=image[off:off+size]
 assert reloc is not None
 at=0;sites=[]
 while at+8<=len(reloc):
  page,size=struct.unpack_from('<II',reloc,at)
  if size==0:break
  assert size>=8 and at+size<=len(reloc)
  for p in range(at+8,at+size,2):
   value=struct.unpack_from('<H',reloc,p)[0];va=0x400000+page+(value&4095)
   if value>>12==3 and 0x5e57a8<=va<0x5e5868:sites.append(f'{va:08x}')
  at+=size
 assert sites==['005e57ac','005e57cc','005e57dc','005e57ec']
 literal=load(RUNS/'293-game-startup-followup/logging-literal.json');before=subprocess.check_output(['git','show',literal['parent_commit']+':'+literal['source']])
 assert hashlib.sha256(before).hexdigest()==literal['source_before_sha256']
 assert (ROOT/literal['source']).read_bytes()==before.replace(literal['old_cpp'].encode(),literal['new_cpp'].encode())
 reader=module('peRead293',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 assert reader.pe_read(image,0x5d6e84,24).hex()==literal['literal_hex']
 build_path=RUNS/'293-game-startup-followup/build-002.json';s=load(build_path)
 assert s['input_unchanged'] and s['source_count']==151 and len(s['project_paths'])==8
 assert not s['compiler_errors'] and not s['other_linker_errors'] and not s['executable']
 receipt_path=ROOT/s['receipt'];assert sha(receipt_path)==s['receipt_sha256'];receipt=load(receipt_path)
 assert receipt['exit_code']==s['exit_code']==1 and sha(ROOT/receipt['log'])==receipt['log_sha256']
 for path,h in s['source_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==h,path
 log=(ROOT/receipt['log']).read_text(encoding='utf8')
 expected=collections.Counter(Path(x).name for x in s['compiled_source_roots'])
 printed=collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$',log));assert printed==expected
 diagnostics=[line for line in log.splitlines() if re.search(r'\berror LNK(?:2001|2019):',line)]
 names={re.findall(r'\((\?[^()]+)\)',line)[0] for line in diagnostics}
 assert len(names)==s['unresolved_names']==269 and len(diagnostics)==s['unresolved_references']==305
 old=load(RUNS/'289-game-startup-link/logging-frame-001.json');closed={x['symbol'] for x in old['frontier']}-names
 assert len(closed)==1 and 'resolve_004898f0' in next(iter(closed))
 warning_lines=[line for line in log.splitlines() if re.search(r'warning [CD]\d+',line)]
 assert len(warning_lines)==3 and all('C4005' in line and 'WIN32_LEAN_AND_MEAN' in line for line in warning_lines)
 build_root=ROOT/'local/builds/v2/game-startup-followup-293'
 toolchain=load(build_root/'build-toolchain.json');assert toolchain['compiler_id']=='MSVC' and toolchain['pointer_size']==4
 app=list(build_root.glob('**/porsche_original.dir/Release/application_main.obj'));assert len(app)==1 and bytes.fromhex(literal['literal_hex']) in app[0].read_bytes()
 assert not list(build_root.glob('**/porsche_original_game_link.exe'))
 v=dict(schema=1,passed=True,audit_sha256=sha(__file__),packets=packet_checks,highlow_prefix_sites=sites,
        fresh_build_sha256=sha(build_path),fresh_compiler_sources=151,source_pins=len(s['source_sha256']),
        unresolved_names=269,unresolved_references=305,closed_getter=sorted(closed),
        compiled_original_newline_found=True,platform_macro_warnings=3,game_executed=False,
        historical_source_pin_note='Earlier26-entry proof snapshots retain their parent Git bytes;292 proves the two explicit current-source changes')
 (RUNS/'293-game-startup-followup/validation.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(passed=True,getter_cases=512,prefix_cases=112,fresh_sources=151,source_pins=v['source_pins'],unresolved_names=269)))
if __name__=='__main__':main()
