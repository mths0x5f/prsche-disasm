"""Shared-cache evidence audit: two native SIMD packets, real fill chain, game graph."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '321-simd-fill-game-integration'
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


def audit_receipt(work):
    n = load(work / 'receipt.json')
    assert n['status'] == 'pass'
    for name, expected in n['inputs_sha256'].items():
        path = ROOT / name
        if not path.exists():
            path = work / name
        assert sha(path) == expected, name
    for group in ('tools_sha256', 'link_libraries_sha256'):
        for name, expected in n[group].items():
            assert sha(ROOT / name) == expected, name
    for name, expected in n['objects_sha256'].items():
        assert sha(work / name) == expected
    for command in n['commands']:
        assert command['exit_code'] == 0
        assert sha(work / command['log']) == command['log_sha256']
    assert sha(work / 'fixture.exe') == n['exe_sha256']
    return n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chain-attempt', required=True)
    parser.add_argument('--build-attempt', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'\d{3}', args.chain_attempt) and re.fullmatch(r'\d{3}', args.build_attempt)
    pe = module('pe321', ROOT / 'scripts/research/audit-v2-frame-service-290.py')
    image = cache.data(ROOT / 'local/game/Porsche.exe')
    image_sha = hashlib.sha256(image).hexdigest()
    packets = {}
    for stem, va, raw_size in [('319-mmx-fill-backend', 0x5b0a40, 176), ('320-sse-fill-backend', 0x5b0b00, 242)]:
        packet = RUNS / stem
        p = load(packet / 'summary.json')
        assert image_sha == p['original_sha256']
        work = ROOT / p['native_attempt']
        if work.name == 'receipt.json':
            work = work.parent
        assert sha(work / 'receipt.json') == p['native_receipt_sha256']
        n = audit_receipt(work)
        assert n['native_cases_passed'] == p['native_cases_passed'] and n['native_cases_passed'] >= 1000
        assert n['native_checks'] == p['native_checks']
        if isinstance(p['source_sha256'], dict):
            for name, expected in p['source_sha256'].items():
                assert sha(packet / name) == expected
        else:
            for key in ('source', 'header', 'verifier', 'rea_response'):
                assert sha(ROOT / p[key]) == p[key + '_sha256']
        expected_body = p.get('original_body_sha256', p.get('original_span_sha256'))
        assert hashlib.sha256(pe.pe_read(image, va, raw_size)).hexdigest() == expected_body
        packets[stem] = dict(summary_sha256=sha(packet / 'summary.json'), native_cases=n['native_cases_passed'],
                             native_checks=n['native_checks'], raw_span_sha256=hashlib.sha256(pe.pe_read(image, va, raw_size)).hexdigest())

    work = ROOT / ('local/experiments/v2-fill-chain-321/attempt-' + args.chain_attempt)
    chain = audit_receipt(work)
    assert chain['native_cases_passed'] == 27648
    for name, va, size in [('dispatcher', 0x53c290, 77), ('scalar', 0x5b0980, 186),
                           ('mmx', 0x5b0a40, 176), ('sse', 0x5b0b00, 242)]:
        assert pe.pe_read(image, va, size) == cache.data(work / (name + '.bin'))

    s = load(RUN / ('build-' + args.build_attempt + '.json'))
    old = load(RUNS / '318-scalar-fill-game-integration/build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')
    assert s['source_manifest'] == old['source_manifest'] and s['source_delta']
    assert s['input_unchanged'] and not s['compiler_errors'] and not s['other_linker_errors']
    assert s['source_count'] == 166 and len(s['project_paths']) == 8
    assert s['unresolved_names'] == 266 and s['unresolved_references'] == 295
    assert s['exit_code'] == 1 and not s['executable'] and not s['game_executed']
    assert sha(ROOT / s['receipt']) == s['receipt_sha256']
    receipt = load(ROOT / s['receipt'])
    assert receipt['exit_code'] == 1 and sha(ROOT / receipt['log']) == receipt['log_sha256']
    log = cache.data(ROOT / receipt['log']).decode('utf8')
    assert collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log)) == collections.Counter(
        Path(x).name for x in s['compiled_source_roots'])
    expected_sources = {(RUNS / stem / name).relative_to(ROOT).as_posix() for stem, name in [
        ('319-mmx-fill-backend', '005b0a40.cpp'), ('320-sse-fill-backend', '005b0b00.cpp')]}
    assert set(s['compiled_source_roots']) - set(old['compiled_source_roots']) == expected_sources
    assert not set(old['compiled_source_roots']) - set(s['compiled_source_roots'])
    assert not any('fixture' in x or 'original-body' in x for x in s['compiled_source_roots'])
    before, after = ({x['symbol'] for x in entry['frontier']} for entry in (old, s))
    closed = {'?heap_fill_mmx_005b0a40@porsche@@YAXPAXII@Z', '?heap_fill_sse_005b0b00@porsche@@YAXPAXII@Z'}
    assert before - after == closed and not after - before
    coff = module('coff321', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    build = ROOT / 'local/builds/v2/simd-fill-game-integration-321'
    objects = {}
    for name in ('005b0a40', '005b0b00'):
        paths = list(build.glob('**/porsche_game_entry_bridges.dir/Release/' + name + '.obj'))
        assert len(paths) == 1
        view = coff.coff_symbols(paths[0])
        assert not view['common'] and not view['weak'] and not view['undefined']
        objects[name] = dict(path=paths[0].relative_to(ROOT).as_posix(), sha256=sha(paths[0]), symbols=view)
    defined = set().union(*(set(x['symbols']['defined']) for x in objects.values()))
    assert closed <= defined
    assert not list(build.glob('**/porsche_original_game_link.exe'))
    cache.check_stable()
    result = dict(schema=1, passed=True, packets=packets, chain_cases=27648, chain_checks=chain['native_checks'],
                  original_new_function_count=2, original_new_indexed_bytes=390,
                  chain_receipt=work.relative_to(ROOT).as_posix() + '/receipt.json',
                  chain_receipt_sha256=sha(work / 'receipt.json'), closed_names=sorted(closed), new_names=[],
                  game_sources=166, source_pins=len(pins), unresolved_names=266, unresolved_references=295,
                  build_report='build-' + args.build_attempt + '.json',
                  build_report_sha256=sha(RUN / ('build-' + args.build_attempt + '.json')),
                  objects=objects, game_executed=False)
    target = RUN / 'validation.json'
    if target.exists():
        assert load(target) == result, 'Completed audit changed'
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'chain_cases', 'game_sources', 'source_pins', 'unresolved_names')}))


if __name__ == '__main__':
    main()
