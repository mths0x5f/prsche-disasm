"""Archive explicitly approved bridge COFFs and link the actual cached game entry.

No compilation, providers, aliases or forced unresolved symbols are generated.
Native bridge proof packets are explicit inputs, not inferred from link success.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/289-game-startup-link'
LOCAL = ROOT / 'local/experiments/v2-game-startup-link-289'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--object', action='append', type=Path, required=True)
    parser.add_argument('--pin', action='append', type=Path, required=True)
    args = parser.parse_args()
    assert args.attempt.isascii() and args.attempt.replace('-', '').isalnum()
    out = LOCAL / args.attempt
    assert not out.exists(), 'Never overwrite an integration attempt'
    objects = [p.resolve() for p in args.object]
    assert len(set(objects)) == len(objects)
    assert all(p.suffix == '.obj' and p.is_file() for p in objects)
    proposal_path = ROOT / 'local/experiments/v2-game-entry-frontier-283/entry-link-proposal.json'
    proposal = json.loads(proposal_path.read_bytes())
    lib = Path(proposal['linker']).with_name('lib.exe')
    replay_path = ROOT / 'scripts/research/replay-v2-game-entry-285.py'
    inputs = [Path(__file__).resolve(), replay_path, proposal_path, lib,
              *objects, *[p.resolve() for p in args.pin]]
    pins = {str(p): sha(p) for p in inputs}
    out.mkdir(parents=True)
    RUN.mkdir(parents=True, exist_ok=True)
    rsp = out / 'objects.rsp'
    rsp.write_text(''.join('"' + str(p) + '"\n' for p in objects), encoding='utf8', newline='\n')
    archive = out / 'porsche_game_entry_bridges.lib'
    command = [str(lib), '/NOLOGO', '/MACHINE:X86', '/OUT:' + str(archive), '@' + str(rsp)]
    started = time.time()
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log_path = out / 'archive.log'
    log_path.write_bytes(result.stdout)
    receipt = dict(command=command, cwd=str(ROOT), started_unix=started,
                   seconds=time.time() - started, exit_code=result.returncode,
                   log=str(log_path.relative_to(ROOT)), log_sha256=sha(log_path),
                   input_sha256=pins)
    save(out / 'archive-receipt.json', receipt)
    assert result.returncode == 0, 'Archive failed; receipt preserved'
    assert all(sha(p) == value for p, value in pins.items()), 'Integration input changed'
    spec = importlib.util.spec_from_file_location('entry_replay285', replay_path)
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    replay.RUN = RUN
    replay.LOCAL = out / 'entry-link'
    sys.argv = [str(replay_path), '--attempt', args.attempt, '--extra-library', str(archive)]
    replay.main()
    assert all(sha(p) == value for p, value in pins.items()), 'Integration input changed during link'
    link_summary = RUN / (args.attempt + '.json')
    summary = dict(schema=1, kind='game-entry-bridge-integration', attempt=args.attempt,
                   input_sha256=pins, compiler_commands=0, archive_commands=1, link_commands=1,
                   archive=str(archive.relative_to(ROOT)), archive_sha256=sha(archive),
                   archive_receipt=str((out / 'archive-receipt.json').relative_to(ROOT)),
                   archive_receipt_sha256=sha(out / 'archive-receipt.json'),
                   entry_link=str(link_summary.relative_to(ROOT)), entry_link_sha256=sha(link_summary),
                   game_objects=[str(p.relative_to(ROOT)) for p in objects],
                   game_executed=False, original_behavior_acceptance=False)
    save(RUN / (args.attempt + '-integration.json'), summary)


if __name__ == '__main__':
    main()
