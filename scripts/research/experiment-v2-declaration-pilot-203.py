"""Exact179 externs on25 frozen201 TUs, one native batch, no body rewrites."""
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import argparse, hashlib, importlib.util, json, os, re, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'203-consumer-declaration-pilot'
OUT=ROOT/'local/experiments/v2-consumer-declarations-203/final'
TRIAGE=RUNS/'201-missing-body-triage/summary.json'
CACHE=ROOT/'local/experiments/v2-missing-body-triage-201/selected-inputs.json'
PRIOR=RUNS/'192-scalar-slice-objects/summary.json'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result


def write(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--finalize-existing',action='store_true'); args=parser.parse_args()
    started=time.perf_counter()
    assert args.finalize_existing or not OUT.exists() or not any(OUT.iterdir()), 'fresh203 output required'
    assert args.finalize_existing or not (RUN/'summary.json').exists(), 'do not overwrite completed203'
    if args.finalize_existing and (RUN/'summary.json').exists():
        previous_bytes=(RUN/'summary.json').read_bytes(); previous=json.loads(previous_bytes)
        assert previous['compiler_log_sha256']==sha(OUT/'logs/changed.log') and previous['compiler_response_sha256']==sha(OUT/'logs/changed.rsp')
        saved=OUT/'previous-finalizer-summary.json'
        assert not saved.exists(), 'do not overwrite an existing finalizer checkpoint'
        saved.write_bytes(previous_bytes)
    for p in (RUN,OUT,OUT/'sources',OUT/'headers',OUT/'objects',OUT/'logs'): p.mkdir(parents=True,exist_ok=True)
    declpath=ROOT/'scripts/research/experiment-v2-declarations-184.py'; coffpath=ROOT/'scripts/research/build-v2-compile-corpus.py'
    declarations=module('decl184_203',declpath); coff=module('coff203',coffpath)
    triage=json.loads(TRIAGE.read_bytes()); cache=json.loads(CACHE.read_bytes()); prior=json.loads(PRIOR.read_bytes())
    assert sha(CACHE)==triage['input_sha256'][relative(CACHE)]
    assert triage['original_sha256']==cache['original_sha256']==prior['original_sha256']==SHA
    targets=triage['clean_declaration_pilot_vas']; assert len(targets)==len(set(targets))==25
    target_rows={r['va']:r for r in cache['audit_rows'] if r['va'] in targets}
    triage_rows={r['va']:r for r in triage['rows']}; assert len(target_rows)==25
    assert cache['current_audit_sha256']==triage['current_audit_sha256']==prior['input_audit_sha256']
    assert relative(ROOT/prior['input_audit'])==triage['current_audit']
    assert not os.environ.get('CL') and not os.environ.get('_CL_'), 'unrecorded compiler options'
    pins={p.resolve():sha(p) for p in (Path(__file__),TRIAGE,CACHE,PRIOR,declpath,coffpath)}
    if args.finalize_existing:
        captured=OUT/'native-capture-driver.py'; assert captured.exists(); pins[captured]=sha(captured)
    pins[ROOT/triage['current_audit']]=triage['current_audit_sha256']
    export=RUNS/'179-ghidra-declarations/export'
    for name in ('functions.jsonl','types.jsonl'):
        path=export/name; pins[path]=triage['input_sha256'][relative(path)]
    registry=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'; pins[registry]=sha(registry)
    accepted={r['entry_va']:r for r in json.loads(registry.read_bytes())['functions'] if r['module']=='Porsche.exe'}
    wip={}; wip_names=('formatter_search','rtti','formatter_stdio')
    for packet in wip_names:
        path=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'/(packet+'.cpp'); pins[path]=sha(path)
        text=path.read_text(encoding='utf8')
        for match in re.finditer(r'\b([A-Za-z_]\w*_([0-9a-f]{8}))\s*\([^;{}]*\)\s*\{',text):
            wip.setdefault(match[2],[]).append(dict(source=relative(path),function=match[1]))
    ownership={va:dict(canonical_owner=accepted.get(va),unregistered_wip_owners=wip.get(va,[]),
                       same_getC_compile_candidate_only=True,implementation_owner_replaced=False) for va in targets}
    # No implementation is copied/recreated: even an existing owner is only flagged.
    types=dict(cache['types'])
    for d in cache['declarations'].values():
        for s in d.get('globals',[]):
            t=s['type']
            if t['path'] not in types and t['name'] in declarations.PRIMITIVES and (t['length'],t['alignment'])==declarations.PRIMITIVES[t['name']]: types[t['path']]=t
    compiler=Path(prior['batches'][0]['command'][0]); assert prior['compiler_sha256']==sha(compiler)
    native_command=prior['batches'][0]['command']
    flags=[s for s in native_command[1:] if s.startswith('/') and not s.startswith('/Fo')]
    assert all(s in flags for s in ('/c','/Od','/Gy','/TP','/W3','/utf-8','/diagnostics:column','/MP6'))
    assert not any(s.startswith('/FI') for s in flags), 'forced context must be explicit per selected TU'
    for name in ('cl.exe','c1xx.dll','c2.dll'): path=compiler.parent/name; pins[path]=sha(path)
    rows=[]; blocked=[]; record_details=[]
    for va in targets:
        old=target_rows[va]; view=triage_rows[va]; assert not old['syntax_passed']
        source=Path(old['generated_source']); pins[source]=old['generated_source_sha256']
        raw=source.read_bytes(); assert hashlib.sha256(raw).hexdigest()==old['generated_source_sha256'] and b'\r' not in raw
        metadata=cache['declarations'][va]; scoped={s.get('name'):s for s in metadata.get('globals',[])}
        missing=view['missing_global_names']; assert set(missing)==set(view['compatible184_declaration_names'])
        entries=[]
        for name in missing:
            symbol=scoped[name]; assert symbol['storage_detail']['memory'] and not symbol['storage_detail']['compound']
            record=dict(identity='Global::'+name,conflict=False,variants=[dict(symbol=symbol,consumer_vas=[va])])
            a,e=declarations.declarations(types,[record])
            if not a or e: blocked.append(dict(va=va,name=name,reasons=e)); break
            a[0]['consumer_metadata_source']=relative(export/'functions.jsonl'); a[0]['consumer_va']=va
            a[0]['conflict_resolution']='This exact179 consumer view only; no cross-consumer storage coalescing'
            entries.extend(a)
        else:
            h=OUT/'headers'/(va+'-globals.h'); expected_header=declarations.header(entries)
            if args.finalize_existing: assert h.read_bytes()==expected_header.encode('utf8')
            else: h.write_text(expected_header,encoding='utf8',newline='\n')
            text=raw.decode('utf8'); scalar=re.search(r'^#include "[^\n]*ghidra-scalars-syntax-only\.h"\n',text,re.M); assert scalar,va
            include='#include "'+h.as_posix()+'"\n'; changed=text[:scalar.end()]+include+text[scalar.end():]
            generated=OUT/'sources'/(va+'.cpp')
            if args.finalize_existing: assert generated.read_bytes()==changed.encode('utf8')
            else: generated.write_text(changed,encoding='utf8',newline='\n')
            marker='/* VA '+va+' */'; assert text.count(marker)==changed.count(marker)==1
            original_body=text.split(marker,1)[1].encode(); generated_body=generated.read_bytes().split(marker.encode(),1)[1]
            assert original_body==generated_body,('body bytes changed',va)
            forced=[str(Path(p).resolve()) for p in old.get('forced_headers',[])]; assert not forced, 'separate native forced-header cohort required'
            closure={}; pending=[generated]+[Path(p) for p in forced]
            while pending:
                path=pending.pop().resolve()
                if path in closure: continue
                closure[path]=sha(path); pins[path]=closure[path]
                for token in re.findall(r'^\s*#include "([^"]+)"',path.read_text(encoding='utf8'),re.M):
                    child=Path(token); pending.append(child if child.is_absolute() else path.parent/child)
            rows.append(dict(va=va,name=old['name'],source_body_sha256=old['source_body_sha256'],
                generated_source=relative(generated),generated_source_sha256=sha(generated),baseline_generated_source=relative(source),
                baseline_generated_source_sha256=old['generated_source_sha256'],preserved_body_sha256=hashlib.sha256(original_body).hexdigest(),body_bytes_preserved=True,
                declaration_header=relative(h),declaration_header_sha256=sha(h),declaration_records=entries,
                dependency_sha256={relative(p):expected for p,expected in closure.items()},forced_headers=forced,
                original_inferred_signature=metadata['inferred_signature'],inferred_model_calling_convention=metadata['inferred_calling_convention'],
                original_ret_evidence=view['local_ret_evidence'],abi_acceptance='Unproved:179 model is navigation only; no original CALL/RET consumer or hardware ABI acceptance',
                ownership=ownership[va],object=relative(OUT/'objects'/(va+'.obj'))))
            record_details.extend(entries)
    def guard():
        def check(item):
            p,expected=item; assert sha(p)==expected,('input/output source mutation',p)
        with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(check,pins.items()))
    guard()
    assert rows, 'all selected metadata blocked'
    rsp=OUT/'logs/changed.rsp'; log=OUT/'logs/changed.log'
    options=flags+['/Fo'+(OUT/'objects').as_posix()+'/']
    rsp_text='\n'.join('"'+s+'"' for s in options+[str(ROOT/r['generated_source']) for r in rows])+'\n'
    if args.finalize_existing:
        assert rsp.read_bytes()==rsp_text.encode('utf-8-sig'); text=log.read_text(encoding='utf8')
        compile_seconds=None; batch_exit_code=None
    else:
        rsp.write_text(rsp_text,encoding='utf-8-sig',newline='\n')
        before=time.perf_counter(); process=subprocess.run([str(compiler),'@'+str(rsp)],cwd=OUT,capture_output=True,encoding='utf8',errors='replace',timeout=180,env={**os.environ,'VSLANG':'1033'})
        compile_seconds=time.perf_counter()-before; text=process.stdout+process.stderr; log.write_text(text,encoding='utf8',newline='\n'); batch_exit_code=process.returncode
    diagnostics=declarations.diagnostics(text); by_va={r['va']:[] for r in rows}
    for d in diagnostics:
        va=declarations.diagnostic_owner(d['source']); assert va in by_va,('unowned compiler diagnostic',d); by_va[va].append(d)
    emitted=re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$',text); assert Counter(emitted)==Counter(by_va.keys()),('ambiguous batch filenames',emitted)
    native=[]; undefined=Counter(); codes=Counter(); warnings=Counter()
    for row in rows:
        obj=ROOT/row['object']; ds=by_va[row['va']]; errors=[d for d in ds if 'error' in d['severity']]
        assert obj.exists()==(not errors),('unattributed codegen outcome',row['va'])
        row.update(compiler_exit_code=None,observed_compiler_exit_code=None,compiled=obj.exists(),code_generation_succeeded=obj.exists(),
                   compiler_outcome_evidence='Fresh valid i386 COFF and zero owned errors' if obj.exists() else 'Owned compiler errors and no COFF',
                   diagnostics=ds,compiler_batch_exit_code=batch_exit_code)
        codes.update(d['code'] for d in errors); warnings.update(d['code'] for d in ds if d['severity']=='warning')
        if obj.exists():
            symbols=coff.coff_symbols(obj); assert any('FUN_'+row['va'] in s for s in symbols['defined'])
            row.update(object_sha256=sha(obj),object_bytes=obj.stat().st_size,symbols=symbols)
            native.append(row); undefined.update(symbols['undefined'])
    guard()
    definitions={s for r in native for s in r['symbols']['defined']+r['symbols']['common']}
    unresolved={s:n for s,n in undefined.items() if s not in definitions}
    report=dict(schema=1,kind='bounded-consumer-extern-native-candidates',module='Porsche.exe',original_sha256=SHA,
        compiler_sha256=sha(compiler),compiler_flags=flags,input_audit=triage['current_audit'],input_audit_sha256=triage['current_audit_sha256'],
        triage_summary=relative(TRIAGE),triage_summary_sha256=sha(TRIAGE),selected_scope_vas=targets,selected=25,objects_compiled=len(native),real_coff_objects=len(native),
        blocked_metadata=blocked,compiled_tus=len(rows),code_generation_failed=len(rows)-len(native),actual_compiler_batches=1,new_compilations=len(rows),jobs=6,
        actual_compiler_batches_this_pass=0 if args.finalize_existing else 1,finalize_existing=bool(args.finalize_existing),
        owned_body_candidates=sum(bool(r['canonical_owner'] or r['unregistered_wip_owners']) for r in ownership.values()),ownership_preflight=ownership,
        input_sha256={relative(p):expected for p,expected in sorted(pins.items(),key=lambda x:str(x[0]))},
        compiler_response=relative(rsp),compiler_response_sha256=sha(rsp),compiler_log=relative(log),compiler_log_sha256=sha(log),compiler_batch_exit_code=batch_exit_code,
        capture_driver=relative(captured) if args.finalize_existing else relative(Path(__file__)),capture_driver_sha256=sha(captured) if args.finalize_existing else sha(Path(__file__)),
        batch_exit_and_timing_sidecars_unavailable=bool(args.finalize_existing),
        error_codes=dict(codes),warning_codes=dict(warnings),warning_vas=[r['va'] for r in rows if any(d['severity']=='warning' for d in r['diagnostics'])],
        subset_undefined_names=len(unresolved),subset_undefined_references=sum(unresolved.values()),subset_undefined_symbols=unresolved,
        compile_seconds=round(compile_seconds,3) if compile_seconds is not None else None,elapsed_seconds=round(time.perf_counter()-started,3),results=rows,
        limits=['Compile candidates only; bodies byte-preserved, no casts, aliases, storage definitions or implementation duplicates.',
                'Only exact179 per-consumer extern views added through184 resolver; unknown metadata blocked.',
                '179 stdcall model is not hardware ABI acceptance. CALL/RET, original behavior, object lifetimes/storage remain open.',
                'No compiler syntax prepass, Ghidra, original execution, archive or union link. New warnings remain explicit.'])
    write(RUN/'summary.json',report)
    write(RUN/'validation.json',dict(schema=1,summary_sha256=sha(RUN/'summary.json'),source_script_sha256=sha(Path(__file__)),input_guards_before_after=True,
        actual_include_closures_pass=True,only_include_changes=True,body_bytes_preserved=True,source_owner_preflight_pass=True,owned_body_candidates=report['owned_body_candidates'],
        compiler_diagnostics_uniquely_attributed=True,objects_compiled=len(native),native_i386_coff_pass=True,native_abi_acceptance=False,union_link_commands=0))
    print(json.dumps({k:report[k] for k in ('selected','objects_compiled','code_generation_failed','owned_body_candidates','error_codes','warning_codes','subset_undefined_names','subset_undefined_references','compile_seconds','elapsed_seconds')},indent=2))


if __name__=='__main__': main()
