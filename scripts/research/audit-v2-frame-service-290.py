"""Independent acceptance audit for the bounded frame-service game objects."""
import hashlib,importlib.util,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/290-frame-service-cluster'
OUT=ROOT/'local/experiments/v2-frame-service-290'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def pe_read(raw,va,n):
 pe=struct.unpack_from('<I',raw,0x3c)[0];count=struct.unpack_from('<H',raw,pe+6)[0];oh=struct.unpack_from('<H',raw,pe+20)[0]
 image=struct.unpack_from('<I',raw,pe+24+28)[0];rva=va-image
 for i in range(count):
  p=pe+24+oh+i*40;vsize,base,rsize,roff=struct.unpack_from('<IIII',raw,p+8)
  if base<=rva and rva+n<=base+rsize:return raw[roff+rva-base:roff+rva-base+n]
 raise AssertionError(hex(va))
def main():
 summary=json.loads((RUN/'summary.json').read_bytes())
 assert summary['original_sha256']==sha(ROOT/'local/game/Porsche.exe')
 assert summary['original_vas']==['00471b60','00487e20'] and summary['original_selected_bytes']==98
 for name,h in summary['input_sha256'].items():
  p=Path(name);p=p if p.is_absolute() else ROOT/p;assert sha(p)==h,(name,h)
 original=(ROOT/'local/game/Porsche.exe').read_bytes()
 asm=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text()
 spans=[('00471b60',11),('00487e20',87)]
 for va,n in spans:
  block=asm.split('; FUNCTION '+va,1)[1].split('; FUNCTION ',1)[0]
  decoded=b''.join(bytes.fromhex(x) for x in re.findall(r'(?m)^'+va[:4]+r'[0-9a-f]{4}\s+([0-9a-f]+)\s+',block))
  assert decoded==pe_read(original,int(va,16),n) and len(decoded)==n,va
 registry=json.loads((ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
 index=[json.loads(x) for x in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
 assert all(not any(int(a,16)<=int(va,16)<=int(b,16) for a,b in x['ranges']) for va,_ in spans for x in index if x['entry_va'] in {r['entry_va'] for r in registry})
 cof=module('coff290audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 expected_defined=['?application_main_function_00471b60@porsche@@YAXXZ','?execute_00487e20@FrameService_290@porsche@@QAEXXZ']
 undefined=[]
 for row,want in zip(summary['results'],expected_defined):
  p=ROOT/row['object'];assert sha(p)==row['object_sha256']
  symbols=cof.coff_symbols(p);assert symbols==row['symbols'] and symbols['defined']==[want]
  assert not symbols['common'] and not symbols['weak']
  undefined+=symbols['undefined']
  assert sha(ROOT/row['generated_source'])==row['generated_source_sha256']
  deps=json.loads((ROOT/row['source_dependencies']).read_bytes())
  assert Path(deps['Data']['Source']).resolve()==(ROOT/row['generated_source']).resolve()
 assert len(undefined)==6 and any('frame_service_root_00628960' in x for x in undefined)
 assert not any('frame_service_root_00628960' in x for x in expected_defined)
 for name,exitcode in [('compile-001',2),('compile-002',0),('fixture-link-002',0),('fixture-native-002',0)]:
  receipt=json.loads((OUT/(name+'.execution.json')).read_bytes())
  assert receipt['exit_code']==exitcode and sha(ROOT/receipt['log'])==receipt['log_sha256']
 assert summary['native_fixture']['exit_code']==0
 oracle=json.loads((RUN/'original-oracles.json').read_bytes());assert len(oracle['cases'])==6
 validation=dict(schema=1,summary_sha256=sha(RUN/'summary.json'),actual_pe_body_bytes=98,
                 original_oracle_cases=6,native_cases_passed=6,game_object_count=2,
                 first_failed_compile_preserved=True,successful_compile_batches=1,
                 actual_coff_undefined_external_symbols=undefined,
                 production_game_global_or_callee_provider_count=0)
 (RUN/'validation.json').write_bytes((json.dumps(validation,indent=2)+'\n').encode())
 print('PE 98B, COFF 2 bodies, original/native 6 cases, receipts verified')
if __name__=='__main__':main()
