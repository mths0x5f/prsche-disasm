"""Batch audit for Run 417: Integration of recovered frame/loop/app_main functions into the game target."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re

from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '417-game-entry-integration'
BUILD = ROOT / 'local/builds/v2/game-entry-integration-417'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_bytes())


EXPECTED_CLOSED = {
    '?application_main_function_00412030@porsche@@YAXXZ',
    '?application_main_function_00413ea0@porsche@@YAXXZ',
    '?application_main_function_00414eb0@porsche@@YAXXZ',
    '?application_main_function_00425780@porsche@@YAXXZ',
    '?application_main_function_004640b0@porsche@@YAXXZ',
    '?application_main_function_00467740@porsche@@YAXXZ',
    '?application_main_function_0048cdf0@porsche@@YAXXZ',
    '?application_main_function_004a54b0@porsche@@YAXXZ',
    '?application_main_function_004a54e0@porsche@@YAXXZ',
    '?application_main_function_004a88a0@porsche@@YAXXZ',
    '?application_main_function_004acb80@porsche@@YAXXZ',
    '?application_main_function_004b68f0@porsche@@YAXXZ',
    '?application_main_function_00563d30@porsche@@YAXXZ',
    '?application_network_change_0048e1a0@porsche@@YIXPAX0III@Z',
    '?game_setup_resource_file_open_0059d8e0@porsche@@YAPAXPBDI@Z',
    '?heap_fill_0053c290@porsche@@YAXPAXII@Z',
    '?render_display_texture_report_005a177b@porsche@@YAXPBDI@Z',
    '?resource_invalid_module_path_0059d650@porsche@@YAXPBD@Z',
    '?splash_progress_load_resource_0059d8e0@porsche@@YAPAXPBDI@Z',
    '?startup_sequence_call_0048cdf0@porsche@@YAXXZ',
    '?startup_sequence_report_005a177b@porsche@@YAXII@Z',
}


def main():
    reader = ManifestReader(ROOT)
    s = load(RUN / 'build-001.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')

    assert s['source_count'] == 185 and len(s['project_paths']) == 8 and s['input_unchanged']
    assert not s['compiler_errors'] and not s['other_linker_errors'] and not s['executable'] and not s['game_executed']
    assert s['exit_code'] == 1 and s['unresolved_names'] == 348 and s['unresolved_references'] == 381

    receipt = load(ROOT / s['receipt'])
    assert sha(ROOT / s['receipt']) == s['receipt_sha256']
    assert sha(ROOT / receipt['log']) == receipt['log_sha256'] and receipt['exit_code'] == 1

    text = (ROOT / receipt['log']).read_text(encoding='utf8')
    printed = collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', text))
    assert printed == collections.Counter(Path(x).name for x in s['compiled_source_roots'])
    assert not any(Path(x).name == 'fixture.cpp' or 'original-body' in x for x in s['compiled_source_roots'])

    diagnostics = [line for line in text.splitlines() if re.search(r'\berror LNK(?:2001|2019):', line)]
    names = {re.findall(r'\((\?[^()]+)\)', line)[0] for line in diagnostics}

    old = load(RUNS / '298-frame-game-integration/build-002.json')
    old_names = {x['symbol'] for x in old['frontier']}

    closed = old_names - names
    assert closed == EXPECTED_CLOSED, f'Mismatch in closed symbols: {closed ^ EXPECTED_CLOSED}'
    assert len(closed) == 21

    # Verify bridge objects exist
    bridge_objs = list(BUILD.glob('**/porsche_game_entry_bridges.dir/Release/*.obj'))
    assert len(bridge_objs) == 39

    reader.cache.check_stable()

    result = dict(
        schema=1,
        passed=True,
        fresh_compiler_sources=185,
        source_pins=len(pins),
        closed_game_names=sorted(closed),
        closed_names_count=len(closed),
        unresolved_names=s['unresolved_names'],
        unresolved_references=s['unresolved_references'],
        build_report_sha256=sha(RUN / 'build-001.json'),
        game_executed=False,
    )
    output = RUN / 'validation.json'
    if output.exists():
        assert load(output) == result, 'Completed audit content changed'
    else:
        output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')

    print(json.dumps({k: result[k] for k in ('passed', 'fresh_compiler_sources', 'source_pins', 'closed_names_count', 'unresolved_names', 'unresolved_references')}))


if __name__ == '__main__':
    main()
