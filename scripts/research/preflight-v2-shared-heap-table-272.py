"""Decide heap-table storage independently of unproved candidate function entries."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
import capstone
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/272-shared-heap-table'
BASE=0x6b4f20;END=BASE+64
RAW='?DAT_006b4f20@@3IA';CAN='?heaps_006b4f20@porsche@@3PAPAUOriginalHeap@1@A'
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 RUN.mkdir(parents=True,exist_ok=True)
 runbase=ROOT/'iterations/v2/001-original-recovery/runs'
 a=load(runbase/'267-heap-table-evidence/summary.json');b=load(runbase/'270-heap-consumer-index/preflight.json');c=load(runbase/'271-heap-candidate-index/summary.json')
 assert a['target_va']=='006b4f20' and a['one_past']=='006b4f60' and a['claimed_storage_bytes']==64
 assert a['initial_bits']['hex']=='00'*64 and a['initial_bits']['source'].startswith('PE loader zero-filled virtual tail')
 assert len(a['table_or_endpoint_HIGHLOW'])==30 and len(a['indexed_operand_references'])==26 and len(a['unindexed_operand_gaps'])==4
 assert c['entry_status']=='unproved' and c['accepted_functions_added']==0 and c['heap_storage_approved']==False
 assert sorted(c['candidate_entry_vas'])==sorted(x['candidate_entry_va'] for x in map(json.loads,(ROOT/c['index']).read_text().splitlines()))
 assert a['existing_support_storage_overlap']==[]
 image=ROOT/'local/game/Porsche.exe';raw=image.read_bytes();assert sha(image)==a['original_sha256']==b['original_sha256']==c['original_sha256']
 pe=struct.unpack_from('<I',raw,0x3c)[0];assert raw[pe:pe+4]==b'PE\0\0'
 n=struct.unpack_from('<H',raw,pe+6)[0];oh=struct.unpack_from('<H',raw,pe+20)[0]
 sec=None;rva=BASE-0x400000
 for i in range(n):
  q=pe+24+oh+i*40;name=raw[q:q+8].split(b'\0')[0].decode();vsize,v,rawsize,rp=struct.unpack_from('<IIII',raw,q+8);flags=struct.unpack_from('<I',raw,q+36)[0]
  if v<=rva and rva+64<=v+vsize:sec=dict(name=name,virtual_size=vsize,virtual_address=v,raw_size=rawsize,raw_pointer=rp,flags=flags);break
 assert sec and sec['name']=='.data' and rva+64>sec['virtual_address']+sec['raw_size'] and (sec['flags']&0x80000000) and not (sec['flags']&0x20000000)
 assert a['initial_bits']['section']['flags']==sec['flags']
 heap=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/heap.cpp';header=ROOT/'iterations/v2/001-original-recovery/source/include/porsche/heap.hpp'
 assert b'OriginalHeap* heaps_006b4f20[16];' in heap.read_bytes() and 'extern OriginalHeap* heaps_006b4f20[16];' in header.read_text()
 assert sha(heap)==load(runbase/'078-shared-runtime-integration/heap/verification.json')['source_sha256'][rel(heap)]
 coff=mod('coff272',ROOT/'scripts/research/build-v2-compile-corpus.py');parser=mod('parse272',ROOT/'scripts/research/audit-v2-nested-calls-229.py')
 cap=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
 consumers=[]
 for old in a['actual_current_native_consumers']:
  if old['undefined']!=RAW:continue
  obj=ROOT/old['object'];assert sha(obj)==old['sha256'] and RAW in coff.coff_symbols(obj)['undefined']
  defined=coff.coff_symbols(obj)['defined'];assert len(defined)==1
  body,relocs=parser.coff_function(obj,defined[0]);refs=[r for r in relocs if r['symbol']==RAW]
  assert refs and all(r['type']==6 for r in refs)
  ins=list(cap.disasm(body,0));views=[]
  for ref in refs:
   ix=next(i for i,x in enumerate(ins) if x.address<=ref['offset']<x.address+x.size)
   inst=ins[ix]
   assert inst.bytes==bytes.fromhex('8b0c8500000000') and ref['offset']==inst.address+3
   assert inst.mnemonic=='mov' and inst.op_str=='ecx, dword ptr [eax*4]'
   assert ix>=1 and ins[ix-1].bytes==bytes.fromhex('83e00f'),('missing 0..15 mask',old['consumer'])
   views.append(dict(relocation=ref,instruction_offset=inst.address,hex=inst.bytes.hex(),mnemonic=inst.mnemonic,operands=inst.op_str,preceding_mask_hex=ins[ix-1].bytes.hex(),effective_slots='0..15'))
  consumers.append(dict(va=old['consumer'],object=rel(obj),object_sha256=sha(obj),defined=defined[0],views=views))
 assert sorted(x['va'] for x in consumers)==['00531c60','00556620']
 report=dict(schema=1,kind='shared-heap-table-storage-preflight',original_sha256=sha(image),storage_va='006b4f20',storage_bytes=64,one_past_va='006b4f60',initial_hex='00'*64,writable_virtual_tail=True,highlow_sites=30,indexed_sites=26,supplemental_decoded_sites=4,canonical_source=rel(heap),canonical_source_sha256=sha(heap),canonical_declaration='OriginalHeap* heaps_006b4f20[16];',canonical_header=rel(header),canonical_header_sha256=sha(header),raw_symbol=RAW,canonical_symbol=CAN,raw_consumers=consumers,entry_liveness_unproved=list(c['candidate_entry_vas']),storage_independent_of_entry_liveness=True,storage_approved=True,alias_approved=True,limits=['No candidate function entry promoted','No neighboring 006b4f60 cell','No original relative layout or computed alias claim','No startup initializer call semantics'])
 (RUN/'preflight.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(storage_approved=True,alias_approved=True,raw_consumers=len(consumers),views=[(x['va'],x['views']) for x in consumers],candidate_entries_unproved=4)))
if __name__=='__main__':main()
