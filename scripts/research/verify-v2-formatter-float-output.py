"""Run167: exact integer decimal engines plus native-original x87 entry proof."""
import argparse
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
BASE,MEM,ARENA,EXIT=0x400000,0x22000000,0x23000000,0x2200f000
VAS=(0x5a3f31,0x5a4054,0x5a4150,0x5abdcc,0x5adaae,0x5adacf,0x5adb2d,0x5adb5b,0x5adf5b,0x5ae17b,0x5adc4f,0x5abcf9,0x5a3f92,0x5a40a9,0x5a4234,0x5abd70)
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EFLAGS

def cases():
 out=[]
 def add(op,a=0,b=0,c=0,d=0,data=b'\0'*32,decimal=46,control=0x37f,prefix=0):out.append((op,a&0xffffffff,b&0xffffffff,c&0xffffffff,d&0xffffffff,decimal,control,prefix,data))
 bits=[0,0x8000000000000000,1,0x8000000000000001,0xfffffffffffff,0x10000000000000,0x7fefffffffffffff,0xffefffffffffffff,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000000,0xfff8000000000000,0x7ff0000000000001,0xfff0000000000001,0x7ff123456789abcd]
 bits.extend(struct.unpack('<Q',struct.pack('<d',v))[0] for v in (1.,-1.,.1,.5,1.25,2.5,9.999999999999998,999.99999,1e-4,1e-5,1e-20,1e20,1e100,1e-100,1e308,1e-308))
 for value,op,precision,caps in itertools.product(bits,range(3),(0,1,2,6,17,21,22,32,128,512),(0,1)):
  add(op,a=precision,b=caps,data=struct.pack('<Q',value))
 for value,op,control,prefix in itertools.product(bits[:15],range(3),(0x37f,0x77f,0xb7f,0xf7f),(0,3,7)):
  add(op,a=6,b=1,data=struct.pack('<Q',value),control=control,prefix=prefix,decimal=44)
 for value,op,status,prefix in itertools.product(bits[:15],range(3),(1,2,4,8,16,32,0x4500,0x473f),(0,7)):
  add(op,a=6,b=1,data=struct.pack('<Q',value),control=0x37f|(status<<16),prefix=prefix)
 for value in bits:add(3,data=struct.pack('<Q',value));add(15,data=struct.pack('<Q',value))
 for a,b in itertools.product((0,1,0x7fffffff,0x80000000,0xffffffff),repeat=2):add(4,a=a,b=b)
 rng=random.Random(167)
 for _ in range(180):
  left=bytes(rng.randrange(256) for _ in range(12));right=bytes(rng.randrange(256) for _ in range(12));data=left+bytes(4)+right
  for op in (5,6,7,8):add(op,data=data)
 for ea,eb,sign in itertools.product((0,1,0x1fdf,0x3ffe,0x3fff,0x4000,0x7ffe,0x7fff),(0,1,0x1fdf,0x3ffe,0x3fff,0x4000,0x7ffe,0x7fff),(0,0x8000)):
  add(8,data=struct.pack('<III',0,0,0x8000|((ea|sign)<<16))+bytes(4)+struct.pack('<III',0,0,0x8000|(eb<<16)))
 for power,keep in itertools.product((-5200,-4932,-4096,-4095,-512,-324,-308,-64,-8,-7,-1,0,1,7,8,64,308,324,512,4095,4096,4932,5200),(0,1)):
  add(9,a=power,b=keep,data=struct.pack('<III',0x12345678,0xabcdef01,0x3fff8000))
 for value,precision,flags in itertools.product(bits,(0,1,6,17,21),(0,1)):
  # Convert the input double layout into the exact original 80-bit helper input.
  raw=value>>52&0x7ff;lo=value&0xffffffff;hi=value>>32&0xfffff
  if not raw and not lo and not hi:extended=bytes(12)
  else:
   exponent=0x7fff if raw==0x7ff else raw+0x3c00 if raw else 0x3c01
   top=(lo>>21)|(hi<<11)|(0x80000000 if raw else 0);bottom=(lo<<11)&0xffffffff
   while not top&0x80000000:top=((top<<1)|(bottom>>31))&0xffffffff;bottom=(bottom<<1)&0xffffffff;exponent-=1
   extended=struct.pack('<III',bottom,top,exponent|((value>>48)&0x8000))
  add(10,a=precision,b=flags,data=extended)
 for text,exponent,count in itertools.product((b'0',b'1',b'4999',b'5000',b'99999999999999999',b'123450000',b'1#INF',b'1#QNAN'),(-324,-4,0,1,308),(-2,-1,0,1,2,6,17,21)):
  add(11,a=32,b=exponent,c=count,data=text+b'\0'+bytes(8))
 for text,sign,exponent,precision,general in itertools.product((b'1234567',b'0000000',b'9999999'),(32,45),(-4,0,1,3),(0,1,6),(0,1)):
  if exponent<=precision+1:
   add(12,a=sign,b=exponent,c=precision,d=(general<<8)|1,data=text+b'\0'+bytes(16))
   add(13,a=sign,b=exponent,c=precision,d=general,data=text+b'\0'+bytes(16))
 for text,count in itertools.product((b'',b'0',b'123456789',b'-12.34e+001'),(0,1,2,7,31)):add(14,a=count,data=text+b'\0'+bytes(32))
 return out

