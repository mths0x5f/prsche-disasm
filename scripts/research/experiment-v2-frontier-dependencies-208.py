"""Nine newly exposed dependencies: exact externs, preserved bodies, one batch."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, os, re, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'208-frontier-dependencies'
OUT=ROOT/'local/experiments/v2-frontier-dependencies-208'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
TARGETS=['0041ebf0','00565cd0','00565e70','00589df0','00589f40','00590250','00590340','00590c60','00590d10']
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
relative=lambda path:Path(path).resolve().relative_to(ROOT).as_posix()


def write(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def main():
    begun=time.perf_counter()
    assert not OUT.exists() or not any(OUT.iterdir()), 'fresh208 capture required'
    assert not (RUN/'summary.json').exists(), 'frozen run cannot be overwritten'
    for path in (RUN,OUT,OUT/'sources',OUT/'headers',OUT/'objects',OUT/'logs'): path.mkdir(parents=True,exist_ok=True)
    declpath=ROOT/'scripts/research/experiment-v2-declarations-184.py'; coffpath=ROOT/'scripts/research/build-v2-compile-corpus.py'
    declarations=load_module('decl184_208',declpath); coff=load_module('coff208',coffpath)
    pins={}
    def read(path,expected=None):
        path=Path(path).resolve(); data=path.read_bytes(); actual=hashlib.sha256(data).hexdigest()
        if expected: assert actual==expected,('stale input',path)
        assert path not in pins or pins[path]==actual
        pins[path]=actual; return data
    for path in (Path(__file__),declpath,coffpath): read(path)
    frontier_path=RUNS/'206-frontier-and-float-union/summary.json'; frontier=json.loads(read(frontier_path))
    prior_path=RUNS/'192-scalar-slice-objects/summary.json'; prior=json.loads(read(prior_path))
    assert frontier['original_sha256']==prior['original_sha256']==SHA
    frontier_functions={r['va']:r for r in frontier['frontier'] if r['category']=='function'}
    assert all(va in frontier_functions and frontier_functions[va]['classification']=='no_compiled_union_body_or_canonical_owner' for va in TARGETS)
    audit_path=ROOT/prior['input_audit']; audit=json.loads(read(audit_path,prior['input_audit_sha256']))
    assert audit['original_sha256']==SHA
    selected={r['va']:r for r in audit['results'] if r['va'] in TARGETS}; assert len(selected)==9
    del audit  # This full audit is parsed exactly once; only nine rows survive.
    export=RUNS/'179-ghidra-declarations/export'
    functions={r['entry_va']:r for r in map(json.loads,read(export/'functions.jsonl').decode().splitlines()) if r['entry_va'] in TARGETS}
    types={r['path']:r for r in map(json.loads,read(export/'types.jsonl').decode().splitlines())}
    assert len(functions)==9 and all(d['module_sha256']==SHA for d in functions.values())
    for d in functions.values():
        for s in d.get('globals',[]):
            t=s['type']
            if t['path'] not in types and t['name'] in declarations.PRIMITIVES and (t['length'],t['alignment'])==declarations.PRIMITIVES[t['name']]: types[t['path']]=t
    catalog_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
    catalog={r['entry_va']:r for r in map(json.loads,read(catalog_path).decode().splitlines())}
    manual_path=ROOT/'research/binary-index/manual-functions.jsonl'
    for r in map(json.loads,read(manual_path).decode().splitlines()):
        if r['module']=='Porsche.exe': catalog[r['entry_va']]=r
    registry_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'
    owners=[r for r in json.loads(read(registry_path))['functions'] if r['module']=='Porsche.exe']
    ownership={}
    for va in TARGETS:
        value=int(va,16); overlaps=[]
        for owner in owners:
            if owner['entry_va']==va: overlaps.append(dict(kind='exact_canonical_entry',owner=owner))
            elif owner['entry_va'] in catalog:
                if any(int(a,16)<=value<=int(b,16) for a,b in catalog[owner['entry_va']]['ranges']): overlaps.append(dict(kind='interior_canonical_range',owner=owner))
        ownership[va]=dict(canonical_overlaps=overlaps,wip_implementation_definitions=[],probe_boundaries=[])
    source_root=ROOT/'iterations/v2/001-original-recovery/source/recovered'
    # Only files containing the nine target spellings are read into the closure;
    # definitions and boundary-only probes are kept distinct.
    for path in sorted(source_root.rglob('*.cpp')):
        text=path.read_text(encoding='utf8')
        if not any(va in text for va in TARGETS): continue
        read(path)
        for va in TARGETS:
            for m in re.finditer(r'\b([A-Za-z_]\w*_'+va+r')\s*\([^;{}]*\)\s*\{',text):
                entry=dict(source=relative(path),name=m[1])
                bucket='probe_boundaries' if 'probe' in path.stem and ('boundary' in m[1] or 'guard' in m[1]) else 'wip_implementation_definitions'
                ownership[va][bucket].append(entry)
    assert not any(x['canonical_overlaps'] or x['wip_implementation_definitions'] for x in ownership.values()),ownership
    assert any(r['name']=='frame_services_boundary_00565cd0' for r in ownership['00565cd0']['probe_boundaries'])
    compiler=Path(prior['batches'][0]['command'][0]); assert sha(compiler)==prior['compiler_sha256']
    for name in ('cl.exe','c1xx.dll','c2.dll'): read(compiler.parent/name)
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    flags=[s for s in prior['batches'][0]['command'][1:] if s.startswith('/') and not s.startswith('/Fo')]
    assert all(s in flags for s in ('/c','/Od','/Gy','/TP','/W3','/utf-8','/diagnostics:column','/MP6'))
    assert not any(s.startswith('/FI') for s in flags)
    rows=[]
    for va in TARGETS:
        old=selected[va]; metadata=functions[va]; source=Path(old['generated_source']); raw=read(source,old['generated_source_sha256'])
        text=raw.decode('utf8'); marker='/* VA '+va+' */'; assert text.count(marker)==1 and b'\r' not in raw
        body=text.split(marker,1)[1]; words=set(re.findall(r'\b[A-Za-z_$][\w$]*\b',body)); accepted=[]; blocked=[]
        for symbol in metadata.get('globals',[]):
            name=symbol.get('name')
            if not name or name not in words: continue
            record=dict(identity='Global::'+name,conflict=False,variants=[dict(symbol=symbol,consumer_vas=[va])])
            a,e=declarations.declarations(types,[record])
            if e: blocked.extend(e)
            else:
                for r in a: r.update(consumer_va=va,consumer_metadata_source=relative(export/'functions.jsonl'),shared_storage_acceptance=False)
                accepted.extend(a)
        header=OUT/'headers'/(va+'-globals.h'); header.write_text(declarations.header(accepted),encoding='utf8',newline='\n')
        scalar=re.search(r'^#include "[^\n]*ghidra-scalars-syntax-only\.h"\n',text,re.M); assert scalar,va
        changed=text[:scalar.end()]+'#include "'+header.as_posix()+'"\n'+text[scalar.end():]
        generated=OUT/'sources'/(va+'.cpp'); generated.write_text(changed,encoding='utf8',newline='\n')
        assert generated.read_bytes().split(marker.encode(),1)[1]==raw.split(marker.encode(),1)[1]
        forced=[str(Path(p).resolve()) for p in old.get('forced_headers',[])]; assert not forced,'Separate forced-header cohort needed'
        closure={}; pending=[generated]+[Path(p) for p in forced]
        while pending:
            path=pending.pop().resolve()
            if path in closure: continue
            read(path); closure[path]=pins[path]
            for token in re.findall(r'^\s*#include "([^"]+)"',path.read_text(encoding='utf8'),re.M):
                child=Path(token); pending.append(child if child.is_absolute() else path.parent/child)
        rows.append(dict(va=va,name=old['name'],source_body_sha256=old['source_body_sha256'],generated_source=relative(generated),generated_source_sha256=sha(generated),
            baseline_generated_source=relative(source),baseline_generated_source_sha256=old['generated_source_sha256'],body_bytes_preserved=True,
            body_after_marker_sha256=hashlib.sha256(raw.split(marker.encode(),1)[1]).hexdigest(),forced_headers=forced,
            dependency_sha256={relative(p):h for p,h in closure.items()},declaration_header=relative(header),declaration_header_sha256=sha(header),
            declaration_records=accepted,unsupported_metadata=blocked,ownership=ownership[va],
            inferred_signature=metadata.get('inferred_signature'),inferred_model_calling_convention=metadata.get('inferred_calling_convention'),
            abi_acceptance=False,object=relative(OUT/'objects'/(va+'.obj'))))
    extraction=OUT/'input-extraction.json'; write(extraction,dict(selected_audit_rows=list(selected.values()),function_metadata=functions,ownership=ownership,full_audit_read_count=1))
    read(extraction)
    def guard():
        def check(item): p,expected=item; assert sha(p)==expected,('input mutation',p)
        with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(check,pins.items()))
    guard()
    rsp=OUT/'logs/native.rsp'; log=OUT/'logs/native.log'; command=[str(compiler),'@'+str(rsp)]
    rsp.write_text('\n'.join('"'+s+'"' for s in flags+['/Fo'+(OUT/'objects').as_posix()+'/']+[str(ROOT/r['generated_source']) for r in rows])+'\n',encoding='utf-8-sig',newline='\n')
    # Durable pre-batch state and immediate post-batch result precede attribution.
    prepare=OUT/'prepare.json'; write(prepare,dict(original_sha256=SHA,command=command,compiler_flags=flags,compiler_sha256=sha(compiler),response_sha256=sha(rsp),
        before_guard_pass=True,input_sha256={relative(p):h for p,h in pins.items()},results=rows))
    before=time.perf_counter(); process=subprocess.run(command,cwd=OUT,capture_output=True,encoding='utf8',errors='replace',timeout=180,env={**os.environ,'VSLANG':'1033'})
    compile_seconds=time.perf_counter()-before; log.write_text(process.stdout+process.stderr,encoding='utf8',newline='\n')
    capture=OUT/'native-capture.json'; write(capture,dict(command=command,observed_compiler_batch_exit_code=process.returncode,compile_seconds=round(compile_seconds,6),
        log=relative(log),log_sha256=sha(log),response=relative(rsp),response_sha256=sha(rsp),prepare=relative(prepare),prepare_sha256=sha(prepare),actual_compiler_batches=1))
    text=log.read_text(encoding='utf8'); diagnostics=declarations.diagnostics(text)
    assert len(re.findall(r'(?m)^.*?:\s*(?:fatal error|error|warning)\s+[CD]\d+:',text))==len(diagnostics),'unattributed fatal/compiler line'
    by_va={va:[] for va in TARGETS}
    for d in diagnostics:
        va=declarations.diagnostic_owner(d['source']); assert va in by_va; by_va[va].append(d)
    assert Counter(re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$',text))==Counter(TARGETS)
    undefined=Counter(); definitions=set(); success=[]; failures=[]; codes=Counter(); warnings=Counter()
    for row in rows:
        va=row['va']; ds=by_va[va]; errors=[d for d in ds if 'error' in d['severity']]; obj=ROOT/row['object']
        assert obj.exists()==(not errors),(va,'inconsistent owned diagnostics/object')
        row.update(compiled=obj.exists(),code_generation_succeeded=obj.exists(),compiler_exit_code=0 if process.returncode==0 and not errors else None,
            observed_compiler_batch_exit_code=process.returncode,compiler_batch_exit_code=process.returncode,diagnostics=ds,
            owned_error_count=len(errors),owned_warning_count=sum(d['severity']=='warning' for d in ds),actual_i386_coff_validated=False,object_only_status_certified=False)
        codes.update(d['code'] for d in errors); warnings.update(d['code'] for d in ds if d['severity']=='warning')
        if obj.exists():
            symbols=coff.coff_symbols(obj); assert any('FUN_'+va in s for s in symbols['defined'])
            row.update(object_sha256=sha(obj),object_bytes=obj.stat().st_size,symbols=symbols,actual_i386_coff_validated=True,object_only_status_certified=True)
            success.append(va); undefined.update(symbols['undefined']); definitions.update(symbols['defined']+symbols['common'])
        else: failures.append(va)
    guard()
    assert sha(log)==json.loads(capture.read_bytes())['log_sha256']
    subset={s:n for s,n in undefined.items() if s not in definitions}
    report=dict(schema=1,kind='bounded-frontier-dependency-candidates',module='Porsche.exe',original_sha256=SHA,compiler_sha256=sha(compiler),compiler_flags=flags,
        input_audit=relative(audit_path),input_audit_sha256=prior['input_audit_sha256'],frontier_summary=relative(frontier_path),frontier_summary_sha256=sha(frontier_path),
        selected_scope_vas=TARGETS,selected=9,full_audit_read_count=1,actual_compiler_batches=1,observed_compiler_batch_exit_code=process.returncode,
        compile_seconds=round(compile_seconds,6),objects_compiled=len(success),real_coff_objects=len(success),code_generation_failed=len(failures),
        compiled_vas=success,failed_vas=failures,error_codes=dict(codes),warning_codes=dict(warnings),
        input_sha256={relative(p):h for p,h in sorted(pins.items(),key=lambda x:str(x[0]))},ownership_preflight=ownership,
        native_capture=relative(capture),native_capture_sha256=sha(capture),compiler_response=relative(rsp),compiler_response_sha256=sha(rsp),
        compiler_log=relative(log),compiler_log_sha256=sha(log),subset_undefined_names=len(subset),subset_undefined_references=sum(subset.values()),subset_undefined_symbols=subset,
        elapsed_seconds=round(time.perf_counter()-begun,3),results=rows,
        limits=['Only nine newly exposed function dependencies; body bytes preserved, exact179 per-consumer externs through184 resolver.',
                'Unsupported declarations and original compiler errors remain explicit; no signature/type/cast/alias/storage guesses.',
                'Compiler/model CC is not original hardware ABI acceptance. No Ghidra/native oracle/union/production changes.'])
    write(RUN/'summary.json',report)
    write(RUN/'validation.json',dict(schema=1,summary_sha256=sha(RUN/'summary.json'),source_script_sha256=sha(Path(__file__)),
        input_guards_before_after=True,canonical_wip_interior_preflight_pass=True,probe_boundary_not_implementation=True,body_bytes_preserved=True,
        actual_include_closures_pass=True,compiler_exit_and_timing_persisted_before_attribution=True,no_unattributed_fatal_diagnostics=True,
        actual_compiler_batches=1,native_i386_coff_pass=True,objects_compiled=len(success),native_abi_acceptance=False,union_link_commands=0))
    print(json.dumps({k:report[k] for k in ('compiled_vas','failed_vas','error_codes','warning_codes','observed_compiler_batch_exit_code','compile_seconds','objects_compiled','subset_undefined_names','elapsed_seconds')},indent=2))


if __name__=='__main__': main()
