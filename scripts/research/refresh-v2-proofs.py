"""Refresh stale proofs in a fresh run, preserving committed report history."""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import subprocess
import sys
from v2_proof_cache import ProofCache

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json'
BIN = ROOT / 'local/builds/v2/001-original-recovery/bin/Release'
PROOF_CACHE = ProofCache()


def digest(path):
    return PROOF_CACHE.digest(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-root', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=4, choices=range(1, 9))
    parser.add_argument('--plan-only', action='store_true')
    parser.add_argument('--update-registry', action='store_true')
    args = parser.parse_args()
    report_root = args.report_root.resolve()
    registry = json.loads(REGISTRY.read_text(encoding='utf8'))
    reports = {f[k] for f in registry['functions'] for k in
               ('verification_report', 'integration_verification_report') if f.get(k)}
    tasks, replacements, unsupported = {}, {}, []
    for relative in sorted(reports):
        report = PROOF_CACHE.document(ROOT / relative)
        stale = [p for p, sha in report['source_sha256'].items()
                 if not (ROOT / p).is_file() or digest(ROOT / p) != sha]
        if not stale:
            continue
        scripts = [p for p in report['source_sha256'] if
                   re.fullmatch(r'scripts/research/verify-v2-[^/]+\.py', p)]
        if not scripts:
            # Early reports predate self-hashing verifier metadata.
            scripts = sorted({f['verification'] for f in registry['functions']
                              if f.get('verification_report') == relative})
            if relative.endswith('/020-thread-bootstrap/verification.json'):
                scripts = ['scripts/research/verify-v2-thread-bootstrap.py']
            if relative.endswith('/015-joint-disk/verification.json'):
                scripts = ['scripts/research/verify-v2-joint-disk.py']
        composite = 'scripts/research/verify-v2-formatter-timer-integration.py'
        if composite in scripts:
            scripts = [composite]
        if len(scripts) != 1:
            unsupported.append({'report': relative, 'ambiguous_verifiers': scripts})
            continue
        script = scripts[0]
        source = (ROOT / script).read_text(encoding='utf8')
        tree = ast.parse(source)
        flags = {a.value for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument'
                 for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)}
        flag = '--report-dir' if '--report-dir' in flags else '--report' if '--report' in flags else None
        if not flag:
            unsupported.append({'report': relative, 'verifier': script, 'missing_fresh_output_flag': True})
            continue
        name = Path(script).stem.removeprefix('verify-v2-')
        if report.get('connected_original_strings'):
            name = 'formatter-error-integration'
        proof_filename = 'full-verification.json' if Path(relative).name == 'full-verification.json' else 'verification.json'
        output = report_root / name / proof_filename
        command = [sys.executable, str(ROOT / script), flag,
                   str(output.parent if flag == '--report-dir' else output)]
        executables = re.findall(r'/bin/Release/([A-Za-z0-9_]+\.exe)', source)
        if script == composite:
            executables = ['startup_timing_integration_probe.exe']
            command += ['--timer-probe', str(BIN/'timer_setup_probe.exe'),
                        '--formatter-probe', str(BIN/'formatter_original_probe.exe'),
                        '--auxiliary-probe', str(BIN/'auxiliary_wait_probe.exe')]
        if report.get('connected_original_strings'):
            # Preserve the stronger connected check when refreshing Run143+.
            executables = ['formatter_error_integration_probe.exe']
            command += ['--connected-strings']
        if '--probe' in flags:
            if not executables:
                # Required --probe options may have no embedded default path.
                # Use the pinned probe TU only when its common EXE exists.
                candidates = {Path(p).stem + '.exe' for p in report['source_sha256']
                              if p.endswith('_probe.cpp')}
                executables = sorted(p for p in candidates if (BIN / p).is_file())
            if len(set(executables)) != 1:
                unsupported.append({'report': relative, 'verifier': script, 'ambiguous_probes': executables})
                continue
            command += ['--probe', str(BIN / executables[0])]
        if '--production-probe' in flags and report.get('uninstrumented_native_equal_instrumented'):
            command += ['--production-probe', str(BIN/'formatter_strings_production_probe.exe')]
        if '--wrapper-probe' in flags and report.get('wrapper_probe_sha256'):
            command += ['--wrapper-probe', str(BIN/'context_range_wrapper_probe.exe')]
        if output == (ROOT / relative).resolve():
            raise RuntimeError(f'Fresh output equals historical report: {relative}')
        # A verifier can expose isolated and connected modes with different
        # original-function coverage. Never collapse them to one script key.
        tasks[tuple(command)] = {'script': script, 'command': command, 'output': str(output)}
        replacements[relative] = output.relative_to(ROOT).as_posix()
    report_root.mkdir(parents=True, exist_ok=True)
    plan = {'tasks': list(tasks.values()), 'replacements': replacements, 'unsupported': unsupported}
    PROOF_CACHE.check_stable()
    (report_root / 'refresh-plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'stale_verifiers': len(tasks), 'unsupported': unsupported}))
    if args.plan_only:
        return
    if unsupported:
        raise SystemExit('Add fresh output flags or resolve ambiguous metadata before running')
    # A report already committed to Git must never become a mutable output.
    tracked = set(subprocess.run(['git', 'ls-files'], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.splitlines())
    if set(replacements.values()) & tracked:
        raise RuntimeError('Choose a new run: requested outputs contain committed reports')

    def execute(task):
        output = Path(task['output'])
        output.parent.mkdir(parents=True, exist_ok=True)
        process = subprocess.run(task['command'], cwd=ROOT, capture_output=True,
                                 text=True, encoding='utf8', errors='replace')
        (output.parent / 'check.log').write_text(process.stdout + process.stderr, encoding='utf8')
        result = {'script': task['script'], 'exit_code': process.returncode, 'output': task['output']}
        if process.returncode:
            result['error_tail'] = (process.stdout + process.stderr)[-1600:]
        print(json.dumps(result), flush=True)
        return result

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(execute, tasks.values()))
    (report_root / 'refresh-result.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf8')
    if any(r['exit_code'] for r in results):
        raise SystemExit('Proof refresh failed; registry was not changed')
    if args.update_registry:
        PROOF_CACHE.check_stable()
        for function in registry['functions']:
            for key in ('verification_report', 'integration_verification_report'):
                if function.get(key) in replacements:
                    function[key] = replacements[function[key]]
        REGISTRY.write_text(json.dumps(registry, indent=2) + '\n', encoding='utf8', newline='\n')


if __name__ == '__main__':
    main()
