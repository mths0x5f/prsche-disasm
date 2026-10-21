"""Batch audit of original open334, storage evidence336 and game335."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '335-resource-open-game-integration'
reader = ManifestReader(ROOT)
cache = reader.cache
hashes = {}


def sha(path):
    path = Path(path).resolve()
    if path not in hashes:
        hashes[path] = hashlib.sha256(cache.data(path)).hexdigest()
    return hashes[path]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    load = cache.document
    rea = module('rea325_for335', ROOT / 'scripts/research/audit-v2-rea-resource-325.py').audit(cache)
    assert rea == load(RUNS / '325-rea-resource-session/validation.json')
    packets = {}
    for folder, cases, mutations in [('334-resource-open', 60480, 6), ('338-search-abi-bindings', 816, 3)]:
        packet = RUNS / folder
        p = load(packet / 'summary.json')
        attempt = ROOT / p['native_attemptdir']
        assert sha(attempt / 'receipt.json') == p['native_receipt_sha256']
        r = load(attempt / 'receipt.json')
        assert r['native_cases_passed'] == p['native_cases_passed'] == cases
        for path, expected in p['source_sha256'].items():
            assert sha(ROOT / path) == expected, path
        for field in ('inputs_sha256', 'tools_sha256', 'link_libraries_sha256', 'compiler_dependencies_sha256', 'outputs_sha256'):
            for path, expected in r.get(field, {}).items():
                assert sha(ROOT / path) == expected, (field, path)
        negative = {n['name'] + '-native': n['exit_code'] for n in r['negative_controls']}
        assert len(negative) == mutations and all(n['detected'] for n in r['negative_controls'])
        for label, command in r['receipts'].items():
            assert sha(ROOT / command['log']) == command['log_sha256']
            assert command['exit_code'] == negative.get(label, 0), label
        if folder.startswith('334'):
            assert r['variants'] == ['/Od /Oy- /GS-', '/O2 /GS']
            assert r['native_cases_per_variant'] == 30240
            assert p['new_production_storage_definitions'] == 0
            for label in ('game-od-native', 'game-o2-native'):
                assert 'cases=30240 checks=151200 failures=0' in cache.data(ROOT / r['receipts'][label]['log']).decode()
        else:
            assert p['new_original_functions'] == 0
            assert 'cases=816 failures=0' in cache.data(ROOT / r['native']['log']).decode()
            proof = p['original_body_proof']
            assert sha(ROOT / proof['path']) == proof['sha256'] and not proof['rerun']
            previous = load(ROOT / proof['path'])
            assert previous['native_cpp_equal_original_x86'] and previous['cases'] == 9374
            for path, expected in previous['source_sha256'].items():
                assert cache.digest(ROOT / path) == expected
        packets[folder] = dict(cases=cases, summary_sha256=sha(packet / 'summary.json'), receipt_sha256=p['native_receipt_sha256'])
    storage = load(RUNS / '336-transform-cell-evidence/evidence.json')
    assert storage['production_storage_authorized'] is False
    assert storage['accepted_storage_owner'] is None and storage['proposed_production_provider'] is None
    assert not storage['complete_layout_proved'] and not storage['writer_coverage_complete']
    for path, expected in storage['input_sha256'].items():
        assert sha(ROOT / path) == expected, path
    triage = load(RUNS / '337-game-frontier-triage/summary.json')
    for path, expected in triage['inputs_sha256'].items():
        assert sha(ROOT / path) == expected, path
    assert not triage['native_rerun'] and not triage['game_graph_modified']
    s = load(RUN / 'build-001.json')
    old = load(RUNS / '332-resource-chain-game-integration/build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    assert s['source_manifest'] == old['source_manifest']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 173 and len(s['project_paths']) == 8
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    source = 'iterations/v2/001-original-recovery/runs/334-resource-open/resource_open_334.cpp'
    assert set(s['compiled_source_roots']) - set(old['compiled_source_roots']) == {source,
        'iterations/v2/001-original-recovery/runs/338-search-abi-bindings/search_bindings_338.cpp'}
    assert set(old['compiled_source_roots']) <= set(s['compiled_source_roots'])
    assert not any('fixture' in path or '421-' in path or '422-' in path for path in s['compiled_source_roots'])
    assert sha(ROOT / s['receipt']) == s['receipt_sha256']
    receipt = load(ROOT / s['receipt'])
    assert receipt['exit_code'] == 1 and sha(ROOT / receipt['log']) == receipt['log_sha256']
    log = cache.data(ROOT / receipt['log']).decode('utf8')
    assert collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log)) == collections.Counter(
        Path(path).name for path in s['compiled_source_roots'])
    before, after = ({x['symbol'] for x in v['frontier']} for v in (old, s))
    closed, exposed = before - after, after - before
    assert closed == {'?file_open_00561ca0@porsche@@YAPAXPBDI@Z', '?compare_005ae3c0@porsche@@YAHPBD0@Z',
                      '?render_settings_read_config_005a1e10@porsche@@YAHPADPBD@Z'}
    assert exposed == {'?resource_open_transform_006ad750@porsche@@3P6APAXPAXPBDI@ZA'}
    assert (s['unresolved_names'], s['unresolved_references']) == (259, 284)
    build = ROOT / 'local/builds/v2/resource-open-game-integration-335'
    coff = module('coff335', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    symbols = {}
    for stem, folder in [('resource_open_334', '334-resource-open'), ('search_bindings_338', '338-search-abi-bindings')]:
        objects = list(build.glob('**/porsche_game_entry_bridges.dir/Release/' + stem + '.obj'))
        assert len(objects) == 1
        view = coff.coff_symbols(objects[0])
        packet_symbols = load(RUNS / folder / 'summary.json')['coff_symbols']
        expected = packet_symbols['game-o2'] if stem == 'resource_open_334' else packet_symbols
        assert view == expected, (stem, view)
        assert not any('006ad750' in name for name in view['defined'])
        symbols[stem] = dict(sha256=sha(objects[0]), **view)
    graph = module('graph335', ROOT / 'scripts/research/v2_build_graph.py')
    entry = list(build.glob('**/porsche_original_game_link.vcxproj'))
    assert len(entry) == 1
    assert graph.compiled_sources(entry[0].parent, 'porsche_original_game_link') == s['compiled_source_roots']
    assert not list(build.glob('**/porsche_original_game_link.exe'))
    cache.check_stable()
    result = dict(schema=1, passed=True, rea_receipt_sha256=rea['receipt_sha256'],
                  native_cases=61296, open_native_cases=60480, binding_native_cases=816, packets=packets,
                  original_functions=2, indexed_body_bytes=339, new_original_functions_in_bindings=0, game_sources=173, source_pins=len(pins),
                  unresolved_names=s['unresolved_names'], unresolved_references=s['unresolved_references'],
                  closed_names=sorted(closed), new_names=sorted(exposed), game_executed=False,
                  build_report_sha256=sha(RUN / 'build-001.json'), objects=symbols, storage_evidence_sha256=sha(RUNS / '336-transform-cell-evidence/evidence.json'),
                  triage_sha256=sha(RUNS / '337-game-frontier-triage/summary.json'))
    target = RUN / 'validation.json'
    if target.exists():
        assert load(target) == result, 'Completed audit changed'
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'native_cases', 'game_sources', 'source_pins', 'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
