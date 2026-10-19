"""Independent audit for Run 424 (input/audio game-target integration).

Re-derives the link frontier from the captured log with the producer's parser,
requires it to match the report, and checks the exact difference against Run
420's build-003: the 17 contracts Runs 421-423 and win32_input.cpp close, and
the 6 new names, which must be exactly the storage cells those runs leave as
declared boundaries.
"""
import collections
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '424-input-audio-game-integration'

CLOSED = {
    '?application_audio_backend_close_0058aac0@porsche@@YAHXZ',
    '?application_audio_backend_configure_0058aa90@porsche@@YAXII@Z',
    '?application_audio_backend_configure_0058fef0@porsche@@YAXII@Z',
    '?application_audio_backend_quiet_0058ff10@porsche@@YAXXZ',
    '?application_audio_backend_start_0058e2d0@porsche@@YAXXZ',
    '?application_audio_backend_stop_0058e2e0@porsche@@YAXXZ',
    '?audio_backend_find_channel_00589d20@porsche@@YAHI@Z',
    '?audio_backend_lock_005896d0@porsche@@YAXXZ',
    '?audio_backend_next_voice_00590340@porsche@@YAIHPAI@Z',
    '?audio_backend_unlock_005896f0@porsche@@YAXXZ',
    '?input_invalid_type_00532eae@porsche@@YAXI@Z',
    '?input_unrecovered_mode_00532e10@porsche@@YAPAXIIPAUInputSlot@1@@Z',
    '?startup_get_keyboard_type@porsche@@YAII@Z',
    '?startup_input_direct_input_create@porsche@@YGHPAXIPAPAX0@Z',
    '?startup_input_get_module_handle@porsche@@YGPAXXZ',
    '?startup_joy_get_dev_caps@porsche@@YAIIPAXI@Z',
    '?startup_joy_get_num_devs@porsche@@YAHXZ',
}
NEW_BOUNDARIES = {
    '?audio_backend_channel_count_006b49a4@porsche@@3FA',
    '?audio_backend_channels_006b4a00@porsche@@3IA',
    '?audio_backend_lock_cs_006b1800@porsche@@3PAEA',
    '?audio_backend_lock_depth_006b499f@porsche@@3EA',
    '?audio_backend_pool_006b4a18@porsche@@3IA',
    '?input_caps_buffer_006bde20@porsche@@3PAEA',
}


def main():
    spec = importlib.util.spec_from_file_location('b424', ROOT / 'scripts/research/build-v2-game-link-424.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)

    s = json.loads((RUN / 'build-001.json').read_text(encoding='utf-8'))
    assert s['source_count'] == 191 and s['input_unchanged']
    assert not s['compiler_errors'] and not s['other_linker_errors'] and not s['game_executed']
    assert s['unresolved_names'] == 412 and s['unresolved_references'] == 436

    log = json.loads((ROOT / s['receipt']).read_text(encoding='utf-8'))['log']
    rederived = collections.Counter()
    for line in (ROOT / log).read_text(encoding='utf-8', errors='replace').splitlines():
        if re.search(r'\berror LNK(?:2001|2019):', line):
            symbol, caller = build.parse_unresolved(line)
            assert symbol != caller
            rederived[symbol] += 1
    assert dict(rederived) == {f['symbol']: len(f['references']) for f in s['frontier']}

    old = {f['symbol'] for f in json.loads(
        (RUNS / '420-game-link-integration/build-003.json').read_text(encoding='utf-8'))['frontier']}
    new = set(rederived)
    assert old - new == CLOSED, sorted((old - new) ^ CLOSED)
    assert new - old == NEW_BOUNDARIES, sorted((new - old) ^ NEW_BOUNDARIES)
    assert len(old) - len(CLOSED) + len(NEW_BOUNDARIES) == len(new) == 412

    print('Run 424 verified: 191 sources, 0 compiler / 0 other linker errors; frontier re-derived '
          'from the log; 423 -> 412 names (17 closed, 6 new storage boundaries); no EXE, game not run')


if __name__ == '__main__':
    main()
