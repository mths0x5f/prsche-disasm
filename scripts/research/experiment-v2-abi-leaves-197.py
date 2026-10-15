"""Two original CALL-free RET mismatches: raw storage correction and native COFF.

Preparation pins original bytes/contracts before copied-project mutation.
Compilation consumes only the bounded197 reinference, never repairs printed calls.
"""
import argparse
from collections import Counter
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/197-call-free-abi'
OUT=ROOT/'local/experiments/v2-abi-analysis-197'
CORPUS=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d'
VAS=['0043f8a0','004930f0']
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


abi=module('abi186','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff197','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def prepare():
    RUN.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    report_path=RUN/'contracts-before-analysis.json'
    assert not report_path.exists(), 'preserve the pre-analysis contract snapshot'
    original=ROOT/'local/game/Porsche.exe'
    raw=original.read_bytes()
    assert digest(original)==abi.SHA
    pe=struct.unpack_from('<I',raw,0x3c)[0]
    machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4)
    assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0]
    sections=[struct.unpack_from('<IIII',raw,pe+24+optional+i*40+8)[1:] for i in range(count)]

    def exact(ins):
        va=int(ins['va'],16)-base
        size=len(ins['bytes'])//2
        section=next((s for s in sections if s[0]<=va and va+size<=s[0]+s[1]),None)
        assert section is not None, ('not backed by original bytes',ins)
        rva,length,offset=section
        assert raw[offset+va-rva:offset+va-rva+size].hex()==ins['bytes'],ins

    catalog={r['entry_va']:r for r in abi.rows(CORPUS/'functions.jsonl')}
    inferred={r['entry_va']:r for r in abi.rows(abi.DECL)}
    registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')
    owners={r['entry_va'] for r in registry['functions'] if r['module']=='Porsche.exe'}
    assert not owners.intersection(VAS)
    index=abi.instruction_index()
    by_address={i['va']:i for i in index[1]}
    census=load(abi.RUN/'summary.json')['original_contract_census']['rows']
    ranking=[]
    for contract in census:
        if contract['ret_agrees']:
            continue
        va=contract['va']
        ins=abi.function_instructions(catalog[va],index)
        calls=[i for i in ins if i['instruction'].startswith('CALL')]
        rets=[i for i in ins if i['instruction'].startswith('RET')]
        reason=('bounded_selected' if va in VAS else
                'already_run193' if va in ('00482f70','00489530') else
                'RET0_requires_independent_nonthiscall_contract' if va in ('0040fff0','005a2eae','005aa907') else
                'no_local_RET_external_tail_JMP' if not rets else
                'contains_CALL_requires_callee_and_hidden_register_tracing')
        ranking.append(dict(va=va,body_bytes=catalog[va]['body_bytes'],call_count=len(calls),
                            inferred_stack_bytes=contract['expected_stack_bytes'],ret_bytes=contract['original_ret_bytes'],reason=reason))
    ranking.sort(key=lambda r:(r['call_count']!=0,r['body_bytes'],r['va']))
    assert sum(r['reason']=='bounded_selected' for r in ranking)==2
    contracts=[]
    for va in VAS:
        ins=abi.function_instructions(catalog[va],index)
        for i in ins:
            exact(i)
            text=i['instruction']
            assert not text.startswith('CALL'),i
            if text.startswith('J'):
                target=int(re.search(r'0x([0-9a-f]+)',text)[1],16)
                assert any(int(a,16)<=target<=int(b,16) for a,b in catalog[va]['ranges']), ('external branch',i)
        assert ins[0]['instruction']=='MOV EDX,dword ptr [ECX]'
        rets=[i for i in ins if i['instruction'].startswith('RET')]
        assert rets and all(i['bytes']=='c20800' for i in rets)
        # The complete instruction sequence has only these stack-argument reads.
        stackreads=[i for i in ins if re.search(r'\[ESP \+ ',i['instruction'])]
        if va=='004930f0':
            assert [i['bytes'] for i in ins]==['8b11','8b02','8901','8b442404','8910','c20800']
            assert [i['va'] for i in stackreads]==['004930f6']
            return_sites=[dict(ret_va='004930fc',eax_defined_at='004930f6',entry_stack_offset=4,save_depth_at_read=0)]
        else:
            assert [i['va'] for i in stackreads]==['0043f8c1','0043f8ec']
            assert all(i['bytes']=='8b442408' for i in stackreads)
            assert by_address['0043f8c5']['bytes']==by_address['0043f8f0']['bytes']=='5e'
            assert by_address['0043f8c6']['bytes']==by_address['0043f8f1']['bytes']=='8910'
            return_sites=[dict(ret_va='0043f8c8',eax_defined_at='0043f8c1',entry_stack_offset=4,save_depth_at_read=4),
                          dict(ret_va='0043f8f3',eax_defined_at='0043f8ec',entry_stack_offset=4,save_depth_at_read=4)]
        body=b''.join(bytes.fromhex(i['bytes']) for i in ins)
        assert len(body)==catalog[va]['body_bytes']
        contracts.append(dict(va=va,original_catalog=catalog[va],before_inference={k:inferred[va][k] for k in ('inferred_signature','parameters','return_storage','extra_pop')},
                              original_instructions=ins,original_body_hex=body.hex(),original_body_sha256=hashlib.sha256(body).hexdigest(),
                              ecx_first_use=ins[0],stack_reads=stackreads,ret_sites=rets,eax_return_producers=return_sites,
                              proposed_input_storage=['ECX:4','Stack[0x4]:4','Stack[0x8]:4'],proposed_return_storage='EAX:4',
                              stack8_semantics='Not read locally; original RET8 consumes this full32 slot. Explicit unused raw32 parameter retained.',
                              type_boundary='Raw32 bit contracts only. Dereference widths are original32; no source class/lifetime or semantic type assumed.',
                              register_boundary='No incoming EDX data use; EDX defined from [ECX] first. Nonvolatile ESI/EDI are saved/restored. Incidental outgoing volatile registers are not accepted as semantic outputs.'))
    consumer_ranges=[('0043f8a0','0043f876','0043f86b','0043f884'),
                     ('004930f0','00490a87','00490a7c','00490aa8'),
                     ('004930f0','004914cd','004914c2','004914dc'),
                     ('004930f0','00491964','0049195a','00491985')]
    consumers=[]
    for callee,callva,start,end in consumer_ranges:
        ins=[i for i in index[1] if int(start,16)<=int(i['va'],16)<=int(end,16)]
        for i in ins:
            exact(i)
        call=by_address[callva]
        assert call['instruction']=='CALL 0x'+callee
        consumer=dict(callee_va=callee,call_va=callva,instructions=ins,
                      stack8_producer='PUSH EBX at0049195e (raw value, not assumed zero)' if callva=='00491964' else 'PUSH 0x0',
                      stack4_producer='PUSH caller LEA temporary output-address',
                      receiver_producer='Caller LEA temporary iterator/address cell into ECX',
                      verification='Original local CALL setup/return consumer bytes only; complete caller high-IR/native lowering remains open')
        if callva=='0043f876':
            assert by_address['0043f87b']['bytes']=='8b00'
            consumer['return_use']='0043f87b MOV EAX,[EAX] consumes returned output-address; PUSH ECX at87d is allocation overwritten fully at880 before its contents can be read'
        elif callva=='004914cd':
            assert by_address['004914d2']['bytes']=='8b00'
            consumer['return_use']='004914d2 MOV EAX,[EAX] consumes returned output-address; EDX overwritten at4914d9'
        else:
            consumer['return_use']='EAX overwritten after CALL; incidental volatile-output compatibility not accepted'
        consumers.append(consumer)
    calls=abi.rows(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl')
    assert {c['from_va'] for c in calls if c['to_function'] in VAS}=={c['call_va'] for c in consumers}
    # Freeze a new bounded exporter from the193 mechanism, never editing193.
    template=ROOT/'scripts/research/ghidra/ExperimentAbiAnalysis193.java'
    java=template.read_text(encoding='utf8').replace('ExperimentAbiAnalysis193','ExperimentAbiLeaves197').replace('193','197')
    java=java.replace('"00482f70","00483290","00489370","00489530"','"0043f8a0","004930f0"')
    java=java.replace('correct("00489530",2,false);correct("00482f70",3,true);','correct("0043f8a0",2,true);correct("004930f0",2,true);')
    java=java.replace('List.of("00489530","00482f70")','List.of("0043f8a0","004930f0")').replace('after-callees','after-storage').replace('all four baseline snapshots','both baseline snapshots')
    exporter=ROOT/'scripts/research/ghidra/ExperimentAbiLeaves197.java'
    exporter.write_text(java,encoding='utf8',newline='\n')
    inputs=[Path(__file__),template,exporter,ROOT/'scripts/research/experiment-v2-abi-leaves-197.ps1',
            ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',
            abi.RUN/'summary.json',abi.DECL,CORPUS/'functions.jsonl',CORPUS/'disassembly.asm',
            ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',original,
            ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json']
    write(report_path,dict(schema=1,original_sha256=abi.SHA,stage='before copied-project analysis mutation',
                          ret_mismatches=42,no_ret_body=1,ranked_queue=ranking,selected=contracts,original_call_consumers=consumers,
                          input_sha256={relative(p):digest(p) for p in inputs},
                          excluded_RET0=['0040fff0','005a2eae','005aa907'],excluded_tail='005a1496'))
    print(json.dumps(dict(prepared=True,selected=VAS,original_instructions=sum(len(c['original_instructions']) for c in contracts),call_sites=len(consumers))))


def compile_capture(attempt):
    contract_path=RUN/'contracts-before-analysis.json'
    contracts=load(contract_path)
    pins={ROOT/n:h for n,h in contracts['input_sha256'].items()}
    current_driver=Path(__file__).resolve()
    prepared_driver_sha=pins[current_driver]
    preserved_driver=OUT/'pre-capture-driver.py'
    if digest(current_driver)!=prepared_driver_sha:
        assert digest(preserved_driver)==prepared_driver_sha, 'preserve the exact pre-capture driver'
        del pins[current_driver]
        pins[preserved_driver]=prepared_driver_sha
        pins[current_driver]=digest(current_driver)
    pins[contract_path]=digest(contract_path)
    export=RUN/f'export/attempt-{attempt:03d}'
    provenance=load(export/'provenance.json')
    result=load(export/'result.json')
    assert provenance['original_project_unchanged'] and provenance['headless_exit_code']==0
    assert provenance['original_project_before']==provenance['original_project_after']
    assert '-readOnly' in provenance['command'] and '-noanalysis' in provenance['command']
    assert result['modified_functions']==VAS
    for record in provenance['files']:
        path=ROOT/record['path']
        assert digest(path)==record['sha256'],path
        pins[path]=record['sha256']
    for path in export.iterdir():
        if path.is_file():
            assert b'\r' not in path.read_bytes(), ('capture must use LF before hashing',path)
            pins[path]=digest(path)
    primitive=ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h'
    pins[primitive]=digest(primitive)
    for path in (abi.COMPILER,abi.DUMPBIN):
        pins[path]=digest(path)
    output=OUT/f'native-{attempt:03d}'
    assert not (RUN/'summary.json').exists(), 'preserve completed197 summary'
    first_batch_path=output/'first-batch.json'
    first_batch=load(first_batch_path) if first_batch_path.exists() else None
    assert not output.exists() or not any(output.iterdir()) or first_batch, 'fresh output or pinned failed batch required'
    output.mkdir(exist_ok=True)
    if first_batch:
        assert first_batch['compiler_exit_code']==1 and first_batch['actual_MP6_batches']==1
        for name in ('driver','log','failed_source'):
            path=ROOT/first_batch[name]
            assert digest(path)==first_batch[name+'_sha256']
            pins[path]=digest(path)
        pins[first_batch_path]=digest(first_batch_path)
    sources,results=[],[]
    for evidence in contracts['selected']:
        va=evidence['va']
        before=load(export/f'before-{va}.json')
        after=load(export/f'after-storage-{va}.json')
        database=after['database']
        assert database['custom_storage'] and database['stack_purge_bytes']==8
        assert database['return_type']=='/undefined4' and database['return_storage']['display']=='EAX:4'
        p=after['inferred']['parameters']
        assert len(p)==3
        expected=[('register',4),('stack',4),('stack',8)]
        for actual,raw_db,(space,offset) in zip(p,database['parameters'],expected):
            nodes=actual['storage']['varnodes']
            assert len(nodes)==1 and nodes[0]['space']==space and nodes[0]['offset']==offset and nodes[0]['bytes']==4
            assert raw_db['bytes']==actual['bytes']==4 and raw_db['type']=='/undefined4'
            assert raw_db['storage']['varnodes']==nodes
        # Undefined4 is deliberately raw database storage. Ghidra may refine its
        # printed view to pointer32. Original MOV dereferences establish width,
        # not signed pointee semantics or a recovered source class.
        view='/int *' if va=='0043f8a0' else '/undefined4 *'
        assert [actual['type'] for actual in p]==[view,view,'/undefined4']
        returned=after['inferred']['return_storage']['varnodes']
        assert returned==[dict(space='register',offset=0,bytes=4,address='register:00000000')]
        assert after['inferred']['return_type']==view and after['inferred']['extra_pop']==12
        assert not after['calls']
        # Adapt raw storage metadata to186's checked native method lowering.
        # The ECX role is established by original first-use, not a printed arg guess.
        params=[]
        for i,actual in enumerate(p):
            nodes=actual['storage']['varnodes']
            params.append(dict(name=actual['name'],this=i==0,hidden_return=False,type=dict(length=4),storage=actual['storage']['display'],
                               storage_detail=dict(serialization='register:00000004:4' if i==0 else f'Stack[0x{i*4:x}]:4',
                                                   stack=i!=0,compound=False,varnodes=nodes)))
        decl=dict(entry_va=va,name='FUN_'+va,parameters=params,varargs=False,return_storage='EAX:4',return_type=dict(length=4))
        text=(export/f'after-storage-{va}.c').read_text(encoding='utf8')
        store_lowering=None
        if va=='004930f0':
            witness=next(i for i in evidence['original_instructions'] if i['va']=='004930fa')
            assert witness['bytes']=='8910' and witness['instruction']=='MOV dword ptr [EAX],EDX'
            ops=[o for o in after['pcode'] if o['instruction_va']=='004930fa']
            assert len(ops)==1 and ops[0]['opcode']=='STORE'
            assert [n['bytes'] for n in ops[0]['inputs']]==[4,4,4]
            assert ops[0]['inputs'][1]['high_name']=='stack_4_bits' and ops[0]['inputs'][2]['high_name']=='puVar1'
            tokens=[t for t in after['tokens'] if t.get('min_va')=='004930fa']
            assert [t['text'] for t in tokens]==['*','stack_4_bits','=','puVar1']
            old='*stack_4_bits = puVar1;'
            new='*stack_4_bits = reinterpret_cast<undefined4>(puVar1);'
            assert text.count(old)==1
            text=text.replace(old,new)
            store_lowering=dict(instruction=witness,pcode=ops[0],tokens=tokens,original_statement=old,native_statement=new,
                                boundary='Exact32-bit pointer representation stored by original MOV; no field/class reinterpretation')
        lowered,native_contract=abi.lower(decl,text)
        if store_lowering:
            lowered='static_assert(sizeof(void*) == 4 && sizeof(undefined4) == 4, "original pointer/rawword widths");\n'+lowered
        assert native_contract['native_stack_bytes']==8
        source=output/(va+'.cpp')
        source.write_text('#include "'+primitive.as_posix()+'"\n'+lowered,encoding='utf8',newline='\n')
        sources.append(source)
        results.append(dict(va=va,before_signature=before['inferred']['signature'],after_signature=after['inferred']['signature'],
                            original_body_sha256=evidence['original_body_sha256'],native_contract=native_contract,
                            generated_source=relative(source),generated_source_sha256=digest(source),
                            raw_database_prototype=database['signature'],inferred_pointer_view=view,
                            original_pointer_store_lowering=store_lowering,
                            pointer_view_boundary='Original32-bit MOV load/store and EAX output-address prove width/storage only; signed pointee/source types are unaccepted inference',
                            dependency_sha256={relative(primitive):digest(primitive)},forced_headers=[]))
    for path,expected in pins.items():
        assert digest(path)==expected,('input changed before compile',path)
    objects=output/'objects'
    objects.mkdir(exist_ok=True)
    pending=list(sources)
    if first_batch:
        cached=first_batch['compiled_unchanged']
        assert cached['va']=='0043f8a0' and digest(ROOT/cached['generated_source'])==cached['generated_source_sha256']
        assert digest(ROOT/cached['object'])==cached['object_sha256']
        pending=[s for s in sources if s.stem!=cached['va']]
        assert [s.stem for s in pending]==['004930f0']
    command=[str(abi.COMPILER),'/nologo','/c','/std:c++17','/O2','/Gy','/GS-','/GR-','/EHs-c-','/W4','/MP6','/Fo'+str(objects)+os.sep,*map(str,pending)]
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    process=subprocess.run(command,cwd=output,capture_output=True,env=env,timeout=120)
    raw=process.stdout+process.stderr
    try:log=raw.decode('utf8')
    except UnicodeDecodeError:log=raw.decode('cp1251')
    logpath=output/'compile.log'
    logpath.write_text(log.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n')
    assert process.returncode==0,log
    for record,evidence in zip(results,contracts['selected']):
        obj=objects/(record['va']+'.obj')
        symbols=coff.coff_symbols(obj)
        assert any('Thiscall_'+record['va'] in s for s in symbols['defined'])
        assert not symbols['undefined'] and not symbols['common'] and not symbols['weak']
        sections=abi.text_sections(obj)
        assert len(sections)==1 and sections[0]['relocations']==0
        disasm=subprocess.run([str(abi.DUMPBIN),'/disasm',str(obj)],cwd=output,capture_output=True,env=env,timeout=60)
        assert disasm.returncode==0
        text=(disasm.stdout+disasm.stderr).decode('utf8',errors='replace').replace('\r\n','\n')
        path=output/(record['va']+'-disassembly.txt')
        path.write_text(text,encoding='utf8',newline='\n')
        rets=re.findall(r'\bret\s+([0-9A-Fa-f]+)h?',text,re.I)
        assert rets and all(int(v,16)==8 for v in rets),('native RET mismatch',record['va'],rets)
        record.update(object=relative(obj),object_sha256=digest(obj),symbols=symbols,native_text_sections=sections,
                      native_ret_bytes=[int(v,16) for v in rets],disassembly=relative(path),disassembly_sha256=digest(path),
                      exact_original_body_byte_match=sections[0]['bytes']==evidence['original_body_hex'],compiled=True,
                      compiler_exit_code=0,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],
                      cache_reused=bool(first_batch and record['va']=='0043f8a0'))
        pins[ROOT/record['generated_source']]=record['generated_source_sha256']
        pins[obj]=record['object_sha256']
    for path,expected in pins.items():
        assert digest(path)==expected,('input changed after compile',path)
    report=dict(schema=1,original_sha256=abi.SHA,selected=VAS,corrected_functions=2,decompilations=4,actual_compiler_batches=2 if first_batch else 1,
                compiler_batches_this_pass=1,compiled_objects=len(results),real_coff_objects=len(results),objects_reused=1 if first_batch else 0,
                first_failed_batch=first_batch,
                compiler_command=command,compiler_exit_code=process.returncode,compiler_log=relative(logpath),compiler_log_sha256=digest(logpath),
                compiler_sha256=digest(abi.COMPILER),prepared_driver_sha256=prepared_driver_sha,
                prepared_driver_artifact=relative(preserved_driver),current_driver_sha256=digest(current_driver),
                exact_original_body_byte_matches=sum(r['exact_original_body_byte_match'] for r in results),
                original_project_unchanged=True,input_guard_before=True,input_guard_after=True,
                input_sha256={relative(p):h for p,h in pins.items()},results=results,
                original_call_consumer_count=4,complete_caller_high_IR_verification=False,
                boundary=['Two isolated raw32 storage contracts only; semantic types/classes/lifetimes remain unknown.',
                          'Unused original stack+8 is retained and consumed by native RET8, not deleted.',
                          'Native compiler output is candidate evidence; original execution/state equivalence and full callers remain open.',
                          'No manual call repair, external branch replacement, guessed algorithms, registry/production/corpus modification.'])
    write(RUN/'summary.json',report)
    print(json.dumps({k:report[k] for k in ('compiled_objects','actual_compiler_batches','exact_original_body_byte_matches','original_project_unchanged')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args()
    prepare() if args.prepare else compile_capture(args.attempt)
