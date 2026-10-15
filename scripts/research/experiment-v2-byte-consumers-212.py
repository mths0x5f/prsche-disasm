"""Original byte+1 reads in two frozen C2065/slice consumers; no allocation."""
import hashlib
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
OUT = ROOT / 'local/experiments/v2-byte-consumers-212'
RUN = RUNS / '212-byte-consumers'
TARGETS = {'00537ed0': ('DAT_005de62c', '00537ed0', 'a02de65d00'),
           '00598630': ('DAT_006b16a4', '00598644', '8a15a5166b00')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize-existing', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('helpers212', ROOT / 'scripts/research/experiment-v2-consumer-views-210.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    sha, relative, write = helper.sha, helper.relative, helper.write
    assert not (RUN / 'summary.json').exists()
    assert args.finalize_existing or not OUT.exists()
    OUT.mkdir(parents=True, exist_ok=args.finalize_existing)
    RUN.mkdir(parents=True, exist_ok=True)
    pins = {}

    def pin(path, expected=None):
        path = Path(path).resolve()
        actual = sha(path)
        assert expected is None or actual == expected, path
        pins[path] = actual
        return path

    def store(path, text):
        data = text.encode('utf8')
        if args.finalize_existing:
            assert path.read_bytes() == data, ('captured native input changed', path)
        else:
            path.write_bytes(data)

    pin(Path(__file__))
    if args.finalize_existing:
        pin(OUT / 'native-capture-driver.py', '49189aa136ddd21baebeb663a66d89b9b447515126557cde6ae7e4211c6392ba')
    pin(Path(helper.__file__))
    cache = json.loads(pin(ROOT / 'local/experiments/v2-missing-body-triage-201/selected-inputs.json').read_bytes())
    assert cache['original_sha256'] == helper.SHA
    owners = json.loads(pin(ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    assert not {r['entry_va'] for r in owners if r['module'] == 'Porsche.exe'} & TARGETS.keys()
    for name in ('formatter_search', 'rtti', 'formatter_stdio'):
        path = pin(ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe' / (name + '.cpp'))
        assert not any(re.search(r'\b\w*' + va + r'\s*\([^;{}]*\)\s*\{', path.read_text(encoding='utf8')) for va in TARGETS)
    globals_path = pin(RUNS / '179-ghidra-declarations/export/globals.jsonl')
    globals_ = {r['identity']: r for r in map(json.loads, globals_path.read_text(encoding='utf8').splitlines())}
    declarations = helper.module('declarations212', pin(ROOT / 'scripts/research/experiment-v2-declarations-184.py'))
    coff = helper.module('coff212', pin(ROOT / 'scripts/research/build-v2-compile-corpus.py'))
    collector = helper.module('collector212', pin(ROOT / 'scripts/research/audit-v2-native-union-204.py'))
    original = pin(ROOT / 'local/game/Porsche.exe', helper.SHA)
    image = original.read_bytes()
    sections = collector.pe_sections(image)
    listing = pin(ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    lines = listing.read_text(encoding='utf8').splitlines()
    types = dict(cache['types'])
    primitive = pin(ROOT / 'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h')
    proof_rows = []
    rows = []
    for va, (name, pc, raw) in TARGETS.items():
        # A uint4 variant proves a 4-byte analysis view exists. It is not selected
        # as a canonical owner and is not substituted for conflicting consumers.
        record = globals_['Global::' + name]
        candidates = [v for v in record['variants'] if v['symbol']['type']['name'] == 'uint'
                      and v['symbol']['type']['length'] == v['symbol']['bytes'] == 4]
        assert candidates, name
        view = candidates[0]
        symbol = view['symbol']
        assert symbol['storage_detail']['memory'] and not symbol['storage_detail']['compound']
        assert len(symbol['storage_detail']['varnodes']) == 1
        assert int(symbol['storage_detail']['varnodes'][0]['offset']) == int(name[4:], 16)
        types[symbol['type']['path']] = symbol['type']
        scoped = [dict(identity=record['identity'], conflict=False, variants=[view])]
        if va == '00598630':
            pointer_bits = next(s for s in cache['declarations'][va]['globals'] if s['name'] == 'DAT_006b17d0')
            assert pointer_bits['type']['name'] == 'int' and pointer_bits['bytes'] == 4
            types[pointer_bits['type']['path']] = pointer_bits['type']
            scoped.append(dict(identity='Global::DAT_006b17d0', conflict=False,
                               variants=[dict(symbol=pointer_bits, consumer_vas=[va])]))
        accepted, rejected = declarations.declarations(types, scoped)
        assert accepted and not rejected, rejected
        header = OUT / (va + '-globals.h')
        store(header, declarations.header(accepted))
        pin(header)
        old = next(r for r in cache['audit_rows'] if r['va'] == va)
        source = pin(Path(old['generated_source']), old['generated_source_sha256'])
        text = source.read_text(encoding='utf8')
        before = name + '._1_1_'
        after = '(reinterpret_cast<const unsigned char *>(&' + name + ')[1])'
        count = text.count(before)
        assert count == (4 if va == '00537ed0' else 1)
        changed = text.replace(before, after)
        first = re.search(r'^#include "[^\n]+"\n', changed, re.M)
        assert first
        changed = changed[:first.end()] + '#include "' + header.as_posix() + '"\n' + changed[first.end():]
        marker = '/* VA ' + va + ' */'
        assert changed.split(marker)[1].replace(after, before) == text.split(marker)[1]
        instructions = []
        spans = [(int(a, 16), int(b, 16)) for a, b in cache['catalog'][va]['ranges']]
        for line in lines:
            m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)', line)
            if not m or not any(a <= int(m[1], 16) <= b for a, b in spans):
                continue
            at_va = int(m[1], 16)
            section = next(s for s in sections if s['va'] <= at_va < s['va'] + s['raw_bytes'])
            at = section['raw_offset'] + at_va - section['va']
            data = bytes.fromhex(m[2])
            assert image[at:at + len(data)] == data
            instructions.append(dict(pc=m[1], bytes=m[2], assembly=m[3]))
        assert next(r for r in instructions if r['pc'] == pc)['bytes'] == raw
        cpp = OUT / (va + '.cpp')
        store(cpp, changed)
        pin(cpp)
        rows.append(dict(va=va, generated_source=relative(cpp), generated_source_sha256=sha(cpp),
                         original_source=relative(source), original_source_sha256=sha(source),
                         dependency_sha256={relative(p): sha(p) for p in (cpp, header, primitive)}))
        proof_rows.append(dict(va=va, printed_slice=before, expression=after, occurrences=count,
                               read_address=f'{int(name[4:], 16) + 1:08x}', read_bytes=1,
                               storage_view_179=view, aggregate_identity_conflicted=record['conflict'],
                               consumer_formal_type=cache['declarations'][va]['globals'],
                               instructions=instructions, all_other_body_bytes_preserved=True,
                               boundary='Private raw uint4 extern view only; no ownership/type coalescing or allocation'))
    proof = RUN / 'proof-before-compile.json'
    store(proof, json.dumps(dict(schema=1, original_sha256=helper.SHA, rows=proof_rows), indent=2) + '\n')
    pin(proof)
    prior = json.loads(pin(RUNS / '192-scalar-slice-objects/summary.json').read_bytes())
    compiler = pin(Path(prior['batches'][0]['command'][0]), prior['compiler_sha256'])
    for name in ('c1xx.dll', 'c2.dll'):
        pin(compiler.parent / name)
    flags = [f for f in prior['batches'][0]['command'][1:] if f.startswith('/') and not f.startswith('/Fo')]
    assert '/MP6' in flags and '/Od' in flags and not os.environ.get('CL') and not os.environ.get('_CL_')
    objects = OUT / 'objects'
    objects.mkdir(exist_ok=args.finalize_existing)
    response = OUT / 'compile.rsp'
    store(response, '\n'.join('"' + str(ROOT / r['generated_source']) + '"' for r in rows) + '\n')
    pin(response)
    for path, expected in pins.items():
        assert sha(path) == expected
    command = [str(compiler), *flags, '/Fo' + str(objects) + os.sep, '@' + str(response)]
    log = OUT / 'compile.log'
    if args.finalize_existing:
        capture = json.loads(pin(OUT / 'batch-exit.json').read_bytes())
        assert capture['command'] == command and capture['log_sha256'] == sha(log)
        exit_code, seconds = capture['compiler_exit_code'], capture['seconds']
    else:
        start = time.perf_counter()
        process = subprocess.run(command, cwd=OUT, capture_output=True, timeout=120, env={**os.environ, 'VSLANG': '1033'})
        seconds = round(time.perf_counter() - start, 3)
        exit_code = process.returncode
        log.write_bytes(process.stdout + process.stderr)
        write(OUT / 'batch-exit.json', dict(command=command, compiler_exit_code=exit_code, seconds=seconds,
                                          log=relative(log), log_sha256=sha(log)))
    assert exit_code == 0, log.read_text(errors='replace')
    assert not re.search(rb'\berror C\d+', log.read_bytes())
    warnings = re.findall(rb'\bwarning (C\d+)', log.read_bytes())
    assert warnings == [b'C4146'], warnings  # Original unsigned negation is defined modulo2^32.
    pin(log)
    for row in rows:
        obj = objects / (row['va'] + '.obj')
        row.update(compiled=True, compiler_exit_code=0, object=relative(obj), object_sha256=sha(obj), symbols=coff.coff_symbols(obj))
    for path, expected in pins.items():
        assert sha(path) == expected
    summary = dict(schema=1, original_sha256=helper.SHA, compiler_sha256=sha(compiler), objects_compiled=2,
                   actual_compiler_batches=1, actual_compiler_batches_this_pass=0 if args.finalize_existing else 1,
                   compiler_exit_code=exit_code, seconds=seconds, warnings=len(warnings), warning_codes=['C4146'],
                   results=rows, input_sha256={relative(p): h for p, h in pins.items()},
                   original_instructions_verified=sum(len(r['instructions']) for r in proof_rows),
                   limits=['Private raw representation declarations only; no canonical data owner',
                           'Full original native execution/caller ABI/global lifetimes remain open',
                           '00598630 signed index arithmetic overflow remains open; unchanged body',
                           'No production changes, stubs or storage allocation',
                           'First driver stopped on C4146 after successful batch; metadata finalization does not recompile'])
    write(RUN / 'summary.json', summary)
    write(RUN / 'validation.json', dict(summary_sha256=sha(RUN / 'summary.json'), input_guards_before_after=True,
                                      objects_compiled=2, actual_compiler_batches=1))
    print(json.dumps(dict(objects=2, seconds=seconds, original_instructions=summary['original_instructions_verified'])))


if __name__ == '__main__':
    main()
