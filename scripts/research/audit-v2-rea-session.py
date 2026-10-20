"""Audit a saved manifest-driven REA session without reopening its binary."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def audit(config_path, attempt, cache=None, hash_file=None):
    data = cache.data if cache else lambda p: Path(p).read_bytes()
    sha = hash_file or (lambda p: hashlib.sha256(data(p)).hexdigest())
    load = lambda p: json.loads(data(p))
    config_path = Path(config_path).resolve()
    config = load(config_path)
    out = ROOT / config['experiment'] / attempt
    payload = lambda name: json.loads(load(out / (name + '.json'))['content'][0]['text'])
    r = load(out / 'receipt.json')
    assert r['exit_code'] == 0 and r['config_sha256'] == sha(config_path)
    assert r['target_sha256'] == r['expected_sha256'] == EXPECTED
    for name, expected in r['output_sha256'].items():
        assert sha(out / name) == expected, name
    pilot = ROOT / 'local/tools/rea-pilot-302/.pilot'
    for path, field in [
        (ROOT / 'scripts/research/rea-session.mjs', 'script_sha256'),
        (ROOT / 'scripts/research/run-v2-rea-session.py', 'runner_sha256'),
        (pilot / 'package/package.json', 'rea_package_json_sha256'),
        (pilot / 'package/scripts/rea.mjs', 'rea_server_sha256'),
        (pilot / 'node/node-v26.12.0-win-x64/node.exe', 'node_sha256'),
    ]:
        assert sha(path) == r[field], field
    for path in (ROOT / 'local/game/Porsche.exe', out / 'Porsche.exe'):
        assert sha(path) == EXPECTED
    status = load(out / 'status.json')
    assert status['connected'] and status['failure'] is None
    assert status['target_sha256_before'] == status['target_sha256_after'] == EXPECTED
    before, after = (payload(name)['result'] for name in ('session-before', 'session-final'))
    assert before['open'] and after['open']
    assert before['sha256'] == after['sha256'] == EXPECTED
    assert before['server_identity'] == after['server_identity']
    assert after['analysis_provider_binding']['provider']['id'] == 'ghidra'
    index_path = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
    index = {int(row['entry_va'], 16): row for row in map(json.loads, data(index_path).splitlines())}
    spec = importlib.util.spec_from_file_location('pe_rea_audit', ROOT / 'scripts/research/audit-v2-frame-service-290.py')
    pe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pe)
    image = data(ROOT / 'local/game/Porsche.exe')
    bodies, repeated, first = {}, [], {}
    for query in config['queries']:
        name = query['label']
        result = load(out / (name + '.json'))
        assert not result.get('isError', False), name
        if query['tool'] != 'analyze_function':
            continue
        n = payload(name)['normalized_result']
        start = int(query['arguments']['procedure'], 16)
        procedure = n['procedure']
        assert int(procedure['address'], 16) == start
        row = index[start]
        ranges = [[int(v, 16) for v in pair] for pair in row['ranges']]
        assert [(int(p['start'], 16), int(p['end'], 16)) for p in procedure['body']['ranges']] == [tuple(p) for p in ranges]
        assert procedure['body']['total_bytes'] == row['body_bytes']
        raw = b''.join(pe.pe_read(image, a, b - a + 1) for a, b in ranges)
        bodies[name] = dict(address=hex(start), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        if start in first:
            assert n == first[start][1], 'Repeated normalized dossier changed'
            repeated.append([first[start][0], name])
        else:
            first[start] = (name, n)
    return dict(schema=1, passed=True, original_sha256=EXPECTED,
                receipt=(out / 'receipt.json').relative_to(ROOT).as_posix(), receipt_sha256=sha(out / 'receipt.json'),
                config_sha256=sha(config_path), index_sha256=sha(index_path), server_pid=status['server_pid'],
                same_server_identity=True, bodies=bodies, repeated_equal=repeated,
                timings_ms=status['timings'], native_acceptance=False, game_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    result = audit(args.config, args.attempt)
    path = args.config.parent / 'validation.json'
    if path.exists():
        assert json.loads(path.read_bytes()) == result, 'Completed audit changed'
    else:
        path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(passed=True, dossiers=len(result['bodies']), repeated_equal=len(result['repeated_equal']))))


if __name__ == '__main__':
    main()
