"""Read-only198 native-union provenance/link-parser audit; no tool execution."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
report = json.loads((RUN/'summary.json').read_bytes())
validation = json.loads((RUN/'validation.json').read_bytes())
assert validation['summary_sha256'] == sha(RUN/'summary.json')
script = ROOT/'scripts/research/audit-v2-native-union-198.py'
assert sha(script) == validation['script_sha256']


def verify(item):
    name, expected = item; path = Path(name) if Path(name).is_absolute() else ROOT/name
    assert sha(path) == expected, ('input mutation', name)


with ThreadPoolExecutor(max_workers=8) as pool: list(pool.map(verify, report['input_sha256'].items()))
assert report['objects'] == report['ordinary_objects']+report['thiscall_objects'] == 1070
assert report['ordinary_objects'] == 924 and report['thiscall_objects'] == 146
assert len({r['va'] for r in report['results']}) == 1070
assert report['new_compilations'] == report['overlapping_vas'] == 0
assert report['symbol_snapshot_cache_reused'] == 1054 and report['actual_symbol_objects_reread'] == 16
assert report['platform_library_pins_reused'] == 531 and report['platform_library_pins_new'] == 0
assert report['actual_library_commands_this_pass'] == report['actual_link_commands_this_pass'] == 0
assert report['captured_library_commands'] == report['captured_link_commands'] == 1
assert report['library']['members'] == 1070 and report['library']['exit_code'] == 0
assert sha(ROOT/report['library']['path']) == report['library']['sha256']
assert sha(ROOT/report['objects_response']['path']) == report['objects_response']['sha256']
for tool in (report['library'], report['diagnostic_link']): assert sha(ROOT/tool['log']) == tool['log_sha256']
capture = json.loads((ROOT/report['captured_summary']).read_bytes())
assert capture['library'] == report['library']
assert capture['objects_response'] == report['objects_response']
for key in ('command', 'exit_code', 'log', 'log_sha256'): assert capture['diagnostic_link'][key] == report['diagnostic_link'][key]
capture_chain = 1
while capture.get('captured_summary'):
    capture = json.loads((ROOT/capture['captured_summary']).read_bytes()); capture_chain += 1
    assert capture['library'] == report['library'] and capture['objects_response'] == report['objects_response']
    for key in ('command', 'exit_code', 'log', 'log_sha256'): assert capture['diagnostic_link'][key] == report['diagnostic_link'][key]
assert capture['actual_library_commands_this_pass'] == capture['actual_link_commands_this_pass'] == 1
assert not (ROOT/report['library']['path']).with_name('diagnostic_union.dll').exists()
definitions = set(); references = {}
for row in report['results']:
    definitions.update(row['symbols']['defined']+row['symbols']['common'])
    for name in row['symbols']['undefined']: references.setdefault(name, set()).add(row['va'])
raw = {name: vas for name, vas in references.items() if name not in definitions}
assert len(raw) == report['raw_union_unresolved_names'] == 403
assert sum(map(len, raw.values())) == report['raw_union_object_references'] == 780
frontier = {r['symbol']: r for r in report['frontier']}; assert set(frontier) == set(raw)
assert Counter(r['category'] for r in frontier.values()) == report['categories'] == {'data': 241, 'function': 145, 'other': 17}
for name, row in frontier.items():
    assert row['referring_object_vas'] == sorted(raw[name])
    if '?PTR_FUN_' in name: assert row['category'] == 'data'
link = report['diagnostic_link']; log = (ROOT/link['log']).read_text(encoding='utf8')
assert int(re.findall(r'(?m)^.*\bLNK1120:.*?(\d+)\s*$', log)[-1]) == len(link['unresolved_symbols']) == 393
assert sum(link['unresolved_symbols'].values()) == link['diagnostic_occurrences'] == 581
assert not link['names_outside_raw_union'] and len(link['raw_union_names_resolved_by_platform_libraries']) == 10
delta = report['delta_from_baseline']
assert delta['old_raw_unresolved_names'] == 387 and delta['old_link_unresolved_names'] == 377
assert len(delta['added_object_vas']) == len(delta['raw_names_added']) == len(delta['link_names_added']) == 16
assert not delta['raw_names_removed'] and not delta['link_names_removed'] and not delta['removed_object_vas']
assert all(frontier[name]['category'] == 'data' for name in delta['raw_names_added'])
pilot_path = RUN/'cli-validation.json'; pilot = json.loads(pilot_path.read_bytes())
assert pilot['script_sha256'] == sha(script) and pilot['overlap_rejected'] and pilot['compiled_overlap_vas'] == 146
assert pilot['archive_link_commands'] == 0 and pilot['exit_code'] != 0
assert sha(ROOT/pilot['fixture']) == pilot['fixture_sha256'] == pilot['fixture_source_sha256']
assert sha(ROOT/pilot['log']) == pilot['log_sha256']
for p in (script, Path(__file__), RUN/'README.md', RUN/'summary.json', RUN/'validation.json', ROOT/report['objects_response']['path'], ROOT/report['library']['log'], ROOT/link['log']):
    assert b'\r' not in p.read_bytes(), ('new artifact not LF', p)
validation.update(read_only_audit_source_sha256=sha(Path(__file__)), readme_sha256=sha(RUN/'README.md'),
                  input_pins_rechecked=True, archive_capture_provenance_pass=True, parser_only_finalization_pass=True,
                  exact_raw_frontier_pass=True, exact_localized_link_frontier_pass=True, exact_195_delta_pass=True,
                  canonical_function_frontier_unchanged=True, ptr_fun_stays_data=True, capture_chain_reports=capture_chain,
                  cli_validation_sha256=sha(pilot_path), repeated_packet_overlap_rejected=True)
(RUN/'validation.json').write_text(json.dumps(validation, indent=2)+'\n', encoding='utf8', newline='\n')
print(json.dumps({k: v for k, v in validation.items() if k not in ('readme_sha256', 'script_sha256', 'read_only_audit_source_sha256')}, indent=2))
