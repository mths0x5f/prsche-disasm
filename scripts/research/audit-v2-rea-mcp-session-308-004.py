"""Audit the distinct-function MCP follow-up without rerunning native analysis."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from v2_shared_manifests import ManifestReader, externalize

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/308-rea-mcp-session'
OUT = ROOT / 'local/experiments/v2-rea-mcp-session-308/004'
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
    baseline = subprocess.run([sys.executable, str(ROOT / 'scripts/research/audit-v2-rea-mcp-session-308.py')],
                              cwd=ROOT, capture_output=True, text=True)
    assert baseline.returncode == 0 and 'PASS REA308' in baseline.stdout
    receipt = data(OUT / 'receipt.json')
    status = data(OUT / 'status.json')
    assert receipt['attempt'] == '004' and receipt['exit_code'] == 0
    assert receipt['runner_log_sha256'] == sha(OUT / 'runner.log')
    assert receipt['target_sha256'] == status['target_sha256_before'] == status['target_sha256_after'] == EXPECTED
    assert sha(ROOT / 'local/game/Porsche.exe') == sha(OUT / 'Porsche.exe') == EXPECTED
    assert status['connected'] is True and status['failure'] is None
    assert type(status['server_pid']) is int and status['server_pid'] > 0
    assert status['stderr_bytes'] == (OUT / 'server-stderr.log').stat().st_size
    listed = data(OUT / 'tools-list.json')['tools']
    assert len(listed) == 207
    assert data(OUT / 'selected-tool-schemas.json')['analyze']['inputSchema']['required'] == ['procedure']

    events = [json.loads(line) for line in (OUT / 'events.jsonl').read_text(encoding='utf8').splitlines()]
    calls = [e['message'] for e in events if e.get('direction') == 'client-to-server'
             and e['message'].get('method') == 'tools/call']
    assert [e['params']['name'] for e in calls] == [
        'open_binary', 'binary_session', 'analyze_function', 'binary_session',
        'analyze_function', 'binary_session', 'analyze_function', 'binary_session', 'close_binary']
    queries = [e for e in calls if e['params']['name'] == 'analyze_function']
    assert [e['params']['arguments'] for e in queries] == [
        {'procedure': '0x00476170'}, {'procedure': '0x00476170'}, {'procedure': '0x00476710'}]
    assert len({e['id'] for e in queries}) == 3
    responses = {e['message']['id'] for e in events if e.get('direction') == 'server-to-client'
                 and 'id' in e['message']}
    assert all(e['id'] in responses for e in calls)
    assert any(e.get('kind') == 'initialized' and e['server_pid'] == status['server_pid'] for e in events)
    sessions = [data(OUT / name)['structuredContent']['result'] for name in
                ('session-before.json', 'session-middle.json', 'session-after.json', 'session-final.json')]
    assert all(s['open'] is True and s['sha256'] == EXPECTED for s in sessions)
    ids = [s['analysis_run']['run_id'] for s in sessions]
    assert len(set(ids)) == 1
    assert all(s['server_identity'] == sessions[0]['server_identity'] for s in sessions)
    assert all(s['analysis_activity']['status'] == 'not_observed' for s in sessions)

    cold = data(OUT / 'function-cold.json')['structuredContent']
    warm = data(OUT / 'function-warm.json')['structuredContent']
    different = data(OUT / 'function-different.json')['structuredContent']
    assert cold['normalized_result'] == warm['normalized_result']
    assert any('Loaded from a local REA analysis snapshot' in x for x in warm['limitations'])
    assert not any('Loaded from a local REA analysis snapshot' in x for x in different['limitations'])
    assert all(e['subject']['digest']['sha256'] == EXPECTED for e in (cold, warm, different))
    assert cold['normalized_result']['procedure']['body']['total_bytes'] == 169
    normal = different['normalized_result']
    assert normal['procedure']['address'] == '0x476710'
    assert normal['procedure']['body']['ranges'] == [{'start': '0x476710', 'end': '0x476797'}]
    assert normal['procedure']['body']['total_bytes'] == 136
    assert [p['address'] for p in normal['callers']] == ['0x476170', '0x476810']
    assert not data(OUT / 'close.json').get('isError', False)
    assert status['timings']['function-different'] < status['timings']['function-cold']
    functions = [json.loads(line) for line in (INDEX / 'functions.jsonl').read_text().splitlines()]
    indexed = next(x for x in functions if x['entry_va'] == '00476710')
    assert indexed['ranges'] == [['00476710', '00476797']] and indexed['body_bytes'] == 136
    call_index = [json.loads(line) for line in (INDEX / 'calls.jsonl').read_text().splitlines()]
    assert {x['from_function'] for x in call_index if x.get('to_function') == '00476710'} == {'00476170', '00476810'}

    input_paths = [ROOT / 'local/game/Porsche.exe', INDEX / 'functions.jsonl', INDEX / 'calls.jsonl']
    source_paths = [ROOT / 'scripts/research/rea-mcp-session-308-004.mjs',
                    ROOT / 'scripts/research/run-v2-rea-mcp-session-308-004.py', Path(__file__),
                    ROOT / 'scripts/research/v2_shared_manifests.py']
    pins = externalize(ROOT, {'input_sha256': {rel(p): sha(p) for p in input_paths}}, 'input')
    pins = externalize(ROOT, {**pins, 'source_sha256': {rel(p): sha(p) for p in source_paths}}, 'source')
    reader = ManifestReader(ROOT)
    reader.verify(pins, 'input', expected_hash_mode='raw')
    reader.verify(pins, 'source', expected_hash_mode='raw')
    outputs = [OUT / p for p in ('events.jsonl', 'tools-list.json', 'function-cold.json',
               'function-warm.json', 'function-different.json', 'session-final.json',
               'server-stderr.log', 'status.json', 'receipt.json')]
    report = dict(schema=1, kind='rea-mcp-distinct-function-followup', status='PASS',
                  original_sha256=EXPECTED, server_pid=status['server_pid'],
                  analysis_run_id=ids[0], queries=['00476170', '00476170', '00476710'],
                  milliseconds={key: status['timings'][key] for key in
                                ('function-cold', 'function-warm', 'function-different')},
                  second_query_source='REA local analysis snapshot; provider did not rerun',
                  third_query_source='distinct function Evidence without snapshot limitation',
                  third_function_bytes=136, third_callers=['00476170', '00476810'],
                  index_match=True, same_mcp_session=True, target_unchanged=True,
                  live_ghidra_pid_observed=False, receipt=dict(path=rel(OUT / 'receipt.json'),
                  sha256=sha(OUT / 'receipt.json')), input_manifest=pins['input_manifest'],
                  source_manifest=pins['source_manifest'],
                  output_sha256={rel(p): sha(p) for p in outputs},
                  limitations=['Third query indicates retained provider state without rerunning cold import; Ghidra process identity was not observed',
                               'No IDE/root MCP registration was performed'])
    immutable(RUN / 'audit-004.json', report)
    print('PASS REA308-004: distinct native function in same MCP session; live Ghidra PID not observed')


if __name__ == '__main__':
    main()
