"""Read-only shared-cache audit of PR22 native/probe evidence and actual game build."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '324-input-modes-game-integration'
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
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    load = cache.document
    p = load(RUNS / '423-input-getstate-modes/summary.json')
    assert sha(ROOT / 'local/game/Porsche.exe') == p['original_sha256']
    for key in ('source', 'header', 'fixture', 'compiler'):
        assert sha(ROOT / p[key]) == p[key + '_sha256']
    out = ROOT / 'local/experiments/v2-input-getstate-423'
    for name, expected in load(out / 'prepare-001.json')['input_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for entry in (p['compile'], p['link'], p['native_fixture']['execution']):
        assert entry['exit_code'] == 0 and sha(ROOT / entry['log']) == entry['log_sha256']
    assert p['native_fixture']['cases'] == p['native_fixture']['cases_passed'] == 24
    probes = {}
    for name, count in [('input', 1026), ('input_snapshot', 13), ('input_buffer', 37), ('startup_input', 8)]:
        path = ROOT / 'local/experiments/pr22-review/snapshot/local/probes' / name
        result = load(path / 'report/verification.json')
        assert result['native_cpp_equal_original_x86'] and result['cases'] == count, name
        assert result['sha256'] == p['original_sha256']
        if isinstance(result.get('source_sha256'), dict):
            for source, expected in result['source_sha256'].items():
                assert sha(ROOT / source) == expected, source
        probes[name] = dict(cases=count, result_sha256=sha(path / 'report/verification.json'),
                            build_log_sha256=sha(path / 'build.log'), verify_log_sha256=sha(path / 'verify.log'))
    s = load(RUN / 'build-001.json')
    old = load(RUNS / '321-simd-fill-game-integration/build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    assert s['source_manifest'] == old['source_manifest']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 166 and len(s['project_paths']) == 8
    assert s['unresolved_names'] == 264 and s['unresolved_references'] == 293
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    assert s['compiled_source_roots'] == old['compiled_source_roots']
    assert not any('421-' in x or '422-' in x or 'fixture' in x for x in s['compiled_source_roots'])
    assert sha(ROOT / s['receipt']) == s['receipt_sha256']
    receipt = load(ROOT / s['receipt'])
    assert receipt['exit_code'] == 1 and sha(ROOT / receipt['log']) == receipt['log_sha256']
    log = cache.data(ROOT / receipt['log']).decode('utf8')
    assert collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log)) == collections.Counter(
        Path(x).name for x in s['compiled_source_roots'])
    before, after = ({x['symbol'] for x in item['frontier']} for item in (old, s))
    closed = {'?input_invalid_type_00532eae@porsche@@YAXI@Z',
              '?input_unrecovered_mode_00532e10@porsche@@YAPAXIIPAUInputSlot@1@@Z'}
    assert before - after == closed and not after - before
    build = ROOT / 'local/builds/v2/input-modes-game-integration-324'
    objects = list(build.glob('**/porsche_original.dir/Release/input_state.obj'))
    assert len(objects) == 1
    coff = module('coff324', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    view = coff.coff_symbols(objects[0])
    assert '?input_caps_buffer_006bde20@porsche@@3PAEA' in view['defined']
    assert not closed.intersection(view['undefined'])
    assert not list(build.glob('**/porsche_original_game_link.exe'))
    cache.check_stable()
    result = dict(schema=1, passed=True, native_cases=24, probes=probes, game_sources=166,
                  source_pins=len(pins), unresolved_names=264, unresolved_references=293,
                  closed_names=sorted(closed), new_names=[], game_executed=False,
                  build_report_sha256=sha(RUN / 'build-001.json'),
                  packet423_sha256=sha(RUNS / '423-input-getstate-modes/summary.json'),
                  object_sha256=sha(objects[0]), symbols=view)
    target = RUN / 'validation.json'
    if target.exists():
        assert load(target) == result, 'Completed audit changed'
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({key: result[key] for key in ('passed', 'native_cases', 'game_sources', 'source_pins', 'unresolved_names')}))


if __name__ == '__main__':
    main()
