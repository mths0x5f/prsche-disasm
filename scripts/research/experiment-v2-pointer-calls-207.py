"""Four bounded original-guided callable declarations over frozen203 sources.

No Ghidra, game/storage definitions, native execution or union build.
"""
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'207-pointer-call-consumers'
OUT=ROOT/'local/experiments/v2-pointer-call-consumers-207'
VAS=['00540480','005404e0','00554530','0058f1f0']
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


abi=module('abi207','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff207','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def index(path):
    parsed=[]
    for line in path.read_text(encoding='utf8').splitlines():
        m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        if m:parsed.append((int(m[1],16),dict(va=m[1],bytes=m[2],instruction=m[3])))
    return [r[0] for r in parsed],[r[1] for r in parsed]


def main():
    assert not (RUN/'summary.json').exists() and (not OUT.exists() or not any(OUT.iterdir())), 'fresh207 required'
    RUN.mkdir(parents=True,exist_ok=True);OUT.mkdir(exist_ok=True)
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();actual=digest(path)
        assert expected is None or actual==expected,('input drift',path)
        assert path not in pins or pins[path]==actual
        pins[path]=actual;return path
    def guard():
        for path,expected in pins.items():assert digest(path)==expected,('input mutation',path)
    for path in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN]:pin(path)
    prior_path=pin(RUNS/'203-consumer-declaration-pilot/summary.json')
    prior=load(prior_path);assert prior['original_sha256']==abi.SHA
    oldrows={r['va']:r for r in prior['results'] if r['va'] in VAS}
    assert set(oldrows)==set(VAS) and all(not r['compiled'] for r in oldrows.values())
    assert Counter(d['code'] for r in oldrows.values() for d in r['diagnostics'])=={'C2064':5,'C2197':1}
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'))
    assert not any(r['module']=='Porsche.exe' and r['entry_va'] in VAS for r in registry['functions'])
    declpath=pin(abi.DECL)
    inferred={r['entry_va']:r for r in map(json.loads,declpath.read_text().splitlines()) if r['entry_va'] in VAS}
    binaries_path=pin(ROOT/'research/binary-index/static/binaries.jsonl')
    binaries=[json.loads(line) for line in binaries_path.read_text().splitlines()]
    imports_path=pin(ROOT/'research/binary-index/static/imports.jsonl')
    assert any(r['path']=='Porsche.exe' and r['dll']=='DSOUND.dll' and r['symbol']=='ordinal:1' and r['iat_rva']=='0x1b2038'
               for r in map(json.loads,imports_path.read_text().splitlines()))
    records=[];original_instructions={};module_proofs=[]
    for name in ['Porsche.exe','opengl1z.dll','opengl3z.dll','voodoo2z.dll']:
        binary=next(r for r in binaries if r['file']==name)
        raw=pin(ROOT/'local/game'/binary['path'],binary['sha256']).read_bytes()
        corpus=ROOT/'research/v2/binaries'/(name+'-'+binary['sha256'][:12])
        catalog={r['entry_va']:r for r in map(json.loads,pin(corpus/'functions.jsonl').read_text().splitlines())}
        ix=index(pin(corpus/'disassembly.asm'))
        pe=struct.unpack_from('<I',raw,0x3c)[0]
        machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
        base=struct.unpack_from('<I',raw,pe+24+28)[0]
        sections=[struct.unpack_from('<IIII',raw,pe+24+optional+i*40+8)[1:] for i in range(count)]
        def exact(ins):
            rva=int(ins['va'],16)-base;length=len(ins['bytes'])//2
            start,size,offset=next(s for s in sections if s[0]<=rva and rva+length<=s[0]+s[1])
            assert raw[offset+rva-start:offset+rva-start+length].hex()==ins['bytes'],ins
        if name=='Porsche.exe':
            # Selected bodies, narrow loader/table/object-creation witnesses and fallback.
            for va in VAS+['00574f80']:
                ins=(abi.function_instructions(catalog[va],ix) if va in catalog else
                     [i for i in ix[1] if int(va,16)<=int(i['va'],16)<=int('00574f84',16)])
                if va=='00574f80':assert [i['bytes']for i in ins]==['33c0','c20400']
                for i in ins:exact(i)
                original_instructions[va]=ins
            windows=[('005751f4','00575220'),('005752cf','005752f4'),('005754aa','005754b8'),
                     ('00594dd7','00594e0d'),('00595002','0059502c'),('0058e65f','0058e66b'),('00597f70','00597f70')]
            for start,end in windows:
                ins=[i for i in ix[1] if int(start,16)<=int(i['va'],16)<=int(end,16)]
                for i in ins:exact(i)
                records.append(dict(module=name,module_sha256=binary['sha256'],window=[start,end],instructions=ins))
            # Exact byte strings supply the decorated names at GetProcAddress setup.
            string_witnesses=[]
            for va,value in [('005c0ba8','_THRASH_setstate@8'),('005c0b94','_THRASH_getstate@4')]:
                rva=int(va,16)-base;start,size,offset=next(s for s in sections if s[0]<=rva<s[0]+s[1])
                actual=raw[offset+rva-start:offset+rva-start+len(value)+1]
                assert actual==value.encode('ascii')+b'\0'
                string_witnesses.append(dict(va=va,value=value,bytes=actual.hex()))
            module_proofs.append(dict(module=name,sha256=binary['sha256'],strings=string_witnesses))
        else:
            exported=[r for r in catalog.values() if r['name'] in ('_THRASH_setstate@8','_THRASH_getstate@4')]
            assert len(exported)==2
            for entry in exported:
                export=next(e for e in binary['exports'] if e['name']==entry['name'])
                assert int(export['rva'],16)+base==int(entry['entry_va'],16) and not export['forwarder']
                ins=abi.function_instructions(entry,ix)
                for i in ins:exact(i)
                rets=[i for i in ins if i['instruction'].startswith('RET')]
                pop=8 if 'setstate' in entry['name'] else 4
                assert rets and all(i['instruction']==f'RET 0x{pop:x}' for i in rets)
                module_proofs.append(dict(module=name,sha256=binary['sha256'],entry=entry,export=export,
                                         original_instructions=ins,local_ret_sites=rets,stack_cleanup=pop,
                                         incoming_register_boundary='Stack parameters; exported stdcall wrappers overwrite ECX before semantic use; no incoming receiver register assigned by consumers'))
    # Exactly the original CALL setup and stack balance, independent of inferred models.
    assert [i['bytes'] for i in original_instructions['00540480']]==['8b442408','8b4c2404','50','51','ff157cd96b00','c3']
    assert [i['bytes'] for i in original_instructions['005404e0']]==['8b442408','8b4c2404','50','51','ff1518d96b00','c3']
    assert [i['bytes'] for i in original_instructions['00554530']]==['56','57','6a0a','ff1584d96b00','6a01','6a0a','8bf0','ff157cd96b00','56','6a0a','8bf8','ff157cd96b00','8bc7','5f','5e','c3']
    release=original_instructions['0058f1f0']
    assert [(i['va'],i['bytes']) for i in release[4:7]]==[('0058f1fe','8b08'),('0058f200','50'),('0058f201','ff5108')]
    sdk=Path('C:/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0')
    sdk_proof=[]
    for relative_name,patterns in [('um/dsound.h',['extern _Check_return_ HRESULT WINAPI DirectSoundCreate','DECLARE_INTERFACE_(IDirectSound, IUnknown)','STDMETHOD_(ULONG,Release)']),
                                   ('um/unknwnbase.h',['ULONG ( STDMETHODCALLTYPE *Release )','IUnknown * This']),
                                   ('shared/basetyps.h',['#define STDMETHODCALLTYPE       __stdcall'])]:
        path=pin(sdk/relative_name);text=path.read_text(encoding='utf-8-sig')
        for pattern in patterns:assert pattern in text,(path,pattern)
        sdk_proof.append(dict(path=relative(path),sha256=digest(path),contract_patterns=patterns))
    contracts=dict(setstate=dict(storage=['006bd97c','006bd918'],calling_convention='stdcall',arguments=['stack+4 raw32','stack+8 raw32'],return_bits='EAX32',callee_cleanup=8,
                                  provenance='GetProcAddress decorated exports, loader alias/table save-restore, actual3renderer export RET8,554530 EAX consumers'),
                   getstate=dict(storage='006bd984',calling_convention='stdcall',arguments=['stack+4 raw32'],return_bits='EAX32',callee_cleanup=4,
                                 provenance='GetProcAddress export+3renderer RET4; fallback574f80 returnsEAX0/RET4;554530 savesEAX'),
                   release=dict(object_storage='006ad760',vtable_byte_offset=8,calling_convention='stdcall',arguments=['stack+4 object pointer32'],return_bits='EAX ULONG32 (discarded here)',callee_cleanup=4,
                                provenance='DSOUND ordinal1 import/DirectSoundCreate output slot, physical PUSHself/CALL[vtable+8], SDKIUnknown third-slot Release'))
    proof=dict(schema=1,original_sha256=abi.SHA,scope=VAS,queries=['006bd97c/006bd918/006bd984 WRITErefs, THRASH export strings and exportedRET','006ad760 WRITErefs, DSOUNDordinal1 thunk, IUnknownVtblRelease'],
               contracts=contracts,selected_original_instructions=original_instructions,loader_windows=records,module_proofs=module_proofs,sdk_proof=sdk_proof,
               inferred179={va:{k:d[k] for k in ('inferred_signature','inferred_calling_convention','extra_pop','parameters','return_storage')}for va,d in inferred.items()},
               confirmed='Exact raw stack widths/cleanup/EAX consumers and callback binding; native header representation only',
               hypotheses='Semantic state/value types, provider behavior, complete caller/volatile-register equivalence and runtime object ownership remain unaccepted')
    write(RUN/'proof-before-compile.json',proof);pin(RUN/'proof-before-compile.json')
    sources=OUT/'sources';headers=OUT/'headers';objects=OUT/'objects';logs=OUT/'logs'
    for folder in (sources,headers,objects,logs):folder.mkdir()
    results=[]
    typedefs='typedef undefined4 (__stdcall *OriginalSetState207)(undefined4,undefined4);\ntypedef undefined4 (__stdcall *OriginalGetState207)(undefined4);\ntypedef undefined4 (__stdcall *OriginalRelease207)(int*);\nstatic_assert(sizeof(OriginalSetState207)==4 && sizeof(OriginalGetState207)==4 && sizeof(OriginalRelease207)==4,"original callback pointer32");\n'
    for va in VAS:
        old=oldrows[va];source=pin(ROOT/old['generated_source'],old['generated_source_sha256'])
        oldheader=pin(ROOT/old['declaration_header'],old['declaration_header_sha256'])
        for name,expected in old['dependency_sha256'].items():pin(ROOT/name,expected)
        text=source.read_text(encoding='utf8');header=oldheader.read_text(encoding='utf8')
        header=header.replace('/* Exact179 memory externs only; no storage/aliases/function prototypes. */','/* Original207 CALL/RET/export-backed callable views; no allocated storage. */')
        header=header.replace('static_assert(sizeof(void*)==4,"x86 required");','static_assert(sizeof(void*)==4 && sizeof(undefined4)==4 && sizeof(int*)==4,"original32-bit storage");\n'+typedefs)
        for symbol,typ in [('DAT_006bd97c','OriginalSetState207'),('DAT_006bd918','OriginalSetState207'),('DAT_006bd984','OriginalGetState207')]:
            header=header.replace('extern undefined *'+symbol+';','extern '+typ+' '+symbol+';')
        generated_header=headers/(va+'-callables.h');generated_header.write_text(header,encoding='utf8',newline='\n')
        needle='#include "'+oldheader.as_posix()+'"';assert text.count(needle)==1
        generated=text.replace(needle,'#include "'+generated_header.as_posix()+'"')
        body_edit=None
        if va=='0058f1f0':
            oldcall='(**(code **)(*DAT_006ad760 + 8))(DAT_006ad760);'
            newcall='(**(OriginalRelease207 *)(*DAT_006ad760 + 8))(DAT_006ad760);'
            assert generated.count(oldcall)==1;generated=generated.replace(oldcall,newcall)
            body_edit=dict(original=oldcall,replacement=newcall,call_va='0058f201',original_bytes='ff5108',proof='OriginalRelease207 raw32stdcall contract from physical caller and SDKthirdslot')
        cpp=sources/(va+'.cpp');cpp.write_text(generated,encoding='utf8',newline='\n')
        include_closure=set();pending=[cpp]
        while pending:
            path=pending.pop().resolve()
            if path in include_closure:continue
            include_closure.add(path);pin(path)
            for name in re.findall(r'^\s*#include\s+"([^"]+)"',path.read_text(encoding='utf8'),re.M):
                child=Path(name);pending.append(child.resolve() if child.is_absolute() else (path.parent/child).resolve())
        results.append(dict(va=va,name='FUN_'+va,generated_source=relative(cpp),generated_source_sha256=digest(cpp),
                            dependency_sha256={relative(p):pins[p] for p in sorted(include_closure)},forced_headers=[],
                            frozen203_source=relative(source),frozen203_source_sha256=digest(source),
                            frozen203_body_sha256=old['preserved_body_sha256'],body_unchanged=body_edit is None,body_edit=body_edit,
                            native_decl_header=relative(generated_header),native_decl_header_sha256=digest(generated_header),
                            original_ret_sites=[i for i in original_instructions[va] if i['instruction'].startswith('RET')]))
    guard()
    flags=prior['compiler_flags'];assert '/MP6' in flags and '/c' in flags and '/Od' in flags
    response=logs/'changed-4.rsp';response.write_text('\n'.join('"'+s+'"' for s in flags+['/Fo'+objects.as_posix()+'/']+[str(ROOT/r['generated_source'])for r in results])+'\n',encoding='utf-8-sig',newline='\n')
    command=[str(abi.COMPILER),'@'+str(response)]
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    started=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);elapsed=time.perf_counter()-started
    # Preserve observed exit and timing before any attribution/report work.
    write(logs/'execution.json',dict(command=command,exit_code=p.returncode,elapsed_seconds=elapsed,actual_compiler_batches=1))
    try:text=(p.stdout+p.stderr).decode('utf8')
    except UnicodeDecodeError:text=(p.stdout+p.stderr).decode('cp1251')
    log=logs/'changed-4.log';log.write_text(text.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n')
    assert p.returncode==0,log.read_text()
    assert not re.search(r'\b(?:error|warning) C\d+',log.read_text()),log.read_text()
    for row in results:
        obj=objects/(row['va']+'.obj');symbols=coff.coff_symbols(obj)
        assert any('FUN_'+row['va'] in name for name in symbols['defined'])
        dis=subprocess.run([str(abi.DUMPBIN),'/disasm',str(obj)],cwd=OUT,env=env,capture_output=True,timeout=60);assert dis.returncode==0
        dispath=logs/(row['va']+'-disassembly.txt')
        dispath.write_text((dis.stdout+dis.stderr).decode('utf8',errors='replace').replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n')
        asm=dispath.read_text();assert re.search(r'\bret\s*\n',asm) and not re.search(r'\bret\s+[0-9]',asm)
        row.update(compiler_exit_code=0,compiled=True,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,
                   object=relative(obj),object_sha256=digest(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],
                   disassembly=relative(dispath),disassembly_sha256=digest(dispath),native_ret_bytes=[0])
        pin(obj);pin(dispath)
    for path in (response,log,logs/'execution.json'):pin(path)
    guard()
    undefined={name:sorted(r['va']for r in results if name in r['undefined_external_symbols'])for name in sorted({n for r in results for n in r['undefined_external_symbols']})}
    report=dict(schema=1,kind='bounded-original-callable-contracts',module='Porsche.exe',original_sha256=abi.SHA,
                selected_scope_vas=VAS,objects_compiled=4,real_coff_objects=4,actual_compiler_batches=1,new_compilations=4,
                compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_batch_exit_code=p.returncode,compile_seconds=elapsed,
                compiler_response=relative(response),compiler_response_sha256=digest(response),compiler_log=relative(log),compiler_log_sha256=digest(log),
                execution_sidecar=relative(logs/'execution.json'),execution_sidecar_sha256=digest(logs/'execution.json'),
                input_sha256={relative(path):h for path,h in pins.items()},results=results,
                subset_undefined_names=len(undefined),subset_undefined_references=sum(map(len,undefined.values())),subset_undefined_symbols=undefined,
                input_guards_before=True,input_guards_after=True,Ghidra_decompilations=0,native_execution=False,production_or_union_changes=False,
                limits=['Raw callable stack/EAX contracts only; opaque state/value semantics remain unaccepted.',
                        '203 bodies retained except the exactSDK/original-proofed Release callable type; no guessed arity or convention.',
                        'Provider behavior, complete source ABI/volatile-register state, object lifetime, indirect-call initialization and original runtime fidelity remain open.'])
    write(RUN/'summary.json',report)
    print(json.dumps({k:report[k]for k in ('objects_compiled','compiler_batch_exit_code','compile_seconds','subset_undefined_names','subset_undefined_references')}))


if __name__=='__main__':main()
