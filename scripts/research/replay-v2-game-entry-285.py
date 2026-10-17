"""Replay the existing normal WinMain link from cached objects; never run the EXE."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/285-normal-entry-replay'
LOCAL = ROOT / 'local/experiments/v2-normal-entry-replay-285'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proposal', type=Path, default=ROOT / 'local/experiments/v2-game-entry-frontier-283/entry-link-proposal.json')
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--extra-library', type=Path)
    args = parser.parse_args()
    assert re.fullmatch(r'[a-zA-Z0-9-]+', args.attempt)
    out = LOCAL / args.attempt
    assert not out.exists(), 'Never overwrite link attempts'
    proposal = json.loads(args.proposal.read_bytes())
    command_args = proposal['args'][:]
    assert not any(x.upper().startswith(('/WHOLEARCHIVE', '/NOENTRY', '/ENTRY:', '/FORCE')) for x in command_args)
    explicit = [Path(x) for x in command_args if not x.startswith('/') and Path(x).is_absolute()]
    if args.extra_library:
        extra = args.extra_library.resolve()
        assert extra.is_file()
        command_args.append(str(extra))
        explicit.append(extra)
    out.mkdir(parents=True)
    RUN.mkdir(parents=True, exist_ok=True)
    command_args = [('/OUT:' + str(out / 'porsche_game.exe')) if x.upper().startswith('/OUT:') else
                    ('/MAP:' + str(out / 'porsche_game.map')) if x.upper().startswith('/MAP:') else x
                    for x in command_args]
    rsp = out / 'link.rsp'
    rsp.write_text('\n'.join('"' + x + '"' if ' ' in x else x for x in command_args) + '\n', encoding='utf8', newline='\n')
    inputs = [args.proposal.resolve(), Path(proposal['linker']), *explicit, Path(__file__).resolve()]
    pins = {str(p): sha(p) for p in inputs}
    command = [proposal['linker'], '@' + str(rsp)]
    env = dict(os.environ, VSLANG='1033')
    started = time.time()
    result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    elapsed = time.time() - started
    log_path = out / 'link.log'
    log_path.write_bytes(result.stdout)
    # Receipt is durable before any parsing or success assertions.
    receipt = dict(command=command, cwd=str(ROOT), args=command_args, started_unix=started,
                   seconds=elapsed, exit_code=result.returncode, log=str(log_path.relative_to(ROOT)),
                   log_sha256=sha(log_path), input_sha256=pins, game_executed=False)
    save(out / 'receipt.json', receipt)
    assert all(sha(p) == value for p, value in pins.items()), 'Input changed during link'
    log = result.stdout.decode('utf8', errors='replace')
    frontier = {}
    other = []
    for line in log.splitlines():
        if re.search(r'\b(?:error|fatal error) LNK(?:2001|2019):', line):
            decorated = re.findall(r'\((\?[^()]+)\)', line)
            if decorated:
                symbol = decorated[0]
                caller = decorated[1] if len(decorated) > 1 else None
            else:
                match = re.search(r'unresolved external symbol\s+(\S+)', line)
                symbol = match.group(1) if match else None
                caller = None
            assert symbol, line
            frontier.setdefault(symbol, []).append(dict(caller=caller, diagnostic=line))
        elif re.search(r'\b(?:error|fatal error) LNK\d+:', line) and 'LNK1120:' not in line:
            other.append(line)
    resolved_libs = {}
    for line in log.splitlines():
        value = line.strip()
        # /VERBOSE:LIB lists searched absolute archive paths, optionally with a colon.
        if value.lower().startswith('searching '):
            candidate = Path(value[10:].rstrip(':'))
            if candidate.is_file():
                resolved_libs[str(candidate)] = sha(candidate)
    summary = dict(schema=1, kind='normal-entry-cached-link-diagnostic', attempt=args.attempt,
                   wholearchive=False, explicit_entry_override=False, compiler_commands=0,
                   link_commands=1, game_executed=False, game_playability_verified=False,
                   cached_input_scope='Existing recovered library graph; not a fresh full source rebuild',
                   input_sha256=pins, searched_library_sha256=resolved_libs,
                   receipt=str((out / 'receipt.json').relative_to(ROOT)), receipt_sha256=sha(out / 'receipt.json'),
                   unresolved_names=len(frontier), unresolved_references=sum(map(len, frontier.values())),
                   frontier=[dict(symbol=k, references=v) for k, v in sorted(frontier.items())],
                   other_linker_diagnostics=other, exit_code=result.returncode, seconds=elapsed,
                   linked_executable=str((out / 'porsche_game.exe').relative_to(ROOT)) if (out / 'porsche_game.exe').is_file() else None,
                   limits=['Original pre-WinMain initialization remains unproved (284/286)',
                           'Diagnostic linking does not accept candidate behavior or ABI contracts'])
    save(RUN / (args.attempt + '.json'), summary)
    print(json.dumps({k: summary[k] for k in ('attempt','exit_code','seconds','unresolved_names','unresolved_references','linked_executable')}))


if __name__ == '__main__':
    main()
