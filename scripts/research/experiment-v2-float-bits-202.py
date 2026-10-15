"""Original-guided raw32/float4 representation repair for one isolated TU.

Consumes existing202 Clang/HighIR/raw-pcode capture; never opens Ghidra.
"""
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/202-float-bit-stores'
OUT=ROOT/'local/experiments/v2-float-bits-202'
EXPORT=OUT/'export'
NATIVE=OUT/'native'
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


abi=module('abi202','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff202','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


HELPERS='''#pragma once
static_assert(sizeof(undefined4)==4 && sizeof(float)==4 && sizeof(void*)==4,"original32-bit storage");
// Character copies preserve representations, including NaNs, without alias UB.
// The temporary is complete before any destination write, including overlap.
static __forceinline undefined4 original_raw4_load(const void* source) {
 undefined4 temporary; unsigned char* d=reinterpret_cast<unsigned char*>(&temporary);
 const unsigned char* s=reinterpret_cast<const unsigned char*>(source);
 d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];return temporary;
}
static __forceinline void original_raw4_store(void* destination,undefined4 temporary) {
 unsigned char* d=reinterpret_cast<unsigned char*>(destination);
 const unsigned char* s=reinterpret_cast<const unsigned char*>(&temporary);
 d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];
}
static __forceinline float original_float4_view(const void* source) {
 undefined4 temporary=original_raw4_load(source);float value;
 unsigned char* d=reinterpret_cast<unsigned char*>(&value);
 const unsigned char* s=reinterpret_cast<const unsigned char*>(&temporary);
 d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];return value;
}
'''

FIXTURE='''extern "C" __declspec(dllimport) void __stdcall ExitProcess(unsigned int);
extern "C" int _fltused=0;
volatile unsigned int failed_cases=0,checked_cases=0;
__declspec(noinline) unsigned int reference_MOV_load(const void* source){
 unsigned int result;__asm{
  mov edx,source
  mov eax,[edx]
  mov result,eax
 }return result;
}
__declspec(noinline) void candidate_copy(void* destination,const void* source){
 unsigned int temporary=original_raw4_load(source);original_raw4_store(destination,temporary);
}
void check(bool ok){++checked_cases;if(!ok)++failed_cases;}
extern "C" void __cdecl entry(){
 const unsigned int patterns[16]={0,0x80000000u,0x3f800000u,0xbf800000u,1,0x007fffffu,0x00800000u,0x7f7fffffu,
  0xff7fffffu,0x7f800000u,0xff800000u,0x7fc12345u,0xffc12345u,0x7f800001u,0xff800001u,0x13579bdfu};
 for(unsigned int p=0;p<16;++p)for(unsigned int alignment=0;alignment<4;++alignment){
  alignas(4) unsigned char arena[64],expected[64];
  for(unsigned int i=0;i<64;++i)arena[i]=static_cast<unsigned char>(i*17+3);
  unsigned char* source=arena+24+alignment;original_raw4_store(source,patterns[p]);
  check(original_raw4_load(source)==reference_MOV_load(source)&&original_raw4_load(source)==patterns[p]);
  volatile float viewed=original_float4_view(source);
  check(original_raw4_load(const_cast<const float*>(&viewed))==patterns[p]);
  for(int overlap=-3;overlap<=3;++overlap){
   for(unsigned int i=0;i<64;++i)arena[i]=static_cast<unsigned char>(i*17+3);
   original_raw4_store(source,patterns[p]);for(unsigned int i=0;i<64;++i)expected[i]=arena[i];
   unsigned int snapshot=reference_MOV_load(source);unsigned char* destination=source+overlap;
   original_raw4_store(expected+24+alignment+overlap,snapshot);
   candidate_copy(destination,source);bool equal=true;
   for(unsigned int i=0;i<64;++i)if(arena[i]!=expected[i])equal=false;check(equal);
  }
  // Original4851e0 captures bits before4851e3 overwrites float4, including alias.
  for(int overlap=-3;overlap<=3;++overlap){
   for(unsigned int i=0;i<64;++i)arena[i]=static_cast<unsigned char>(i*17+3);
   original_raw4_store(source,patterns[p]);unsigned int captured=original_raw4_load(source);
   original_raw4_store(source+overlap,0x40600000u); // stand-in for the later FSTP result bytes
   original_raw4_store(arena+48,captured);check(original_raw4_load(arena+48)==patterns[p]);
  }
 }
 check(checked_cases==1024);ExitProcess(failed_cases?1:0);
}
'''


def main(finalize_existing=False):
    assert not (RUN/'summary.json').exists(), 'preserve completed202 snapshot'
    capture_metadata=None
    if finalize_existing:
        capture_metadata=load(NATIVE/'capture-incomplete.json')
        assert digest(ROOT/capture_metadata['capture_driver'])==capture_metadata['capture_driver_sha256']
        for name,expected in capture_metadata['files_sha256'].items():assert digest(ROOT/name)==expected,('captured artifact changed',name)
    else:
        assert not NATIVE.exists(), 'fresh native202 output required'
    RUN.mkdir(parents=True,exist_ok=True)
    NATIVE.mkdir(exist_ok=finalize_existing)
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();actual=digest(path)
        assert expected is None or actual==expected,('source drift',path)
        pins[path]=actual
        return path
    if finalize_existing:
        pin(NATIVE/'capture-incomplete.json')
        pin(ROOT/capture_metadata['capture_driver'],capture_metadata['capture_driver_sha256'])
    summary200=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/200-global-float-views/summary.json'))
    old=next(r for r in summary200['results'] if r['va']=='00485100')
    assert old['compiled'] and len(old['diagnostics'])==9 and all(d['code']=='C4244' for d in old['diagnostics'])
    source=pin(ROOT/old['original_generated_source'],old['original_generated_source_sha256'])
    alias_header=pin(ROOT/old['alias_header'],old['alias_header_sha256'])
    baseline_object=pin(ROOT/old['object'],old['object_sha256'])
    for name,expected in old['dependency_sha256'].items():pin(ROOT/name,expected)
    for path in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',
                 ROOT/'scripts/research/export-v2-float-bits-202.ps1',ROOT/'scripts/research/ghidra/ExportRawFloatStores202.java',
                 OUT/'capture-provenance.json',*EXPORT.iterdir(),abi.COMPILER,abi.DUMPBIN]:
        if path.is_file():pin(path)
    capture=load(EXPORT/'original-00485100.json')
    original=load(EXPORT/'original-instructions.json')
    provenance=load(OUT/'capture-provenance.json')
    assert provenance['original_project_unchanged'] and provenance['headless_exit_code']==0
    assert provenance['read_only'] and not provenance['autoanalysis']
    for record in provenance['files']:pin(ROOT/record['path'],record['sha256'])
    assert capture['complete'] and not capture['calls']
    raw_path=pin(ROOT/'local/game/Porsche.exe',abi.SHA)
    raw=raw_path.read_bytes();pe=struct.unpack_from('<I',raw,0x3c)[0]
    machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4)
    assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0]
    sections=[struct.unpack_from('<IIII',raw,pe+24+optional+i*40+8)[1:] for i in range(count)]
    for ins in original:
        rva=int(ins['va'],16)-base;length=len(ins['bytes'])//2
        start,size,offset=next(s for s in sections if s[0]<=rva and rva+length<=s[0]+s[1])
        assert raw[offset+rva-start:offset+rva-start+length].hex()==ins['bytes'],ins
    instructions={i['va']:i for i in original}
    stores={p['instruction_va']:p for p in capture['pcode'] if p['opcode']=='STORE'}
    text=source.read_text(encoding='utf8');before=text
    edits=[]
    store_specs=[('0048511f',4,1),('00485125',5,2),('0048512b',6,3),('0048513f',8,5),
                 ('00485145',9,6),('0048514b',10,7),('004851d7',4,5),('004851dd',5,6)]
    def replace(old_text,new_text,kind,pcs,witness):
        nonlocal text
        assert text.count(old_text)==1,(old_text,text.count(old_text))
        text=text.replace(old_text,new_text)
        edits.append(dict(kind=kind,original=old_text,replacement=new_text,pcs=pcs,witness=witness))
    for pc,dst,src in store_specs:
        instruction=instructions[pc];high=stores[pc]
        assert instruction['assembly'].startswith('MOV ') and high['inputs'][2]['bytes']==4
        assert high['inputs'][2]['high_type']=='/float'
        tokens=[t for t in capture['tokens'] if t.get('min_va')==pc]
        assert any(t['text']=='param_1' for t in tokens)
        replace(f'param_1[{dst}] = param_2[{src}];',f'param_1[{dst}] = original_raw4_load(&param_2[{src}]);',
                'raw_MOV4_store',[pc],dict(instruction=instruction,high_store=high,tokens=tokens))
    # Capture before the intervening FSTP: do not reload a potentially aliased src.
    assert instructions['004851e0']['bytes']=='8b470c' and instructions['004851e3']['bytes']=='d91e'
    final=stores['004851e5'];assert final['inputs'][2]['bytes']==4 and final['inputs'][2]['high_name']=='fVar3'
    producer_tokens=[t for t in capture['tokens'] if t.get('min_va')=='004851e0']
    assert any(t['text']=='fVar3' for t in producer_tokens)
    replace('fVar3 = param_2[7];','undefined4 raw_004851e0 = original_raw4_load(&param_2[7]);','raw_MOV4_capture_before_FSTP',
            ['004851e0'],dict(instruction=instructions['004851e0'],tokens=producer_tokens,intervening_FSTP=instructions['004851e3']))
    replace('param_1[6] = fVar3;','param_1[6] = raw_004851e0;','raw_MOV4_store_after_FSTP',['004851e5'],
            dict(instruction=instructions['004851e5'],high_store=final,tokens=[t for t in capture['tokens'] if t.get('min_va')=='004851e5']))
    # Eight CAST occurrences in six statement lines are bit views in high IR.
    read_pcs=['00485173','00485170','00485182','0048517d','00485185','00485188','0048519b','00485196']
    matches=list(re.finditer(r'\(float\)param_1\[(5|9)\]',text))
    assert len(matches)==len(read_pcs)==8
    read_edits=[]
    for match,pc in zip(matches,read_pcs):
        casts=[p for p in capture['pcode'] if p['opcode']=='CAST' and p['output'].get('high_type')=='/float'
               and p['inputs'][0].get('defined_at','').startswith('(ram, 0x'+pc.lstrip('0')+',')]
        assert len(casts)==1 and casts[0]['inputs'][0]['bytes']==casts[0]['output']['bytes']==4
        assert casts[0]['inputs'][0]['high_type']=='/undefined4'
        ts=[t for t in capture['tokens'] if t.get('min_va')==pc and t['text']=='param_1']
        assert len(ts)==1
        read_edits.append(dict(kind='raw32_to_float4_view',original=match[0],replacement=f'original_float4_view(&param_1[{match[1]}])',
                               pcs=[pc],witness=dict(instruction=instructions[pc],high_CAST=casts[0],tokens=ts)))
    # Apply from the end so occurrence mapping remains exact, then keep all witnesses.
    for match,edit in reversed(list(zip(matches,read_edits))):text=text[:match.start()]+edit['replacement']+text[match.end():]
    edits+=read_edits
    # Independent line-level whitelist: branch/arithmetic lines differ only in the eight views.
    old_lines=before.splitlines();new_lines=text.splitlines();assert len(old_lines)==len(new_lines)
    allowed_old={e['original'] for e in edits if e['kind']!='raw32_to_float4_view'}
    for a,b in zip(old_lines,new_lines):
        if a!=b:
            assert a.strip() in allowed_old or re.search(r'\(float\)param_1\[(5|9)\]',a),(a,b)
            assert re.sub(r'\(float\)param_1\[(5|9)\]',r'VIEW(\1)',a)==re.sub(r'original_float4_view\(&param_1\[(5|9)\]\)',r'VIEW(\1)',b) or a.strip() in allowed_old
    header=NATIVE/'original-raw4-202.h';header.write_text(HELPERS,encoding='utf8',newline='\n')
    insertion='#include "'+header.as_posix()+'"\n'
    text=text.replace('#line 1 "porsche_method_00485100"',insertion+'#line 1 "porsche_method_00485100"')
    cpp=NATIVE/'00485100.cpp';cpp.write_text('#include "'+alias_header.as_posix()+'"\n'+text,encoding='utf8',newline='\n')
    primitive=pin(ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h')
    fixture=NATIVE/'bitcopy-fixture.cpp'
    fixture.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+FIXTURE,encoding='utf8',newline='\n')
    for path in (header,cpp,fixture):pin(path)
    write(RUN/'proof-before-compile.json',dict(schema=1,original_sha256=abi.SHA,original_instruction_count=len(original),
                                             stores=9,read_view_occurrences=8,read_statement_lines=6,edits=edits,
                                             original_signature=capture['inferred']['signature'],all_other_body_lines_preserved=True))
    pin(RUN/'proof-before-compile.json')
    for path,expected in pins.items():assert digest(path)==expected,('input changed before compile',path)
    objects=NATIVE/'objects';objects.mkdir(exist_ok=finalize_existing)
    flags=summary200['compiler_flags'];assert '/MP6' in flags and '/O2' in flags
    command=[str(abi.COMPILER),*flags,'/Fo'+str(objects)+os.sep,str(cpp),str(fixture)]
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        if finalize_existing:
            path=NATIVE/name
            assert digest(path)==capture_metadata['files_sha256'][relative(path)]
            return SimpleNamespace(returncode=capture_metadata['execution_log_exit_codes'][name]),path
        p=subprocess.run(list(map(str,command)),cwd=NATIVE,env=env,capture_output=True,timeout=120)
        try:log=(p.stdout+p.stderr).decode('utf8')
        except UnicodeDecodeError:log=(p.stdout+p.stderr).decode('cp1251')
        path=NATIVE/name;path.write_text(log.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n')
        return p,path
    compiled,log=run(command,'compile.log');assert compiled.returncode==0,log.read_text()
    assert 'C4244' not in log.read_text() and not re.search(r'\b(?:warning|error) C\d+',log.read_text()),log.read_text()
    obj=objects/'00485100.obj';symbols=coff.coff_symbols(obj)
    assert '__ftol3' not in symbols['undefined']
    assert symbols['defined']==['?invoke@Thiscall_00485100@@QAEPAIPAMG@Z']
    native,disasm=run([abi.DUMPBIN,'/disasm',obj],'corrected-disassembly.txt');assert native.returncode==0
    baseline,bdisasm=run([abi.DUMPBIN,'/disasm',baseline_object],'baseline-disassembly.txt');assert baseline.returncode==0
    baseline_text=bdisasm.read_text();native_text=disasm.read_text()
    assert len(re.findall(r'call\s+__ftol3',baseline_text))==9
    assert len(re.findall(r'\bcvtdq2pd\b',baseline_text))==2
    assert not re.search(r'__ftol3|\b(?:cvtdq2pd|cvtpd2ps|cvtsi2ss|cvtsi2sd|cvttss2si|fild|fistp)\b',native_text,re.I)
    assert re.findall(r'\bret\s+([0-9A-Fa-f]+)',native_text)==['8']
    assert instructions['004851f8']['bytes']=='8bc1' and instructions['004851fe']['bytes']=='c20800'
    executable=NATIVE/'bitcopy-fixture.exe';link=abi.COMPILER.with_name('link.exe')
    kernel=ROOT/'local/tools/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'
    if not kernel.exists():kernel=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')
    pin(link);pin(kernel)
    linked,linklog=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(executable),objects/'bitcopy-fixture.obj',kernel],'fixture-link.log')
    assert linked.returncode==0,linklog.read_text()
    fixture_run,fixture_log=run([executable],'fixture-native.log');assert fixture_run.returncode==0,('fixture failed',fixture_run.returncode)
    fixture_dis,fixture_disasm=run([abi.DUMPBIN,'/disasm',objects/'bitcopy-fixture.obj'],'fixture-disassembly.txt');assert fixture_dis.returncode==0
    for path,expected in pins.items():assert digest(path)==expected,('input changed after native',path)
    include_closure=set();pending=[cpp]
    while pending:
        path=pending.pop().resolve()
        if path in include_closure:continue
        include_closure.add(path);assert path in pins
        for name in re.findall(r'^\s*#include\s+"([^"]+)"',path.read_text(encoding='utf8'),re.M):
            child=Path(name);pending.append(child.resolve() if child.is_absolute() else (path.parent/child).resolve())
    row=dict(va='00485100',compiled=True,compiler_exit_code=0,generated_source=relative(cpp),generated_source_sha256=digest(cpp),
             object=relative(obj),object_sha256=digest(obj),defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],
             dependency_sha256={relative(p):pins[p] for p in sorted(include_closure)},forced_headers=[],
             original_source=relative(source),original_source_sha256=digest(source),original_header=relative(alias_header),original_header_sha256=digest(alias_header),
             native_ret_bytes=[8],native_text_sections=abi.text_sections(obj))
    for path in [obj,objects/'bitcopy-fixture.obj',executable,log,disasm,bdisasm,linklog,fixture_log,fixture_disasm]:pin(path)
    report=dict(schema=1,original_sha256=abi.SHA,compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,
                actual_compiler_batches=1,changed_game_TUs=1,synthetic_fixture_TUs=1,real_coff_objects=1,results=[row],
                metadata_finalize_existing=finalize_existing,compiler_commands_this_pass=0 if finalize_existing else 1,
                native_execution_commands_this_pass=0 if finalize_existing else 1,capture_metadata=capture_metadata,
                numeric_float_to_uint_calls_before=9,numeric_float_to_uint_calls_after=0,numeric_uint_to_float_sequences_before=2,numeric_uint_to_float_sequences_after=0,
                original_instructions_checked=len(original),raw_MOV_store_repairs=9,raw_read_view_occurrences=8,all_other_body_lines_preserved=True,
                fixture=dict(exit_code=0,representation_cases=1024,final_count_check=1,patterns=16,alignments=4,overlap_deltas=list(range(-3,4)),
                             includes_signed_zero=True,includes_NaN_payloads=True,capture_before_overwrite_alias=True,executable=relative(executable),sha256=digest(executable)),
                compiler_command=command,compiler_exit_code=0,compiler_log=relative(log),compiler_log_sha256=digest(log),
                input_sha256={relative(p):h for p,h in pins.items()},input_guards_before=True,input_guards_after=True,original_project_unchanged=True,
                supersedes_unsafe_run200_object=True,original_200_object_unchanged=digest(baseline_object)==old['object_sha256'],
                boundary=['Known representation-conversion defects repaired only; no branch/arithmetic rewrite.',
                          'Bitcopy fixture verifies representations/overlap, not original complete function behavior.',
                          'Original x87 versus native SSE arithmetic, exceptions, NaN branch behavior and full-body fidelity remain open.',
                          'No production/registry/game/union change; unsafe200 object remains excluded.'])
    write(RUN/'summary.json',report)
    print(json.dumps({k:report[k] for k in ('real_coff_objects','raw_MOV_store_repairs','raw_read_view_occurrences','numeric_float_to_uint_calls_after','numeric_uint_to_float_sequences_after')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finalize-existing',action='store_true')
    main(parser.parse_args().finalize_existing)
