"""Read-only native evidence and fresh game-graph audit for scalar fill."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '318-scalar-fill-game-integration'
reader = ManifestReader(ROOT)
cache = reader.cache
hashes = {}


def sha(path):
    path = Path(path).resolve()
    if path not in hashes:
        hashes[path] = hashlib.sha256(cache.data(path)).hexdigest()
    return hashes[path]


def load(path):
    return cache.document(path)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    packet = RUNS / '317-scalar-fill-backend'
    p = load(packet / 'summary.json')
    work = ROOT / p['native_attempt']
    assert sha(work / 'receipt.json') == p['native_receipt_sha256']
    n = load(work / 'receipt.json')
    assert n['status'] == p['native_status'] == 'pass'
    assert n['native_cases_passed'] == p['native_cases_passed'] == 1296
    assert n['native_checks'] == p['native_checks'] == 9075
    for name, expected in p['source_sha256'].items():
        assert sha(packet / name) == expected
    for name, expected in n['inputs_sha256'].items():
        path = ROOT / name
        if not path.exists():
            path = work / name
        assert sha(path) == expected, name
    for group in ('tools_sha256', 'link_libraries_sha256'):
        for name, expected in n[group].items():
            assert sha(ROOT / name) == expected
    for name, expected in n['objects_sha256'].items():
        assert sha(work / name) == expected
    for cmd in n['commands']:
        assert cmd['exit_code'] == 0 and sha(work / cmd['log']) == cmd['log_sha256']
    assert sha(work / 'fixture.exe') == n['exe_sha256'] == p['native_executable_sha256']
    pe = module('pe318', ROOT / 'scripts/research/audit-v2-frame-service-290.py')
    image = cache.data(ROOT / 'local/game/Porsche.exe')
    assert hashlib.sha256(image).hexdigest() == p['original_sha256']
    span = pe.pe_read(image, 0x5b0980, 186)
    assert span == cache.data(work / 'original-span-005b0980.bin')
    assert span[30:32] == bytes.fromhex(p['gap_bytes_hex']) == b'\x8b\xff'
    assert hashlib.sha256(span).hexdigest() == p['original_span_sha256']
    assert span[:30] == cache.data(work / 'original-range1.bin')
    assert span[32:] == cache.data(work / 'original-range2.bin')

    s = load(RUN / 'build-001.json')
    old = load(RUNS / '314-pr7-pr9-game-integration/build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    assert s['source_manifest'] == old['source_manifest'] and s['source_delta']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 164 and len(s['project_paths']) == 8
    assert s['unresolved_names'] == 268 and s['unresolved_references'] == 297
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    assert sha(ROOT / s['receipt']) == s['receipt_sha256']
    receipt = load(ROOT / s['receipt'])
    assert receipt['exit_code'] == 1 and sha(ROOT / receipt['log']) == receipt['log_sha256']
    log = cache.data(ROOT / receipt['log']).decode('utf8')
    assert collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log)) == collections.Counter(
        Path(x).name for x in s['compiled_source_roots'])
    assert set(s['compiled_source_roots']) - set(old['compiled_source_roots']) == {
        (packet / '005b0980.cpp').relative_to(ROOT).as_posix()}
    assert not set(old['compiled_source_roots']) - set(s['compiled_source_roots'])
    assert not any('fixture' in x or 'original-body' in x for x in s['compiled_source_roots'])
    before, after = ({x['symbol'] for x in item['frontier']} for item in (old, s))
    closed = {'?heap_fill_scalar_005b0980@porsche@@YAXPAXII@Z'}
    assert before - after == closed and not after - before
    build = ROOT / 'local/builds/v2/scalar-fill-game-integration-318'
    objects = list(build.glob('**/porsche_game_entry_bridges.dir/Release/005b0980.obj'))
    assert len(objects) == 1
    coff = module('coff318', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    view = coff.coff_symbols(objects[0])
    assert not view['common'] and not view['weak'] and not view['undefined']
    assert set(view['defined']) - {'__Avx2WmemEnabledWeakValue'} == closed | {
        '?heap_fill_scalar_005b0980_core@porsche@@YAPAXPAXII@Z'}
    assert not list(build.glob('**/porsche_original_game_link.exe'))
    cache.check_stable()
    result = dict(schema=1, passed=True, native_cases=1296, native_checks=9075,
                  original_function_count=1, original_indexed_bytes=184, original_span_bytes=186,
                  native_scope='16 alignments, 27 lengths in 0..129, three DWORD patterns; memory/EAX/ABI',
                  closed_names=sorted(closed), new_names=[], game_sources=164, source_pins=len(pins),
                  unresolved_names=268, unresolved_references=297, game_executed=False,
                  build_report_sha256=sha(RUN / 'build-001.json'),
                  packet317_sha256=sha(packet / 'summary.json'),
                  object_path=objects[0].relative_to(ROOT).as_posix(),
                  object_sha256=sha(objects[0]), symbols=view)
    output = RUN / 'validation.json'
    if output.exists():
        assert load(output) == result, 'Completed audit changed'
    else:
        output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'native_cases', 'game_sources', 'source_pins',
                                           'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
