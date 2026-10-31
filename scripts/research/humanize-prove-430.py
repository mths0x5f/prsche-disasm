"""Run 430: proves generated spec files with the oracle and keeps only what passes.

For each humanized/specs/<prefix>_*.json: runs verify-v2-humanized-430.py on it (20000 cases),
removes failures and functions that crash the harness (the first unreported one, then retries
the rest), deletes their sources and records them in local/experiments/humanize-gen/rejected.json
so the generator does not produce them again.

Usage: py -3 scripts/research/humanize-prove-430.py --prefix g1
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
SPECS = RUN / 'humanized/specs'
REJECTED = ROOT / 'local/experiments/humanize-gen/rejected.json'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--cases', type=int, default=20000)
    args = ap.parse_args()
    REJECTED.parent.mkdir(parents=True, exist_ok=True)
    rejected = json.loads(REJECTED.read_text()) if REJECTED.exists() else {}
    total_pass = 0
    for spec in sorted(SPECS.glob(f'{args.prefix}_*.json')):
        if spec.name.endswith('.oracle.json'):
            continue
        todo = json.loads(spec.read_text(encoding='utf-8'))
        passed, lines = {}, []
        work = dict(todo)
        while work:
            tmp = SPECS / f'{spec.stem}_try.json'
            tmp.write_text(json.dumps(work), encoding='utf-8')
            r = subprocess.run(['py', '-3', str(ROOT / 'scripts/research/verify-v2-humanized-430.py'), '--batch', tmp.stem,
                                '--cases', str(args.cases)], capture_output=True, text=True, cwd=ROOT)
            tmp.unlink()
            (SPECS / f'{tmp.stem}.oracle.json').unlink(missing_ok=True)
            out = r.stdout
            if 'VC6 compile failed' in out:
                bad = set(re.findall(r'h_([0-9a-f]{8})\.cpp', out)) & set(work)
                if not bad:
                    print(out[-1500:])
                    raise SystemExit('compile failure without a culprit')
                for va in bad:
                    rejected[va] = 'compile'
                    work.pop(va)
                continue
            done = set()
            for m in re.finditer(r'^(PASS|FAIL) ([0-9a-f]{8}) .*$', out, re.M):
                done.add(m.group(2))
                if m.group(1) == 'PASS':
                    passed[m.group(2)] = work[m.group(2)]
                    lines.append(m.group(0))
                else:
                    rejected[m.group(2)] = 'oracle'
            if 'functions' in out:
                break
            rest = sorted(set(work) - done)
            if not rest:
                break
            rejected[rest[0]] = 'crash'
            work = {k: work[k] for k in rest[1:]}
        for va in todo:
            if va not in passed:
                (RUN / 'humanized' / f'{va}.cpp').unlink(missing_ok=True)
        if passed:
            spec.write_text(json.dumps(passed, indent=1, sort_keys=True), encoding='utf-8')
            (SPECS / f'{spec.stem}.oracle.json').write_text(json.dumps(dict(
                schema=3, harness='original Porsche.exe mapped at 0x00400000', cases_per_function=args.cases,
                functions=sorted(passed), output=lines), indent=1) + '\n', encoding='utf-8')
        else:
            spec.unlink()
        total_pass += len(passed)
        print(spec.name, len(passed), '/', len(todo), flush=True)
        REJECTED.write_text(json.dumps(rejected, indent=1, sort_keys=True))
    print('passed', total_pass)


if __name__ == '__main__':
    main()
