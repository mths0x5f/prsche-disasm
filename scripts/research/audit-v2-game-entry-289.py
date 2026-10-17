"""Verify the captured normal-entry integration without rebuilding or execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/289-game-startup-link'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_bytes())


def main():
    integration_path = RUN / 'logging-frame-001-integration.json'
    integration = load(integration_path)
    checked = {}
    for name, value in integration['input_sha256'].items():
        assert sha(name) == value, name
        checked[name] = value
    for key in ('archive', 'archive_receipt', 'entry_link'):
        assert sha(ROOT / integration[key]) == integration[key + '_sha256']
    archive_receipt = load(ROOT / integration['archive_receipt'])
    assert archive_receipt['exit_code'] == 0
    assert sha(ROOT / archive_receipt['log']) == archive_receipt['log_sha256']
    for name, value in archive_receipt['input_sha256'].items():
        assert sha(name) == value, name
    link = load(ROOT / integration['entry_link'])
    receipt_path = ROOT / link['receipt']
    assert sha(receipt_path) == link['receipt_sha256']
    receipt = load(receipt_path)
    assert receipt['exit_code'] == link['exit_code'] == 1120
    for name, value in receipt['input_sha256'].items():
        assert sha(name) == value, name
        checked[name] = value
    assert not any(x.upper().startswith(('/WHOLEARCHIVE', '/NOENTRY', '/ENTRY:', '/FORCE')) for x in receipt['args'])
    log_path = ROOT / receipt['log']
    assert sha(log_path) == receipt['log_sha256']
    log = log_path.read_text(encoding='utf8')
    lines = [x for x in log.splitlines() if re.search(r'\bLNK(?:2001|2019):', x)]
    names = {re.findall(r'\((\?[^()]+)\)', x)[0] for x in lines}
    assert len(names) == link['unresolved_names'] == 270
    assert len(lines) == link['unresolved_references'] == 306
    assert names == {x['symbol'] for x in link['frontier']}
    assert not link['other_linker_diagnostics'] and not link['linked_executable']
    assert not (log_path.parent / 'porsche_game.exe').exists()
    baseline = load(ROOT / 'iterations/v2/001-original-recovery/runs/285-normal-entry-replay/cached-001.json')
    old_names = {x['symbol'] for x in baseline['frontier']}
    removed = sorted(old_names - names)
    added = sorted(names - old_names)
    assert removed == ['?application_main_function_00471b60@porsche@@YAXXZ', '?application_main_log@porsche@@YAXPBD@Z']
    assert len(added) == 5 and any('resolve_004898f0' in x for x in added)
    direct = sum(any(r['caller'] == '?app_main_004b6a50@porsche@@YAHHPAPAD@Z' for r in x['references']) for x in link['frontier'])
    assert direct == 18
    spec = importlib.util.spec_from_file_location('coff289', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    coff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(coff)
    definitions = []
    assert len(integration['game_objects']) == 4
    for name in integration['game_objects']:
        assert 'fixture' not in Path(name).name.lower()
        symbols = coff.coff_symbols(ROOT / name)
        assert not symbols['weak'] and not symbols['common']
        definitions.extend(symbols['defined'])
    assert len(definitions) == len(set(definitions)) == 12
    assert set(removed) <= set(definitions)
    assert not any('frame_service_root_00628960' in x for x in definitions)
    searched = {}
    for line in log.splitlines():
        match = re.fullmatch(r'\s*(?:Searching|Поиск)\s+([A-Za-z]:.*\.lib):\s*', line)
        if match:
            searched[match.group(1)] = sha(match.group(1))
    assert str(ROOT / integration['archive']) in searched
    validation = dict(schema=1, passed=True, audit_sha256=sha(__file__),
                      integration_sha256=sha(integration_path), input_sha256=checked,
                      searched_library_sha256=searched, game_objects=4,
                      unique_defined_symbols=12, unresolved_names=270,
                      unresolved_references=306, direct_app_main_unresolved=18,
                      removed_symbols=removed, exposed_symbols=added,
                      compiler_commands=0, game_executed=False)
    (RUN / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(passed=True, input_pins=len(checked), unresolved_names=270,
                          direct_app_main_unresolved=18, removed=2, exposed=5)))


if __name__ == '__main__':
    main()
