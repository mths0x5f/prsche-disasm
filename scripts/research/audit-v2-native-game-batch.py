"""Read-only acceptance for config-driven original/native subsystem batches."""
import argparse
import collections
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]


@functools.lru_cache(maxsize=1)
def legacy_native_runner():
    # Frozen tool input before optional SDK libraries; never substitute source inputs.
    return subprocess.check_output(
        ['git', 'cat-file', 'blob', '0733c15bb343c2043d6e3f642e82bc40b26dccde'], cwd=ROOT)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def audit_import_thunk(data, symbol, imported):
    """Prove a platform adapter is only JMP [the original Win32 import]."""
    machine, sections, _, table, count, optional, _ = struct.unpack_from('<HHIIIHH', data)
    assert machine == 0x14c and optional == 0
    strings = table + count * 18

    def name(index):
        offset = table + index * 18
        raw = data[offset:offset + 8]
        if raw[:4] == b'\0' * 4:
            start = strings + struct.unpack_from('<I', raw, 4)[0]
            return data[start:data.index(b'\0', start)].decode('ascii')
        return raw.rstrip(b'\0').decode('ascii')

    entries = []
    index = 0
    while index < count:
        offset = table + index * 18
        if name(index) == symbol:
            entries.append(struct.unpack_from('<Ih', data, offset + 8))
        index += 1 + data[offset + 17]
    assert len(entries) == 1
    value, section = entries[0]
    assert 1 <= section <= sections
    offset = 20 + (section - 1) * 40
    size, raw, relocations = struct.unpack_from('<III', data, offset + 16)
    relocation_count = struct.unpack_from('<H', data, offset + 32)[0]
    code = data[raw + value:raw + size]
    assert code == b'\xff\x25\0\0\0\0' and relocation_count == 1
    address, target, kind = struct.unpack_from('<IIH', data, relocations)
    assert address == value + 2 and kind == 6 and name(target) == imported
    return code.hex()


def audit_native(cfg, cache, sha):
    load = cache.document
    native_cfg = load(ROOT / cfg['native_config'])
    native = load(ROOT / cfg['native_receipt'])
    assert native['status'] == 'PASS'
    assert native['config'] == cfg['native_config']
    assert native['original_sha256'] == native_cfg['original_sha256']
    for group in ('inputs_sha256', 'outputs_sha256'):
        assert native[group], group
        for name, expected in native[group].items():
            actual = sha(ROOT / name)
            if (group == 'inputs_sha256' and actual != expected
                    and name == 'scripts/research/verify-v2-native-batch.py'
                    and expected == '9c53c1110f9094449e59c72a2d08f076f796a553a3500a43d978267c72169e98'):
                actual = hashlib.sha256(legacy_native_runner()).hexdigest()
            assert actual == expected, f'{group}: {name}'
    pe = cache.data(ROOT / native_cfg['original_pe'])
    assert hashlib.sha256(pe).hexdigest() == native_cfg['original_sha256']
    utility = module('native_batch_pe', ROOT / 'scripts/research/verify-v2-native-batch.py')
    assert native['original_bodies'] == native_cfg['original_bodies']
    for body in native['original_bodies']:
        data = utility.pe_at(pe, int(body['va'], 16), body['bytes'])
        assert hashlib.sha256(data).hexdigest() == body['sha256']
    assert set(native['variants']) == {'od', 'o2'}
    mutations = {item['name']: item for item in native_cfg['mutations']}
    assert {item['name'] for item in native['mutation_controls']} == set(mutations)
    for item in native['mutation_controls']:
        assert item['detected'] and item['exit_code'] == mutations[item['name']].get('expected_exit', 10)
    for name, receipt in native['receipts'].items():
        expected = next((item.get('expected_exit', 10) for key, item in mutations.items()
                         if name == f'mutation-{key}-native'), 0)
        assert receipt['exit_code'] == expected, name
        assert sha(ROOT / receipt['log']) == receipt['log_sha256'], name
    total_cases = 0
    for variant, result in native['variants'].items():
        receipt = native['receipts'][f'{variant}-native']
        output = cache.data(ROOT / receipt['log']).decode('utf8')
        assert native_cfg['pass_marker'] in output
        case_marker = re.search(r'\bcases=(\d+)\b', output)
        assert case_marker, 'native result must report its measured case count'
        total_cases += int(case_marker.group(1))
        assert result['output_sha256'] == receipt['log_sha256']
    assert total_cases == cfg['native_cases']
    dependencies = module('native_batch_dependencies', ROOT / 'scripts/research/audio_recovery_provenance.py')
    paths = dependencies.dependency_paths(ROOT / native['attempt_dir'])
    pinned = {(ROOT / name).resolve() for name in native['inputs_sha256']}
    assert paths <= pinned, 'compiler dependency closure not pinned'

    result = dict(cases=cfg['native_cases'], mutations=len(mutations),
                  receipt_sha256=sha(ROOT / cfg['native_receipt']))
    reused = []
    for proof in cfg.get('reused_chains', []):
        path = ROOT / proof['auditor']
        assert sha(path) == proof['auditor_sha256']
        verifier = module('native_batch_reused_chain', path)
        work = ROOT / proof['work']
        assert sha(work / 'receipt.json') == proof['receipt_sha256']
        receipt = verifier.audit_receipt(work)
        verifier.cache.check_stable()
        assert receipt['native_cases_passed'] == proof['cases']
        for body in proof['original_bodies']:
            assert utility.pe_at(pe, int(body['va'], 16), body['bytes']) == cache.data(work / body['file'])
        reused.append(dict(cases=proof['cases'], receipt_sha256=proof['receipt_sha256'], rerun=False))
    if reused:
        result['reused_chains'] = reused
    return result


