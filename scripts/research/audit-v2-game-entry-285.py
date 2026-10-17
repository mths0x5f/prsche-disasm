"""Read-only recheck of the two cached normal-entry link attempts."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/285-normal-entry-replay'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    frontiers = []
    checked = {}
    searched = {}
    for attempt in ('cached-001', 'candidates-002'):
        p = RUN / (attempt + '.json')
        summary = json.loads(p.read_bytes())
        receipt_path = ROOT / summary['receipt']
        assert sha(receipt_path) == summary['receipt_sha256']
        receipt = json.loads(receipt_path.read_bytes())
        assert receipt['exit_code'] == summary['exit_code'] == 1120
        assert not receipt['game_executed'] and not summary['linked_executable']
        assert summary['compiler_commands'] == 0 and summary['link_commands'] == 1
        assert not any(x.upper().startswith(('/WHOLEARCHIVE', '/NOENTRY', '/ENTRY:', '/FORCE')) for x in receipt['args'])
        expected_rsp = '\n'.join('"' + x + '"' if ' ' in x else x for x in receipt['args']) + '\n'
        rsp = Path(receipt['command'][1][1:])
        assert rsp.read_bytes() == expected_rsp.encode('utf8')
        for name, value in receipt['input_sha256'].items():
            assert sha(name) == value, name
            checked[name] = value
        log_path = ROOT / receipt['log']
        assert sha(log_path) == receipt['log_sha256']
        log = log_path.read_text(encoding='utf8')
        lines = [x for x in log.splitlines() if re.search(r'\bLNK(?:2001|2019):', x)]
        names = {re.findall(r'\((\?[^()]+)\)', x)[0] for x in lines}
        assert len(names) == summary['unresolved_names'] == 267
        assert len(lines) == summary['unresolved_references'] == 303
        assert names == {x['symbol'] for x in summary['frontier']}
        assert not summary['other_linker_diagnostics']
        assert not (log_path.parent / 'porsche_game.exe').exists()
        frontiers.append(names)
        for line in log.splitlines():
            match = re.fullmatch(r'\s*(?:Searching|Поиск)\s+([A-Za-z]:.*\.lib):\s*', line)
            if match:
                lib = Path(match.group(1))
                assert lib.is_file(), str(lib)
                searched[str(lib)] = sha(lib)
        for q in (p, receipt_path, log_path, rsp):
            checked[str(q)] = sha(q)
    assert frontiers[0] == frontiers[1]
    candidate = ROOT / 'local/experiments/v2-native-union-274/porsche_native_union_candidates.lib'
    old = json.loads((ROOT / 'iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json').read_bytes())
    assert sha(candidate) == old['library']['sha256']
    assert str(candidate) in searched, 'Candidate archive was not searched by the linker'
    assert len(searched) >= 20
    report = dict(schema=1, passed=True, input_sha256=checked,
                  audit_script_sha256=sha(__file__), searched_library_sha256=searched,
                  searched_library_pin_timing='Read-only audit after preserved link attempts; replay summaries retain empty English-only search extraction',
                  candidate_archive_actually_searched=True, same_frontier=True,
                  unresolved_names=267, unresolved_references=303,
                  compiler_commands=0, link_attempts=2, game_executed=False)
    (RUN / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(passed=True, input_pins=len(checked), searched_libraries=len(searched),
                          unresolved_names=267, unresolved_references=303, candidate_frontier_change=0)))


if __name__ == '__main__':
    main()
