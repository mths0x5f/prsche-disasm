"""Batch audit for Run 420: Integration of Heap Shutdown (418) and Frame Root Lifecycle (419) into the game target."""
import collections
import hashlib
import json
from pathlib import Path
import re

from v2_shared_manifests import ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '420-game-link-integration'
BUILD = ROOT / 'local/builds/v2/game-link-integration-420'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_bytes())


EXPECTED_CLOSED = {
    '?app_loop_post_tick_pipeline_004b68f0@porsche@@YAXXZ',
    '?application_context_heap_selector_005e4fec@porsche@@YAIXZ',
    '?application_context_heap_state_005e4fe8@porsche@@YAPAXXZ',
    '?application_pool_shutdown_005678f0@porsche@@YAXXZ',
    '?context_selector_pointer_005e4fec@porsche@@YAPAXXZ',
    '?frame_service_root_00628960@porsche@@3IA',
    '?platform_flush_0059eb20@porsche@@YAXXZ',
    '?startup_sequence_call_00471b70@porsche@@YAXXZ',
}


def main():
    reader = ManifestReader(ROOT)
    s = load(RUN / 'build-002.json')
    _, pins = reader.verify(s, 'source', expected_hash_mode='crlf-to-lf')

    assert s['source_count'] == 188 and len(s['project_paths']) == 8 and s['input_unchanged']
    assert not s['compiler_errors'] and not s['other_linker_errors'] and not s['executable'] and not s['game_executed']
    assert s['exit_code'] == 1 and s['unresolved_names'] == 415 and s['unresolved_references'] == 446

    receipt = load(ROOT / s['receipt'])
    assert sha(ROOT / s['receipt']) == s['receipt_sha256']
    assert sha(ROOT / receipt['log']) == receipt['log_sha256'] and receipt['exit_code'] == 1

    text = (ROOT / receipt['log']).read_text(encoding='utf8')
    printed = collections.Counter(re.findall(r'(?m)^\s+([A-Za-z0-9_.-]+\.cpp)\s*$', text))
    assert printed == collections.Counter(Path(x).name for x in s['compiled_source_roots'])
    assert not any(Path(x).name == 'fixture.cpp' or 'original-body' in x for x in s['compiled_source_roots'])

    names = {item['symbol'] for item in s['frontier']}

    old = load(RUNS / '417-game-entry-integration/build-001.json')
    old_names = {x['symbol'] for x in old['frontier']}

    closed = old_names - names
    assert closed == EXPECTED_CLOSED, f'Mismatch in closed symbols: {closed ^ EXPECTED_CLOSED}'
    assert len(closed) == 8

    # Verify bridge objects exist
    bridge_objs = list(BUILD.glob('**/porsche_game_entry_bridges.dir/Release/*.obj'))
    assert len(bridge_objs) == 42

    reader.cache.check_stable()

    result = dict(
        schema=1,
        passed=True,
        fresh_compiler_sources=188,
        source_pins=len(pins),
        closed_game_names=sorted(closed),
        closed_names_count=len(closed),
        unresolved_names=s['unresolved_names'],
        unresolved_references=s['unresolved_references'],
        build_report_sha256=sha(RUN / 'build-002.json'),
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
