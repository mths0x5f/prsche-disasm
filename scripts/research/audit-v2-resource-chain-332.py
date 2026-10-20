"""Batch audit of REA333, native329/331, existing search proof and game332."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '332-resource-chain-game-integration'
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
    rea = module('rea333', ROOT / 'scripts/research/audit-v2-rea-session.py').audit(
        RUNS / '333-rea-resource-followup/queries.json', '001', cache, sha)
    assert rea == load(RUNS / '333-rea-resource-followup/validation.json')
    packets = {}
    for name, cases in [('329-resource-constructor', 13824), ('331-drive-letter', 6912)]:
        run = RUNS / name
        s = load(run / 'summary.json')
        attempt = ROOT / s.get('native_attempt', s.get('native_attemptdir'))
        assert sha(attempt / 'receipt.json') == s['native_receipt_sha256']
        r = load(attempt / 'receipt.json')
        assert r['native_cases_passed'] == s['native_cases_passed'] == cases
        for source, expected in s['source_sha256'].items():
            path = run / source if '/' not in source else ROOT / source
            assert sha(path) == expected, source
        for field in ('inputs_sha256', 'tools_sha256', 'link_libraries_sha256', 'compiler_dependencies_sha256'):
            for path, expected in r.get(field, {}).items():
                assert sha(ROOT / path) == expected, (name, field, path)
        for path, expected in r.get('objects_sha256', {}).items():
            assert sha(attempt / path) == expected
        for path, expected in r.get('outputs_sha256', {}).items():
            assert sha(ROOT / path) == expected
        if 'exe_sha256' in r:
            assert sha(attempt / 'fixture.exe') == r['exe_sha256']
        for command in r.get('commands', []):
            assert command['exit_code'] == 0
            assert sha(attempt / command['log']) == command['log_sha256']
        negative = {n['name'] + '-native': n.get('exit_code') for n in r['negative_controls']}
        assert len(negative) == 3 and all(n['detected'] for n in r['negative_controls'])
        for label, command in r.get('receipts', {}).items():
            assert sha(ROOT / command['log']) == command['log_sha256']
            assert command['exit_code'] == negative.get(label, 0)
        if name.startswith('329'):
            assert r['native_checks'] == 124431 and r['negative_controls_detected'] == 3
            assert 'cases=13824 checks=124431 failures=0 negative_controls=3/3' in cache.data(attempt / 'native.log').decode()
        else:
            assert 'cases=6912 failures=0' in cache.data(attempt / 'native.log').decode()
        cross = s['rea333_cross_review']
        path = ROOT / cross['path'] if isinstance(cross, dict) else run / cross
        expected_cross = cross['sha256'] if isinstance(cross, dict) else s['rea333_cross_review_sha256']
        assert sha(path) == expected_cross
        packets[name] = dict(cases=cases, summary_sha256=sha(run / 'summary.json'),
                             receipt_sha256=s['native_receipt_sha256'])
    search = load(RUNS / '330-canonical-search-intake/summary.json')
    for field in ('inputs_sha256', 'outputs_sha256'):
        for path, expected in search[field].items():
            assert sha(ROOT / path) == expected, ('search', path)
    assert search['new_recovered_vas'] == 0 and search['new_data_providers'] == 0
    assert not search['game_graph_modified']
    for proof in search['reused_172_proof']:
        p = load(ROOT / proof['path'])
        assert sha(ROOT / proof['path']) == proof['sha256']
        assert p['native_cpp_equal_original_x86'] and p['cases'] == 9374
        for path, expected in p['source_sha256'].items():
            assert reader.cache.digest(ROOT / path) == expected, ('search normalized source', path)
    s = load(RUN / 'build-001.json')
    old = load(RUNS / '328-resource-device-game-integration/build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    assert s['source_manifest'] == old['source_manifest']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 171 and len(s['project_paths']) == 8
    assert (s['unresolved_names'], s['unresolved_references']) == (261, 286)
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    new_sources = {f'iterations/v2/001-original-recovery/runs/{r}/{file}' for r, file in [
        ('329-resource-constructor', 'resource_constructor_329.cpp'),
        ('331-drive-letter', 'drive_letter_331.cpp')]}
    new_sources.add(search['canonical_source'])
    assert set(s['compiled_source_roots']) - set(old['compiled_source_roots']) == new_sources
    assert set(old['compiled_source_roots']) <= set(s['compiled_source_roots'])
    assert not any('fixture' in p or '421-' in p or '422-' in p for p in s['compiled_source_roots'])
    assert sha(ROOT / s['receipt']) == s['receipt_sha256']
    receipt = load(ROOT / s['receipt'])
    assert receipt['exit_code'] == 1 and sha(ROOT / receipt['log']) == receipt['log_sha256']
    log = cache.data(ROOT / receipt['log']).decode('utf8')
    assert collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log)) == collections.Counter(
        Path(p).name for p in s['compiled_source_roots'])
    before, after = ({x['symbol'] for x in v['frontier']} for v in (old, s))
    closed = {'?request_exists_00568260@porsche@@YAIPBDIPAX@Z', '?resource_drive_letter_005916a0@porsche@@YAEPBD@Z',
              '?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z'}
    assert before - after == closed and not after - before
    build = ROOT / 'local/builds/v2/resource-chain-game-integration-332'
    coff = module('coff332', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    symbols = {}
    for stem, packet in [('resource_constructor_329', '329-resource-constructor'), ('drive_letter_331', '331-drive-letter'), ('formatter_search', '330-canonical-search-intake')]:
        objects = list(build.glob('**/porsche_game_entry_bridges.dir/Release/' + stem + '.obj'))
        assert len(objects) == 1
        view = coff.coff_symbols(objects[0])
        summary = load(RUNS / packet / 'summary.json')
        expected = summary.get('coff_symbols', dict(defined=summary.get('game_object_defined'), undefined=summary.get('game_object_undefined')))
        extra_defined = {'??_C@_01LFCBOECM@?4@'} if stem == 'drive_letter_331' else set()
        extra_undefined = {'@__security_check_cookie@4', '___security_cookie'} if stem == 'drive_letter_331' else set()
        assert set(view['defined']) == set(expected['defined']) | extra_defined
        assert set(view['undefined']) == set(expected['undefined']) | extra_undefined
        symbols[stem] = dict(sha256=sha(objects[0]), **view)
    graph = module('graph332', ROOT / 'scripts/research/v2_build_graph.py')
    entry = list(build.glob('**/porsche_original_game_link.vcxproj'))
    assert len(entry) == 1
    assert graph.compiled_sources(entry[0].parent, 'porsche_original_game_link') == s['compiled_source_roots']
    assert not list(build.glob('**/porsche_original_game_link.exe'))
    cache.check_stable()
    result = dict(schema=1, passed=True, rea_receipt_sha256=rea['receipt_sha256'], packets=packets,
                  native_cases=20736, original_functions=2, indexed_body_bytes=162, canonical_search_reused_functions=3,
                  game_sources=171, source_pins=len(pins), unresolved_names=261,
                  unresolved_references=286, closed_names=sorted(closed), new_names=[],
                  search_packet_sha256=sha(RUNS / '330-canonical-search-intake/summary.json'),
                  game_executed=False, build_report_sha256=sha(RUN / 'build-001.json'), objects=symbols)
    target = RUN / 'validation.json'
    if target.exists():
        assert load(target) == result, 'Completed audit changed'
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'native_cases', 'game_sources', 'source_pins', 'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