def audit(config_path):
    reader = ManifestReader(ROOT)
    cache = reader.cache
    load = cache.document
    hashes = {}

    def sha(path):
        path = Path(path).resolve()
        if path not in hashes:
            hashes[path] = hashlib.sha256(cache.data(path)).hexdigest()
        return hashes[path]

    cfg = load(config_path)
    batches = cfg.get('native_batches', [cfg])
    native_proofs = [audit_native(item, cache, sha) for item in batches]
    assert sum(item['cases'] for item in native_proofs) == cfg['native_cases']

    rea_module = module('native_batch_rea', ROOT / 'scripts/research/audit-v2-rea-session.py')
    rea = [rea_module.audit(ROOT / item['config'], item['attempt'], cache, sha)
           for item in cfg['rea_sessions']]
    for name, expected in cfg['evidence_sha256'].items():
        assert sha(ROOT / name) == expected, name
    build_cfg = load(ROOT / cfg['build_config'])
    run, build = ROOT / build_cfg['run'], ROOT / build_cfg['build']
    current_path = run / f"build-{cfg['build_attempt']}.json"
    current, baseline = load(current_path), load(ROOT / cfg['baseline'])
    _, pins = reader.verify(current, 'source', expected_hash_mode='crlf-to-lf')
    assert current['input_unchanged'] and not current['compiler_errors'] and not current['other_linker_errors']
    old_sources, sources = set(baseline['compiled_source_roots']), set(current['compiled_source_roots'])
    assert old_sources <= sources and sources - old_sources == set(cfg['added_sources'])
    assert current['source_count'] == len(sources)
    assert collections.Counter(Path(p).name for p in current['project_paths']) == collections.Counter(
        Path(p).name for p in baseline['project_paths'])
    assert not any('fixture' in p.lower() or 'probe' in Path(p).name.lower() for p in sources)
    assert sha(ROOT / current['receipt']) == current['receipt_sha256']
    receipt = load(ROOT / current['receipt'])
    assert sha(ROOT / receipt['log']) == receipt['log_sha256']
    compiler_events = re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', cache.data(ROOT / receipt['log']).decode('utf8'))
    assert collections.Counter(compiler_events) == collections.Counter(Path(p).name for p in sources)
    before, after = ({item['symbol'] for item in report['frontier']} for report in (baseline, current))
    assert before - after == set(cfg['expected_closed_names'])
    assert after - before == set(cfg['expected_new_names'])
    assert current['unresolved_names'] == len(after)
    assert current['unresolved_references'] == sum(len(item['references']) for item in current['frontier'])
    assert current['exit_code'] == receipt['exit_code'] == (1 if after else 0)
    assert current['game_executed'] is False and bool(current['executable']) == (not after)
    coff = module('native_batch_coff', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    definitions = collections.defaultdict(list)
    for path in build.glob('**/*.obj'):
        for symbol in coff.coff_symbols(path)['defined']:
            definitions[symbol].append(path.relative_to(build).as_posix())
    for symbol, owner in cfg['canonical_providers'].items():
        assert len(definitions[symbol]) == 1, symbol
        actual = definitions[symbol][0]
        # CMake disambiguates equal source basenames into different object paths.
        assert (actual == owner if '/' in owner else Path(actual).name == owner), symbol
    for symbol in cfg['expected_new_names']:
        assert not definitions[symbol], f'fabricated provider: {symbol}'
    platform = []
    for thunk in cfg.get('platform_import_thunks', []):
        candidates = list(build.glob('**/' + thunk['object']))
        assert len(candidates) == 1
        path = candidates[0]
        view = coff.coff_symbols(path)
        assert view['defined'] == [thunk['symbol']] and view['undefined'] == [thunk['import_symbol']]
        code = audit_import_thunk(cache.data(path), thunk['symbol'], thunk['import_symbol'])
        imports = [json.loads(line) for line in cache.data(ROOT / thunk['index']).decode('utf8').splitlines()]
        assert thunk['original_import'] in imports
        platform.append(dict(symbol=thunk['symbol'], import_symbol=thunk['import_symbol'],
                             code=code, object_sha256=sha(path), original_import=thunk['original_import']))
    graph = module('native_batch_graph', ROOT / 'scripts/research/v2_build_graph.py')
    entries = list(build.glob('**/porsche_original_game_link.vcxproj'))
    assert len(entries) == 1
    assert graph.compiled_sources(entries[0].parent, 'porsche_original_game_link') == current['compiled_source_roots']
    cache.check_stable()
    result = dict(schema=1, passed=True, native_cases=cfg['native_cases'],
                mutations=sum(item['mutations'] for item in native_proofs),
                rea=rea, source_pins=len(pins), game_sources=len(sources),
                build_sha256=sha(current_path), unresolved_names=len(after),
                unresolved_references=current['unresolved_references'],
                closed_names=sorted(before - after), new_names=sorted(after - before),
                canonical_providers=cfg['canonical_providers'], game_executed=False,
                executable=current['executable'])
    if 'native_batches' in cfg:
        result['native_proofs'] = native_proofs
    else:
        result['native_receipt_sha256'] = native_proofs[0]['receipt_sha256']
    if platform:
        result['platform_import_thunks'] = platform
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.config.resolve())
    output = args.config.parent / 'validation.json'
    if output.exists():
        assert json.loads(output.read_bytes()) == result, 'completed audit changed'
    else:
        output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({key: result[key] for key in ('passed', 'native_cases', 'mutations', 'game_sources',
                                                  'source_pins', 'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
