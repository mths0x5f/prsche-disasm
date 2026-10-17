"""Bounded PE reference and constructor preflight for two startup float cells."""
import hashlib,json,struct
from pathlib import Path
import capstone

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/286-startup-state-consumers'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CELLS=(0x5e6724,0x5e6720)
FUNCS=((0x4035e0,20),(0x403600,19))

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def load(path):return json.loads(Path(path).read_bytes())

def main():
 RUN.mkdir(parents=True,exist_ok=True)
 pe_path=ROOT/'local/game/Porsche.exe';data=pe_path.read_bytes();assert sha(pe_path)==SHA
 pe=struct.unpack_from('<I',data,0x3c)[0];assert data[pe:pe+4]==b'PE\0\0'
 base=struct.unpack_from('<I',data,pe+24+28)[0];assert base==0x400000
 n=struct.unpack_from('<H',data,pe+6)[0];oh=struct.unpack_from('<H',data,pe+20)[0]
 sections=[]
 for i in range(n):
  p=pe+24+oh+i*40
  vs,va,rawsize,raw=struct.unpack_from('<IIII',data,p+8)
  sections.append(dict(name=data[p:p+8].split(b'\0')[0].decode(),virtual_size=vs,rva=va,raw_size=rawsize,raw=raw,chars=struct.unpack_from('<I',data,p+36)[0]))
 def at(va,size):
  rva=va-base
  x=[s for s in sections if s['rva']<=rva and rva+size<=s['rva']+s['raw_size']]
  assert len(x)==1,(hex(va),size)
  s=x[0];return data[s['raw']+rva-s['rva']:s['raw']+rva-s['rva']+size]
 def occurrences(va):
  needle=struct.pack('<I',va);out=[];pos=data.find(needle)
  while pos>=0:
   mapped=[dict(section=s['name'],va=f'{base+s["rva"]+pos-s["raw"]:08x}') for s in sections if s['raw']<=pos and pos+4<=s['raw']+s['raw_size']]
   out.append(dict(file_offset=f'{pos:08x}',mapped=mapped))
   pos=data.find(needle,pos+1)
  return out
 c=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);c.detail=True
 bodies=[];direct=[]
 for start,size in FUNCS:
  blob=at(start,size);ins=list(c.disasm(blob,start));assert sum(i.size for i in ins)==size and ins[-1].mnemonic=='ret'
  body=[]
  for i in ins:
   operands=[]
   for op in i.operands:
    if op.type==capstone.x86.X86_OP_MEM and op.mem.base==0 and op.mem.index==0:
     target=op.mem.disp&0xffffffff
     # Capstone 5 reports FSTP's memory operand as read; D9 /3 is a store.
     access='write' if i.mnemonic=='fstp' or op.access&capstone.CS_AC_WRITE else 'read'
     operands.append(dict(target=f'{target:08x}',size=op.size,access=access))
     if target in CELLS:direct.append(dict(pc=f'{i.address:08x}',instruction=i.mnemonic+' '+i.op_str,bytes=bytes(i.bytes).hex(),cell=f'{target:08x}',access=operands[-1]['access'],width=op.size))
   body.append(dict(pc=f'{i.address:08x}',bytes=bytes(i.bytes).hex(),mnemonic=i.mnemonic,operands=i.op_str,absolute_memory_operands=operands))
  bodies.append(dict(entry=f'{start:08x}',bytes=size,sha256=hashlib.sha256(blob).hexdigest(),instructions=body))
 assert [(x['pc'],x['cell'],x['access'],x['width']) for x in direct]==[('004035ed','005e6724','write',4),('00403606','005e6724','read',4),('0040360c','005e6720','write',4)],direct
 assert occurrences(0x5e6724)==[dict(file_offset='000035ee',mapped=[dict(section='.text',va='004035ee')]),dict(file_offset='00003608',mapped=[dict(section='.text',va='00403608')])]
 assert occurrences(0x5e6720)==[dict(file_offset='0000360e',mapped=[dict(section='.text',va='0040360e')])]
 assert all(not occurrences(cell+delta) for cell in CELLS for delta in (1,2,3))
 assert occurrences(0x4035e0)==[dict(file_offset='001cb004',mapped=[dict(section='.data',va='005cb004')])]
 assert occurrences(0x403600)==[dict(file_offset='001cb008',mapped=[dict(section='.data',va='005cb008')])]
 assert at(0x5cb000,12)==struct.pack('<III',0,0x4035e0,0x403600)
 assert at(0x5b24a8,4)==bytes.fromhex('0000803f')
 for cell in CELLS:
  assert at(cell,4)==b'\0'*4
  sec=next(s for s in sections if s['rva']<=cell-base< s['rva']+s['virtual_size'])
  assert sec['name']=='.data' and sec['chars']&0x80000000 and not sec['chars']&0x20000000
 old=load(ROOT/'iterations/v2/001-original-recovery/runs/284-original-entry-audit/summary.json')
 assert old['original_sha256']==SHA and old['constructor_tables'][0]['first_nonzero']==dict(slot='005cb004',target='004035e0')
 registry_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json';registry=load(registry_path)['functions']
 assert not any(x['entry_va'] in ('004035e0','00403600') for x in registry)
 index_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
 index=[json.loads(x) for x in index_path.read_text().splitlines()]
 for start,size in FUNCS:
  assert not any(any(int(a,16)<=start<=int(b,16) for a,b in f['ranges']) for f in index)
 recovered=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe';headers=ROOT/'iterations/v2/001-original-recovery/source/include'
 source_files=sorted([*recovered.rglob('*.cpp'),*recovered.rglob('*.hpp'),*headers.rglob('*.hpp')])
 assert source_files and not any(any(token in x.read_text(errors='replace') for token in ('005e6724','005e6720','004035e0','00403600')) for x in source_files)
 source_tree_sha=hashlib.sha256(''.join(rel(x)+' '+sha(x)+'\n' for x in source_files).encode()).hexdigest()
 union_path=ROOT/'iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json';union=load(union_path)
 assert not any(any(token in name.lower() for token in ('005e6724','005e6720','004035e0','00403600')) for row in union['results'] for name in row['symbols']['defined'])
 numerator=struct.unpack('<f',at(0x5b24a8,4))[0];denominator=struct.unpack('<f',at(0x5e6724,4))[0]
 # The denominator at loader time is zero; constructor 1 writes the exact float bits first.
 assert numerator==1.0 and denominator==0.0
 ratio=1.0/struct.unpack('<f',struct.pack('<I',0x00800000))[0]
 result_bits=struct.unpack('<I',struct.pack('<f',ratio))[0];assert result_bits==0x7e800000
 paths=[pe_path,index_path,registry_path,union_path,ROOT/'iterations/v2/001-original-recovery/runs/284-original-entry-audit/summary.json',ROOT/'iterations/v2/001-original-recovery/runs/284-original-entry-audit/validation.json']
 report=dict(schema=1,kind='read-only-constructor-consumer-preflight',original_sha256=SHA,input_sha256={rel(x):sha(x) for x in paths},bodies=bodies,constructor_order=['005cb004 -> 004035e0','005cb008 -> 00403600'],table_prefix_hex=at(0x5cb000,12).hex(),storage=[dict(va=f'{cell:08x}',width=4,section='.data',initial_hex='00000000',raw_occurrences=occurrences(cell),interior_literal_occurrences=0) for cell in CELLS],direct_memory_uses=direct,formula=dict(numerator_source='005b24a8',numerator_bits='3f800000',denominator_written_to='005e6724',denominator_bits='00800000',instruction='x87 FLD 1.0; FDIV FLT_MIN; FSTP float32',derived_result_bits=f'{result_bits:08x}',result_destination='005e6720',derived_not_original_execution=True),ownership=dict(registry_body_owners=0,indexed_body_ranges=0,source_file_count=len(source_files),source_tree_sha256=source_tree_sha,source_literal_matches=0,current_274_exact_symbol_definitions=0),decision='bounded isolated proof candidate; no game integration justified from direct consumers alone',minimal_packet_if_requested=['two distinct original 4-byte cells, no 8-byte merged layout claim','two exact 20B/19B constructor bodies in the recorded table order','x87/native fixture must compare float output bits and relevant FP state under original control word','trace any computed or indirect alias before claiming game-visible use'],limits=['No direct later read of 005e6720 found; indirect/computed reads not excluded','No claim that these two constructors replace the original constructor table or CRT','No compiler, native executable or original runtime oracle in Run286'])
 (RUN/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 validation=dict(schema=1,summary_sha256=sha(RUN/'summary.json'),script_sha256=sha(__file__),read_only=True,original_sha256=SHA,exact_PE_bytes_and_order=True,direct_cell_references=3,source_and_registry_owner_checks=True)
 (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(constructors=2,direct_uses=3,downstream_direct_output_reads=0,derived_result_bits=f'{result_bits:08x}',decision='isolated preflight only')))
if __name__=='__main__':main()
