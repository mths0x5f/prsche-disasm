"""Bounded exact-owner and raw ABI preflight for two original file operations."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
import capstone

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/276-file-operation-reuse'
BASE=ROOT/'iterations/v2/001-original-recovery/runs'
VAs=('00568200','005682a0')
RAW={'00568200':'?FUN_00568200@@YAIH@Z','005682a0':'?FUN_005682a0@@YAHIEII@Z'}
CAN={'00568200':'?operation_queue_00568200@porsche@@YAIPAUFileOperation@1@@Z','005682a0':'?operation_allocate_005682a0@porsche@@YAPAUFileOperation@1@IEPAXI@Z'}
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 RUN.mkdir(parents=True,exist_ok=True)
 union=load(BASE/'274-shared-heap-union/summary.json')
 queue=load(BASE/'275-link-frontier-queue/summary.json')
 assert queue['union_summary_sha256']==sha(BASE/'274-shared-heap-union/summary.json')
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')
 owners=[x for x in registry['functions'] if x['entry_va'] in VAs]
 assert len(owners)==2 and all(x['source'].endswith('/files.cpp') and x['status']=='native-differential-verified' for x in owners)
 assert not any(x['va'] in VAs for x in union['results'])
 assert all(next(x for x in queue['tasks'] if x.get('original_va')==va)['action']=='accepted_owner_reuse_review' for va in VAs)
 original=ROOT/'local/game/Porsche.exe';pe=original.read_bytes()
 assert sha(original)==union['original_sha256']
 peoff=struct.unpack_from('<I',pe,0x3c)[0];assert pe[peoff:peoff+4]==b'PE\0\0'
 n=struct.unpack_from('<H',pe,peoff+6)[0];oh=struct.unpack_from('<H',pe,peoff+20)[0]
 def body(va,size):
  rva=int(va,16)-0x400000
  for i in range(n):
   q=peoff+24+oh+i*40;vs,addr,rs,ptr=struct.unpack_from('<IIII',pe,q+8)
   if addr<=rva and rva+size<=addr+rs:return pe[ptr+rva-addr:ptr+rva-addr+size]
  raise AssertionError(('PE raw span absent',va))
 index={x['entry_va']:x for x in map(json.loads,(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()) if x['entry_va'] in VAs}
 cap=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
 targets=[]
 for va in VAs:
  item=index[va];assert len(item['ranges'])==1 and int(item['ranges'][0][1],16)-int(va,16)+1==item['body_bytes']
  blob=body(va,item['body_bytes']);ins=list(cap.disasm(blob,int(va,16)))
  assert sum(x.size for x in ins)==len(blob) and ins[-1].mnemonic=='ret' and ins[-1].size==1
  assert not any(int(y,16)>int(va,16) and int(y,16)<=int(item['ranges'][0][1],16) for y in VAs if y!=va)
  targets.append(dict(va=va,size=len(blob),sha256=hashlib.sha256(blob).hexdigest(),raw_symbol=RAW[va],canonical_symbol=CAN[va],original_ret_pop=0,original_instructions=len(ins)))
 fn=mod('coff276fn',ROOT/'scripts/research/audit-v2-nested-calls-229.py')
 coff=mod('coff276symbols',ROOT/'scripts/research/build-v2-compile-corpus.py')
 consumers=[]
 for va in ('00568ae0','00568b10','00568b50','00568b90'):
  row=next(x for x in union['results'] if x['va']==va)
  obj=ROOT/row['object'];assert sha(obj)==row['object_sha256']
  symbols=coff.coff_symbols(obj);assert all(RAW[x] in symbols['undefined'] for x in VAs)
  defined=symbols['defined'];assert len(defined)==1
  code,refs=fn.coff_function(obj,defined[0]);ins=list(cap.disasm(code,0))
  sites=[]
  for target in VAs:
   hits=[x for x in refs if x['symbol']==RAW[target]];assert len(hits)==1 and hits[0]['type']==20
   hit=hits[0];i=next(j for j,x in enumerate(ins) if x.address<=hit['offset']<x.address+x.size)
   op=ins[i];assert op.mnemonic=='call' and op.bytes[0]==0xe8 and hit['offset']==op.address+1
   expected_pop=4 if target=='00568200' else 16
   assert i+1<len(ins) and ins[i+1].mnemonic=='add' and ins[i+1].op_str==f'esp, {expected_pop:#x}'.replace('0x4','4').replace('0x10','0x10')
   if target=='00568200':assert ins[i-1].mnemonic=='push'
   else:assert sum(x.mnemonic=='push' for x in ins[i-8:i])==4 and ins[i-1].mnemonic=='push'
   # The caller's shared epilogue performs caller-side cleanup; no callee-pop ABI.
   neighborhood=[dict(offset=x.address,hex=x.bytes.hex(),mnemonic=x.mnemonic,operands=x.op_str) for x in ins[max(0,i-7):min(len(ins),i+7)]]
   sites.append(dict(target=target,relocation=hit,call_offset=op.address,caller_pop_bytes=expected_pop,neighborhood=neighborhood))
  consumers.append(dict(va=va,object=rel(obj),object_sha256=sha(obj),source=row['generated_source'],source_sha256=row['generated_source_sha256'],defined=defined[0],sites=sites))
 source=ROOT/owners[0]['source'];header=ROOT/'iterations/v2/001-original-recovery/source/include/porsche/files.hpp'
 assert all(x['source']==rel(source) for x in owners)
 previous=BASE/'078-shared-runtime-integration/joint-disk/verification.json';verified=load(previous)
 assert verified['native_cpp_equal_original_x86'] and all(va in verified['function_vas'] for va in VAs)
 assert verified['source_sha256'][rel(source)]==sha(source) and verified['source_sha256'][rel(header)]==sha(header)
 assert 'std::uint32_t __cdecl operation_queue_00568200(FileOperation* op)' in source.read_text()
 assert 'FileOperation* __cdecl operation_allocate_005682a0(std::uint32_t type,std::uint8_t group,void* context,std::uint32_t index)' in source.read_text()
 assert all(CAN[va].startswith('?operation_') for va in VAs)
 report=dict(schema=1,kind='exact-canonical-file-operation-preflight',original_sha256=sha(original),union_summary=rel(BASE/'274-shared-heap-union/summary.json'),union_summary_sha256=sha(BASE/'274-shared-heap-union/summary.json'),registry=rel(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'),registry_sha256=sha(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'),prior_oracle=rel(previous),prior_oracle_sha256=sha(previous),prior_oracle_cases=verified['cases'],source=rel(source),source_sha256=sha(source),header=rel(header),header_sha256=sha(header),targets=targets,consumers=consumers,consumer_count=len(consumers),raw_references=8,entry_liveness_proven=True,proposed_batch='one /MP6 two exact fragment TUs, two directive-only aliases and private native differential fixture',limits=['No caller object edits','No global storage clones','No handle_device ABI claim','Disk/event/platform behavior outside controlled fixture'])
 (RUN/'preflight.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(targets=len(targets),consumers=len(consumers),raw_references=8,source=rel(source))))
if __name__=='__main__':main()
