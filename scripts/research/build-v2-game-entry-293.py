"""Capture a fresh current-source CMake game-target build; never execute the game."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

from v2_build_graph import compiled_sources, projects, cmake_inputs
from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/293-game-startup-followup'
BUILD = ROOT / 'local/builds/v2/game-startup-followup-293'
OUT = ROOT / 'local/experiments/v2-game-startup-followup-293'
CMAKE = ROOT / 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def capture(command, name):
    receipt = OUT / (name + '.receipt.json')
    log = OUT / (name + '.log')
    assert not receipt.exists() and not log.exists(), 'Do not overwrite attempts'
    start = time.time()
    result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, VSLANG='1033'),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log.write_bytes(result.stdout)
    record = dict(command=list(map(str, command)), cwd=str(ROOT), started_unix=start,
                  seconds=time.time() - start, exit_code=result.returncode,
                  log=log.relative_to(ROOT).as_posix(), log_sha256=sha(log))
    save(receipt, record)
    return result, record, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['configure', 'build'], required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    assert args.attempt.replace('-', '').isalnum() and args.attempt.isascii()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.phase == 'configure':
        command = [str(CMAKE), '-S', str(RUN), '-B', str(BUILD), '-G', 'Visual Studio 17 2022', '-A', 'Win32']
        result, record, receipt = capture(command, 'configure-' + args.attempt)
        print(json.dumps(record))
        assert result.returncode == 0, 'Configure failed; receipt preserved'
        return
    assert not (OUT / ('before-' + args.attempt + '.json')).exists(), 'Unique build attempts only'
    assert not (RUN / ('build-' + args.attempt + '.json')).exists(), 'Completed summary exists'
    entries = list(BUILD.rglob('porsche_original_game_link.vcxproj'))
    assert len(entries) == 1, 'Resolve the explicit excluded target, not ALL_BUILD'
    sources = compiled_sources(entries[0].parent, 'porsche_original_game_link')
    graph = projects(entries[0].parent, 'porsche_original_game_link')
    extras = [Path(__file__), RUN / 'CMakeLists.txt', RUN / 'logging-literal.json',
              RUN.parent / '289-game-startup-link/CMakeLists.txt',
              RUN.parent / '289-game-startup-link/bridge-sources.cmake',
              RUN.parent / '102-original-game-link/CMakeLists.txt',
              ROOT / 'scripts/research/v2_build_graph.py',
              *[ROOT / p for p in cmake_inputs()]]
    pins = source_hashes(extras, compiled_sources=sources)
    command = [str(CMAKE), '--build', str(BUILD), '--config', 'Release',
               '--target', 'porsche_original_game_link', '--parallel', '4']
    save(OUT / ('before-' + args.attempt + '.json'), dict(source_sha256=pins, source_count=len(sources)))
    result, receipt, receipt_path = capture(command, 'build-' + args.attempt)
    # Preserve compiler/linker results before inspecting or asserting their content.
    log = result.stdout.decode('utf8', errors='replace')
    frontier = {}
    other = []
    compiler = []
    for line in log.splitlines():
        if re.search(r'\berror LNK(?:2001|2019):', line):
            symbols = re.findall(r'\((\?[^()]+)\)', line)
            assert symbols, line
            frontier.setdefault(symbols[0], []).append(dict(caller=symbols[1] if len(symbols) > 1 else None, diagnostic=line))
        elif re.search(r'\b(?:fatal )?error LNK\d+:', line) and 'LNK1120:' not in line:
            other.append(line)
        elif re.search(r'\b(?:fatal )?error C\d+:', line):
            compiler.append(line)
    after = source_hashes(extras, compiled_sources=sources)
    output = BUILD / 'bin/Release/porsche_original_game_link.exe'
    summary = dict(schema=1, kind='fresh-current-source-game-entry-build', attempt=args.attempt,
                   source_sha256=pins, source_hash_normalization='CRLF to LF, v2_source_dependencies convention',
                   project_paths=[p.relative_to(ROOT).as_posix() for p in graph],
                   compiled_source_roots=sources, source_count=len(sources),
                   input_unchanged=pins == after, receipt=receipt_path.relative_to(ROOT).as_posix(),
                   receipt_sha256=sha(receipt_path), exit_code=result.returncode,
                   seconds=receipt['seconds'], unresolved_names=len(frontier),
                   unresolved_references=sum(map(len, frontier.values())),
                   frontier=[dict(symbol=k, references=v) for k, v in sorted(frontier.items())],
                   compiler_errors=compiler, other_linker_errors=other,
                   executable=output.relative_to(ROOT).as_posix() if output.is_file() else None,
                   game_executed=False, whole_game_acceptance=False)
    save(RUN / ('build-' + args.attempt + '.json'), summary)
    print(json.dumps({k: summary[k] for k in ('exit_code', 'seconds', 'source_count', 'unresolved_names', 'unresolved_references', 'executable', 'input_unchanged')}))
    assert pins == after, 'Source changed during build; receipt preserved'


if __name__ == '__main__':
    main()
