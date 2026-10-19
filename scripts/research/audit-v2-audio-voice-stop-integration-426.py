"""Independent audit for Run 426 (audio voice stop game-target integration).

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
RUN = RUNS / '426-audio-voice-stop-game-integration'

CLOSED = {
    '?application_audio_backend_release_0058ac30@porsche@@YAXI@Z',
    '?audio_backend_stop_voice_0058a8b0@porsche@@YAXI@Z',
}
NEW_BOUNDARIES = {
    '?audio_backend_stamp_006b49a8@porsche@@3IA',
    '?audio_voice_table_006b489c@porsche@@3IA',
}


def main():
    spec = importlib.util.spec_from_file_location('b426', ROOT / 'scripts/research/build-v2-game-link-426.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)

    s = json.loads((RUN / 'build-001.json').read_text(encoding='utf-8'))
    assert s['source_count'] == 192 and s['input_unchanged']
    assert not s['compiler_errors'] and not s['other_linker_errors'] and not s['game_executed']
    assert s['unresolved_names'] == 412 and s['unresolved_references'] == 439

    log = json.loads((ROOT / s['receipt']).read_text(encoding='utf-8'))['log']
    rederived = collections.Counter()
    for line in (ROOT / log).read_text(encoding='utf-8', errors='replace').splitlines():
        if re.search(r'\berror LNK(?:2001|2019):', line):
            symbol, caller = build.parse_unresolved(line)
            assert symbol != caller
            rederived[symbol] += 1
    assert dict(rederived) == {f['symbol']: len(f['references']) for f in s['frontier']}

    old = {f['symbol'] for f in json.loads(
        (RUNS / '424-input-audio-game-integration/build-001.json').read_text(encoding='utf-8'))['frontier']}
    new = set(rederived)
    assert old - new == CLOSED, sorted((old - new) ^ CLOSED)
    assert new - old == NEW_BOUNDARIES, sorted((new - old) ^ NEW_BOUNDARIES)
    assert len(old) - len(CLOSED) + len(NEW_BOUNDARIES) == len(new) == 412

    print('Run 426 verified: 192 sources, 0 compiler / 0 other linker errors; frontier re-derived '
          'from the log; 412 names kept (2 closed, 2 new storage boundaries), 436 -> 439 references')


if __name__ == '__main__':
    main()
