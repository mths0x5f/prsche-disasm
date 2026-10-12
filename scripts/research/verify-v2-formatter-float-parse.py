"""Run170: native original integer parser/packer and full memory/ABI/FPU proof."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
from v2_source_dependencies import source_hashes
ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS=(0x5ac716,0x5abb07,0x5ab90d,0x5ab956,0x5ab9ac,0x5aba38,0x5aba53,0x5aba5f,0x5aba7a,0x5adb88)
SHARED=(0x5adaae,0x5adacf,0x5adb2d,0x5adb5b,0x5adf5b,0x5ae17b,0x5abc9f,0x5abccc,0x5abc73,0x5abc89)
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EFLAGS
ARENA,STACK,EXIT=0x24000000,0x22000000,0x2200f000

def make_uc(image,module):
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(0x400000,0x300000);uc.mem_map(ARENA,0x10000);uc.mem_map(STACK,0x10000)
 for s in module['sections']:
  if s['raw_size']:uc.mem_write(0x400000+s['rva'],image[s['raw_offset']:s['raw_offset']+s['raw_size']])
 return uc

def original(uc,row,index,ctype,coverage):
 op,a,b,c,d,e,width,decimal,control,prefix,variant,data=row
 put=lambda p,v:uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 get=lambda p:struct.unpack('<I',uc.mem_read(p,4))[0]
 uc.mem_write(ARENA,bytes((i*13+index*7+0x21)&255 for i in range(8192)));uc.mem_write(ARENA+0x100,data)
 uc.mem_write(ARENA+0x1000,ctype);uc.mem_write(ARENA+0x1200,ctype)
 if variant&1:
  for offset in (0x1000+63*2,0x1000+255*2,0x1200+63*2):uc.mem_write(ARENA+offset,bytes([uc.mem_read(ARENA+offset,1)[0]|4]))
 for va,value in ((0x5e54dc,width),(0x5e54e0,decimal),(0x5e52d0,ARENA+0x1000)):put(va,value)
 if op==0:args=[ARENA+0x800,ARENA+0xc00,ARENA+0x100,a,b,c,d]
 elif op==1:
  uc.mem_write(ARENA+0x500,bytes(uc.mem_read(0x5e6140 if a==32 else 0x5e6128,24)));put(ARENA+0x510,a);args=[ARENA+0x100,ARENA+0x800,ARENA+0x500]
 elif op in (2,3,4,8):args=[ARENA+0x100,a]
 elif op==5:args=[(ARENA+0x100+a)&0xffffffff,ARENA+0x100]
 elif op in (6,7):args=[ARENA+0x100]
 elif op==9:args=[ARENA+0x100,a,ARENA+0x800]
 else:args=[ARENA+0x800,ARENA+0x100]
 frames=[];stages=bytearray();events='';class_calls=0
 def emit(tag,phase,data):stages.extend(struct.pack('<III',tag,phase,len(data))+data)
 def hook(m,va,_size,_data):
  nonlocal events,class_calls
  sp=m.reg_read(UC_X86_REG_ESP)
  while frames and frames[-1][0]==va and frames[-1][1]+4==sp:
   ret,_,tag,out=frames.pop();emit(tag,1,bytes(m.mem_read(out,12)))
  if va==EXIT:m.emu_stop();return
  coverage[va]=coverage.get(va,0)+1
  arg=lambda n:get(sp+4+n*4)
  tags={0x5ab9ac:1,0x5aba7a:2,0x5adb88:3,0x5ae17b:4}
  if va in tags:
   tag=tags[va];out=arg(2) if tag==3 else arg(0)
   if tag in (1,2):emit(tag,0,bytes(m.mem_read(arg(0),12)));emit(tag,2,struct.pack('<I',arg(1)))
   elif tag==3:emit(tag,0,bytes(m.mem_read(arg(0),arg(1))));emit(tag,2,struct.pack('<I',arg(1)))
   else:emit(tag,0,bytes(m.mem_read(arg(0),12))+struct.pack('<II',arg(1),arg(2)))
   frames.append((get(sp),sp,tag,out))
  if va==0x5a2eae:
   value,mask=arg(0),arg(1);result=m.mem_read(get(0x5e52d0)+value*2,1)[0]&mask
   events+=f'class:{value:08x}:{mask:08x}:{result:08x};';class_calls+=1
   if variant&2 and class_calls==1:
    for p,v in ((0x5e54dc,1),(0x5e54e0,44),(0x5e52d0,ARENA+0x1200)):put(p,v)
   m.reg_write(UC_X86_REG_EAX,result);m.reg_write(UC_X86_REG_EIP,get(sp));m.reg_write(UC_X86_REG_ESP,sp+4)
 handle=uc.hook_add(UC_HOOK_CODE,hook);sp=STACK+0x8000;uc.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),EXIT,*args));uc.reg_write(UC_X86_REG_ESP,sp)
 for reg in (UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI):uc.reg_write(reg,0x12345678)
 uc.reg_write(UC_X86_REG_EFLAGS,2);uc.emu_start((VAS+(0x5abc9f,0x5abccc))[op],0,count=2000000);uc.hook_del(handle)
 assert not frames and uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==sp+4,(index,'completion')
 assert all(uc.reg_read(reg)==0x12345678 for reg in (UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI))
 result=uc.reg_read(UC_X86_REG_EAX) if op<=4 or op==7 or op>=10 else 0
 return {'case':index,'result':f'{result:08x}','events':events,'width':f'{get(0x5e54dc):08x}','decimal':f'{get(0x5e54e0):08x}','ctype':f'{get(0x5e52d0):08x}','memory':bytes(uc.mem_read(ARENA,8192)).hex()},bytes(stages)

def cases():
 rows=[]
 def add(op,a=0,b=0,c=0,d=0,e=0,width=1,decimal=46,control=0x37f,prefix=0,variant=0,data=bytes(32)):
  rows.append((op,a&0xffffffff,b&0xffffffff,c&0xffffffff,d&0xffffffff,e&0xffffffff,width,decimal,control,prefix,variant,data))
 texts=[b'',b' ',b'\t\r\n',b'.',b'-',b'+',b'+.',b'-.',b'0',b'-0',b'000.000',b'1',b'123',b'1.25',b'.0001',b'1e',b'1e+',b'1e-',b'1e0',b'1d3',b'1D-3',b'1+2',b'1-2',b'1.2.3',b'inf',b'nan',b'\v1',b'\f1',b' \t-12.34e+001x',b'1e000009x',b'0e+000x']
 texts += [b'1e'+str(x).encode() for x in (-5201,-5200,-4932,-4096,-4095,-324,-308,308,324,4095,4096,4932,5200,5201,999999)]
 texts += [b'12345678901234567890123'+bytes([x])+bytes([y])+b'7890' for x,y in itertools.product(b'459',b'049')]
 for text,op in itertools.product(texts,(0,10,11)):
  add(op,data=text+b'\0')
 for text,keep,implicit,width in itertools.product(texts,(0,1),(0,1),(1,2)):
  add(0,a=keep,d=implicit,width=width,data=text+b'\0')
 for text,exp,dot in itertools.product((b'1',b'1.',b'1e2',b'1.1e2',b'0.1',b'123000'),(-5201,-5200,-4096,-1,0,1,4096,5200,5201,0x7fffffff,-0x80000000),(0,1,-1,0x7fffffff,-0x80000000)):
  add(0,b=exp,c=dot,data=text+b'\0')
 for text,width,variant,decimal in itertools.product((b'1?2x',b'1\xff2',b'.?1',b'1e?2',b'1,2',b'1.2'),(1,2),(0,1,2,3),(46,44,255)):
  add(0,width=width,variant=variant,decimal=decimal,data=text+b'\0')
 for exponent,sign,mantissa,low,outwidth in itertools.product((0,1,0x3bcd,0x3bce,0x3bff,0x3c00,0x3c01,0x3f80,0x3fff,0x4000,0x407e,0x407f,0x43fe,0x43ff,0x7ffe,0x7fff),(0,0x8000),(0,1,0x7fffffffffffffff,0x8000000000000000,0x8000000000000001,0xffffffffffffffff),(0,1,0x8000,0xffff),(32,64)):
  add(1,a=outwidth,data=struct.pack('<HQH',low,mantissa,exponent|sign))
 for value,bit,op in itertools.product((bytes(12),bytes([255])*12,struct.pack('<III',0x80000000,1,1),struct.pack('<III',0,0,1)),(0,1,23,24,31,32,33,52,53,63,64,65,94),(2,3,4,8)):
  add(op,a=bit,data=value)
 for bit in (95,96,127,128,4096):add(8,a=bit,data=bytes([255])*12)
 for bit,op in itertools.product((-31,-17,-1),(2,3,4,8)):add(op,a=bit,data=bytes([255])*12)
 for outwidth in (0,1,31,63,65,0xffffffff):add(1,a=outwidth,data=struct.pack('<HQH',0xffff,0x8000000000000001,0x3fff))
 for offset in (-4,0,4,8,12):add(5,a=offset,data=bytes(range(32)))
 for op,value in itertools.product((6,7),(bytes(12),bytes([255])*12,struct.pack('<III',0,0,1))):add(op,data=value)
 for count in (1,2,9,17,24,25):
  for value in (bytes([1])*count,bytes([9])*count,bytes([1])+bytes(count-1),bytes((i%10 for i in range(count-1)))+bytes([1])):add(9,a=count,data=value)
 rng=random.Random(170)
 for _ in range(150):
  value=rng.randbytes(12)
  for op in (1,2,3,4,8):add(op,a=rng.choice((32,64)) if op==1 else rng.randrange(1,95),data=value)
 for _ in range(100):add(0,a=rng.randrange(2),b=rng.getrandbits(32),c=rng.getrandbits(32),d=rng.randrange(2),data=rng.choice(texts)+b'\0')
 for width,decimal in itertools.product((0,0xffffffff,0x7fffffff),(0,0x1234002c,0xffffff2e)):add(0,width=width,decimal=decimal,data=b'1,23e4\0')
 for op,cw,fp in itertools.product((0,1,9,10,11),(0x37f,0x77f,0xb7f,0xf7f),(0,1,7)):
  data=b'12345.6789e-20\0' if op in (0,10,11) else struct.pack('<HQH',0xffff,0x8abcdef012345678,0x3fff) if op==1 else bytes([1,2,3,4,5])
  add(op,a=64 if op==1 else 5 if op==9 else 1,control=cw,prefix=fp,data=data)
 return rows

def mapped(image,module,va,n):
 rva=va-0x400000;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+max(s['raw_size'],s['vsize']))
 start=s['raw_offset']+rva-s['rva'];return image[start:start+n]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--probe',required=True,type=Path);parser.add_argument('--report-dir',required=True,type=Path);parser.add_argument('--limit',type=int);parser.add_argument('--no-stage-trace',action='store_true');parser.add_argument('--report-name',default='verification.json');args=parser.parse_args()
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');path=ROOT/'local/game'/module['path'];image=path.read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 probe_image=args.probe.read_bytes();pe_offset=struct.unpack_from('<I',probe_image,0x3c)[0]
 assert probe_image[pe_offset:pe_offset+4]==b'PE\0\0' and struct.unpack_from('<H',probe_image,pe_offset+4)[0]==0x14c and struct.unpack_from('<H',probe_image,pe_offset+24)[0]==0x10b
 rows=cases();rows=rows[:args.limit] if args.limit else rows
 inputs=''.join(str(i)+' '+str(row[0])+' '+' '.join(f'{x:x}' for x in row[1:-1])+' '+row[-1].hex()+'\n' for i,row in enumerate(rows))
 run=subprocess.run([str(args.probe.resolve()),str(path)],input=inputs,text=True,capture_output=True,timeout=120)
 args.report_dir.mkdir(parents=True,exist_ok=True)
 # Keep full trace evidence losslessly, with independent observer/production
 # artifacts. Deterministic gzip also avoids oversized GitHub blobs.
 trace_name=args.report_name.removesuffix('.json')+'-probe-output.jsonl.gz'
 (args.report_dir/trace_name).write_bytes(gzip.compress(run.stdout.encode('utf8'),mtime=0))
 assert run.returncode==0,(run.returncode,run.stderr,len(run.stdout.splitlines()))
 results=[json.loads(line) for line in run.stdout.splitlines()];assert len(results)==len(rows)
 uc=make_uc(image,module);coverage={};stage_events=0
 for i,item in enumerate(results):
  if item['recovered']!=item['original']:
   fields=[key for key in item['recovered'] if item['recovered'][key]!=item['original'][key]]
   raise AssertionError((i,rows[i],fields,{key:(item['recovered'][key],item['original'][key]) for key in fields if key!='memory'},'memory first difference',next((j//2 for j,(a,b) in enumerate(zip(item['recovered']['memory'],item['original']['memory'])) if a!=b),None)))
  emulated,stages=original(uc,rows[i],i,mapped(image,module,0x5e52da,512),coverage)
  assert emulated=={key:value for key,value in item['original'].items() if key!='fpu'},(i,'Unicorn original state')
  if not args.no_stage_trace:assert stages.hex()==item['stages'],(i,rows[i],'intermediate',stages.hex(),item['stages'])
  else:assert not item['stages']
  position=0
  while position<len(stages):position+=12+struct.unpack_from('<I',stages,position+8)[0];stage_events+=1
 entries={int(r['entry_va'],16):r for r in map(json.loads,(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
 def pin(va):
  f=entries[va];body=b''.join(mapped(image,module,int(a,16),int(b,16)-int(a,16)+1) for a,b in f['ranges']);assert len(body)==f['body_bytes'];return {'ranges':f['ranges'],'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest()}
 functions={f'{va:08x}':pin(va) for va in VAS};shared={f'{va:08x}':pin(va) for va in SHARED}
 prefix='iterations/v2/001-original-recovery/'
 compiled=[prefix+'source/recovered/'+name for name in ('formatter_float_parse_probe.cpp','Porsche.exe/formatter_float_parse.cpp','Porsche.exe/formatter_float_output.cpp','Porsche.exe/formatter_float_helpers.cpp','Porsche.exe/formatter_runtime.cpp','Porsche.exe/formatter_strings.cpp','Porsche.exe/formatter_crt_runtime.cpp','Porsche.exe/context_move.cpp')]
 paths=[prefix+'runs/170-formatter-float-parse/CMakeLists.txt',prefix+'runs/170-formatter-float-parse/README.md','scripts/research/verify-v2-formatter-float-parse.py','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/static/binaries.jsonl']
 tables={f'{va:08x}':{'bytes':n,'sha256':hashlib.sha256(mapped(image,module,va,n)).hexdigest()} for va,n in ((0x5acbb7,48),(0x5e6128,24),(0x5e6140,24),(0x5e52da,512),(0x5e6380,348),(0x5e64e0,348))}
 assert struct.unpack('<I',mapped(image,module,0x5e52d0,4))[0]==0x5e52da
 assert mapped(image,module,0x5e54dc,8)==struct.pack('<II',1,46)
 text=(ROOT/(prefix+'source/recovered/Porsche.exe/formatter_float_output_data.inc')).read_text()
 for va,name in ((0x5e6380,'positive'),(0x5e64e0,'negative')):
  array=re.search('formatter_float_powers_'+name+'_'+f'{va:08x}'+r'\[348\] = \{(.*?)\};',text,re.S).group(1)
  assert bytes(int(x,16) for x in re.findall(r'0x([0-9a-f]{2})',array))==mapped(image,module,va,348)
 text=(ROOT/(prefix+'source/recovered/Porsche.exe/formatter_float_helpers.cpp')).read_text()
 for va,width in ((0x5e6128,64),(0x5e6140,32)):
  array=re.search('formatter_float_pack'+str(width)+'_config_'+f'{va:08x}'+r'\[6\]\s*=\s*\{(.*?)\}',text,re.S).group(1)
  values=[int(x.rstrip('uU'),0)&0xffffffff for x in array.split(',')]
  assert struct.pack('<6I',*values)==mapped(image,module,va,24)
 reloc=next(s for s in module['sections'] if s['name']=='.reloc');data=image[reloc['raw_offset']:reloc['raw_offset']+reloc['raw_size']];position=0;sites=[]
 while position+8<=len(data):
  page,size=struct.unpack_from('<II',data,position)
  if not size:break
  assert size>=8 and position+size<=len(data)
  for offset in range(position+8,position+size,2):
   entry=struct.unpack_from('<H',data,offset)[0];assert entry>>12 in (0,3)
   if entry>>12==3:sites.append(0x400000+page+(entry&4095))
  position+=size
 result={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':list(functions),'full_function_vas':list(functions) if not args.limit else [],'partial_function_vas':[],'functions':functions,'shared_original_bodies':shared,'cases':len(rows),'native_cpp_equal_original_x86':True,'native_original_hardware_equal':True,'unrecovered_dependencies':[],'tables':tables,'source_sha256':source_hashes(paths,compiled_sources=compiled),'probe_sha256':hashlib.sha256(args.probe.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(inputs.encode()).hexdigest(),'output_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'case_results':[{'op':rows[i][0],'sha256':hashlib.sha256(json.dumps(item['recovered'],sort_keys=True).encode()).hexdigest()} for i,item in enumerate(results)],'original_execution':{'image_base':'30000000','relocation':'PE HIGHLOW relocation directory only','redirected_boundary':'005a2eae canonical character classification callback only','comparison':'8192 bytes poisoned arena, result, mutable globals, boundary trace, native x87 control/status/tag/80-byte registers','abi':'cdecl ESP, EBX/ESI/EDI and direction flag checked in native harness','unused_canonical_paths':'aborting link guards; never called'}}
 result.update(intermediate_stage_events=stage_events,private_stage_trace_enabled=not args.no_stage_trace,unicorn_returns_memory_equal=True,original_x86_coverage={f'{va:08x}':coverage.get(va,0) for va in VAS+SHARED})
 result['native_original_relocation']={'original_image_base':'00400000','private_image_base':'30000000','highlow_count':len(sites),'highlow_sites_le32_sha256':hashlib.sha256(b''.join(struct.pack('<I',s) for s in sites)).hexdigest(),'relative_branches_and_calls_unchanged':True,'iat_hook_count':0}
 result['limits']=['Readable input/output buffers and canonical32/64 packing configurations; other output widths tested for no-write behavior. Invalid pointers and nonterminating zero/count0 direct digit-normalization inputs excluded.',
 'Classification is an explicit canonical151 typed boundary, given unsigned byte inputs and mask4. Private callback returns table classification and tests caller reloads by mutating width/decimal/table on first invocation. The117-byte original boundary is separately pinned; no new implementation claimed here.',
 'Native x87 control/status/tag and80-byte register contents compare exactly, excluding implementation-dependent instruction/data addresses. Own10 bodies and their shared arithmetic use integer instructions; no FPU flags are masked.',
 'No live game or visual acceptance.']
 result['canonical_classification_boundary']=pin(0x5a2eae)
 result['private_build']={'compiler':'MSVC19.44','platform':'Win32','configuration':'Release','pe_machine':'014c','pe_optional_magic':'010b','production_trace_absent':args.no_stage_trace}
 assert all(result['original_x86_coverage'][f'{va:08x}'] for va in VAS+SHARED)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 (args.report_dir/args.report_name).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps({'ok':True,'functions':len(functions),'bytes':sum(f['body_bytes'] for f in functions.values()),'cases':len(rows),'stage_events':stage_events}))
if __name__=='__main__':main()
