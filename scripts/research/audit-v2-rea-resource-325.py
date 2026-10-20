"""Read-only audit of the completed persistent REA resource session."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/325-rea-resource-session'
OUT = ROOT / 'local/experiments/v2-rea-resource-325/001'
EXPECTED = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def audit(cache=None):
    data = cache.data if cache else lambda p: Path(p).read_bytes()
    load = lambda p: json.loads(data(p))
    sha = lambda p: hashlib.sha256(data(p)).hexdigest()
    payload = lambda name: json.loads(load(OUT / (name + '.json'))['content'][0]['text'])
    receipt = load(OUT / 'receipt.json')
    assert receipt['exit_code'] == 0 and receipt['target_sha256'] == EXPECTED
    for name, expected in receipt['output_sha256'].items():
        assert sha(OUT / name) == expected, name
    pilot = ROOT / 'local/tools/rea-pilot-302/.pilot'
    for path, field in [
        (ROOT / 'scripts/research/rea-resource-session-325.mjs', 'script_sha256'),
        (ROOT / 'scripts/research/run-v2-rea-resource-325.py', 'runner_sha256'),
        (pilot / 'package/package.json', 'rea_package_json_sha256'),
        (pilot / 'package/scripts/rea.mjs', 'rea_server_sha256'),
        (pilot / 'node/node-v26.12.0-win-x64/node.exe', 'node_sha256'),
    ]:
        assert sha(path) == receipt[field], field
    for path in (ROOT / 'local/game/Porsche.exe', OUT / 'Porsche.exe'):
        assert sha(path) == EXPECTED
    status = load(OUT / 'status.json')
    assert status['connected'] and status['failure'] is None
    assert status['target_sha256_before'] == status['target_sha256_after'] == EXPECTED
    before, after = (payload(name)['result'] for name in ('session-before', 'session-final'))
    assert before['open'] and after['open']
    assert before['sha256'] == after['sha256'] == EXPECTED
    assert before['server_identity'] == after['server_identity']
    assert after['server_identity']['server']['version'] == '6.7.0'
    assert after['analysis_provider_binding']['provider']['id'] == 'ghidra'
    assert payload('exists-cold')['normalized_result'] == payload('exists-warm')['normalized_result']
    bodies = {}
    for name, start, size in [
        ('exists-cold', 0x561b80, 20), ('request-exists', 0x533f00, 52),
        ('request-constructor', 0x568260, 51), ('open-wrapper', 0x561ca0, 63),
        ('device-route', 0x568e90, 35), ('device-prefix', 0x591760, 27),
    ]:
        envelope = load(OUT / (name + '.json'))
        assert not envelope.get('isError', False)
        procedure = payload(name)['normalized_result']['procedure']
        assert int(procedure['address'], 16) == start
        assert procedure['body']['ranges'] == [dict(start=hex(start), end=hex(start + size - 1))]
        assert procedure['body']['total_bytes'] == size
        bodies[name] = dict(address=hex(start), bytes=size)
    spec = importlib.util.spec_from_file_location('pe325', ROOT / 'scripts/research/audit-v2-frame-service-290.py')
    pe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pe)
    raw = bytes.fromhex(payload('callback-region-bytes')['normalized_result']['bytes_hex'])
    assert len(raw) == 276 and raw == pe.pe_read(data(ROOT / 'local/game/Porsche.exe'), 0x561ce0, 276)
    error = load(OUT / 'callback-function.json')
    assert error['isError'] and payload('callback-function')['error']['code'] == 'invalid_request'
    assert 'No procedure exists' in json.dumps(payload('callback-function'))
    return dict(schema=1, passed=True, original_sha256=EXPECTED,
                receipt='local/experiments/v2-rea-resource-325/001/receipt.json',
                receipt_sha256=sha(OUT / 'receipt.json'), server_pid=status['server_pid'],
                same_server_identity=True, repeat_normalized_equal=True, bodies=bodies,
                callback_bytes=276, callback_sha256=hashlib.sha256(raw).hexdigest(),
                callback_function_recognized=False, timings_ms=status['timings'],
                native_acceptance=False, game_executed=False)


def main():
    result = audit()
    RUN.mkdir(parents=True, exist_ok=True)
    target = RUN / 'validation.json'
    if target.exists():
        assert json.loads(target.read_bytes()) == result, 'Completed audit changed'
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(passed=True, bodies=len(result['bodies']), callback_function_recognized=False)))


if __name__ == '__main__':
    main()
