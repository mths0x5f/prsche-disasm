"""Batch native x86 COFF compilation for the Run184 declaration audit.

Each forced-header cohort is compiled in /MP6 batches. Any batch-level error
discards that batch directory and recompiles every member individually in a
separate directory. This is syntax/code-generation evidence only.
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('object_audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
FLAGS = ['/nologo', '/c', '/Od', '/Gy', '/TP', '/W3', '/utf-8', '/diagnostics:column']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, default=ROOT / 'local/experiments/v2-declaration-compat-184/full/audit.json')
    parser.add_argument('--prior', type=Path, default=ROOT / 'iterations/v2/001-original-recovery/runs/185-incremental-pcode-objects/summary.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'local/experiments/v2-build-corpus-188')
    parser.add_argument('--summary', type=Path, default=ROOT / 'iterations/v2/001-original-recovery/runs/188-batched-corpus-objects/summary.json')
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--limit', type=int, help='Compile only the first N syntax-pass rows (pilot use).')
    parser.add_argument('--disable-cache', action='store_true', help='Compile all selected TUs for a clean batch pilot.')
    args = parser.parse_args()
    assert args.batch_size > 0
    audit_path, prior_path, output = args.audit.resolve(), args.prior.resolve(), args.output.resolve()
    audit = json.loads(audit_path.read_bytes())
    prior = json.loads(prior_path.read_bytes())
    assert audit['original_sha256'] == prior['original_sha256'] == base.ORIGINAL_SHA
    assert audit['language'] == 'cpp' and prior['pseudo_c_sha256'] == audit['pseudo_c_sha256']
    corpus = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/decompiled.c'
    assert digest(corpus) == audit['pseudo_c_sha256']
    compiler = Path(audit['compiler']).resolve()
    assert audit['compiler_version'] == prior['compiler_version']
    assert digest(compiler) == prior['compiler_sha256']

    # Validate every recorded prior input before considering any cached object.
    prior_inputs = prior.get('input_sha256', {})
    assert prior_inputs, 'prior report lacks complete input closure'
    pins = {audit_path: digest(audit_path), prior_path: digest(prior_path), compiler: digest(compiler), corpus.resolve(): digest(corpus)}
    for name, expected in prior_inputs.items():
        path = ROOT / name
        assert digest(path) == expected, ('prior closure changed', name)
        pins[path.resolve()] = expected
    for name, expected in prior.get('source_sha256', {}).items():
        path = ROOT / name
        assert digest(path) == expected, ('prior builder source changed', name)
        pins[path.resolve()] = expected
    for name, expected in audit.get('headers_sha256', {}).items():
        path = Path(name).resolve()
        assert digest(path) == expected, name
        pins[path] = expected
    for name, expected in audit.get('cache_inputs_sha256', {}).items():
        path = Path(name).resolve()
        assert digest(path) == expected, name
        pins[path] = expected

    old_rows = {row['va']: row for row in prior['results'] if row.get('compiler_exit_code') == 0}
    selected = [row for row in audit['results'] if row.get('syntax_passed')]
    if args.limit is not None:
        assert args.limit > 0
        selected = selected[:args.limit]
    assert not output.exists() or not any(output.iterdir()), f'refusing stale output directory: {output}'
    output.mkdir(parents=True, exist_ok=True)
    begin = time.perf_counter()
    results, pending = [], []
    for row in selected:
        source = Path(row['generated_source']).resolve()
        assert digest(source) == row['generated_source_sha256'], source
        forced = row.get('forced_headers', [])
        for header in forced:
            assert Path(header).is_file(), header
            pins[Path(header).resolve()] = digest(header)
        old = old_rows.get(row['va'])
        if not args.disable_cache and old and old.get('generated_source_sha256') == row['generated_source_sha256'] and old.get('forced_headers', []) == forced:
            old_source = ROOT / old['generated_source']
            old_obj = ROOT / old['object']
            assert digest(old_source) == old['generated_source_sha256']
            assert digest(old_obj) == old['object_sha256']
            assert old.get('source_body_sha256') == row.get('source_body_sha256')
            # Ensure prior compilation used the same codegen flags and compiler.
            prior_command = old['command']
            assert Path(prior_command[0]).resolve() == compiler
            prior_flags = [arg for arg in prior_command[1:] if arg.startswith('/') and not arg.startswith('/Fo') and not arg.startswith('/FI') and arg != '/MP6']
            assert prior_flags == FLAGS
            results.append({'va': row['va'], 'name': row['name'], 'source_body_sha256': row.get('source_body_sha256'),
                            'generated_source': relative(source), 'generated_source_sha256': row['generated_source_sha256'],
                            'compiler_exit_code': 0, 'command': old['command'], 'log_sha256': old['log_sha256'],
                            'object': old['object'], 'object_sha256': old['object_sha256'],
                            'symbols': old['symbols'], 'object_reused': True, 'reused_from': relative(prior_path),
                            'reused_command': old['command'], 'reused_log_sha256': old['log_sha256'],
                            'forced_headers': forced, 'compatibility_header': row.get('compatibility_header')})
        else:
            pending.append(row)

    env = {**os.environ, 'VSLANG': '1033'}
    cohorts = defaultdict(list)
    for row in pending:
        cohorts[tuple(row.get('forced_headers', []))].append(row)
    batch_counts = {'attempted': 0, 'succeeded': 0, 'fallback_batches': 0, 'fallback_objects': 0}
    batch_records = []
    for cohort_index, (headers, rows) in enumerate(sorted(cohorts.items(), key=lambda item: item[0])):
        for batch_index in range(0, len(rows), args.batch_size):
            batch = rows[batch_index:batch_index + args.batch_size]
            tag = f'cohort-{cohort_index:03d}-batch-{batch_index // args.batch_size:04d}'
            batch_dir = output / (tag + '-batch')
            batch_dir.mkdir()
            sources = [Path(row['generated_source']).resolve() for row in batch]
            command = [str(compiler), *FLAGS, '/MP6', '/Fo' + str(batch_dir) + os.sep]
            command.extend('/FI' + header for header in headers)
            command.extend(map(str, sources))
            batch_counts['attempted'] += 1
            proc = subprocess.run(command, cwd=batch_dir, env=env, capture_output=True, timeout=600)
            log = proc.stdout + proc.stderr
            (batch_dir / 'batch.log').write_bytes(log)
            expected = {row['va']: batch_dir / (row['va'] + '.obj') for row in batch}
            valid = proc.returncode == 0
            if valid:
                try:
                    for obj in expected.values():
                        base.coff_symbols(obj)
                except (OSError, AssertionError, ValueError):
                    valid = False
            batch_record = {'batch': tag, 'command': command, 'exit_code': proc.returncode,
                            'log_sha256': hashlib.sha256(log).hexdigest(), 'members': [r['va'] for r in batch],
                            'objects_valid': valid, 'directory': relative(batch_dir)}
            batch_records.append(batch_record)
            if valid:
                batch_counts['succeeded'] += 1
                for row in batch:
                    obj = expected[row['va']]
                    results.append(make_result(row, obj, 0, command, log, base))
                continue
            batch_counts['fallback_batches'] += 1
            # Retain the failed batch directory for evidence. Individual retry outputs are isolated.
            fallback_dir = output / (tag + '-fallback')
            fallback_dir.mkdir()
            batch_record['fallback_directory'] = relative(fallback_dir)
            for row in batch:
                source = Path(row['generated_source']).resolve()
                objdir = fallback_dir / row['va']
                objdir.mkdir()
                obj = objdir / (row['va'] + '.obj')
                one = [str(compiler), *FLAGS, '/Fo' + str(obj)]
                one.extend('/FI' + header for header in headers)
                one.append(str(source))
                individual = subprocess.run(one, cwd=objdir, env=env, capture_output=True, timeout=90)
                ilog = individual.stdout + individual.stderr
                (objdir / 'compile.log').write_bytes(ilog)
                code = individual.returncode
                if code == 0:
                    try:
                        base.coff_symbols(obj)
                    except (OSError, AssertionError, ValueError):
                        code = 1
                results.append(make_result(row, obj, code, one, ilog, base))
                batch_counts['fallback_objects'] += 1
            batch_record['individual_exit_codes'] = {r['va']: r['compiler_exit_code'] for r in results if r['va'] in batch_record['members']}
            (fallback_dir / 'fallback.json').write_text(json.dumps(batch_record, indent=2) + '\n', encoding='utf8')
            (batch_dir / 'batch.json').write_text(json.dumps(batch_record, indent=2) + '\n', encoding='utf8')

    results.sort(key=lambda row: row['va'])
    compiled = [r for r in results if r['compiler_exit_code'] == 0]
    definitions, references = defaultdict(list), defaultdict(list)
    for row in compiled:
        for symbol in row['symbols']['defined'] + row['symbols']['common']:
            definitions[symbol].append(row['va'])
        for symbol in row['symbols']['undefined']:
            references[symbol].append(row['va'])
    unresolved = {name: vas for name, vas in sorted(references.items()) if name not in definitions}
    response = output / 'objects.rsp'
    response.write_text('\n'.join('"' + str((ROOT / row['object']).resolve()) + '"' for row in compiled) + '\n', encoding='utf8', newline='\n')
    library = output / 'porsche_automatic_candidates.lib'
    lib_command = [str(compiler.with_name('lib.exe')), '/nologo', '/out:' + str(library), '@' + str(response)]
    lib_proc = subprocess.run(lib_command, cwd=output, env=env, capture_output=True, timeout=600)
    lib_log = lib_proc.stdout + lib_proc.stderr
    (output / 'library.log').write_bytes(lib_log)
    assert lib_proc.returncode == 0, lib_log.decode(errors='replace')
    for path, expected_hash in pins.items():
        assert digest(path) == expected_hash, ('input changed during build', str(path))
    for row in results:
        assert digest(ROOT / row['generated_source']) == row['generated_source_sha256']
        if row['compiler_exit_code'] == 0:
            assert digest(ROOT / row['object']) == row['object_sha256']

    report = {'schema': 1, 'kind': 'batched-automatic-compile-candidates', 'original_sha256': base.ORIGINAL_SHA,
              'pseudo_c_sha256': audit['pseudo_c_sha256'], 'input_audit': relative(audit_path), 'input_audit_sha256': digest(audit_path),
              'compiler_version': audit['compiler_version'], 'compiler_sha256': digest(compiler),
              'syntax_candidates': len(selected), 'objects_compiled': len(compiled),
              'objects_reused': sum(bool(r.get('object_reused')) for r in compiled),
              'code_generation_failed': len(results) - len(compiled), 'batch_size': args.batch_size,
              'batch_counts': batch_counts, 'elapsed_seconds': round(time.perf_counter() - begin, 3),
              'batches': batch_records,
              'undefined_symbol_names': len(unresolved), 'undefined_object_references': sum(map(len, unresolved.values())),
              'undefined_symbols': unresolved,
              'library': {'path': relative(library), 'sha256': digest(library), 'bytes': library.stat().st_size,
                          'command': lib_command, 'log_sha256': hashlib.sha256(lib_log).hexdigest()},
              'input_sha256': {relative(path): value for path, value in pins.items()},
              'source_sha256': {relative(Path(__file__)): digest(__file__), 'scripts/research/build-v2-compile-corpus.py': digest(ROOT / 'scripts/research/build-v2-compile-corpus.py')},
              'results': results,
              'limits': ['Isolated syntax/code-generation and x86 COFF evidence; no game executable or behavioral acceptance.',
                         'Cached objects require byte-identical generated TU, forced-header set, source-body hash, compiler binary, options, and validated prior input closure.',
                         'Run185 current compiler SHA is pinned and matched; historical Run178/181 compiler binary SHA was not recorded, so historical byte identity remains unproven.',
                         'Any batch failure or missing/invalid member object causes full-batch individual fallback in a separate fresh directory.',
                         'No dependency stubs, storage guesses, or game sources modified.']}
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({key: report[key] for key in ('syntax_candidates', 'objects_compiled', 'objects_reused', 'code_generation_failed', 'batch_counts', 'elapsed_seconds', 'undefined_symbol_names')}))


def make_result(row, obj, code, command, log, base):
    source = Path(row['generated_source']).resolve()
    result = {'va': row['va'], 'name': row['name'], 'source_body_sha256': row.get('source_body_sha256'),
              'generated_source': relative(source), 'generated_source_sha256': row['generated_source_sha256'],
              'compiler_exit_code': code, 'command': command, 'log_sha256': hashlib.sha256(log).hexdigest(),
              'object_reused': False, 'forced_headers': row.get('forced_headers', []),
              'compatibility_header': row.get('compatibility_header')}
    if code == 0:
        result.update(object=relative(obj), object_sha256=digest(obj), symbols=base.coff_symbols(obj))
    return result


if __name__ == '__main__':
    main()
