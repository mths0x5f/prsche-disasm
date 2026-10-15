"""Two PE-proven caller-clean direct-call declarations; bodies unchanged."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, os, re, struct, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'211-direct-call-contracts'
OUT=ROOT/'local/experiments/v2-direct-call-contracts-211'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CALLERS=['00565cd0','00565e70']; CALLEES=['00590290','00565ea0']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()
def write(path,value): path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result


def main():
    started=time.perf_counter(); assert not OUT.exists() or not any(OUT.iterdir()); assert not (RUN/'summary.json').exists()
    for p in (RUN,OUT,OUT/'sources',OUT/'objects',OUT/'logs'): p.mkdir(parents=True,exist_ok=True)
    pins={}
    def read(path,expected=None):
        path=Path(path).resolve(); raw=path.read_bytes(); actual=hashlib.sha256(raw).hexdigest()
        if expected: assert actual==expected,('stale input',path)
        assert path not in pins or pins[path]==actual; pins[path]=actual; return raw
    read(Path(__file__))
    prior_path=RUNS/'208-frontier-dependencies/summary.json'; prior=json.loads(read(prior_path)); assert prior['original_sha256']==SHA
    prior_rows={r['va']:r for r in prior['results']}; assert all(not prior_rows[va]['compiled'] for va in CALLERS)
    catalog_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
    catalog={r['entry_va']:r for r in map(json.loads,read(catalog_path).decode().splitlines())}
    manual_path=ROOT/'research/binary-index/manual-functions.jsonl'
    for r in map(json.loads,read(manual_path).decode().splitlines()):
        if r['module']=='Porsche.exe': catalog[r['entry_va']]=r
    registry_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'
    registry=[r for r in json.loads(read(registry_path))['functions'] if r['module']=='Porsche.exe']; ownership={}
    for va in CALLERS+CALLEES:
        value=int(va,16); overlaps=[]
        for owner in registry:
            assert owner['entry_va'] in catalog,('unindexed owner extent',owner['entry_va'])
            if any(int(a,16)<=value<=int(b,16) for a,b in catalog[owner['entry_va']]['ranges']): overlaps.append(owner)
        ownership[va]=dict(canonical_exact_or_interior=overlaps,wip_implementations=[],probe_boundaries=[])
    source_root=ROOT/'iterations/v2/001-original-recovery/source/recovered'
    for path in sorted(source_root.rglob('*.cpp')):
        text=path.read_text(encoding='utf8')
        if not any(va in text for va in ownership): continue
        read(path)
        for va in ownership:
            for m in re.finditer(r'\b([A-Za-z_]\w*_'+va+r')\s*\([^;{}]*\)\s*\{',text):
                bucket='probe_boundaries' if 'probe' in path.stem and 'boundary' in m[1] else 'wip_implementations'
                ownership[va][bucket].append(dict(source=relative(path),name=m[1]))
    assert not any(r['canonical_exact_or_interior'] or r['wip_implementations'] for r in ownership.values()),ownership
    binary_path=ROOT/'local/game/Porsche.exe'; image=read(binary_path,SHA)
    nt=struct.unpack_from('<I',image,0x3c)[0]; assert image[nt:nt+4]==b'PE\0\0'
    count=struct.unpack_from('<H',image,nt+6)[0]; optional=struct.unpack_from('<H',image,nt+20)[0]; imagebase=struct.unpack_from('<I',image,nt+24+28)[0]
    sections=[]
    for i in range(count):
        at=nt+24+optional+40*i; size,rva,rawsize,offset=struct.unpack_from('<IIII',image,at+8); sections.append((imagebase+rva,imagebase+rva+rawsize,offset))
    def original_bytes(va,n):
        matches=[(a,offset) for a,b,offset in sections if a<=va and va+n<=b]; assert len(matches)==1
        a,offset=matches[0]; return image[offset+va-a:offset+va-a+n]
    asm_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm'
    addresses=set(CALLERS+CALLEES+['00590070']); instructions={va:[] for va in addresses}
    for line in read(asm_path).decode().splitlines():
        match=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        if not match: continue
        value=int(match[1],16)
        for va in addresses:
            if any(int(a,16)<=value<=int(b,16) for a,b in catalog[va]['ranges']):
                raw=bytes.fromhex(match[2]); assert original_bytes(value,len(raw))==raw
                instructions[va].append(dict(va=match[1],bytes=match[2],instruction=match[3]))
    for va in instructions: assert sum(len(bytes.fromhex(r['bytes'])) for r in instructions[va])==catalog[va]['body_bytes']
    by_address={r['va']:r for values in instructions.values() for r in values}
    assert ''.join(r['bytes'] for r in instructions['00590290'])=='33c0c3'
    def direct_call(pc,target):
        r=by_address[pc]; raw=bytes.fromhex(r['bytes']); assert len(raw)==5 and raw[0]==0xe8
        assert int(pc,16)+5+struct.unpack_from('<i',raw,1)[0]==int(target,16); return r
    call1=direct_call('00565d07','00590290'); call2=direct_call('00565e93','00565ea0')
    for va,expected in {'00565d05':'51','00565d06':'50','00565d0c':'83c408','00565d0f':'85c0','00565e8b':'6a00','00565e8d':'50','00565e98':'83c408','00565e9b':'c3',
                        '00565ea0':'56','00565ea1':'57','00565ea2':'8b7c240c','00565ea6':'0fbe7704','00565ec5':'8b07'}.items(): assert by_address[va]['bytes']==expected
    assert [r['va'] for r in instructions['00565ea0'] if '[ESP' in r['instruction']]==['00565ea2']
    assert [r['bytes'] for r in instructions['00565ea0'] if r['instruction'].startswith('RET')]==['c3','c3']
    contracts=[dict(caller='00565cd0',callee='00590290',call=call1,pushed_stack_bytes=8,caller_cleanup=by_address['00565d0c'],
        stack_arguments=[dict(entry_offset=4,width=4,value='EAX: caller param_1 with original low-byte flag normalization'),dict(entry_offset=8,width=4,value='ECX: caller param_2')],
        callee_local_inputs=[],callee_unused_stack_offsets=[4,8],direct_incoming_gp_inputs=[],return_contract='EAX=0 by XOR EAX,EAX; RET0',
        prototype_before='undefined4 FUN_00590290(void);',prototype_after='undefined4 __cdecl FUN_00590290(uint param_1,undefined4 param_2);'),
        dict(caller='00565e70',callee='00565ea0',call=call2,pushed_stack_bytes=8,caller_cleanup=by_address['00565e98'],
        stack_arguments=[dict(entry_offset=4,width=4,value='EAX: caller param_3 object address'),dict(entry_offset=8,width=4,value='literal0')],
        callee_local_inputs=[dict(entry_offset=4,width=4,representation='raw object address',load=by_address['00565ea2'],stack_delta_at_load=-8)],
        callee_unused_stack_offsets=[8],direct_incoming_gp_inputs=[],return_contract='EAX raw32 returned through RET0; caller does not transform EAX',
        prototype_before='undefined4 FUN_00565ea0(int *param_1);',prototype_after='undefined4 __cdecl FUN_00565ea0(void *param_1,undefined4 unused_stack_8);',
        boundary='void* is a PE-proven raw pointer32 call view only; no inferred pointee/class/lifetime semantics; nested full-body/caller fidelity remains open')]
    evidence_path=OUT/'original-call-evidence.json'; write(evidence_path,dict(original_sha256=SHA,instructions=instructions,contracts=contracts,ownership=ownership,
        bounded_body_bytes=sum(catalog[va]['body_bytes'] for va in CALLERS+CALLEES),nested590070='Stack-only validator read for incoming volatile register seam; no compilation/behavior acceptance',
        abi_limit='Two specific direct caller-clean edges only; not whole-caller/callee/native execution equivalence'))
    read(evidence_path)
    declpath=ROOT/'scripts/research/experiment-v2-declarations-184.py'; coffpath=ROOT/'scripts/research/build-v2-compile-corpus.py'
    declarations=load_module('decl211',declpath); coff=load_module('coff211',coffpath); read(declpath); read(coffpath)
    prepare208=json.loads(read(ROOT/'local/experiments/v2-frontier-dependencies-208/prepare.json'))
    compiler=Path(prepare208['command'][0]); flags=prior['compiler_flags']; assert '/MP6' in flags
    for name in ('cl.exe','c1xx.dll','c2.dll'): read(compiler.parent/name)
    assert sha(compiler)==prior['compiler_sha256'] and not os.environ.get('CL') and not os.environ.get('_CL_')
    rows=[]
    for contract in contracts:
        va=contract['caller']; old=prior_rows[va]; source=ROOT/old['generated_source']; raw=read(source,old['generated_source_sha256']); text=raw.decode()
        before=contract['prototype_before']; after=contract['prototype_after']; assert text.count(before)==1
        changed=text.replace(before,after); marker='/* VA '+va+' */'; assert changed.split(marker,1)[1]==text.split(marker,1)[1]
        generated=OUT/'sources'/(va+'.cpp'); generated.write_text(changed,encoding='utf8',newline='\n')
        closure={}; pending=[generated]+[Path(p) for p in old.get('forced_headers',[])]
        while pending:
            path=pending.pop().resolve()
            if path in closure: continue
            read(path); closure[path]=pins[path]
            for token in re.findall(r'^\s*#include "([^"]+)"',path.read_text(),re.M):
                child=Path(token); pending.append(child if child.is_absolute() else path.parent/child)
        rows.append(dict(va=va,name=old['name'],source_body_sha256=old['source_body_sha256'],baseline_generated_source=relative(source),baseline_generated_source_sha256=sha(source),
            generated_source=relative(generated),generated_source_sha256=sha(generated),body_bytes_preserved=True,prototype_before=before,prototype_after=after,direct_call_contract=contract,
            dependency_sha256={relative(p):h for p,h in closure.items()},forced_headers=old.get('forced_headers',[]),object=relative(OUT/'objects'/(va+'.obj'))))
    def guard():
        def check(item): p,expected=item; assert sha(p)==expected,('input mutation',p)
        with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(check,pins.items()))
    guard(); rsp=OUT/'logs/native.rsp'; log=OUT/'logs/native.log'
    rsp.write_text('\n'.join('"'+s+'"' for s in flags+['/Fo'+(OUT/'objects').as_posix()+'/']+[str(ROOT/r['generated_source']) for r in rows])+'\n',encoding='utf-8-sig',newline='\n')
    command=[str(compiler),'@'+str(rsp)]; prepare_path=OUT/'prepare.json'
    write(prepare_path,dict(command=command,before_guard_pass=True,response_sha256=sha(rsp),input_sha256={relative(p):h for p,h in pins.items()},results=rows))
    before=time.perf_counter(); process=subprocess.run(command,cwd=OUT,capture_output=True,encoding='utf8',errors='replace',timeout=120,env={**os.environ,'VSLANG':'1033'})
    elapsed=time.perf_counter()-before; log.write_text(process.stdout+process.stderr,encoding='utf8',newline='\n')
    capture=OUT/'native-capture.json'; write(capture,dict(observed_compiler_batch_exit_code=process.returncode,compile_seconds=round(elapsed,6),command=command,
        prepare=relative(prepare_path),prepare_sha256=sha(prepare_path),response_sha256=sha(rsp),log_sha256=sha(log),actual_compiler_batches=1))
    text=log.read_text(); ds=declarations.diagnostics(text); by_va={va:[] for va in CALLERS}
    assert len(re.findall(r'(?m)^.*?:\s*(?:fatal error|error|warning)\s+[CD]\d+:',text))==len(ds)
    for d in ds:
        va=declarations.diagnostic_owner(d['source']); assert va in by_va; by_va[va].append(d)
    assert Counter(re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$',text))==Counter(CALLERS)
    success=[]; failures=[]; undefined=Counter(); definitions=set(); warning_codes=Counter()
    for row in rows:
        va=row['va']; errors=[d for d in by_va[va] if 'error' in d['severity']]; obj=ROOT/row['object']; assert obj.exists()==(not errors)
        row.update(compiled=obj.exists(),code_generation_succeeded=obj.exists(),compiler_exit_code=0 if process.returncode==0 and not errors else None,
            observed_compiler_batch_exit_code=process.returncode,owned_error_count=len(errors),owned_warning_count=sum(d['severity']=='warning' for d in by_va[va]),
            diagnostics=by_va[va],actual_i386_coff_validated=False,object_only_status_certified=False)
        warning_codes.update(d['code'] for d in by_va[va] if d['severity']=='warning')
        if obj.exists():
            symbols=coff.coff_symbols(obj); assert any('FUN_'+va in s for s in symbols['defined'])
            row.update(object_sha256=sha(obj),symbols=symbols,actual_i386_coff_validated=True,object_only_status_certified=True)
            success.append(va); undefined.update(symbols['undefined']); definitions.update(symbols['defined']+symbols['common'])
        else: failures.append(va)
    guard(); subset={s:n for s,n in undefined.items() if s not in definitions}
    report=dict(schema=1,module='Porsche.exe',original_sha256=SHA,compiler_sha256=sha(compiler),compiler_flags=flags,selected_scope_vas=CALLERS,selected=2,
        objects_compiled=len(success),real_coff_objects=len(success),compiled_vas=success,failed_vas=failures,code_generation_failed=len(failures),
        actual_compiler_batches=1,observed_compiler_batch_exit_code=process.returncode,compile_seconds=round(elapsed,6),warning_codes=dict(warning_codes),
        evidence=relative(evidence_path),evidence_sha256=sha(evidence_path),ownership_preflight=ownership,input_sha256={relative(p):h for p,h in pins.items()},
        compiler_response=relative(rsp),compiler_response_sha256=sha(rsp),compiler_log=relative(log),compiler_log_sha256=sha(log),native_capture=relative(capture),native_capture_sha256=sha(capture),
        subset_undefined_names=len(subset),subset_undefined_references=sum(subset.values()),subset_undefined_symbols=subset,results=rows,elapsed_seconds=round(time.perf_counter()-started,3),
        limits=['Two exact PE-proven direct-call declarations only; no body, callee implementation, source class, ABI bridge or storage changes.',
                'Both caller-clean edges pass8bytes; unused callee slots remain explicit; rawvoid* proves address width, not pointee semantics.',
                'Original nested/full-body/caller fidelity and native execution comparison remain backlog; no union/production changes.'])
    write(RUN/'summary.json',report)
    write(RUN/'validation.json',dict(schema=1,summary_sha256=sha(RUN/'summary.json'),source_script_sha256=sha(Path(__file__)),input_guards_before_after=True,
        original_pe_body_bytes_pass=True,original_call_rel32_and_cleanup_pass=True,ownership_exact_interior_wip_pass=True,
        bodies_preserved=True,only_two_prototype_edits=True,exit_and_timing_persisted_before_parse=True,objects_compiled=len(success),actual_compiler_batches=1,
        native_i386_coff_pass=True,nested_full_body_or_caller_fidelity=False,union_link_commands=0))
    print(json.dumps({k:report[k] for k in ('compiled_vas','failed_vas','observed_compiler_batch_exit_code','compile_seconds','warning_codes','subset_undefined_names','elapsed_seconds')},indent=2))


if __name__=='__main__': main()
