"""Read-only original-byte, callable/source and native-COFF audit for207."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/207-pointer-call-consumers'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('coff207audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def main():
    summary=load(RUN/'summary.json');proof=load(RUN/'proof-before-compile.json')
    assert summary['original_sha256']==proof['original_sha256']==coff.ORIGINAL_SHA
    for name,expected in summary['input_sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        assert digest(path)==expected,('input drift',name)
    binaries=[json.loads(r)for r in (ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()]
    byte_readers={}
    for name in ['Porsche.exe','opengl1z.dll','opengl3z.dll','voodoo2z.dll']:
        record=next(r for r in binaries if r['file']==name)
        raw=(ROOT/'local/game'/record['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==record['sha256']
        pe=struct.unpack_from('<I',raw,0x3c)[0]
        machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
        base=struct.unpack_from('<I',raw,pe+24+28)[0]
        sections=[struct.unpack_from('<IIII',raw,pe+24+optional+i*40+8)[1:] for i in range(count)]
        byte_readers[name]=(raw,base,sections)
    def exact(module,instruction):
        raw,base,sections=byte_readers[module];rva=int(instruction['va'],16)-base;length=len(instruction['bytes'])//2
        start,size,offset=next(s for s in sections if s[0]<=rva and rva+length<=s[0]+s[1])
        assert raw[offset+rva-start:offset+rva-start+length].hex()==instruction['bytes'],(module,instruction)
    counts=dict(Porsche_consumer=0,Porsche_fallback=0,Porsche_loader=0,renderer_exports=0)
    for va,instructions in proof['selected_original_instructions'].items():
        for instruction in instructions:exact('Porsche.exe',instruction)
        counts['Porsche_fallback' if va=='00574f80' else 'Porsche_consumer']+=len(instructions)
    for window in proof['loader_windows']:
        for instruction in window['instructions']:exact('Porsche.exe',instruction)
        counts['Porsche_loader']+=len(window['instructions'])
    export_pops=[]
    for module in proof['module_proofs']:
        for instruction in module.get('original_instructions',[]):exact(module['module'],instruction)
        counts['renderer_exports']+=len(module.get('original_instructions',[]))
        if 'local_ret_sites' in module:
            pop=module['stack_cleanup'];assert pop in (4,8)
            assert all(r['instruction']==f'RET 0x{pop:x}'for r in module['local_ret_sites'])
            export_pops.append((module['module'],module['entry']['name'],pop))
    assert len(export_pops)==6 and sorted(p for _,_,p in export_pops)==[4,4,4,8,8,8]
    assert proof['contracts']['setstate']['callee_cleanup']==8
    assert proof['contracts']['getstate']['callee_cleanup']==proof['contracts']['release']['callee_cleanup']==4
    assert len(proof['sdk_proof'])==3
    for sdk in proof['sdk_proof']:
        assert digest(sdk['path'])==sdk['sha256']
        text=Path(sdk['path']).read_text(encoding='utf-8-sig');assert all(p in text for p in sdk['contract_patterns'])
    assert summary['objects_compiled']==4 and summary['compiler_batch_exit_code']==0 and summary['compile_seconds']>0
    execution=load(ROOT/summary['execution_sidecar'])
    assert execution['exit_code']==0 and execution['elapsed_seconds']==summary['compile_seconds'] and execution['actual_compiler_batches']==1
    assert len(summary['results'])==len(set(r['va']for r in summary['results']))==4
    for row in summary['results']:
        before=(ROOT/row['frozen203_source']).read_text(encoding='utf8')
        after=(ROOT/row['generated_source']).read_text(encoding='utf8')
        marker='/* VA '+row['va']+' */';a=before.split(marker,1)[1];b=after.split(marker,1)[1]
        if row['body_edit']:
            edit=row['body_edit'];assert a.count(edit['original'])==1
            assert a.replace(edit['original'],edit['replacement'])==b and row['va']=='0058f1f0'
            assert edit['call_va']=='0058f201' and edit['original_bytes']=='ff5108'
        else:assert a==b
        symbols=coff.coff_symbols(ROOT/row['object']);assert symbols==row['symbols']
        assert symbols['defined']==row['defined_external_symbols'] and symbols['undefined']==row['undefined_external_symbols']
        assert digest(ROOT/row['object'])==row['object_sha256']
        asm=(ROOT/row['disassembly']).read_text(encoding='utf8')
        assert re.search(r'\bret\s*\n',asm) and not re.search(r'\bret\s+[0-9]',asm)
        # These callbacks clean their arguments, including COM Release.
        assert not re.search(r'\badd\s+esp,',asm,re.I)
        header=(ROOT/row['native_decl_header']).read_text(encoding='utf8')
        assert 'typedef undefined4 (__stdcall *OriginalSetState207)(undefined4,undefined4);' in header
        assert 'typedef undefined4 (__stdcall *OriginalGetState207)(undefined4);' in header
        assert 'typedef undefined4 (__stdcall *OriginalRelease207)(int*);' in header
        if row['va'] in ('00540480','00554530'):assert 'DAT_006bd97c@@3P6GIII@ZA' in asm
        if row['va']=='005404e0':assert 'DAT_006bd918@@3P6GIII@ZA' in asm
        if row['va']=='00554530':
            assert 'DAT_006bd984@@3P6GII@ZA' in asm
            assert asm.count('DAT_006bd97c@@3P6GIII@ZA')==2
            assert re.search(r'mov\s+eax,dword ptr \[ebp-8\]',asm)
        if row['va']=='0058f1f0':
            assert re.search(r'mov\s+eax,dword ptr \[edx\+8\]',asm)
            assert re.search(r'call\s+eax',asm) and re.search(r'xor\s+eax,eax',asm)
    baseline=RUN.parent/'206-frontier-and-float-union/summary.json'
    existing={r['va']for r in load(baseline)['results']};new={r['va']for r in summary['results']}
    assert not existing&new
    paths=[RUN/'summary.json',RUN/'proof-before-compile.json',Path(__file__)]
    paths += [ROOT/r[k]for r in summary['results']for k in ('generated_source','native_decl_header','disassembly')]
    assert all(b'\r'not in p.read_bytes()for p in paths)
    validation=dict(schema=1,summary_sha256=digest(RUN/'summary.json'),audit_source_sha256=digest(Path(__file__)),
                    compiled_VAs=sorted(new),actual_compiler_batches=1,compiler_batch_exit_code=0,compile_seconds=summary['compile_seconds'],
                    PE_instruction_counts=counts,original_PE_bytes_passed=True,renderer_export_contracts=6,
                    original_sdk_Release_contract_passed=True,three_bodies_unchanged=True,one_Release_callable_type_only=True,
                    native_call_stack_cleanup_and_RET0_passed=True,all_input_SHA_guards_passed=True,
                    subset_undefined_names=summary['subset_undefined_names'],subset_undefined_references=summary['subset_undefined_references'],
                    disjoint_with_run206=True,run206_summary_sha256=digest(baseline),Ghidra_decompilations=0,
                    new_text_LF_before_SHA=True,complete_runtime_fidelity=False,union_rebuilt=False)
    (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(validation))


if __name__=='__main__':main()
