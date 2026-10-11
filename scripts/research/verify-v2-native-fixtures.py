"""Run the native OS and link fixtures with current target dependency pins."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from v2_build_graph import compiled_sources, cmake_inputs
from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
NATIVE = (
    ('native_core_smoke', 'native-core'),
    ('native_thread_smoke', 'native-thread'),
    ('native_window_smoke', 'native-window'),
    ('native_window_lifecycle', 'native-window-lifecycle'),
    ('formatter_error_native_probe', 'native-formatter-error'),
    ('formatter_lowio_native_probe', 'native-formatter-lowio'),
    ('formatter_crt_native_probe', 'native-formatter-crt'),
)
LINK = ('native_window_chain', 'window_links_probe',
        'win32_window_bindings_compile_fixture')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-root', type=Path, required=True)
    parser.add_argument('--build-root', type=Path,
                        default=ROOT/'local/builds/v2/001-original-recovery')
    args = parser.parse_args()
    run, build = args.report_root.resolve(), args.build_root.resolve()
    run.mkdir(parents=True, exist_ok=True)
    tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=ROOT,
                                         text=True).splitlines())
    outputs = [run/(name+'-result.json') for _, name in NATIVE]
    outputs += [run/'window-link-checks.json']
    for output in outputs:
        if output.relative_to(ROOT).as_posix() in tracked:
            raise RuntimeError('Choose a fresh run; committed results are immutable')
    link_results = []
    for target, name in (*NATIVE, *((t, None) for t in LINK)):
        binary = build/'bin/Release'/(target+'.exe')
        sources = compiled_sources(build, target)
        deps = cmake_inputs()+['scripts/build-v2.ps1',
            'scripts/research/v2_build_graph.py',
            'scripts/research/verify-v2-native-fixtures.py']
        hashes = source_hashes(deps, compiled_sources=sources)
        executable_sha = hashlib.sha256(binary.read_bytes()).hexdigest()
        process = subprocess.run([str(binary)], cwd=ROOT, capture_output=True,
                                 text=True, encoding='utf8', errors='replace',
                                 timeout=30)
        if process.returncode:
            raise RuntimeError(f'{target}: exit {process.returncode}: '
                               f'{process.stdout}\n{process.stderr}')
        if (hashes != source_hashes(deps, compiled_sources=sources) or
            executable_sha != hashlib.sha256(binary.read_bytes()).hexdigest()):
            raise RuntimeError('Sources or executable changed during fixture execution')
        report = {'schema':1, 'date':datetime.now(timezone.utc).date().isoformat(),
            'command':binary.relative_to(ROOT).as_posix(), 'exit_code':0,
            'stdout':process.stdout, 'stderr':process.stderr,
            'probe_sha256':executable_sha, 'game_launch_verified':False,
            'compiled_source_count':len(sources), 'source_sha256':hashes}
        if name:
            results = [json.loads(line) for line in process.stdout.splitlines()
                       if line.startswith('{')]
            if len(results)!=1 or not (results[0].get('passed') or
                                      results[0].get('fixture_passed')):
                raise RuntimeError(f'{target}: missing successful fixture result')
            report['result'] = results[0]
            output = run/(name+'-result.json')
            output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
        else:
            report['target'] = target
            link_results.append(report)
        print(json.dumps({'target':target,'exit_code':0}),flush=True)
    (run/'window-link-checks.json').write_bytes(
        (json.dumps(link_results,indent=2)+'\n').encode())


if __name__=='__main__':
    main()
