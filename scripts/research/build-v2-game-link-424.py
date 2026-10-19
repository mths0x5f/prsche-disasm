"""Capture a fresh current-source CMake game-target build for Run 424; never execute the game."""
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
from v2_shared_manifests import ManifestReader, externalize

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/424-input-audio-game-integration'
RUN420 = ROOT / 'iterations/v2/001-original-recovery/runs/420-game-link-integration'
BUILD = ROOT / 'local/builds/v2/input-audio-integration-424'
OUT = ROOT / 'local/experiments/v2-input-audio-integration-424'

# Resolve CMake
CMAKE_CANDIDATES = [
    ROOT / 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe',
    Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'),
    Path('C:/Program Files/Microsoft Visual Studio/2022/Community/Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'),
]
CMAKE = next((c for c in CMAKE_CANDIDATES if c.is_file()), Path('cmake.exe'))


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


UNRESOLVED_RE = re.compile(
    r'(?:s[íi]mbolo externo n[ãa]o resolvido|unresolved external symbol)[,\s]+(.*)$', re.I)
CALLER_RE = re.compile(
    r'(?:referenciad[oa] na fun[çc][ãa]o|referenced in function)\s+(.*)$', re.I)


def parse_unresolved(line):
    """Return (missing_symbol, caller) from one LNK2001/LNK2019 diagnostic.

    The missing symbol is whatever follows "unresolved external symbol": a quoted
    demangled name followed by its "(?decorated)" form, or a bare C-linkage name.
    The caller is read only after "referenced in function". Taking the first
    "(?decorated)" on the line instead would report the caller as missing
    whenever the missing symbol has C linkage.
    """
    m = UNRESOLVED_RE.search(line)
    assert m, f'Cannot parse LNK symbol from: {line}'
    rest = m.group(1)
    if rest.startswith('"'):
        close = rest.find('"', 1)
        assert close > 0, f'Unterminated quoted symbol in: {line}'
        tail = rest[close + 1:]
        decorated = re.match(r'\s*\((\?[^()]+)\)', tail)
        symbol = decorated.group(1) if decorated else rest[1:close]
        after = tail[decorated.end():] if decorated else tail
    else:
        symbol = re.split(r'[,\s]', rest, maxsplit=1)[0]
        after = rest[len(symbol):]
    caller = None
    c = CALLER_RE.search(after)
    if c:
        text = c.group(1)
        decorated = re.search(r'\((\?[^()]+)\)', text)
        caller = decorated.group(1) if decorated else re.split(r'[\s\[]', text.strip().strip('"'), maxsplit=1)[0]
    assert symbol, f'Empty LNK symbol in: {line}'
    return symbol, caller


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['configure', 'build'], required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    assert args.attempt.replace('-', '').isalnum() and args.attempt.isascii()
    OUT.mkdir(parents=True, exist_ok=True)
    generator = 'Visual Studio 18 2026' if Path('C:/Program Files/Microsoft Visual Studio/18').is_dir() else 'Visual Studio 17 2022'
    if args.phase == 'configure':
        command = [str(CMAKE), '-S', str(RUN), '-B', str(BUILD), '-G', generator, '-A', 'Win32']
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
    extras = [Path(__file__), RUN / 'CMakeLists.txt', RUN420 / 'CMakeLists.txt', RUN420 / 'entry_bridges_420.cpp',
              RUN.parent / '417-game-entry-integration/CMakeLists.txt',
              RUN.parent / '417-game-entry-integration/entry_bridges_417.cpp',
              RUN.parent / '418-heap-shutdown-closure/heap_shutdown_418.hpp',
              RUN.parent / '418-heap-shutdown-closure/heap_shutdown_418.cpp',
              RUN.parent / '419-frame-root-lifecycle/frame_root_lifecycle_419.hpp',
              RUN.parent / '419-frame-root-lifecycle/frame_root_lifecycle_419.cpp',
              RUN.parent / '421-audio-backend-lock-pool/audio_backend_lock_pool_421.hpp',
              RUN.parent / '421-audio-backend-lock-pool/audio_backend_lock_pool_421.cpp',
              RUN.parent / '422-audio-channel-voice-lookup/audio_channel_voice_lookup_422.hpp',
              RUN.parent / '422-audio-channel-voice-lookup/audio_channel_voice_lookup_422.cpp',
              RUN.parent.parent / 'source/platform/win32_input.cpp',
              RUN.parent / '298-frame-game-integration/CMakeLists.txt',
              RUN.parent / '293-game-startup-followup/logging-literal.json',
              RUN.parent / '293-game-startup-followup/CMakeLists.txt',
              ROOT / 'scripts/research/v2_shared_manifests.py',
              ROOT / 'scripts/research/v2_proof_cache.py',
              RUN.parent / '289-game-startup-link/CMakeLists.txt',
              RUN.parent / '289-game-startup-link/bridge-sources.cmake',
              RUN.parent / '102-original-game-link/CMakeLists.txt',
              ROOT / 'scripts/research/v2_build_graph.py',
              *[ROOT / p for p in cmake_inputs()]]
    pins = source_hashes(extras, compiled_sources=sources)
    command = [str(CMAKE), '--build', str(BUILD), '--clean-first', '--config', 'Release',
               '--target', 'porsche_original_game_link', '--parallel', '6']
    before = externalize(ROOT, dict(schema=2, source_sha256=pins, source_count=len(sources)), 'source', 'crlf-to-lf')
    reader = ManifestReader(ROOT)
    reader.verify(before, 'source', expected_hash_mode='crlf-to-lf')
    save(OUT / ('before-' + args.attempt + '.json'), before)
    result, receipt, receipt_path = capture(command, 'build-' + args.attempt)
    # Preserve compiler/linker results before inspecting or asserting their content.
    log = result.stdout.decode('utf8', errors='replace')
    frontier = {}
    other = []
    compiler = []
    for line in log.splitlines():
        if re.search(r'\berror LNK(?:2001|2019):', line):
            symbol, caller = parse_unresolved(line)
            frontier.setdefault(symbol, []).append(dict(caller=caller, diagnostic=line))
        elif re.search(r'\b(?:fatal )?error LNK\d+:', line) and 'LNK1120:' not in line:
            other.append(line)
        elif re.search(r'\b(?:fatal )?error C\d+:', line):
            compiler.append(line)
    after = source_hashes(extras, compiled_sources=sources)
    output = BUILD / 'bin/Release/porsche_original_game_link.exe'
    summary = dict(schema=2, kind='grouped-frame-current-source-game-entry-build', attempt=args.attempt,
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
    summary = externalize(ROOT, summary, 'source', 'crlf-to-lf', before['source_manifest'])
    reader.verify(summary, 'source', expected_hash_mode='crlf-to-lf')
    reader.cache.check_stable()
    save(RUN / ('build-' + args.attempt + '.json'), summary)
    print(json.dumps({k: summary[k] for k in ('exit_code', 'seconds', 'source_count', 'unresolved_names', 'unresolved_references', 'executable', 'input_unchanged')}))
    assert pins == after, 'Source changed during build; receipt preserved'


if __name__ == '__main__':
    main()
