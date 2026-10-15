"""Read-only109-body frontier census; no compiler/Ghidra/oracle/tool execution."""
from collections import Counter, defaultdict
import argparse, bisect, hashlib, importlib.util, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'iterations/v2/001-original-recovery/runs/201-missing-body-triage'
OUT = ROOT/'local/experiments/v2-missing-body-triage-201'
RUNS = RUN.parent
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(Path(path).read_bytes())
relative = lambda path: Path(path).resolve().relative_to(ROOT).as_posix()


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf8', newline='\n')


def capture():
    cache = OUT/'selected-inputs.json'
    if cache.exists():
        data = json.loads(cache.read_bytes())
        assert sha(ROOT/data['frontier_summary']) == data['input_sha256'][data['frontier_summary']]
        # The immutable full audit was read once; subsequent report refinements
        # use only this pinned109-row extraction, never parse5772 rows again.
        return data
    pins = {}

    def read(path):
        path = Path(path); raw = path.read_bytes(); pins[relative(path)] = digest(raw); return raw

    frontier_path = RUNS/'199-native-abi-union/summary.json'; frontier = json.loads(read(frontier_path))
    ordinary_path = ROOT/frontier['ordinary_summary']; ordinary = json.loads(read(ordinary_path))
    audit_path = ROOT/ordinary['input_audit']; raw = read(audit_path)
    assert digest(raw) == ordinary['input_audit_sha256']
    audit = json.loads(raw); selected = [r for r in frontier['frontier'] if r['classification'] == 'no_compiled_union_body_or_canonical_owner']
    canonical = [r for r in frontier['frontier'] if r['classification'] == 'canonical_recovered_owner_outside_candidate_union']
    assert len(selected) == 109 and len(canonical) == 36 and all(r['category'] == 'function' for r in selected)
    wanted = {r['va'] for r in selected}; rows = [r for r in audit['results'] if r['va'] in wanted]
    assert len(rows) == 109
    declarations_path = RUNS/'179-ghidra-declarations/export/functions.jsonl'
    declarations = {r['entry_va']:r for r in map(json.loads, read(declarations_path).decode().splitlines()) if r['entry_va'] in wanted}
    catalog_path = ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
    catalog = {r['entry_va']:r for r in map(json.loads, read(catalog_path).decode().splitlines()) if r['entry_va'] in wanted}
    proof_paths = {'186': RUNS/'186-thiscall-compatibility/summary.json', '194': RUNS/'194-global-aliases/summary.json',
                   '196': RUNS/'196-thiscall-leaf-delta/summary.json', '197': RUNS/'197-call-free-abi/summary.json'}
    proofs = {name: json.loads(read(path)) for name, path in proof_paths.items()}
    for row in rows:
        path = Path(row['generated_source']); path = path if path.is_absolute() else ROOT/path
        assert digest(read(path)) == row['generated_source_sha256']
    data = dict(schema=1, original_sha256=SHA, frontier_summary=relative(frontier_path), ordinary_summary=relative(ordinary_path),
                current_audit=relative(audit_path), current_audit_sha256=pins[relative(audit_path)], full_audit_functions=len(audit['results']),
                full_audit_read_count=1, input_sha256=pins, selected_frontier=selected, canonical_reference_only=canonical,
                audit_rows=rows, declarations=declarations, catalog=catalog, proofs=proofs,
                proof_paths={key:relative(path) for key,path in proof_paths.items()})
    write(cache, data); return data


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--capture-only', action='store_true'); args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True); RUN.mkdir(parents=True, exist_ok=True); data = capture()
    if 'local_ret_evidence' not in data:
        asm = ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm'; raw = asm.read_bytes()
        data['input_sha256'][relative(asm)] = digest(raw)
        ranges = sorted((int(a,16),int(b,16),va) for va,c in data['catalog'].items() for a,b in c['ranges'])
        starts = [r[0] for r in ranges]; facts = {va:dict(local_ret_sites=[], call_instructions=0, instructions=0) for va in data['catalog']}
        for line in raw.decode().splitlines():
            match = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
            if not match: continue
            address = int(match[1],16); i = bisect.bisect_right(starts,address)-1
            if i < 0 or address > ranges[i][1]: continue
            va = ranges[i][2]; fact = facts[va]; fact['instructions'] += 1; instruction = match[3]
            if instruction.startswith('CALL'): fact['call_instructions'] += 1
            if instruction.startswith('RET'):
                fact['local_ret_sites'].append(dict(va=match[1], bytes=match[2], instruction=instruction,
                    stack_pop=int(instruction.split(' ',1)[1],16) if ' ' in instruction else 0))
        data['local_ret_evidence'] = facts
        path = RUNS/'179-ghidra-declarations/export/types.jsonl'; raw = path.read_bytes(); data['input_sha256'][relative(path)] = digest(raw)
        data['types'] = {r['path']:r for r in map(json.loads,raw.decode().splitlines())}
        write(OUT/'selected-inputs.json',data)
    spec = importlib.util.spec_from_file_location('decl184',ROOT/'scripts/research/experiment-v2-declarations-184.py')
    vocabulary = importlib.util.module_from_spec(spec); spec.loader.exec_module(vocabulary)
    types = dict(data['types'])
    for d in data['declarations'].values():
        for s in d.get('globals',[]):
            t=s['type']
            if t['path'] not in types and t['name'] in vocabulary.PRIMITIVES and (t['length'],t['alignment']) == vocabulary.PRIMITIVES[t['name']]: types[t['path']]=t
    audit_rows = data['audit_rows']; decls = data['declarations']; counts = Counter(); codes = Counter(); code_functions = Counter(); source_patterns = Counter()
    rows = []; categories = defaultdict(list); missing_names = Counter()
    patterns = {'own_thiscall_definition':r'\b__thiscall\s+FUN_[0-9a-f]+\s*\(',
                'pointer_address_store':r'(?m)^\s*(?:\*\w+|\w+\[[^\n]+?\])\s*=\s*&(?:PTR_|DAT_|s_)\w+\s*;',
                'partial_scalar':r'\._\d+_\d+_', 'extended_float':r'\bfloat(?:10|16)\b',
                'hidden_register_or_stack':r'\b(?:in_|unaff_|extraout_|in_stack_)\w+',
                'narrow_vocabulary':r'\b(?:u?int[3567]|u?longlong[0-9]+)\b',
                'qualified_call_or_function_pointer':r'\b(?:__thiscall|__fastcall|__stdcall)\s*\*|\(\s*\*[^\n;]+\)\s*\('}
    for old in audit_rows:
        va = old['va']; d = decls[va]; cc = d.get('inferred_calling_convention', 'unknown'); counts[cc] += 1
        source = Path(old['generated_source']); source = source if source.is_absolute() else ROOT/source
        text = source.read_text(encoding='utf8'); assert sha(source) == old['generated_source_sha256']
        marker = '/* VA '+va+' */'; body = text.split(marker, 1)[1] if marker in text else text
        errors = [r for r in old.get('diagnostics', []) if 'error' in r['severity']]
        per_codes = Counter(r['code'] for r in errors); codes.update(per_codes); code_functions.update(per_codes.keys())
        cats = Counter(r.get('category','uncategorized') for r in errors)
        hits = {name:len(re.findall(pattern,body)) for name,pattern in patterns.items() if re.search(pattern,body)}; source_patterns.update(hits.keys())
        names = sorted({m[1] for r in errors if (m:=re.match(r'([^ :]+):',r['message'])) and r['code'] in ('C2065','C3861','C2061')})
        missing_globals = [name for name in names if re.match(r'^_?(?:DAT|PTR|LAB|s_|u_)[A-Za-z0-9_]*',name)]
        missing_names.update(missing_globals)
        scoped = {r.get('name'):r for r in d.get('globals',[])}
        matching = [name for name in missing_globals if name in scoped]
        alias = [name for name in missing_globals if name.startswith('_') and name[1:] in scoped]
        compatible = []; incompatible = {}
        for name in matching:
            accepted, excluded = vocabulary.declarations(types,[dict(identity='Global::'+name, conflict=False, variants=[dict(symbol=scoped[name],consumer_vas=[va])])])
            if accepted: compatible.append(name)
            else: incompatible[name]=excluded[0]['reason']
        group = []
        if per_codes['C3865']: group.append('thiscall_declaration_or_definition')
        if missing_globals: group.append('missing_global_declarations_or_printed_aliases')
        if any(code in per_codes for code in ('C2660','C2664','C2197','C2198','C2371','C2733')): group.append('caller_prototype_or_type_contract')
        if 'partial_scalar' in hits: group.append('partial_scalar_representation')
        if 'pointer_address_store' in hits: group.append('pointer_address_to_raw_word_candidate')
        if 'narrow_vocabulary' in hits or any(name in ('NAN','INFINITY','ABS','uint3','int3') for name in names): group.append('type_or_constant_vocabulary')
        if 'extended_float' in hits: group.append('extended_float_representation')
        if 'hidden_register_or_stack' in hits: group.append('hidden_register_or_stack_contract')
        if per_codes['C2653']: group.append('qualified_class_declaration')
        win_names = {'LPCRITICAL_SECTION','LPCSTR','LPCWSTR','LPVOID','DWORD','LPTIME_ZONE_INFORMATION','EnterCriticalSection','LeaveCriticalSection','WideCharToMultiByte','Sleep','SetLastError','GetTimeZoneInformation'}
        if set(names)&win_names: group.append('platform_type_or_import_declaration')
        if set(names)&{'RTTI_Type_Descriptor','ROUND','SQRT','uchar','NAN','INFINITY'}: group.append('decompiler_type_or_intrinsic_vocabulary')
        for name in group: categories[name].append(va)
        row = dict(va=va, inferred_calling_convention=cc, inferred_signature=d.get('inferred_signature'), extra_pop=d.get('extra_pop'),
                   noreturn=d.get('noreturn'), varargs=d.get('varargs'), this_pointer=d.get('this_pointer'), return_storage=d.get('return_storage'),
                   parameter_storage=[dict(name=p.get('name'),bytes=p['type']['length'],storage=p.get('storage'),this=p.get('this')) for p in d.get('parameters',[])],
                   original_catalog_bytes=data['catalog'][va].get('body_bytes'), original_catalog_ranges=data['catalog'][va].get('ranges'),
                   syntax_passed=old.get('syntax_passed'), error_codes=dict(per_codes), error_categories=dict(cats), source_patterns=hits,
                   missing_global_names=missing_globals, exact_scoped179_names=matching, leading_underscore_formal_candidates=alias,
                   compatible184_declaration_names=compatible, unsupported184_declaration_names=incompatible,
                   local_ret_evidence=data['local_ret_evidence'][va],
                   source=relative(source), source_sha256=old['generated_source_sha256'], groups=group,
                   diagnostics=errors, declaration_header=old.get('declaration_header'), scalar_slice_header=old.get('scalar_slice_header'),
                   logs={k:old[k] for k in ('batch_log','compiler_log','batch_id','log_sha256','compiler_command') if k in old})
        row['diagnostic_record'] = data['current_audit']+'#/results[va='+va+']'
        row['raw_log_candidates'] = [relative(path) for path in {source.with_suffix('.log'),Path(old.get('baseline_generated_source',old['generated_source'])).with_suffix('.log')} if path.exists()]
        row['source_excerpt'] = [dict(line=n,text=line.strip()) for n,line in enumerate(source.read_text(encoding='utf8').splitlines(),1)
                                 if any(name in line for name in missing_globals) or re.search(r'\._\d+_\d+_|\b__thiscall\b|\b(?:ROUND|SQRT|RTTI_Type_Descriptor)\b|\b\w+::',line)][:8]
        rows.append(row)
    only_globals = [r for r in rows if r['missing_global_names'] and set(r['error_codes']) <= {'C2065','C3861'}
                    and len(r['missing_global_names'])==len(r['compatible184_declaration_names'])
                    and all(re.match(r'^_?(?:DAT|PTR|LAB|s_|u_)[A-Za-z0-9_]*:',d['message']) for d in r['diagnostics'])]
    coverage194 = []
    for c in data['proofs']['194']['cases']:
        target = next((r for r in rows if r['va']==c['va'] and c['alias'] in r['missing_global_names']),None)
        if target: coverage194.append(dict(va=c['va'],alias=c['alias'],classification=c['classification'],
            token_ram_width_agrees=c.get('token_ram_width_agrees'),acceptance=c.get('acceptance'),evidence_path=data['proof_paths']['194']))
    report = dict(schema=1, original_sha256=SHA, frontier_summary=data['frontier_summary'], current_audit=data['current_audit'],
                  current_audit_sha256=data['current_audit_sha256'], target_missing_body_vas=len(rows), canonical_owner_reference_only=36,
                  calling_conventions=dict(counts), error_diagnostic_codes=dict(codes.most_common()), functions_by_error_code=dict(code_functions.most_common()),
                  functions_by_source_pattern=dict(source_patterns.most_common()), groups={k:dict(functions=len(v),vas=sorted(v)) for k,v in categories.items()},
                  missing_global_names=dict(missing_names.most_common()), rows=rows,
                  complete_error_surface_184_declaration_candidates=[r['va'] for r in only_globals],
                  exact194_consumer_alias_coverage=coverage194,
                  known196_target_overlap=sorted(set(r['va'] for r in rows)&set(r['va'] for r in data['proofs']['196']['results'] if r['compiled'])),
                  known197_target_overlap=sorted(set(r['va'] for r in rows)&set(r['va'] for r in data['proofs']['197']['results'] if r['compiled'])),
                  clean_declaration_pilot_vas=[r['va'] for r in only_globals if 'partial_scalar' not in r['source_patterns']],
                  latent_partial_scalar_in_declaration_candidates=[r['va'] for r in only_globals if 'partial_scalar' in r['source_patterns']],
                  canonical_owner_references=[dict(va=r['va'],symbol=r['symbol'],canonical_owners=r['canonical_owners']) for r in data['canonical_reference_only']],
                  input_sha256={**data['input_sha256'], relative(Path(__file__)):sha(Path(__file__)), relative(OUT/'selected-inputs.json'):sha(OUT/'selected-inputs.json')},
                  full_audit_read_count=1, compiler_commands=0, ghidra_commands=0,
                  extra_pop_counts=dict(Counter(str(r['extra_pop']) for r in rows)), noreturn_counts=dict(Counter(str(r['noreturn']) for r in rows)),
                  local_ret_pop_sets=dict(Counter(','.join(map(str,sorted({s['stack_pop'] for s in r['local_ret_evidence']['local_ret_sites']}))) or 'no_local_RET' for r in rows)),
                  boundary='Exactly109 no-owner missing bodies in199 dependency frontier; overlapping compiler/source-pattern groups, not independent fix counts or full-game estimate.')
    write(OUT/'diagnostics.json', report)
    if not args.capture_only:
        report['recommended_fix_classes'] = [
            dict(rank=1,name='exact_consumer179_extern_declaration_delta',current_surface_functions=73,compatible_some_names_functions=sum(bool(r['compatible184_declaration_names']) for r in rows),
                 complete_current_error_surface_functions=len(only_globals),clean_first_pilot_functions=len(report['clean_declaration_pilot_vas']),
                 evidence=['Run179 per-function globals type/storage/declarator','Run184 exact native layout/declaration resolver','Run196 consumer-specific variant mechanism'],
                 next='Only the25 clean listed TUs: per-TU externs from exact179 metadata, no storage; compile changed TUs once in a later assigned packet.27 names-only surfaces include two latent partial-scalar users. No successful compilation is predicted as fact.'),
            dict(rank=2,name='caller_prototype_and_qualified_call_contracts',functions=len(categories['caller_prototype_or_type_contract']),
                 invalid_thiscall_declaration_functions=len(categories['thiscall_declaration_or_definition']),qualified_class_functions=len(categories['qualified_class_declaration']),
                 evidence=['Actual C2660/C2664/C2197 diagnostics and source lines','Run179 inferred signatures are navigation only','Run197 exact ECX/stack/RET/output evidence is a method, with zero directly covered target VAs'],
                 next='Choose a repeated callee signature from these61 caller rows; trace actual CALL setup/RET/output before changing declarations or qualified calls. No bulk cdecl/thiscall substitution.'),
            dict(rank=3,name='printed_global_access_alias_extension',functions=sum(bool(r['leading_underscore_formal_candidates']) for r in rows),
                 exact_proven_alias_pairs=sum(bool(r['token_ram_width_agrees']) for r in coverage194),exact_proven_target_functions=len({r['va'] for r in coverage194 if r['token_ram_width_agrees']}),
                 evidence=['Run194 two exact target address/width pairs','Run194 register-varnode alias00655a0c remains unproved','Same alias spelling at other consumers is not a reusable consumer proof'],
                 next='Apply only two frozen194 per-consumer access views in a separate candidate packet, preserving representation gaps; extend token/raw-instruction evidence before handling other19 alias consumers.')]
        report['input_sha256'][relative(ROOT/'scripts/research/experiment-v2-declarations-184.py')]=sha(ROOT/'scripts/research/experiment-v2-declarations-184.py')
        if (RUN/'README.md').exists(): report['input_sha256'][relative(RUN/'README.md')]=sha(RUN/'README.md')
        write(RUN/'summary.json',report)
    print(json.dumps({key:report[key] for key in ('calling_conventions','functions_by_error_code','functions_by_source_pattern','groups')}, indent=2))


if __name__ == '__main__': main()
