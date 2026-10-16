"""Turn a validated actual diagnostic-link frontier into a bounded research queue."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CATALOG = ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
MANUAL = ROOT/'research/binary-index/manual-functions.jsonl'
REGISTRY = ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'
SOURCE = ROOT/'iterations/v2/001-original-recovery/source'
HEX = re.compile(r'^[0-9a-f]{8}$')
digest = lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative = lambda p:Path(p).resolve().relative_to(ROOT).as_posix()


def runtime_input(value,catalog):
    if value.get('original_sha256')!=SHA or value.get('module')!='Porsche.exe':
        raise ValueError('Runtime-miss input identity mismatch')
    entries = value.get('missing_entry_vas')
    if not isinstance(entries,list) or any(not isinstance(v,str) or not HEX.fullmatch(v.lower()) for v in entries):
        raise ValueError('Runtime-miss VAs must be eight hexadecimal digits')
    unique = sorted({v.lower() for v in entries})
    return dict(vas=unique,duplicates_removed=len(entries)-len(unique),
        known=[v for v in unique if v in catalog],unknown=[v for v in unique if v not in catalog],
        execution_claimed=False)


def remove_noncode(text):
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern,lambda m:''.join('\n' if c=='\n' else ' ' for c in m[0]),text)


def definitions(text):
    code = remove_noncode(text)
    pattern = r'(?m)^[ \t]*([^;{}\n]*\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:noexcept\s*)?)\{'
    rows = []
    for m in re.finditer(pattern,code):
        name = m[2]
        if name in ('if','for','while','switch','catch'):
            continue
        suffix = re.search(r'_([0-9a-fA-F]{8})$',name)
        rows.append(dict(name=name,va=suffix[1].lower() if suffix else None,line=code[:m.start()].count('\n')+1))
    return rows


def owner_state(va,owners,wip,compiled,interiors):
    matches = owners.get(va,[])
    if len(matches)>1:
        return 'duplicate_registry_owner_conflict'
    if va in compiled:
        return 'compiled_VA_symbol_contract_review'
    if len(matches)==1:
        return 'accepted_partial_owner_trace' if 'partial' in matches[0]['status'] else 'accepted_owner_reuse_review'
    if interiors.get(va):
        return 'registered_interior_entry_review'
    if wip.get(va):
        return 'WIP_exact_definition_review'
    return 'original_body_trace_required'


def source_reference_guard(refs,objects):
    return sorted(set(refs)-set(objects))


def self_tests():
    tests = []
    catalog = {'005a3719':{}}
    r = runtime_input(dict(original_sha256=SHA,module='Porsche.exe',missing_entry_vas=['005a3719','005A3719','ffffffff']),catalog)
    assert r['known']==['005a3719'] and r['unknown']==['ffffffff'] and r['duplicates_removed']==1
    tests.append('runtime known/unknown/dedup retains unknown as coverage gap')
    try:
        runtime_input(dict(original_sha256='0'*64,module='Porsche.exe',missing_entry_vas=[]),catalog)
        raise AssertionError('wrong SHA accepted')
    except ValueError:
        tests.append('runtime wrong original identity rejected')
    assert owner_state('005a3719',{'005a3719':[{'status':'full'},{'status':'full'}]}, {},{}, {})=='duplicate_registry_owner_conflict'
    tests.append('duplicate registry VA never silently selects an owner')
    assert source_reference_guard(['005a3719','unknown'],{'005a3719':{}})==['unknown']
    tests.append('unmapped object reference remains explicit blocker')
    assert owner_state('005a3719',{}, {}, {'005a3719':{}}, {})=='compiled_VA_symbol_contract_review'
    tests.append('compiled VA is contract review rather than missing body')
    scan = definitions('// void fake_005a3719() {}\nvoid real_005a376b(int x) {}\nconst char* s="void fake_005a3719() {}";\n')
    assert [r['va'] for r in scan]==['005a376b']
    tests.append('comments/strings cannot manufacture exact WIP definitions')
    return tests


def main(args):
    tests = self_tests()
    if args.self_test:
        print(json.dumps(dict(passed=True,tests=tests)))
        return
    if not args.union_summary or not args.run or not args.output:
        raise ValueError('--union-summary, --run and --output are required')
    run,out = args.run.resolve(),args.output.resolve()
    assert run.is_relative_to(ROOT/'iterations/v2/001-original-recovery/runs') and out.is_relative_to(ROOT/'local')
    assert not run.exists() and not out.exists(), 'Fresh run/output required'
    pins,recorded = {},{}
    def read(path,expected=None):
        path = Path(path).resolve()
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if expected is not None:
            assert sha==expected, ('Recorded input SHA drift',path)
            recorded[relative(path)]=sha
        assert path not in pins or pins[path]==sha, ('Input mutation while reading',path)
        pins[path]=sha
        return raw
    read(Path(__file__))
    summary_path = args.union_summary.resolve()
    s = json.loads(read(summary_path))
    validation_path = summary_path.parent/'validation.json'
    v = json.loads(read(validation_path))
    assert v['summary_sha256']==digest(summary_path) and s['original_sha256']==SHA
    assert v['input_guards_before_after'] and v['selected_source_include_object_closures_pass'] and v['cached_symbol_identity_pass']
    library = s['library']
    archive = ROOT/library['path']
    read(archive,library['sha256'])
    assert archive.stat().st_size==library['bytes'] and library['members']==s['objects']==v['objects']
    assert s['input_guard']['before'] and s['input_guard']['after']
    link = s['diagnostic_link']
    log = read(ROOT/link['log'],link['log_sha256']).decode('utf8')
    expected = link['unresolved_symbols']
    actual = Counter()
    for line in log.splitlines():
        if not re.search(r'\bLNK(?:2001|2019)\b',line):
            continue
        tail = re.split(r'\bLNK(?:2001|2019):\s*',line,maxsplit=1)[1]
        m = re.search(r'\(([_@?][^()\s]+)\)',tail)
        if m:
            symbol = m[1]
        else:
            names = [n for n in expected if re.search(r'(?<!\S)'+re.escape(n)+r'(?!\S)',tail)]
            assert len(names)==1, ('Unmapped actual link diagnostic',line)
            symbol = names[0]
        actual[symbol]+=1
    assert dict(actual)==expected and sum(actual.values())==link['diagnostic_occurrences']
    fatal = re.findall(r'(?m)^.*\bLNK1120:.*?(\d+)\s*$',log)
    assert fatal and int(fatal[-1])==len(actual) and not link['dll_created']
    frontier = [r for r in s['frontier'] if r.get('diagnostic_link_unresolved') is True]
    assert len({r['symbol'] for r in frontier})==len(frontier)
    assert {r['symbol'] for r in frontier}==set(actual), 'Unmapped/misflagged diagnostic frontier'
    objects = {}
    compiled = {}
    for row in s['results']:
        assert row['va'] not in objects, ('Duplicate source reference identity',row['va'])
        objects[row['va']]=row
        if row.get('cohort')!='support':
            assert HEX.fullmatch(row['va']) and row['va'] not in compiled, 'Duplicate compiled VA'
            compiled[row['va']]=row
    assert len(compiled)==v['unique_function_vas']==s['function_objects']
    # Reuse validated union symbol snapshots and closure attestations; do not
    # reopen1117COFFs or hash all6900 historical compile inputs.
    pinmap = s['input_sha256']
    catalog_rows = [json.loads(line) for line in read(CATALOG,pinmap[relative(CATALOG)]).decode().splitlines()]
    catalog = {}
    for row in catalog_rows:
        assert row['entry_va'] not in catalog, 'Duplicate original catalog entry'
        catalog[row['entry_va']]=row
    for row in map(json.loads,read(MANUAL,pinmap[relative(MANUAL)]).decode().splitlines()):
        if row['module']=='Porsche.exe':
            # Manual entries are explicit indexed supplements, not inferred bodies.
            catalog[row['entry_va']]=row
    registry = json.loads(read(REGISTRY,pinmap[relative(REGISTRY)]))['functions']
    owners = defaultdict(list)
    for row in registry:
        if row['module']=='Porsche.exe':
            assert row['sha256']==SHA
            owners[row['entry_va']].append(row)
    navigation = {}
    for row in frontier:
        suffix = re.search(r'_([0-9a-fA-F]{8})(?=@)',row['symbol'])
        navigation[row['symbol']]=row.get('va') or (suffix[1].lower() if suffix else None)
    targets = {va for va in navigation.values() if va}
    interiors = defaultdict(list)
    for va in targets:
        for entry,rows in owners.items():
            if entry==va or entry not in catalog:
                continue
            if any(int(a,16)<=int(va,16)<=int(b,16) for a,b in catalog[entry]['ranges']):
                interiors[va].extend(dict(va=entry,source=r['source']) for r in rows)
    source_files = sorted([*(SOURCE/'recovered/Porsche.exe').glob('*.cpp'),*(SOURCE/'platform').glob('*.cpp')])
    source_inventory = [relative(path) for path in source_files]
    wip,by_name = defaultdict(list),defaultdict(list)
    for path in source_files:
        text = read(path,pinmap.get(relative(path))).decode('utf8')
        for d in definitions(text):
            found = dict(source=relative(path),line=d['line'],name=d['name'])
            by_name[d['name']].append(found)
            if d['va'] in targets and path.parent.name=='Porsche.exe':
                wip[d['va']].append(found)
    runtime = runtime_input(json.loads(read(args.runtime_misses.resolve())),catalog) if args.runtime_misses else None
    groups = defaultdict(list)
    for row in frontier:
        va = navigation[row['symbol']]
        # Suffix-derived provider VAs are navigation only; do not merge their
        # native symbol contracts with FUN entries or invent an alias.
        key = (row['category'],row.get('va') or row['symbol'])
        groups[key].append(row)
    tasks = []
    ranks = {'blocked_source_mapping':0,'duplicate_registry_owner_conflict':0,'compiled_VA_symbol_contract_review':1,
        'accepted_owner_reuse_review':2,'WIP_exact_definition_review':2,'canonical_provider_contract_review':2,
        'accepted_partial_owner_trace':3,'registered_interior_entry_review':3,'scalar_storage_proof_required':4,
        'original_body_trace_required':5,'shared_data_view_trace_required':6,'data_layout_trace_required':7,
        'index_coverage_gap':8,'external_native_contract_review':9}
    for (category,key),rows in groups.items():
        names = sorted(r['symbol'] for r in rows)
        va = navigation[names[0]]
        refs = sorted({x for r in rows for x in r['referring_object_vas']})
        unmapped = source_reference_guard(refs,objects)
        own = owners.get(va,[]) if va else []
        definitions_ = wip.get(va,[]) if va else []
        body = catalog.get(va) if va else None
        canonical_provider = category=='other' and any('@porsche@@' in n for n in names)
        if unmapped:
            action='blocked_source_mapping'
        elif canonical_provider:
            action='canonical_provider_contract_review'
        elif category=='function':
            action=owner_state(va,owners,wip,compiled,interiors)
            if action=='original_body_trace_required' and not body:
                action='index_coverage_gap'
        elif category=='data':
            variants=[x['symbol'] for r in rows for x in r.get('ghidra_variants',[])]
            widths={x.get('bytes') for x in variants}
            types={x.get('type',{}).get('path') for x in variants}
            scalar=bool(variants) and widths=={4} and types<= {'/int','/uint','/undefined4','/unsigned int'}
            action='shared_data_view_trace_required' if len(names)>1 or any(r.get('observed_conflict') for r in rows) else 'scalar_storage_proof_required' if scalar else 'data_layout_trace_required'
        else:
            action='external_native_contract_review'
        bare = re.match(r'^\?([^@]+)@',names[0])
        provider_definitions=by_name.get(bare[1],[]) if canonical_provider and bare else []
        task=dict(kind=category,action=action,original_va=va,
            VA_identity='frontier_original_VA' if rows[0].get('va') else 'original_suffix_navigation_only' if va else 'unmapped_native_name',
            native_symbols=names,native_reference_ids=refs,fanout=len(refs),diagnostic_occurrences=sum(actual[n] for n in names),
            original_body_bytes=body.get('body_bytes') if body and category!='data' else None,
            indexed_entry_known=bool(body) if category!='data' else None,
            accepted_owners=[dict(source=r['source'],status=r['status'],calling_convention=r['calling_convention']) for r in own],
            exact_source_definition_candidates=definitions_ if category!='data' else [],
            platform_provider_definition_candidates=provider_definitions,
            compiled_entry=va in compiled if va else False,
            registered_interior_candidates=interiors.get(va,[]),unmapped_reference_ids=unmapped,
            executable_action_approved=False)
        if category=='data':
            variants=[x['symbol'] for r in rows for x in r.get('ghidra_variants',[])]
            task['storage_views']=sorted({(x.get('storage'),x.get('type',{}).get('path')) for x in variants},key=str)
            task['scalar_policy']='Initializer/permissions/HIGHLOW+indexed MEM widths/overlap/WIP/alias identity proof required before one physical cell; metadata is navigation only'
        tasks.append(task)
    if runtime:
        for va in runtime['vas']:
            match=next((t for t in tasks if t['original_va']==va and t['kind']=='function'),None)
            if match:
                match['runtime_miss_input_reported']=True
            else:
                tasks.append(dict(kind='runtime-miss-input',action='original_body_trace_required' if va in catalog else 'index_coverage_gap',
                    original_va=va,VA_identity='unexecuted_user_supplied_entry_report',native_symbols=[],native_reference_ids=[],fanout=0,
                    diagnostic_occurrences=0,original_body_bytes=catalog.get(va,{}).get('body_bytes'),indexed_entry_known=va in catalog,
                    executable_action_approved=False,runtime_miss_input_reported=True))
    tasks.sort(key=lambda t:(ranks[t['action']],-t['fanout'],t.get('original_body_bytes') or 0x10000000,t['original_va'] or '',str(t['native_symbols'])))
    for i,task in enumerate(tasks,1):
        task['rank']=i
    assert sorted([relative(p) for p in [*(SOURCE/'recovered/Porsche.exe').glob('*.cpp'),*(SOURCE/'platform').glob('*.cpp')]])==source_inventory,'Source inventory changed'
    for path,sha in pins.items():
        assert digest(path)==sha, ('Before/after input mutation',path)
    run.mkdir(parents=True);out.mkdir(parents=True)
    write=lambda path,value:path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
    write(out/'source-definition-cache.json',dict(schema=1,source_inventory=source_inventory,
        source_sha256={relative(p):sha for p,sha in pins.items() if p in source_files},scoped_definition_candidates=dict(wip),
        boundary='Canonical/platform source scan only; no probe TUs or5772decompiler corpus; candidates do not establish semantics/ABI'))
    command=['py','-3',relative(Path(__file__)),'--union-summary',relative(summary_path),'--run',relative(run),'--output',relative(out)]
    if args.runtime_misses:
        command+=['--runtime-misses',relative(args.runtime_misses)]
    counts=dict(actual_unresolved_names=len(actual),actual_diagnostic_occurrences=sum(actual.values()),tasks=len(tasks),
        categories=dict(Counter(t['kind'] for t in tasks)),actions=dict(Counter(t['action'] for t in tasks)),
        excluded_resolved_frontier_rows=len(s['frontier'])-len(frontier),compiled_function_VAs=len(compiled),
        scoped_source_files=len(source_files),recorded_source_registry_index_archive_pins_checked=len(recorded))
    report=dict(schema=1,kind='automated-original-frontier-task-queue',module='Porsche.exe',original_sha256=SHA,
        union_summary=relative(summary_path),union_summary_sha256=digest(summary_path),union_validation=relative(validation_path),
        union_validation_sha256=digest(validation_path),actual_archive=library['path'],actual_archive_sha256=library['sha256'],
        diagnostic_log=link['log'],diagnostic_log_sha256=link['log_sha256'],command=command,counts=counts,tasks=tasks,
        runtime_miss_input=runtime,meaningful_guard_tests=tests,input_sha256={relative(p):sha for p,sha in pins.items()},
        reused_symbol_snapshot_rows=len(s['results']),object_files_reread=0,compiler_commands=0,linker_commands=0,native_execution_commands=0,Ghidra_commands=0,
        priority_policy='Owner/mapping and ABI contract review first; then exact scalar proofs/original body tracing; within class fanout descending and indexed body size ascending. Rank is scheduling only.',
        policies=['Accepted/partial/WIP/registered-interior definitions remain distinct; no body recovery duplicated before owner review.',
            'Source definition candidates are exact lexical navigation, never hardware ABI/semantic acceptance; probe TUs excluded.',
            'Same-VA native mangles are retained independently; shared physical storage or aliases require original/native proof.',
            'Original suffix provider names are navigation only; noVA CRT/platform contracts remain explicit.',
            'No implementation, alias, storage allocation or native execution is generated.',
            'Runtime-miss JSON is parsed input only; full game-native miss collection is not implemented until a game EXE exists.'])
    write(run/'summary.json',report)
    write(run/'validation.json',dict(schema=1,passed=True,summary_sha256=digest(run/'summary.json'),script_sha256=digest(Path(__file__)),
        summary_validation_archive_and_link_log_SHA=True,before_after_pins_pass=True,guarded_inputs=len(pins),
        actual_diagnostic_names=len(actual),actual_occurrences=sum(actual.values()),unmapped_source_reference_tasks=sum(bool(t.get('unmapped_reference_ids')) for t in tasks),
        tests=tests,object_files_reread=0,native_execution_commands=0))
    readme='# 245 — automated original frontier queue\n\n'+f'Input: `{relative(summary_path)}`; actual archive SHA `{library["sha256"]}`. Summary/validation/archive/link-log provenance and before/after source/registry/index pins passed. Reparsed actual link: **{len(actual)} unresolved names / {sum(actual.values())} diagnostics**; {len(tasks)} research tasks, {counts["excluded_resolved_frontier_rows"]} resolved raw-frontier rows excluded.\n\n'
    readme+='The script reuses validated union symbol/closure snapshots and scans canonical/platform C++ definitions; it reads no decompiler corpus and invokes no compiler/linker/native/Ghidra. WIP/probe/interior/duplicate ownership and ABI mismatch remain separate. Ranking schedules proof work; it approves no implementation, data allocation or alias.\n\n'
    readme+='Priority classes: '+', '.join(f'{k}={v}' for k,v in counts['actions'].items())+'. Full exact contracts/reference IDs are in `summary.json`; the original frontier is not copied wholesale.\n\n'
    readme+='Top bounded review targets:\n\n'+''.join(f'- {t["rank"]}. `{t["original_va"] or t["native_symbols"][0]}`: {t["action"]}, fanout{t["fanout"]}, indexed bytes{t.get("original_body_bytes")}.\n' for t in tasks[:8])
    readme+='\nExecuted:\n\n```powershell\n'+' '.join('"'+a+'"' if ' ' in a else a for a in command)+'\n```\n\n'
    readme+='Six meaningful parser/owner guards passed (runtime known/unknown/dedup and wrongSHA, duplicate owner VA, unmapped refs, compiled ABI frontier, comments/strings). Optional `--runtime-misses` accepts an identity-pinned entry list, retaining unknown VAs as index gaps. It is only an input parser; game-native execution/miss capture is **not implemented** until an EXE exists. Future batches remain manual proof/implementation tasks; no full x86 translator or game behavior is inferred.\n'
    (run/'README.md').write_text(readme,encoding='utf8',newline='\n')
    print(json.dumps(dict(counts=counts,top=[dict(rank=t['rank'],va=t['original_va'],action=t['action'],fanout=t['fanout']) for t in tasks[:5]],pins=len(pins))))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--union-summary',type=Path)
    parser.add_argument('--run',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--runtime-misses',type=Path)
    parser.add_argument('--self-test',action='store_true')
    main(parser.parse_args())
