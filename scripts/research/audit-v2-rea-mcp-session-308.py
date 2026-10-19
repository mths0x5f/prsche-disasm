"""Audit the real REA stdio session and its cold/snapshot-warm requests."""
import hashlib
import json
from pathlib import Path

from v2_shared_manifests import ManifestReader, externalize

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'local/experiments/v2-rea-mcp-session-308'
GOOD = BASE / '003'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/308-rea-mcp-session'
INDEX = ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
EXPECTED = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def data(path):
    return json.loads(path.read_bytes())


def immutable(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(raw)
    except FileExistsError:
        if path.read_bytes() != raw:
            raise ValueError('Existing audit differs: ' + str(path))


def main():
    attempts = {}
    for number in ('001', '002', '003'):
        directory = BASE / number
        receipt_path = directory / 'receipt.json'
        receipt = data(receipt_path)
        assert receipt['attempt'] == number
        assert receipt['runner_log_sha256'] == sha(directory / 'runner.log')
        assert receipt['target_sha256'] == EXPECTED
        attempts[number] = dict(path=rel(receipt_path), sha256=sha(receipt_path),
                                exit_code=receipt['exit_code'], seconds=receipt['seconds'])
    assert attempts['001']['exit_code'] != 0
    assert attempts['002']['exit_code'] != 0
    assert attempts['003']['exit_code'] == 0
    assert 'spawn EPERM' in (BASE / '001/runner.log').read_text()
    assert 'First analyze_function returned isError' in (BASE / '002/runner.log').read_text()
    assert 'procedure: Invalid input' in data(BASE / '002/function-cold.json')['content'][0]['text']
    assert sha(ROOT / 'local/game/Porsche.exe') == EXPECTED
    assert sha(GOOD / 'Porsche.exe') == EXPECTED

    status = data(GOOD / 'status.json')
    assert status['connected'] is True and status['failure'] is None
    assert type(status['server_pid']) is int and status['server_pid'] > 0
    assert status['target_sha256_before'] == status['target_sha256_after'] == EXPECTED
    assert status['stderr_bytes'] == (GOOD / 'server-stderr.log').stat().st_size
    tools = data(GOOD / 'tools-list.json')['tools']
    assert len(tools) == 207
    schemas = data(GOOD / 'selected-tool-schemas.json')
    assert schemas['analyze']['inputSchema']['required'] == ['procedure']
    assert {schemas[key]['name'] for key in ('open', 'session', 'analyze', 'close')} == {
        'open_binary', 'binary_session', 'analyze_function', 'close_binary'}

    events = [json.loads(line) for line in (GOOD / 'events.jsonl').read_text(encoding='utf8').splitlines()]
    calls = [item['message'] for item in events if item.get('direction') == 'client-to-server'
             and item['message'].get('method') == 'tools/call']
    assert [message['params']['name'] for message in calls] == [
        'open_binary', 'binary_session', 'analyze_function', 'binary_session',
        'analyze_function', 'binary_session', 'close_binary']
    query_calls = [message for message in calls if message['params']['name'] == 'analyze_function']
    assert [message['params']['arguments'] for message in query_calls] == [
        {'procedure': '0x00476170'}, {'procedure': '0x00476170'}]
    assert query_calls[0]['id'] != query_calls[1]['id']
    responses = {item['message']['id'] for item in events if item.get('direction') == 'server-to-client'
                 and 'id' in item['message']}
    assert all(message['id'] in responses for message in calls)
    assert any(item.get('kind') == 'initialized' and item['server_pid'] == status['server_pid']
               for item in events)

    sessions = [data(GOOD / name)['structuredContent']['result'] for name in
                ('session-before.json', 'session-middle.json', 'session-after.json')]
    assert all(item['open'] is True and item['sha256'] == EXPECTED for item in sessions)
    run_ids = [item['analysis_run']['run_id'] for item in sessions]
    assert len(set(run_ids)) == 1
    identities = [item['server_identity'] for item in sessions]
    assert identities[0] == identities[1] == identities[2]
    assert identities[0]['server']['version'] == '6.7.0'
    cold = data(GOOD / 'function-cold.json')['structuredContent']
    warm = data(GOOD / 'function-warm.json')['structuredContent']
    assert cold['normalized_result'] == warm['normalized_result']
    assert cold['subject']['digest']['sha256'] == warm['subject']['digest']['sha256'] == EXPECTED
    assert warm['evidence_id'] != cold['evidence_id']
    assert any('Loaded from a local REA analysis snapshot' in item for item in warm['limitations'])
    assert not any('Loaded from a local REA analysis snapshot' in item for item in cold['limitations'])
    normal = cold['normalized_result']
    assert normal['procedure']['address'] == '0x476170'
    assert normal['procedure']['body']['total_bytes'] == 169
    assert normal['procedure']['body']['ranges'] == [{'start': '0x476170', 'end': '0x476218'}]
    assert [x['address'] for x in normal['callers']] == ['0x487e20']
    assert [x['address'] for x in normal['callees']] == ['0x476710']
    assert [x['address'] for x in normal['unresolved_calls']] == ['0x4761c0', '0x4761f1']
    assert cold['relationship_coverage']['status'] == 'partial'
    assert not data(GOOD / 'close.json').get('isError', False)

    functions = [json.loads(line) for line in (INDEX / 'functions.jsonl').read_text().splitlines()]
    indexed = next(item for item in functions if item['entry_va'] == '00476170')
    assert indexed['body_bytes'] == 169 and indexed['ranges'] == [['00476170', '00476218']]
    calls_index = [json.loads(line) for line in (INDEX / 'calls.jsonl').read_text().splitlines()]
    assert any(x['from_va'] == '00487e4d' and x['to_va'] == '00476170' for x in calls_index)
    assert any(x['from_va'] == '0047619b' and x['to_va'] == '00476710' for x in calls_index)

    input_paths = [ROOT / 'local/game/Porsche.exe', INDEX / 'functions.jsonl', INDEX / 'calls.jsonl']
    source_paths = [ROOT / 'scripts/research/rea-mcp-session-308.mjs',
                    ROOT / 'scripts/research/run-v2-rea-mcp-session-308.py', Path(__file__),
                    ROOT / 'scripts/research/v2_shared_manifests.py']
    pins = externalize(ROOT, {'input_sha256': {rel(p): sha(p) for p in input_paths}}, 'input')
    pins = externalize(ROOT, {**pins, 'source_sha256': {rel(p): sha(p) for p in source_paths}}, 'source')
    reader = ManifestReader(ROOT)
    reader.verify(pins, 'input', expected_hash_mode='raw')
    reader.verify(pins, 'source', expected_hash_mode='raw')
    output_paths = [GOOD / name for name in ('events.jsonl', 'tools-list.json',
                    'selected-tool-schemas.json', 'function-cold.json', 'function-warm.json',
                    'session-before.json', 'session-middle.json', 'session-after.json',
                    'server-stderr.log', 'status.json', 'receipt.json')]
    result = dict(schema=1, kind='rea-persistent-mcp-session', status='PASS',
                  target_sha256=EXPECTED, package_version='6.7.0',
                  sdk_client_version='2.3.1', server_pid=status['server_pid'],
                  analysis_run_id=run_ids[0], tools_list_count=len(tools),
                  function='00476170', function_bytes=169,
                  callers=['00487e20'], callees=['00476710'],
                  unresolved_calls=['004761c0', '004761f1'],
                  cold_ms=status['timings']['function-cold'],
                  warm_ms=status['timings']['function-warm'],
                  warm_source='local REA analysis snapshot; provider did not rerun',
                  identical_normalized_result=True, cached_index_match=True,
                  target_unchanged=True, attempts=attempts,
                  input_manifest=pins['input_manifest'], source_manifest=pins['source_manifest'],
                  output_sha256={rel(p): sha(p) for p in output_paths},
                  limitations=['The warm speed measures REA snapshot reuse, not live Ghidra process reuse',
                               'Two indirect call targets remain unresolved',
                               'This SDK-protocol test did not register tools in the IDE or root ALL_TOOLS'])
    immutable(RUN / 'audit.json', result)
    print('PASS REA308: same MCP server and run ID; native cold query and snapshot-warm repeat')


if __name__ == '__main__':
    main()
