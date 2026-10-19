"""Check selective PR intake, fresh native receipts and the actual game graph."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re

from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '310-pr-intake-integration'
BUILD = ROOT / 'local/builds/v2/pr-intake-310'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_bytes())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def receipt(value):
    assert value['exit_code'] == 0, value
    assert sha(ROOT / value['log']) == value['log_sha256']
    if 'output' in value:
        assert sha(ROOT / value['output']) == value['output_sha256']


def main():
    reader = ManifestReader(ROOT)
    native = load(RUN / 'native-002.json')
    reader.verify(native, 'source', expected_hash_mode='crlf-to-lf')
    assert native['source_count'] == 21 and native['source_unchanged']
    assert native['native_cases'] == 5 and native['assertions'] == 18
    assert native['native_vas'] == ['00412030', '00425780']
    assert len(native['untested_native_vas']) == 19 and native['production_data_providers'] == 0
    for r in native['receipts']:
        receipt(r)
    for p, expected in native['tool_sha256'].items():
        assert sha(p) == expected
    for item in native['objects'].values():
        assert sha(ROOT / item['path']) == item['sha256']

    helper = load(RUNS / '311-pr4-shutdown-helpers/summary.json')
    for key in ('source', 'header', 'verifier'):
        assert sha(ROOT / helper[key]) == helper[key + '_sha256']
    helper_path = ROOT / helper['native_attempt']
    assert sha(helper_path) == helper['native_attempt_sha256']
    hn = load(helper_path)
    assert hn['status'] == helper['native_status'] == 'native-pass'
    assert hn['native_cases_passed'] == helper['native_cases_passed'] == 5
    assert helper['new_game_data_definitions'] == 0
    for p, expected in hn['input_sha256'].items():
        assert sha(ROOT / p) == expected
    for name, expected in hn['toolchain_sha256'].items():
        assert sha(hn['toolchain_paths'][name]) == expected
    for r in hn['receipts'].values():
        receipt(r)

    pe = module('pe310', ROOT / 'scripts/research/audit-v2-frame-service-290.py')
    image = (ROOT / 'local/game/Porsche.exe').read_bytes()
    assert hashlib.sha256(image).hexdigest() == native['original_sha256'] == helper['original_sha256']
    for va, data in native['original_body_hex'].items():
        assert pe.pe_read(image, int(va, 16), len(bytes.fromhex(data))).hex() == data

    s = load(RUN / 'build-002.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    previous = load(RUNS / '309-disk-slot-game-integration/build-001.json')
    assert s['source_manifest'] == previous['source_manifest'] and s['source_delta']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 161 and len(s['project_paths']) == 8
    assert s['unresolved_names'] == 268 and s['unresolved_references'] == 304
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    rp = ROOT / s['receipt']
    assert sha(rp) == s['receipt_sha256']
    r = load(rp)
    assert r['exit_code'] == 1 and sha(ROOT / r['log']) == r['log_sha256']
    log = (ROOT / r['log']).read_text(encoding='utf8')
    printed = collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log))
    assert printed == collections.Counter(Path(p).name for p in s['compiled_source_roots'])
    added = set(s['compiled_source_roots']) - set(previous['compiled_source_roots'])
    assert {Path(p).name for p in added} == {'00412030.cpp', '00425780.cpp', 'shutdown_helpers_311.cpp'}
    assert not set(previous['compiled_source_roots']) - set(s['compiled_source_roots'])
    assert not any('fixture' in p or 'original-body' in p for p in s['compiled_source_roots'])
    old = {x['symbol'] for x in previous['frontier']}
    new = {x['symbol'] for x in s['frontier']}
    closed = {f'?application_main_function_{va}@porsche@@YAXXZ'
              for va in ('00412030', '00425780', '004a54b0', '004a54e0')}
    assert old - new == closed and len(new - old) == 8
    coff = module('coff310', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    fresh_objects = {}
    for name in ('00412030', '00425780', 'shutdown_helpers_311'):
        objects = list(BUILD.glob(f'**/porsche_game_entry_bridges.dir/Release/{name}.obj'))
        assert len(objects) == 1
        view = coff.coff_symbols(objects[0])
        assert not view['common'] and not view['weak']
        # Current MSVC headers emit a CRT COMDAT flag, unrelated to game storage.
        assert all(symbol.startswith('?application_main_function_') or
                   symbol == '__Avx2WmemEnabledWeakValue' for symbol in view['defined'])
        fresh_objects[name] = dict(path=objects[0].relative_to(ROOT).as_posix(),
                                   sha256=sha(objects[0]), symbols=view)
    defined = set().union(*(set(x['symbols']['defined']) for x in fresh_objects.values()))
    assert defined - {'__Avx2WmemEnabledWeakValue'} == closed
    assert not list(BUILD.glob('**/porsche_original_game_link.exe'))
    reader.cache.check_stable()
    result = dict(schema=1, passed=True, native_cases=10, original_bytes=275,
                  compiled_pr3_sources=21, integrated_functions=4, game_sources=161,
                  build_report_sha256=sha(RUN / 'build-002.json'),
                  native310_sha256=sha(RUN / 'native-002.json'),
                  helper311_sha256=sha(RUNS / '311-pr4-shutdown-helpers/summary.json'),
                  source_pins=len(pins), closed_names=sorted(closed), new_names=sorted(new-old),
                  unresolved_names=268, unresolved_references=304,
                  fresh_objects=fresh_objects, game_executed=False)
    output = RUN / 'validation.json'
    if output.exists():
        assert load(output) == result, 'Completed audit changed'
    else:
        output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps({key: result[key] for key in (
        'passed', 'native_cases', 'integrated_functions', 'game_sources',
        'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
