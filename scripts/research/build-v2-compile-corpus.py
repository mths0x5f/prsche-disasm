"""Emit real x86 COFF for syntax-pass candidates without inventing dependencies.

This isolated experiment consumes a pinned Run178 audit, not accepted production.
It preserves each generated TU and reports unresolved/duplicate COFF symbols.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return path.resolve().relative_to(ROOT).as_posix()


def coff_symbols(path):
    data = path.read_bytes()
    machine, _, _, offset, count, optional, _ = struct.unpack_from('<HHLLLHH', data)
    assert machine == 0x14c and optional == 0, 'expected ordinary x86 COFF'
    assert offset + count * 18 + 4 <= len(data)
    strings = offset + count * 18
    string_size = struct.unpack_from('<L', data, strings)[0]
    assert strings + string_size <= len(data)
    result = {'defined': [], 'undefined': [], 'common': [], 'weak': []}
    index = 0
    while index < count:
        start = offset + index * 18
        raw_name, value, section, kind, storage, auxiliary = struct.unpack_from('<8sLhHBB', data, start)
        if raw_name[:4] == b'\0' * 4:
            name_offset = struct.unpack_from('<L', raw_name, 4)[0]
            assert 4 <= name_offset < string_size
            end = data.index(b'\0', strings + name_offset, strings + string_size)
            name = data[strings + name_offset:end].decode('ascii')
        else:
            name = raw_name.rstrip(b'\0').decode('ascii')
        if storage == 2:
            bucket = 'defined' if section > 0 or section == -1 else 'common' if value else 'undefined'
            result[bucket].append(name)
        elif storage == 105:
            result['weak'].append(name)
        index += auxiliary + 1
    assert index == count
    return {key: sorted(set(values)) for key, values in result.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, default=ROOT / 'local/experiments/v2-compile-corpus-178/prototypes-cpp-0000/audit.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'local/experiments/v2-build-corpus-181')
    parser.add_argument('--summary', type=Path, default=ROOT / 'iterations/v2/001-original-recovery/runs/181-corpus-objects/summary.json')
    parser.add_argument('--jobs', type=int, default=6)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    assert args.jobs > 0
    audit_bytes = args.audit.read_bytes()
    audit = json.loads(audit_bytes)
    assert audit['original_sha256'] == ORIGINAL_SHA and audit['language'] == 'cpp'
    corpus = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/decompiled.c'
    assert sha(corpus.read_bytes()) == audit['pseudo_c_sha256']
    modules = [json.loads(line) for line in (ROOT / 'research/binary-index/static/binaries.jsonl').read_text().splitlines()]
    original = next(row for row in modules if row['file'] == 'Porsche.exe')
    assert sha((ROOT / 'local/game' / original['path']).read_bytes()) == ORIGINAL_SHA
    scalars = args.audit.parent.parent / 'ghidra-scalars-syntax-only.h'
    assert sha(scalars.read_bytes()) == audit['primitive_header_sha256']
    for name, expected in audit.get('headers_sha256', {}).items():
        assert sha(Path(name).read_bytes()) == expected, name
    selected = [row for row in audit['results'] if row['syntax_passed']]
    if args.limit:
        selected = selected[:args.limit]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    compiler = Path(audit['compiler'])
    environment = {**os.environ, 'VSLANG': '1033'}
    begin = time.perf_counter()

    def compile_one(row):
        source = args.audit.parent / (row['va'] + '.cpp')
        assert sha(source.read_bytes()) == row['generated_source_sha256'], source
        obj = output / (row['va'] + '.obj')
        # Keep declarations/algorithms unchanged. /Gy gives each real body its own section.
        command = [str(compiler), '/nologo', '/c', '/Od', '/Gy', '/TP', '/W3', '/utf-8', '/diagnostics:column', '/Fo' + str(obj)]
        command += ['/FI' + name for name in audit.get('headers_sha256', {})]
        command.append(str(source.resolve()))
        process = subprocess.run(command, cwd=output, env=environment, capture_output=True, timeout=90)
        log = process.stdout + process.stderr
        (output / (row['va'] + '.log')).write_bytes(log)
        result = {'va': row['va'], 'name': row['name'], 'source_body_sha256': row['source_body_sha256'],
                  'generated_source': relative(source), 'generated_source_sha256': row['generated_source_sha256'],
                  'compiler_exit_code': process.returncode, 'log_sha256': sha(log), 'command': command}
        if process.returncode == 0:
            result.update(object=relative(obj), object_sha256=sha(obj.read_bytes()), symbols=coff_symbols(obj))
        return result

    results = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        pending = [pool.submit(compile_one, row) for row in selected]
        for future in as_completed(pending):
            results.append(future.result())
            if len(results) % 100 == 0:
                print(json.dumps({'objects_attempted': len(results), 'total': len(selected)}), flush=True)
    results.sort(key=lambda row: row['va'])
    successful = [row for row in results if row['compiler_exit_code'] == 0]
    definitions = defaultdict(list)
    references = defaultdict(list)
    weak = defaultdict(list)
    for row in successful:
        for name in row['symbols']['defined'] + row['symbols']['common']:
            definitions[name].append(row['va'])
        for name in row['symbols']['undefined']:
            references[name].append(row['va'])
        for name in row['symbols']['weak']:
            weak[name].append(row['va'])
    unresolved = {name: vas for name, vas in sorted(references.items()) if name not in definitions}
    library_result = None
    if successful:
        library = output / 'porsche_automatic_candidates.lib'
        response = output / 'objects.rsp'
        response.write_text('\n'.join('"' + str((ROOT / row['object']).resolve()) + '"' for row in successful) + '\n', encoding='utf8', newline='\n')
        command = [str(compiler.with_name('lib.exe')), '/nologo', '/out:' + str(library), '@' + str(response)]
        process = subprocess.run(command, cwd=output, env=environment, capture_output=True, timeout=90)
        log = process.stdout + process.stderr
        (output / 'library.log').write_bytes(log)
        library_result = {'command': command, 'exit_code': process.returncode, 'log_sha256': sha(log)}
        if process.returncode == 0:
            library_result.update(path=relative(library), bytes=library.stat().st_size, sha256=sha(library.read_bytes()))
    report = {'schema': 1, 'module': 'Porsche.exe', 'original_sha256': ORIGINAL_SHA,
              'pseudo_c_sha256': audit['pseudo_c_sha256'], 'input_audit': relative(args.audit), 'input_audit_sha256': sha(audit_bytes),
              'syntax_pass_candidates': len(selected), 'objects_compiled': len(successful), 'code_generation_failed': len(results) - len(successful),
              'jobs': args.jobs, 'elapsed_seconds': round(time.perf_counter() - begin, 3), 'compiler_version': audit['compiler_version'],
              'undefined_symbol_names': len(unresolved), 'undefined_object_references': sum(map(len, unresolved.values())),
              'undefined_symbols': unresolved, 'weak_externals': dict(sorted(weak.items())),
              'duplicate_definitions': {name: vas for name, vas in sorted(definitions.items()) if len(vas) > 1},
              'library': library_result, 'results': results,
              'source_sha256': {relative(Path(__file__)): sha(Path(__file__).read_bytes().replace(b'\r\n', b'\n'))},
              'limits': ['Isolated automatic compile candidates; accepted production/registry unchanged.',
                         'Primitive types and forward signatures remain Run178 syntax scaffolding, not original ABI proof.',
                         'No dependency/storage definitions or function stubs supplied; COFF closure is diagnostic only.',
                         'Archive creation is not executable linking or evidence of runtime fidelity. Original startup is not included unless its body actually compiles.']}
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({key: report[key] for key in ('syntax_pass_candidates', 'objects_compiled', 'code_generation_failed', 'undefined_symbol_names', 'undefined_object_references', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
