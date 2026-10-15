"""Bounded read-only194 printed-global/access-width evidence; no storage guesses."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import capstone
from capstone.x86 import X86_OP_MEM,X86_OP_IMM

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'local/experiments/v2-global-aliases-194';RUN=ROOT/'iterations/v2/001-original-recovery/runs/194-global-aliases'
GH=ROOT/'local/tools/ghidra_12.1.3_PUBLIC';SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CASES=[('00401000','_DAT_005e6664'),('00401060','_DAT_005b23f8'),('00401060','_DAT_00655a0c'),('00485100','_DAT_005b242c'),('00485100','_DAT_005b24a8'),('00485c50','_DAT_005b2680'),('00485c50','DAT_006b0068'),('00405a90','_DAT_005b2480'),('00405a90','_DAT_005b2520'),('00456d70','_DAT_005b3e3c'),('005a0c50','s_C_tv_mn_vu_fdesaB_rp_fe_005e5083'),('00432b60','s___1f___1f___1f_005cd1a0')]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')
def source_pins():
 paths=[ROOT/'scripts/research/ghidra/ExportGlobalAliases194.java',GH/'Ghidra/Features/Decompiler/src/decompile/cpp/printc.cc',GH/'Ghidra/Features/Decompiler/lib/Decompiler-src.zip',GH/'Ghidra/Features/Decompiler/lib/Decompiler.jar',GH/'Ghidra/Features/Decompiler/os/win_x86_64/decompile.exe',GH/'Ghidra/Framework/SoftwareModeling/lib/SoftwareModeling.jar',ROOT/'iterations/v2/001-original-recovery/runs/179-ghidra-declarations/export/globals.jsonl',ROOT/'iterations/v2/001-original-recovery/runs/179-ghidra-declarations/export/functions.jsonl']
 return {str(p):sha(p) for p in paths}
def binary():
 records=map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines());meta=next(r for r in records if r['file']=='Porsche.exe');path=ROOT/'local/game'/meta['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA;return path,raw
def key(n):return (n['space'],n['offset'],n['bytes'])
def pe_mapping(raw):
 assert raw[:2]==b'MZ';pe=struct.unpack_from('<I',raw,0x3c)[0];assert raw[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',raw,pe+4)[0]==0x14c
 optional=pe+24;assert struct.unpack_from('<H',raw,optional)[0]==0x10b
 imagebase=struct.unpack_from('<I',raw,optional+28)[0];sections=[];table=optional+struct.unpack_from('<H',raw,pe+20)[0]
 for i in range(struct.unpack_from('<H',raw,pe+6)[0]):
  size,rva,rawsize,pointer=struct.unpack_from('<IIII',raw,table+i*40+8);sections.append((rva,size,rawsize,pointer))
 def offset(va,length):
  rva=va-imagebase
  for begin,size,rawsize,pointer in sections:
   if begin<=rva<begin+max(size,rawsize):assert rva-begin+length<=rawsize;return pointer+rva-begin
  raise AssertionError('instruction outside original PE sections')
 return offset
def constant(n,state):return int(n['offset']) if n['constant'] else state.get(key(n))
def raw_accesses(instruction,address):
 state={};access=[]
 for op in instruction['raw_pcode']:
  code=op['opcode'];ins=op['inputs'];out=op.get('output')
  if code in ('LOAD','STORE') and len(ins)>=2 and constant(ins[1],state)==address:
   access.append({'kind':code,'bytes':out['bytes'] if code=='LOAD' else ins[2]['bytes'],'sequence':op['sequence'],'pointer':'constant or intra-instruction constant COPY/ADD/SUB chain'})
  if out:
   values=[constant(n,state) for n in ins];value=None
   if code=='COPY' and values and values[0] is not None:value=values[0]
   elif code in ('INT_ADD','INT_SUB') and all(v is not None for v in values):value=values[0]+values[1] if code=='INT_ADD' else values[0]-values[1]
   if value is not None:state[key(out)]=value&((1<<(8*out['bytes']))-1)
 return access
def report():
 pins=json.loads((OUT/'capture-pins.json').read_text());assert pins==source_pins(),'capture source/tool/input mutation'
 capture=json.loads((OUT/'export/result.json').read_text());assert capture['original_sha256']==SHA and not capture['analysis'] and capture['read_only'] and capture['program_changed_before']==capture['program_changed_after']
 path,raw=binary();offset_for_va=pe_mapping(raw);decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True;records=[]
 assert len(capture['cases'])==12
 for case in capture['cases']:
  address=int(case['address'],16);instructions=[];pcmin=int(case['function_min'],16);pcmax=int(case['function_max'],16)
  for original in case['original_references']:
   pc=int(original['pc'],16);data=bytes.fromhex(original['bytes']);assert pcmin<=pc<=pcmax;offset=offset_for_va(pc,len(data));assert raw[offset:offset+len(data)]==data
   decoded=list(decoder.disasm(data,pc));assert len(decoded)==1 and decoded[0].size==len(data);ins=decoded[0];memory=[];immediates=[]
   for operand in ins.operands:
    if operand.type==X86_OP_MEM and operand.mem.base==0 and operand.mem.index==0 and operand.mem.disp&0xffffffff==address:memory.append({'bytes':operand.size,'access':operand.access,'segment':operand.mem.segment})
    if operand.type==X86_OP_IMM and operand.imm&0xffffffff==address:immediates.append({'value':address,'bytes':operand.size})
   sleigh=raw_accesses(original,address);widths={r['bytes'] for r in sleigh};native_widths={r['bytes'] for r in memory}
   agreement=bool(sleigh) and bool(memory) and widths==native_widths and ins.mnemonic!='lea'
   instructions.append({'pc':original['pc'],'pe_file_offset':offset,'bytes':original['bytes'],'original_bytes_verified':True,'capstone':ins.mnemonic+' '+ins.op_str,'capstone_memory_operands':memory,'capstone_address_immediates':immediates,'sleigh_direct_accesses':sleigh,'direct_access_width_agrees':agreement,'address_only':bool(immediates) or (ins.mnemonic=='lea' and bool(memory)),'raw_instruction':original})
  occurrences=[]
  for token in case['tokens']:
   vn=token.get('varnode');occurrences.append({'text':token['text'],'pc':token.get('pc'),'node_bytes':vn['bytes'] if vn else None,'node_space':vn['space'] if vn else None,'node_address':vn['address'] if vn else None,'node_type':vn.get('high_type') if vn else None,'token_consumer':token.get('consumer'),'token':token})
  widths=sorted({a['bytes'] for ins in instructions if ins['direct_access_width_agrees'] for a in ins['sleigh_direct_accesses']});classification='direct_original_memory_access' if widths else 'address_only' if any(i['address_only'] for i in instructions) else 'unresolved_instruction_link'
  records.append({'va':case['va'],'alias':case['alias'],'address':case['address'],'classification':classification,'original_direct_access_widths':widths,'tokens':occurrences,'formal_symbols':case.get('formal_symbols_at_address',[]),'listing_data':case.get('listing_data'),'instructions':instructions,'limits':['Printed token PC is a normalized consumer PC, not automatically the original memory-access PC.','Access width/type is per consumer; no global identity conflict resolution, alias coalescing, storage allocation or signedness inference from spelling.']})
 result={'schema':1,'module':'Porsche.exe','original_sha256':SHA,'original_binary':str(path),'capstone_version':capstone.__version__,'input_pins':pins,'script_sha256':sha(Path(__file__)),'cases':records,'classification_counts':dict(Counter(r['classification'] for r in records)),'program_changed_before':capture['program_changed_before'],'program_changed_after':capture['program_changed_after'],'bound':'Twelve aliases only; original project -noanalysis -readOnly; no code/data edits or native declarations.'}
 dump(RUN/'summary.json',result);print(json.dumps({'cases':len(records),'classifications':result['classification_counts'],'token_occurrences':sum(len(r['tokens']) for r in records),'verified_instructions':sum(len(r['instructions']) for r in records)}))
 for r in records:print(json.dumps({'va':r['va'],'alias':r['alias'],'kind':r['classification'],'widths':r['original_direct_access_widths'],'token_sizes':sorted({t['node_bytes'] for t in r['tokens'] if t['node_bytes'] is not None}),'formal_sizes':sorted({s['bytes'] for s in r['formal_symbols']})}))
def main():
 p=argparse.ArgumentParser();p.add_argument('--report',action='store_true');args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);(OUT/'export').mkdir(exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 if args.report:report()
 else:
  cases=[{'va':va,'alias':name,'address':re.search(r'([0-9a-f]{8})$',name).group(1)} for va,name in CASES];assert len(cases)<=12;dump(OUT/'cases.json',cases);dump(OUT/'capture-pins.json',source_pins());binary();print(json.dumps({'cases':len(cases),'output':str(OUT/'export'),'project':'local/experiments/binary-index-ghidra/binary-index','flags':['-noanalysis','-readOnly']}))
if __name__=='__main__':main()
