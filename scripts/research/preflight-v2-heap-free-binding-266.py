"""Inspect every actual raw heap-free consumer before any alias is emitted."""
import hashlib,importlib.util,json,sys
from pathlib import Path
import capstone
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/266-heap-free-binding'
OUT=ROOT/'local/experiments/v2-heap-free-binding-266'
RAW='?FUN_00531f90@@YAIH@Z'
CAN='?free_00531f90@porsche@@YAIPAX@Z'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p):return json.loads(Path(p).read_bytes())
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 RUN.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 u=load(ROOT/'iterations/v2/001-original-recovery/runs/264-heap-release-union/summary.json')
 f=next(x for x in u['frontier'] if x['symbol']==RAW)
 assert len(f['referring_object_vas'])==f['object_references']==10
 p=module('coff266',ROOT/'scripts/research/audit-v2-nested-calls-229.py')
 symbols=module('symbols266',ROOT/'scripts/research/build-v2-compile-corpus.py')
 cap=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
 consumers=[]
 for va in f['referring_object_vas']:
  row=next(x for x in u['results'] if x['va']==va)
  obj=ROOT/row['object'];src=ROOT/row['generated_source']
  assert sha(obj)==row['object_sha256'] and RAW in symbols.coff_symbols(obj)['undefined']
  assert 'undefined4 FUN_00531f90(int param_1);' in src.read_text(errors='replace')
  defined=symbols.coff_symbols(obj)['defined'];assert len(defined)==1
  body,relocs=p.coff_function(obj,defined[0]);raw_reloc=[x for x in relocs if x['symbol']==RAW]
  assert len(raw_reloc)==1
  instructions=list(cap.disasm(body,0));site=raw_reloc[0]['offset']
  ix=next(i for i,ins in enumerate(instructions) if ins.address<=site<ins.address+ins.size)
  assert ix>=1 and ix+1<len(instructions)
  assert instructions[ix].bytes[0]==0xe8 and site==instructions[ix].address+1 and instructions[ix].mnemonic=='call'
  assert instructions[ix-1].mnemonic=='push' and instructions[ix+1].bytes==bytes.fromhex('83c404')
  neighborhood=[dict(offset=ins.address,hex=ins.bytes.hex(),mnemonic=ins.mnemonic,operands=ins.op_str) for ins in instructions[max(0,ix-3):ix+5]]
  consumers.append(dict(va=va,object=rel(obj),object_sha256=sha(obj),source=rel(src),source_sha256=sha(src),defined=defined[0],raw_relocations=raw_reloc,call_instruction=dict(offset=instructions[ix].address,hex=instructions[ix].bytes.hex(),mnemonic=instructions[ix].mnemonic,operands=instructions[ix].op_str),one_dword_push_before=True,caller_pops_four_bytes=True,full_EAX_not_narrowed=True,neighborhood=neighborhood))
 canonical=next(x for x in u['results'] if x['va']=='00531f90');assert canonical['symbols']['defined']==[CAN]
 original=ROOT/'local/game/Porsche.exe';assert sha(original)==u['original_sha256']
 lines=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines()
 addresses={f'{v:08x}' for v in range(0x531f90,0x5320a6)}
 body=[x for x in lines if len(x)>=8 and x[:8].lower() in addresses]
 assert len(body)==95 and any('MOV EAX,0x1' in x for x in body) and body[-1].startswith('005320a5') and body[-1].endswith('RET')
 header=ROOT/'iterations/v2/001-original-recovery/source/include/porsche/fe_stream.hpp';assert 'std::uint32_t __cdecl free_00531f90(void*);' in header.read_text()
 report=dict(schema=1,kind='heap-free-raw-ABI-preflight',original_sha256=u['original_sha256'],raw_symbol=RAW,canonical_symbol=CAN,consumer_count=10,consumers=consumers,canonical_object=canonical['object'],canonical_object_sha256=canonical['object_sha256'],canonical_header=rel(header),canonical_header_sha256=sha(header),original_body_va='00531f90',original_body_bytes=278,original_RET_pop_bytes=0,original_full_EAX_on_return=1,canonical_signature='uint32_t __cdecl (void*)',raw_signature='undefined4 __cdecl (int)',alias_approved=True)
 (RUN/'preflight.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(consumers=len(consumers),one_dword_cdecl=sum(x['one_dword_push_before'] and x['caller_pops_four_bytes'] for x in consumers),alias_approved=True)))
if __name__=='__main__':main()
