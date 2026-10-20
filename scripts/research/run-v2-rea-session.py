"""Run a manifest-driven immutable persistent REA MCP session."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]

PILOT = ROOT / 'local/tools/rea-pilot-302/.pilot'
NODE = PILOT / 'node/node-v26.12.0-win-x64/node.exe'
TARGET = ROOT / 'local/game/Porsche.exe'
EXPECTED = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    if not args.attempt.isdigit() or len(args.attempt) != 3:
        raise ValueError('Three-digit attempt ID required')
    config_path = args.config.resolve()
    config_path.relative_to(ROOT)
    config = json.loads(config_path.read_bytes())
    experiment = (ROOT / config['experiment']).resolve()
    experiment.relative_to(ROOT / 'local/experiments')
    out = experiment / args.attempt
    out.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    target = out / 'Porsche.exe'
    script = ROOT / 'scripts/research/rea-session.mjs'
    cmd = [str(NODE), str(script), str(target), str(out), str(config_path)]
    receipt = dict(schema=1, attempt=args.attempt, command=cmd,
                   cwd=str(ROOT), source_original=str(TARGET), expected_sha256=EXPECTED,
                   config=str(config_path.relative_to(ROOT)), config_sha256=sha(config_path),
                   source_commit=subprocess.check_output(['git', '-C', str(PILOT.parent), 'rev-parse', 'HEAD'], text=True).strip(),
                   script_sha256=sha(script), runner_sha256=sha(Path(__file__)),
                   rea_package_json_sha256=sha(PILOT / 'package/package.json'),
                   rea_server_sha256=sha(PILOT / 'package/scripts/rea.mjs'))
    code = 1
    try:
        if sha(TARGET) != EXPECTED:
            raise ValueError('Original SHA drift')
        shutil.copyfile(TARGET, target)
        if sha(target) != EXPECTED:
            raise ValueError('Copy SHA drift')
        env = os.environ.copy()
        for key in tuple(env):
            upper = key.upper()
            if upper == 'GITHUB_PAT_TOKEN' or upper.endswith(('_API_KEY', '_TOKEN')):
                env.pop(key)
        env.update(PATH=str(NODE.parent) + os.pathsep + env.get('PATH', ''),
                   GHIDRA_INSTALL_DIR=str(ROOT / 'local/tools/ghidra_12.1.3_PUBLIC'),
                   JAVA_HOME=str(ROOT / 'local/tools/jdk-25.0.4.1+1'),
                   REA_ANALYSIS_PROVIDER='ghidra', REA_GHIDRA_STARTUP_TIMEOUT_MS='1200000',
                   REA_GHIDRA_DISABLED_ANALYZERS='WindowsResourceReference',
                   NPM_CONFIG_CACHE=str(PILOT / 'npm-cache'),
                   NPM_CONFIG_PREFIX=str(PILOT / 'npm-prefix'),
                   NPM_CONFIG_USERCONFIG=str(PILOT / 'npmrc'),
                   NPM_CONFIG_OFFLINE='false', TEMP=str(PILOT / 'tmp'), TMP=str(PILOT / 'tmp'))
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=1800)
        code = proc.returncode
        output = proc.stdout
    except Exception as exc:
        output = (type(exc).__name__ + ': ' + str(exc) + '\n').encode()
    (out / 'runner.log').write_bytes(output)
    outputs = {path.name: sha(path) for path in sorted(out.iterdir())
               if path.is_file() and path.name != 'Porsche.exe'}
    receipt.update(exit_code=code, seconds=time.perf_counter() - start,
                   runner_log_sha256=sha(out / 'runner.log'),
                   target_sha256=sha(target) if target.exists() else None,
                   node_sha256=sha(NODE), output_sha256=outputs)
    save(out / 'receipt.json', receipt)
    print(json.dumps(dict(attempt=args.attempt, exit_code=code,
                          seconds=round(receipt['seconds'], 3),
                          preview=output[:1200].decode(errors='replace'))))
    if code:
        raise SystemExit(code)


if __name__ == '__main__':
    main()
