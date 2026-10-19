"""Batch-check native PR7/PR9 evidence and the fresh actual game dependency graph."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '314-pr7-pr9-game-integration'
BUILD = ROOT / 'local/builds/v2/pr7-pr9-game-integration-314'
reader = ManifestReader(ROOT)
cache = reader.cache
raw_hashes = {}


def sha(path):
    path = Path(path).resolve()
    if path not in raw_hashes:
        raw_hashes[path] = hashlib.sha256(cache.data(path)).hexdigest()
    return raw_hashes[path]


def load(path):
    return cache.document(path)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    p312 = RUNS / '312-pr7-fill-dispatch'
    p313 = RUNS / '313-pr9-resource-open'
    a, b = load(p312 / 'summary.json'), load(p313 / 'summary.json')
    work = ROOT / a['native_attempt']
    assert sha(work / 'receipt.json') == a['native_receipt_sha256']
    n = load(work / 'receipt.json')
    assert n['status'] == a['native_status'] == 'pass'
    assert n['native_cases_passed'] == a['native_cases_passed'] == 28
    assert n['native_checks'] == a['native_checks'] == 211
    for name, expected in a['source_sha256'].items():
        assert sha(p312 / name) == expected
    for name, expected in n['inputs_sha256'].items():
        if re.match(r'^[a-f0-9]{40}:', name):
            assert hashlib.sha256(subprocess.check_output(['git', 'show', name], cwd=ROOT)).hexdigest() == expected
        else:
            path = ROOT / name
            if not path.exists():
                path = work / name
            assert sha(path) == expected, name
    for pins in (n['tools_sha256'], n['link_libraries_sha256']):
        for name, expected in pins.items():
            assert sha(ROOT / name) == expected
    for name, expected in n['objects_sha256'].items():
        assert sha(work / name) == expected
    for cmd in n['commands']:
        assert cmd['exit_code'] == 0 and sha(work / cmd['log']) == cmd['log_sha256']
    assert sha(work / 'fixture.exe') == n['exe_sha256'] == a['native_executable_sha256']
    for key in ('source', 'header', 'verifier'):
        assert sha(ROOT / b[key]) == b[key + '_sha256']
    assert sha(ROOT / b['native_attempt']) == b['native_attempt_sha256']
    m = load(ROOT / b['native_attempt'])
    assert m['status'] == b['native_status'] == 'native-pass'
    assert m['native_cases_passed'] == b['native_cases_passed'] == 9
    for key in ('input_sha256', 'transitive_include_sha256', 'toolchain_sha256'):
        for name, expected in m[key].items():
            assert sha(ROOT / name) == expected
    for cmd in m['receipts'].values():
        assert cmd['exit_code'] == 0 and sha(ROOT / cmd['log']) == cmd['log_sha256']
        if 'output' in cmd:
            assert sha(ROOT / cmd['output']) == cmd['output_sha256']
    pe = module('pe314', ROOT / 'scripts/research/audit-v2-frame-service-290.py')
    image = cache.data(ROOT / 'local/game/Porsche.exe')
    assert hashlib.sha256(image).hexdigest() == a['original_sha256'] == b['original_sha256']
    assert hashlib.sha256(pe.pe_read(image, 0x53c290, 77)).hexdigest() == a['original_body_sha256']
    assert pe.pe_read(image, 0x53c290, 77) == cache.data(work / 'original-0053c290.bin')
    assert pe.pe_read(image, 0x5cc588, 5) == b'%s%s\0'

    s = load(RUN / 'build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    old = load(RUNS / '310-pr-intake-integration/build-002.json')
    assert s['source_manifest'] == old['source_manifest'] and s['source_delta']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 163 and len(s['project_paths']) == 8
    assert s['unresolved_names'] == 269 and s['unresolved_references'] == 298
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    rpath = ROOT / s['receipt']
    assert sha(rpath) == s['receipt_sha256']
    receipt = load(rpath)
    assert receipt['exit_code'] == 1 and sha(ROOT / receipt['log']) == receipt['log_sha256']
    log = cache.data(ROOT / receipt['log']).decode('utf8')
    assert collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log)) == collections.Counter(
        Path(p).name for p in s['compiled_source_roots'])
    added = set(s['compiled_source_roots']) - set(old['compiled_source_roots'])
    assert {Path(p).name for p in added} == {'0053c290.cpp', 'resource_open_313.cpp'}
    assert not set(old['compiled_source_roots']) - set(s['compiled_source_roots'])
    assert not any('fixture' in p or 'original-body' in p for p in s['compiled_source_roots'])
    before, after = ({x['symbol'] for x in entry['frontier']} for entry in (old, s))
    closed = {'?heap_fill_0053c290@porsche@@YAXPAXII@Z',
              '?game_setup_resource_file_open_0059d8e0@porsche@@YAPAXPBDI@Z',
              '?splash_progress_load_resource_0059d8e0@porsche@@YAPAXPBDI@Z'}
    assert before - after == closed and len(after - before) == 4
    coff = module('coff314', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    objects = {}
    for name in ('0053c290', 'resource_open_313'):
        paths = list(BUILD.glob(f'**/porsche_game_entry_bridges.dir/Release/{name}.obj'))
        assert len(paths) == 1
        view = coff.coff_symbols(paths[0])
        assert not view['common'] and not view['weak']
        objects[name] = dict(path=paths[0].relative_to(ROOT).as_posix(), sha256=sha(paths[0]), symbols=view)
    defined = set().union(*(set(x['symbols']['defined']) for x in objects.values()))
    # Readonly COMDAT is the already-checked five-byte original format literal.
    support = {'__Avx2WmemEnabledWeakValue', '??_C@_04HDOCAJNK@?$CFs?$CFs@'}
    assert defined - support == closed | {'?resource_open_0059d8e0@porsche@@YAPAXPBDI@Z'}
    assert not list(BUILD.glob('**/porsche_original_game_link.exe'))
    cache.check_stable()
    result = dict(schema=1, passed=True, native_cases=37, original_body_bytes=283,
                  integrated_original_functions=2, closed_names=sorted(closed), new_names=sorted(after-before),
                  game_sources=163, source_pins=len(pins), unresolved_names=269, unresolved_references=298,
                  build_report_sha256=sha(RUN / 'build-001.json'),
                  packet312_sha256=sha(p312 / 'summary.json'), packet313_sha256=sha(p313 / 'summary.json'),
                  fresh_objects=objects, game_executed=False)
    output = RUN / 'validation.json'
    if output.exists():
        assert load(output) == result, 'Completed audit changed'
    else:
        output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'native_cases', 'game_sources', 'source_pins',
                                           'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