def mapped(image,module,va,n):
 rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+n<=s['rva']+max(s['raw_size'],s['vsize']))
 offset=s['raw_offset']+rva-s['rva'];return image[offset:offset+n]

def make_uc(image,module):
 uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000);uc.mem_map(MEM,0x10000);uc.mem_map(ARENA,0x10000)
 for s in module['sections']:
  if s['raw_size']:uc.mem_write(BASE+s['rva'],image[s['raw_offset']:s['raw_offset']+s['raw_size']])
 return uc

def original(uc,row,coverage):
 op,a,b,c,d,decimal,control,prefix,data=row
 put=lambda p,v:uc.mem_write(p,struct.pack('<I',v&0xffffffff))
 get=lambda p:struct.unpack('<I',uc.mem_read(p,4))[0]
 stages=hashlib.sha256();stage_events=0;frames=[]
 def emit(tag,phase,payload):
  nonlocal stage_events
  stages.update(struct.pack('<III',tag,phase,len(payload)));stages.update(payload);stage_events+=1
 def text(p):
  data=bytearray()
  while True:
   value=bytes(uc.mem_read(p+len(data),1));data.extend(value)
   if value==b'\0':return bytes(data)
 uc.mem_write(ARENA,b'\xa5'*4096);uc.mem_write(ARENA+16,data);put(0x5e54e0,decimal)
 if op<=2:args=[ARENA+16,ARENA+1024,a,b][:3 if op==1 else 4]
 elif op==3:args=[ARENA+1024,ARENA+16]
 elif op==4:args=[a,b,ARENA+1024]
 elif op in (5,8):args=[ARENA+16,ARENA+32]
 elif op in (6,7):args=[ARENA+16]
 elif op==9:args=[ARENA+16,a,b]
 elif op==10:args=[get(ARENA+16),get(ARENA+20),get(ARENA+24),a,b,ARENA+1024]
 elif op in (11,12,13):
  for offset,value in ((64,a),(68,b),(72,17),(76,ARENA+16)):put(ARENA+offset,value)
  if op==11:args=[ARENA+1024,c,ARENA+64]
  else:
   uc.mem_write(ARENA+1024,data)
   args=[ARENA+1024,c,d&255,ARENA+64,d>>8] if op==12 else [ARENA+1024,c,ARENA+64,d]
 elif op==14:uc.mem_write(ARENA+1024,data);args=[ARENA+1024,a]
 else:args=[get(ARENA+16),get(ARENA+20),ARENA+1024,ARENA+2048]
 def hook(m,address,_size,_data):
  esp=m.reg_read(UC_X86_REG_ESP)
  while frames and frames[-1][0]==address and frames[-1][1]+4==esp:
   _ret,_sp,tag,out,meta=frames.pop()
   if tag==4:emit(tag,1,bytes(m.mem_read(meta+4,4)));emit(tag,3,text(out))
   else:emit(tag,1,bytes(m.mem_read(out,10 if tag==1 else 12 if tag==2 else 5+m.mem_read(out+3,1)[0])))
  tags={0x5abdcc:1,0x5adf5b:2,0x5adc4f:3,0x5abcf9:4}
  if address in tags:
   tag=tags[address];arg=lambda i:get(esp+4+i*4);out=arg(5) if tag==3 else arg(0);meta=arg(2) if tag==4 else 0
   if tag==1:emit(tag,0,bytes(m.mem_read(arg(1),8)))
   elif tag==2:emit(tag,0,bytes(m.mem_read(arg(0),12))+bytes(m.mem_read(arg(1),12)))
   elif tag==3:emit(tag,0,struct.pack('<5I',arg(0),arg(1),arg(2)&0xffff,arg(3),arg(4)&255))
   else:emit(tag,0,struct.pack('<3I',arg(1),get(meta),get(meta+4)));emit(tag,2,text(get(meta+12)))
   frames.append((get(esp),esp,tag,out,meta))
  if address==EXIT:m.emu_stop()
  if address in coverage:coverage[address]+=1
 handle=uc.hook_add(UC_HOOK_CODE,hook)
 uc.mem_write(MEM+0x100,struct.pack('<H',control&0xffff));uc.mem_write(MEM+0x108,struct.pack('<d',7.25))
 setup=bytes.fromhex('dbe3')+bytes.fromhex('d9ee')*8+bytes.fromhex('dbe3d92d')+struct.pack('<I',MEM+0x100)
 setup+=(bytes.fromhex('dd05')+struct.pack('<I',MEM+0x108))*prefix
 setup+=b'\xe9'+struct.pack('<i',EXIT-(MEM+0x1000+len(setup)+5));uc.mem_write(MEM+0x1000,setup);uc.emu_start(MEM+0x1000,0,count=1000)
 if control>>16:
  code=bytes.fromhex('d935')+struct.pack('<I',MEM+0x300)+b'\xe9'+struct.pack('<i',EXIT-(MEM+0x3000+11));uc.mem_write(MEM+0x3000,code);uc.emu_start(MEM+0x3000,0,count=1000)
  put(MEM+0x304,get(MEM+0x304)|((control>>16)&0x473f))
  code=bytes.fromhex('d925')+struct.pack('<I',MEM+0x300)+b'\xe9'+struct.pack('<i',EXIT-(MEM+0x3000+11));uc.mem_write(MEM+0x3000,code);uc.emu_start(MEM+0x3000,0,count=1000)
 sp=MEM+0x8000;uc.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),EXIT,*args));uc.reg_write(UC_X86_REG_ESP,sp)
 for reg in (UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI):uc.reg_write(reg,0x12345678)
 uc.reg_write(UC_X86_REG_EFLAGS,2);uc.emu_start(VAS[op],0,count=2000000)
 assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==sp+4,(row,'abi')
 assert all(uc.reg_read(reg)==0x12345678 for reg in (UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI))
 assert not uc.reg_read(UC_X86_REG_EFLAGS)&0x400
 result=uc.reg_read(UC_X86_REG_EAX) if op in (0,1,2,4,10,12,13,15) else 0
 code=bytes.fromhex('dd35')+struct.pack('<I',MEM+0x200)+b'\xe9'+struct.pack('<i',EXIT-(MEM+0x2000+11));uc.mem_write(MEM+0x2000,code);uc.emu_start(MEM+0x2000,0,count=1000)
 fpu=bytes(uc.mem_read(MEM+0x200,108));uc.hook_del(handle)
 assert not frames,frames
 return {'return':result,'arena':bytes(uc.mem_read(ARENA,4096)).hex(),'fpu':(fpu[:2]+fpu[4:6]+fpu[8:10]+fpu[28:108]).hex(),'stage_sha256':stages.hexdigest(),'stage_events':stage_events}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--probe',required=True,type=Path);parser.add_argument('--report-dir',required=True,type=Path);parser.add_argument('--limit',type=int);parser.add_argument('--no-stage-trace',action='store_true');parser.add_argument('--report-name',default='verification.json');args=parser.parse_args()
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe');path=ROOT/'local/game'/module['path'];image=path.read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
 inputs=cases()[:args.limit];protocol='\n'.join(' '.join(map(str,row[:-1]))+' '+row[-1].hex() for row in inputs)+'\n'
 process=subprocess.run([str(args.probe.resolve()),str(path.resolve())],input=protocol,text=True,capture_output=True)
 assert process.returncode==0,(process.returncode,process.stderr,process.stdout[-1000:])
 native=[json.loads(row) for row in process.stdout.splitlines()];assert len(native)==len(inputs)
 coverage={va:0 for va in VAS};uc=make_uc(image,module);results=[];emulator_differences=[];emulator_memory_differences=[];stage_differences=[]
 for index,(case,row) in enumerate(zip(inputs,native)):
  recovered,hardware=row['recovered'],row['original'];assert recovered==hardware,(index,case,'nativeoriginal',{k:(recovered[k],hardware[k]) for k in hardware if recovered[k]!=hardware[k]})
  emulated=original(uc,case,coverage)
  if not args.no_stage_trace and (emulated['stage_sha256'],emulated['stage_events'])!=(row['stage_sha256'],row['stage_events']):
   bits=int.from_bytes(case[-1][:8],'little');assert case[0]<=2 and bits>>52&0x7ff==0x7ff and bits&0xfffffffffffff,(index,case,'intermediatestage')
   stage_differences.append({'case':index,'native_sha256':row['stage_sha256'],'original_unicorn_sha256':emulated['stage_sha256'],'native_events':row['stage_events'],'original_unicorn_events':emulated['stage_events'],'reason':'Unicorn FLD/FSTP NaN quieting/payload differs; retained unmasked.'})
  if (emulated['return'],emulated['arena'])!=(hardware['return'],hardware['arena']):
   bits=int.from_bytes(case[-1][:8],'little');assert case[0]<=2 and bits>>52&0x7ff==0x7ff and bits&0xfffffffffffff,(index,case,'unexpectedemulatedmemory')
   emulator_memory_differences.append({'case':index,'input':list(case[:-1])+[case[-1].hex()],'hardware':hardware,'unicorn':emulated,'reason':'Original FLD/FSTP NaN payload/quieting differs in Unicorn; native original is authoritative.'})
  if emulated['fpu']!=hardware['fpu']:emulator_differences.append({'case':index,'input':list(case[:-1])+[case[-1].hex()],'hardware_fpu':hardware['fpu'],'unicorn_fpu':emulated['fpu']})
  arena=bytes.fromhex(hardware['arena']);results.append({'input':list(case[:-1])+[case[-1].hex()],'return':hardware['return'],'arena_sha256':hashlib.sha256(arena).hexdigest(),'output_hex':arena[1024:].split(b'\0')[0].hex(),'fpu':hardware['fpu'],'stage_events':row['stage_events'],'stage_sha256':row['stage_sha256']})
 entries={int(r['entry_va'],16):r for r in map(json.loads,(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())};functions={}
 for va in VAS:
  f=entries[va];body=b''.join(mapped(image,module,int(a,16),int(b,16)-int(a,16)+1) for a,b in f['ranges']);assert len(body)==f['body_bytes'];functions[f'{va:08x}']={'ranges':f['ranges'],'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest()}
 prefix='iterations/v2/001-original-recovery/';compiled=[prefix+'source/recovered/Porsche.exe/'+name+'.cpp' for name in ('formatter_float_output','formatter_runtime','formatter_strings','formatter_crt_runtime','context_move')]
 paths=[prefix+'source/recovered/formatter_float_output_probe.cpp',prefix+'runs/167-formatter-float-output/CMakeLists.txt',prefix+'runs/167-formatter-float-output/README.md','scripts/research/verify-v2-formatter-float-output.py','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/static/binaries.jsonl']
 data_text=(ROOT/(prefix+'source/recovered/Porsche.exe/formatter_float_output_data.inc')).read_text();tables={}
 for va,name in ((0x5e6380,'positive'),(0x5e64e0,'negative')):
  array=re.search('formatter_float_powers_'+name+'_'+f'{va:08x}'+r'\[348\] = \{(.*?)\};',data_text,re.S).group(1);data=bytes(int(x,16) for x in re.findall(r'0x([0-9a-f]{2})',array));assert data==mapped(image,module,va,348);tables[f'{va:08x}']={'bytes':348,'sha256':hashlib.sha256(data).hexdigest()}
 assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
 report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,'function_vas':list(functions),'full_function_vas':list(functions) if not args.limit else [],'partial_function_vas':[],'functions':functions,'cases':len(results),'native_cpp_equal_original_x86':True,'native_original_hardware_equal':True,'unicorn_returns_memory_equal':not emulator_memory_differences,'case_results':results,'unicorn_x87_differences':emulator_differences,'unicorn_memory_differences':emulator_memory_differences,'original_x86_coverage':{f'{va:08x}':count for va,count in coverage.items()},'tables':tables,'source_sha256':source_hashes(paths,compiled_sources=compiled),'probe_sha256':hashlib.sha256(args.probe.read_bytes()).hexdigest(),'unrecovered_dependencies':[],
 'limits':['All conversion calls execute actual original code/data in a private mapping at30000000; probe is linked at10000000. Only original PE HIGHLOW relocation cells are rebased, as by a PE loader; no relative branch/call patching, import replacement or host decimal conversion.',
 'Native original/recovered compare exact4096-byte arenas, meaningful returns, cdecl stack/nonvolatile registers/DF and full x87 control/status/tag plus all eight80-bit register values. FPU instruction/data pointer addresses differ by implementation and are not semantic-state comparisons.',
 'Unicorn missing hardware x87 exception/stack details are recorded individually without suppressing flags; native-original hardware is authoritative for x87 effects.',
 'Positive/negative power tables are exact348-byte originals, including the4096 power used by the parser. Scale helper inputs have absolute exponent at most5200; public formatter precision0..512 and valid ample buffers. Unmasked x87 exceptions/invalid pointers are outside comparison domain.',
 'Unused canonical dependency functions have aborting private link guards; no guards occur in the conversion graph. Parse5ac716 and pack5abb07 are separate unrecovered engines in this packet.',
 'No live game or visual acceptance.']}
 report['intermediate_stage_events']=sum(r['stage_events'] for r in results);report['unicorn_intermediate_differences']=stage_differences
 report['private_stage_trace_enabled']=not args.no_stage_trace
 reloc=next(s for s in module['sections'] if s['name']=='.reloc');data=image[reloc['raw_offset']:reloc['raw_offset']+reloc['raw_size']];offset=0;sites=[]
 while offset+8<=len(data):
  page,size=struct.unpack_from('<II',data,offset)
  if not size:break
  assert size>=8 and offset+size<=len(data)
  for p in range(offset+8,offset+size,2):
   value=struct.unpack_from('<H',data,p)[0];assert value>>12 in (0,3)
   if value>>12==3:sites.append(BASE+page+(value&4095))
  offset+=size
 report['native_original_relocation']={'original_image_base':'00400000','private_image_base':'30000000','highlow_count':len(sites),'highlow_sites_le32_sha256':hashlib.sha256(b''.join(struct.pack('<I',s) for s in sites)).hexdigest(),'relative_branches_and_calls_unchanged':True,'iat_hook_count':0}
 if not args.limit:assert all(coverage.values()),coverage
 args.report_dir.mkdir(parents=True,exist_ok=True);(args.report_dir/args.report_name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps({'ok':True,'functions':len(functions),'bytes':sum(f['body_bytes'] for f in functions.values()),'cases':len(inputs),'unicorn_x87_differences':len(emulator_differences),'stage_events':report['intermediate_stage_events']}))
if __name__=='__main__':main()
