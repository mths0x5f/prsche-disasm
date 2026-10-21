"""Shared read-only audit for ABI batch proof, REA evidence and actual game intake."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def audit(config_path):
    reader = ManifestReader(ROOT)
    cache, hashes = reader.cache, {}
    load = cache.document

    def sha(path):
        path = Path(path).resolve()
        if path not in hashes:
            hashes[path] = hashlib.sha256(cache.data(path)).hexdigest()
        return hashes[path]

    cfg = load(config_path)
    native = load(ROOT / cfg['native_config'])
    build_cfg = load(ROOT / cfg['build_config'])
    run, build = ROOT / build_cfg['run'], ROOT / build_cfg['build']
    packet = load(ROOT / native['summary'])
    attempt = ROOT / packet['native_attemptdir']
    assert sha(attempt / 'receipt.json') == packet['native_receipt_sha256']
    receipt = load(attempt / 'receipt.json')
    assert packet['new_original_functions'] == receipt['new_original_functions'] == 0
    assert packet['native_cases_passed'] == receipt['native_cases_passed'] == native['cases']
    for name, expected in packet['source_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for group in ('inputs_sha256', 'outputs_sha256'):
        for name, expected in receipt[group].items():
            assert sha(ROOT / name) == expected, name
    negatives = {n['name'] + '-native': n['exit_code'] for n in receipt['negative_controls']}
    assert len(negatives) == len(native['mutations']) and all(n['detected'] for n in receipt['negative_controls'])
    for name, command in receipt['receipts'].items():
        assert command['exit_code'] == negatives.get(name, 0), name
        assert sha(ROOT / command['log']) == command['log_sha256']
    assert f"cases={native['cases']} failures=0" in cache.data(ROOT / receipt['receipts']['native']['log']).decode()
    for proof in packet['original_body_proofs']:
        assert sha(ROOT / proof['path']) == proof['sha256'] and not proof['rerun']
        old = load(ROOT / proof['path'])
        assert old['native_cpp_equal_original_x86'] and old['cases'] == proof['cases']
        for name, expected in old['source_sha256'].items():
            assert cache.digest(ROOT / name) == expected, name
    rea = module('batch_rea', ROOT / 'scripts/research/audit-v2-rea-session.py').audit(
        ROOT / cfg['rea_config'], cfg['rea_attempt'], cache, sha)
    heap = load(ROOT / cfg['heap_evidence'])
    assert heap['production_provider_added'] is False
    assert heap['rea_receipt_sha256'] == rea['receipt_sha256']
    for name, expected in heap['input_sha256'].items():
        assert sha(ROOT / name) == expected, name
    current = load(run / 'build-001.json')
    baseline = load(ROOT / cfg['baseline'])
    _, pins = reader.verify(current, 'source', expected_hash_mode='crlf-to-lf')
    assert current['input_unchanged'] and not current['compiler_errors'] and not current['other_linker_errors']
    old_sources, sources = set(baseline['compiled_source_roots']), set(current['compiled_source_roots'])
    assert sources - old_sources == {native['source']} and old_sources <= sources
    assert current['source_count'] == len(sources) == baseline['source_count'] + 1
    assert collections.Counter(Path(p).name for p in current['project_paths']) == collections.Counter(
        Path(p).name for p in baseline['project_paths'])
    assert not any('fixture' in p for p in sources)
    assert sha(ROOT / current['receipt']) == current['receipt_sha256']
    game_receipt = load(ROOT / current['receipt'])
    assert sha(ROOT / game_receipt['log']) == game_receipt['log_sha256']
    log = cache.data(ROOT / game_receipt['log']).decode('utf8')
    assert collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', log)) == collections.Counter(Path(p).name for p in sources)
    before, after = ({r['symbol'] for r in s['frontier']} for s in (baseline, current))
    closed, added = before - after, after - before
    assert closed == set(native['expected_defined'])
    assert added == set(cfg['expected_new_names'])
    assert current['unresolved_names'] == len(after)
    assert current['unresolved_references'] == sum(len(r['references']) for r in current['frontier'])
    assert current['exit_code'] == game_receipt['exit_code'] == (1 if after else 0)
    assert current['game_executed'] is False
    assert bool(current['executable']) == (not after)
    coff = module('batch_coff', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    objects = list(build.glob('**/porsche_game_entry_bridges.dir/Release/' + Path(native['source']).stem + '.obj'))
    assert len(objects) == 1
    view = coff.coff_symbols(objects[0])
    assert view == packet['coff_symbols']
    assert set(view['defined']) == set(native['expected_defined'])
    assert set(view['undefined']) == set(native['expected_undefined'])
    definitions = collections.Counter()
    for path in build.glob('**/*.obj'):
        definitions.update(coff.coff_symbols(path)['defined'])
    assert all(definitions[name] == 1 for name in native['expected_defined'] + native['expected_undefined'])
    graph = module('batch_graph', ROOT / 'scripts/research/v2_build_graph.py')
    entries = list(build.glob('**/porsche_original_game_link.vcxproj'))
    assert len(entries) == 1
    assert graph.compiled_sources(entries[0].parent, 'porsche_original_game_link') == current['compiled_source_roots']
    cache.check_stable()
    return dict(schema=1, passed=True, native_cases=native['cases'], mutations=len(negatives),
                new_original_functions=0, reused_proofs=packet['original_body_proofs'], rea=rea,
                binding_summary_sha256=sha(ROOT / native['summary']), heap_evidence_sha256=sha(ROOT / cfg['heap_evidence']),
                build_sha256=sha(run / 'build-001.json'), game_sources=len(sources), source_pins=len(pins),
                unresolved_names=len(after), unresolved_references=current['unresolved_references'],
                closed_names=sorted(closed), new_names=sorted(added), symbols=view,
                object_sha256=sha(objects[0]), game_executed=False, executable=current['executable'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.config.resolve())
    output = args.config.parent / 'validation.json'
    if output.exists():
        assert json.loads(output.read_bytes()) == result, 'Completed audit changed'
    else:
        output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({k: result[k] for k in ('passed', 'native_cases', 'game_sources', 'source_pins', 'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
