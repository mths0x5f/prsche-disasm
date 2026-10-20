"""Batch audit of REA325, native326/327 and the actual game328 build."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '328-resource-device-game-integration'
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
    rea = module('rea325', ROOT / 'scripts/research/audit-v2-rea-resource-325.py').audit(cache)
    assert rea == load(RUNS / '325-rea-resource-session/validation.json')
    packets = {}
    for name, cases in [('326-resource-exists', 9216), ('327-resource-open-callback-evidence', 10240)]:
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
        for label, command in r.get('receipts', {}).items():
            assert sha(ROOT / command['log']) == command['log_sha256']
            assert command['exit_code'] == (12 if label == 'route-ignores-separator-native' else
                                            10 if label in ('prefix-truncates-EAX-native', 'prefix-off-by-one-native') else 0)
        if name.startswith('326'):
            assert r['native_checks'] == 175117
            assert 'cases=9216 checks=175117 failures=0' in cache.data(attempt / 'native.log').decode()
            cross = load(run / s['rea_cross_review'])
            assert sha(run / s['rea_cross_review']) == s['rea_cross_review_sha256']
        else:
            assert len(s['negative_controls']) == 3 and all(x['detected'] for x in s['negative_controls'])
            assert 'cases=10240 failures=0' in cache.data(attempt / 'native.log').decode()
        packets[name] = dict(cases=cases, summary_sha256=sha(run / 'summary.json'),
                             receipt_sha256=s['native_receipt_sha256'])
    s = load(RUN / 'build-001.json')
    old = load(RUNS / '324-input-modes-game-integration/build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    assert s['source_manifest'] == old['source_manifest']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 168 and len(s['project_paths']) == 8
    assert (s['unresolved_names'], s['unresolved_references']) == (264, 289)
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    new_sources = {f'iterations/v2/001-original-recovery/runs/{r}/{file}' for r, file in [
        ('326-resource-exists', 'resource_exists_326.cpp'),
        ('327-resource-open-callback-evidence', 'resource_device_327.cpp')]}
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
    closed = {'?file_exists_00561b80@porsche@@YAHPBD@Z', '?file_device_name_00568e90@porsche@@YAIPBD@Z',
              '?disk_path_device_00591760@porsche@@YAEPBD@Z'}
    exposed = {'?request_exists_00568260@porsche@@YAIPBDIPAX@Z', '?resource_drive_letter_005916a0@porsche@@YAEPBD@Z',
               '?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z'}
    assert before - after == closed and after - before == exposed
    build = ROOT / 'local/builds/v2/resource-device-game-integration-328'
    coff = module('coff328', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    symbols = {}
    for stem, packet in [('resource_exists_326', '326-resource-exists'), ('resource_device_327', '327-resource-open-callback-evidence')]:
        objects = list(build.glob('**/porsche_game_entry_bridges.dir/Release/' + stem + '.obj'))
        assert len(objects) == 1
        view = coff.coff_symbols(objects[0])
        summary = load(RUNS / packet / 'summary.json')
        expected = summary.get('coff_symbols', dict(defined=summary.get('game_object_defined'), undefined=summary.get('game_object_undefined')))
        assert set(view['defined']) == set(expected['defined'])
        assert set(view['undefined']) == set(expected['undefined'])
        symbols[stem] = dict(sha256=sha(objects[0]), **view)
    graph = module('graph328', ROOT / 'scripts/research/v2_build_graph.py')
    entry = list(build.glob('**/porsche_original_game_link.vcxproj'))
    assert len(entry) == 1
    assert graph.compiled_sources(entry[0].parent, 'porsche_original_game_link') == s['compiled_source_roots']
    assert not list(build.glob('**/porsche_original_game_link.exe'))
    cache.check_stable()
    result = dict(schema=1, passed=True, rea_receipt_sha256=rea['receipt_sha256'], packets=packets,
                  native_cases=19456, original_functions=4, indexed_body_bytes=134,
                  game_sources=168, source_pins=len(pins), unresolved_names=264,
                  unresolved_references=289, closed_names=sorted(closed), new_names=sorted(exposed),
                  game_executed=False, build_report_sha256=sha(RUN / 'build-001.json'), objects=symbols)
    target = RUN / 'validation.json'
    if target.exists():
        assert load(target) == result, 'Completed audit changed'
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'native_cases', 'game_sources', 'source_pins', 'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
