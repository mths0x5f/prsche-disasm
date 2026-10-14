"""Incremental automatic-candidate COFF build from pinned syntax/source inputs.

Reuse byte-identical Run181 objects, compile only changed/new TUs, never emit stubs.
Historical compiler byte identity is not available in Run178/181 and is disclosed.
"""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('object_audit181', ROOT / 'scripts/research/build-v2-compile-corpus.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, default=ROOT / 'local/experiments/v2-pcode-compat-180/prototypes-cpp-0000/audit.json')
    parser.add_argument('--prior', type=Path, default=ROOT / 'iterations/v2/001-original-recovery/runs/181-corpus-objects/summary.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'local/experiments/v2-build-corpus-182')
    parser.add_argument('--summary', type=Path, default=ROOT / 'iterations/v2/001-original-recovery/runs/182-incremental-objects/summary.json')
    parser.add_argument('--jobs', type=int, default=6)
    args = parser.parse_args()
    assert args.jobs > 0
    audit = json.loads(args.audit.read_bytes())
    prior = json.loads(args.prior.read_bytes())
    old_audit_path = ROOT / prior['input_audit']
    assert digest(old_audit_path) == prior['input_audit_sha256']
    old_audit = json.loads(old_audit_path.read_bytes())
    assert audit['original_sha256'] == prior['original_sha256'] == base.ORIGINAL_SHA
    assert audit['pseudo_c_sha256'] == prior['pseudo_c_sha256']
    assert digest(ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/decompiled.c') == audit['pseudo_c_sha256']
    assert audit['compiler_version'] == prior['compiler_version'] == old_audit['compiler_version']
    assert audit['compiler'] == old_audit['compiler'] and audit['language'] == 'cpp'
    assert audit['primitive_header_sha256'] == old_audit['primitive_header_sha256']
    pins = {args.audit.resolve(): digest(args.audit), args.prior.resolve(): digest(args.prior), old_audit_path: digest(old_audit_path)}
    for name, expected in {**audit['cache_inputs_sha256'], **audit['headers_sha256']}.items():
        path = Path(name)
        assert digest(path) == expected, name
        pins[path.resolve()] = expected
    compiler = Path(audit['compiler'])
    pins[compiler.resolve()] = digest(compiler)
    if 'compiler_sha256' in prior:
        assert pins[compiler.resolve()] == prior['compiler_sha256']
    # A prior delta may contain helper includes: verify that complete recorded
    # dependency closure before reusing even byte-identical translation units.
    for name, expected in prior.get('input_sha256', {}).items():
        assert digest(ROOT / name) == expected, ('prior dependency changed', name)
        pins[(ROOT / name).resolve()] = expected
    prior_rows = {row['va']: row for row in prior['results'] if row['compiler_exit_code'] == 0}
    selected = [row for row in audit['results'] if row['syntax_passed']]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    begin = time.perf_counter()
    results, pending = [], []
    for row in selected:
        source = Path(row['generated_source'])
        assert digest(source) == row['generated_source_sha256'], source
        old = prior_rows.get(row['va'])
        if old and old['generated_source_sha256'] == row['generated_source_sha256'] and old.get('forced_headers', []) == row['forced_headers']:
            assert digest(ROOT / old['object']) == old['object_sha256'], old['object']
            assert old['source_body_sha256'] == row['source_body_sha256']
            results.append({**old, 'generated_source': relative(source), 'object_reused': True, 'reused_from': relative(args.prior), 'forced_headers': row['forced_headers'], 'compatibility_header': row.get('compatibility_header')})
        else:
            pending.append(row)
    environment = {**os.environ, 'VSLANG': '1033'}

    def compile_one(row):
        source = Path(row['generated_source'])
        obj = output / (row['va'] + '.obj')
        command = [str(compiler), '/nologo', '/c', '/Od', '/Gy', '/TP', '/W3', '/utf-8', '/diagnostics:column', '/Fo' + str(obj)]
        command += ['/FI' + name for name in row['forced_headers']]
        command.append(str(source))
        process = subprocess.run(command, cwd=output, env=environment, capture_output=True, timeout=90)
        log = process.stdout + process.stderr
        (output / (row['va'] + '.log')).write_bytes(log)
        result = {'va': row['va'], 'name': row['name'], 'source_body_sha256': row['source_body_sha256'],
                  'generated_source': relative(source), 'generated_source_sha256': row['generated_source_sha256'],
                  'compiler_exit_code': process.returncode, 'command': command, 'log_sha256': hashlib.sha256(log).hexdigest(),
                  'object_reused': False, 'forced_headers': row['forced_headers'], 'compatibility_header': row.get('compatibility_header')}
        if process.returncode == 0:
            result.update(object=relative(obj), object_sha256=digest(obj), symbols=base.coff_symbols(obj))
        return result

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for future in as_completed([pool.submit(compile_one, row) for row in pending]):
            results.append(future.result())
    results.sort(key=lambda row: row['va'])
    compiled = [row for row in results if row['compiler_exit_code'] == 0]
    definitions, references = defaultdict(list), defaultdict(list)
    for row in compiled:
        for name in row['symbols']['defined'] + row['symbols']['common']:
            definitions[name].append(row['va'])
        for name in row['symbols']['undefined']:
            references[name].append(row['va'])
    unresolved = {name: vas for name, vas in sorted(references.items()) if name not in definitions}
    response = output / 'objects.rsp'
    response.write_text('\n'.join('"' + str(ROOT / row['object']) + '"' for row in compiled) + '\n', encoding='utf8', newline='\n')
    library = output / 'porsche_automatic_candidates.lib'
    command = [str(compiler.with_name('lib.exe')), '/nologo', '/out:' + str(library), '@' + str(response)]
    process = subprocess.run(command, cwd=output, env=environment, capture_output=True, timeout=90)
    (output / 'library.log').write_bytes(process.stdout + process.stderr)
    assert process.returncode == 0
    for path, expected in pins.items():
        assert digest(path) == expected, ('input changed during build', str(path))
    for row in results:
        assert digest(ROOT / row['generated_source']) == row['generated_source_sha256']
        if row['compiler_exit_code'] == 0:
            assert digest(ROOT / row['object']) == row['object_sha256']
    report = {'schema': 1, 'kind': 'incremental-automatic-compile-candidates', 'original_sha256': base.ORIGINAL_SHA,
              'pseudo_c_sha256': audit['pseudo_c_sha256'], 'input_audit': relative(args.audit), 'input_audit_sha256': digest(args.audit),
              'compiler_version': audit['compiler_version'], 'compiler_sha256': pins[compiler.resolve()],
              'syntax_candidates': len(selected), 'objects_compiled': len(compiled), 'objects_reused': sum(row['object_reused'] for row in compiled),
              'compiler_invocations': len(pending), 'code_generation_failed': len(results) - len(compiled),
              'elapsed_seconds': round(time.perf_counter() - begin, 3), 'undefined_symbol_names': len(unresolved),
              'undefined_object_references': sum(map(len, unresolved.values())), 'undefined_symbols': unresolved,
              'library': {'path': relative(library), 'sha256': digest(library), 'bytes': library.stat().st_size},
              'input_sha256': {relative(path): expected for path, expected in pins.items()},
              'source_sha256': {relative(Path(__file__)): digest(__file__), 'scripts/research/build-v2-compile-corpus.py': digest(ROOT / 'scripts/research/build-v2-compile-corpus.py')},
              'results': results, 'limits': ['Private automatic candidate archive; no game executable or behavioral acceptance.',
                         'Reused objects have byte-identical generated TUs, unchanged scalar closure and matching recorded compiler path/version.',
                         'Historical Run178/181 compiler binary SHA was not recorded. Current compiler binary SHA is pinned; historical byte identity remains unproven.',
                         'No header is force-included unless its individual TU provenance explicitly requests it. No guessed dependency/storage definitions.']}
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({key: report[key] for key in ('objects_compiled', 'objects_reused', 'compiler_invocations', 'code_generation_failed', 'elapsed_seconds', 'undefined_symbol_names')}))


if __name__ == '__main__':
    main()
