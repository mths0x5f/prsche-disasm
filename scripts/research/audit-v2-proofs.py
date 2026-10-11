"""One batched SHA audit for all current function and integration proofs."""
import argparse
import json
from pathlib import Path
import subprocess

from v2_proof_cache import ProofCache

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path,
                        default=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    cache = ProofCache()
    registry = cache.document(args.registry)
    reports = {f[k] for f in registry['functions'] for k in
               ('verification_report', 'integration_verification_report') if f.get(k)}
    expected = {}
    for name in sorted(reports):
        proof = cache.document(ROOT/name)
        if proof.get('native_cpp_equal_original_x86') is not True:
            raise RuntimeError(f'Proof does not claim equality: {name}')
        for source, sha in proof['source_sha256'].items():
            if source in expected and expected[source] != sha:
                raise RuntimeError(f'Conflicting current dependency pins: {source}')
            expected[source] = sha
    for source, sha in sorted(expected.items()):
        if cache.digest(ROOT/source) != sha:
            raise RuntimeError(f'Stale proof dependency: {source}')
    tools = ('scripts/research/audit-v2-proofs.py', 'scripts/research/v2_proof_cache.py')
    tool_hashes = {name:cache.digest(ROOT/name) for name in tools}
    cache.check_stable()
    output = args.report.resolve()
    if output in { (ROOT/name).resolve() for name in reports } or output in {
        (ROOT/name).resolve() for name in expected }:
        raise RuntimeError('Audit output cannot overwrite a proof or dependency')
    tracked = subprocess.run(['git','ls-files','--error-unmatch','--',output.relative_to(ROOT).as_posix()],
                             cwd=ROOT,capture_output=True)
    if tracked.returncode == 0:
        raise RuntimeError('Choose a fresh report; committed audits are immutable')
    result = {'schema':1, 'all_current_source_pins_match':True,
              'functions':len(registry['functions']), 'proof_reports':len(reports),
              'source_sha256':expected, 'audit_cache':cache.counts,
              'audit_tools_sha256':tool_hashes,
              'behavior_retested':False, 'game_launch_verified':False}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({key:result[key] for key in ('functions','proof_reports','audit_cache')}))


if __name__=='__main__':
    main()
