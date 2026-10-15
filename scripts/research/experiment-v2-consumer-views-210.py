"""Two bounded original consumer lowerings; no storage or production edits."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '210-consumer-views'
OUT = ROOT / 'local/experiments/v2-consumer-views-210'
TARGETS = ['004012b0', '004032d0']
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    assert not (RUN / 'summary.json').exists() and not (OUT / 'batch-exit.json').exists(), 'Do not repeat a captured batch'
    assert not (OUT / 'compile.log').exists() and not list(OUT.glob('objects/*.obj'))
    OUT.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    pins = {}

    def pin(path, expected=None):
        path = Path(path).resolve()
        actual = sha(path)
        assert expected is None or expected == actual, path
        assert path not in pins or pins[path] == actual
        pins[path] = actual
        return path

    pin(Path(__file__))
    cache_path = pin(ROOT / 'local/experiments/v2-missing-body-triage-201/selected-inputs.json')
    cache = json.loads(cache_path.read_bytes())
    selection_path = pin(RUNS / '209-printed-alias-selection/summary.json')
    selection = json.loads(selection_path.read_bytes())
    assert cache['original_sha256'] == selection['original_sha256'] == SHA
    selected = {r['va']: r for r in selection['selected']}
    registry = pin(ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json')
    owners = {r['entry_va'] for r in json.loads(registry.read_bytes())['functions'] if r['module'] == 'Porsche.exe'}
    assert not owners.intersection(TARGETS)
    wip = []
    for name in ('formatter_search', 'rtti', 'formatter_stdio'):
        path = pin(ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe' / (name + '.cpp'))
        for va in TARGETS:
            assert not re.search(r'\b\w*' + va + r'\s*\([^;{}]*\)\s*\{', path.read_text(encoding='utf8'))
        wip.append(relative(path))
    for name in ('functions.jsonl', 'types.jsonl'):
        path = RUNS / '179-ghidra-declarations/export' / name
        pin(path, cache['input_sha256'][relative(path)])
    declarations = module('declarations210', pin(ROOT / 'scripts/research/experiment-v2-declarations-184.py'))
    coff = module('coff210', pin(ROOT / 'scripts/research/build-v2-compile-corpus.py'))
    union = module('union210', pin(ROOT / 'scripts/research/audit-v2-native-union-204.py'))
    original = pin(ROOT / 'local/game/Porsche.exe', SHA)
    image = original.read_bytes()
    sections = union.pe_sections(image)
    listing = pin(ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    instruction_rows = {va: [] for va in TARGETS}
    ranges = {va: [(int(a, 16), int(b, 16)) for a, b in cache['catalog'][va]['ranges']] for va in TARGETS}
    for line in listing.read_text(encoding='utf8').splitlines():
        match = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)', line)
        if not match:
            continue
        address = int(match[1], 16)
        va = next((va for va, spans in ranges.items() if any(a <= address <= b for a, b in spans)), None)
        if va is None:
            continue
        section = next(s for s in sections if s['va'] <= address < s['va'] + s['raw_bytes'])
        at = section['raw_offset'] + address - section['va']
        raw = bytes.fromhex(match[2])
        assert image[at:at + len(raw)] == raw
        instruction_rows[va].append(dict(pc=match[1], bytes=match[2], assembly=match[3]))
    original_by_pc = {r['pc']: r for rows in instruction_rows.values() for r in rows}
    required = {'004012cf': 'db05ac665e00', '004032d0': '8b0d1c675e00',
                '004032da': '8b01', '004032dc': '6a01', '004032de': 'ff10',
                '004032e0': 'c7051c675e0000000000', '004032ea': 'c3'}
    for pc, raw in required.items():
        assert original_by_pc[pc]['bytes'] == raw
    types = dict(cache['types'])
    primitive = pin(ROOT / 'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h')
    rows = []
    edits = []
    for va in TARGETS:
        original_source = pin(ROOT / selected[va]['source'], selected[va]['source_sha256'])
        source = original_source.read_text(encoding='utf8')
        metadata = cache['declarations'][va]
        entries = []
        for symbol in metadata['globals']:
            if va == '004012b0' and symbol['name'] == 'DAT_005e66ac':
                continue  # Its formal1-byte view is insufficient for original signed FILD32.
            if va == '004032d0':
                assert symbol['name'] == 'DAT_005e671c'
                assert symbol['declaration'] == 'undefined4 *DAT_005e671c'
                assert symbol['type']['class'].endswith('PointerDataType')
                assert (symbol['type']['length'], symbol['bytes']) == (4, 4)
                continue  # Exact179 declarator; pointer type is absent from the global type-manager export.
            t = symbol['type']
            if t['path'] not in types and t['name'] in declarations.PRIMITIVES:
                assert (t['length'], t['alignment']) == declarations.PRIMITIVES[t['name']]
                types[t['path']] = t
            record = dict(identity='Global::' + symbol['name'], conflict=False,
                          variants=[dict(symbol=symbol, consumer_vas=[va])])
            accepted, rejected = declarations.declarations(types, [record])
            assert accepted and not rejected, (va, rejected)
            entries.extend(accepted)
        header = OUT / (va + '-globals.h')
        extra = ('\nextern int _DAT_005e66ac;\nstatic_assert(sizeof(int) == 4, "FILD signed32");\n'
                 if va == '004012b0' else '\nextern undefined4 *DAT_005e671c;\nstatic_assert(sizeof(DAT_005e671c) == 4, "original pointer32");\n')
        header.write_text(declarations.header(entries) + extra, encoding='utf8', newline='\n')
        pin(header)
        insertion = re.search(r'^#include "[^\n]+"\n', source, re.M)
        assert insertion
        generated = source[:insertion.end()] + '#include "' + header.as_posix() + '"\n' + source[insertion.end():]
        if va == '004032d0':
            before = '    (**(code **)*DAT_005e671c)(1);'
            after = ('    uint *original_vtable = reinterpret_cast<uint *>(*DAT_005e671c);\n'
                     '    reinterpret_cast<void (__thiscall *)(void *, uint)>(original_vtable[0])(DAT_005e671c, 1);')
            assert generated.count(before) == 1
            generated = generated.replace(before, after)
            edits.append(dict(va=va, before=before, after=after, proof_pcs=list(required)[1:],
                              contract='original caller supplies ECX=self and stack uint32=1; callee cleans4; return ignored'))
        else:
            marker = '/* VA ' + va + ' */'
            assert generated.split(marker)[1] == source.split(marker)[1]
            edits.append(dict(va=va, extern='_DAT_005e66ac', storage='005e66ac:4', signed=True,
                              proof_pcs=['004012cf'], contract='FILD m32int, not raw float or unsigned conversion; no body edit'))
        cpp = OUT / (va + '.cpp')
        cpp.write_text(generated, encoding='utf8', newline='\n')
        pin(cpp)
        rows.append(dict(va=va, generated_source=relative(cpp), generated_source_sha256=sha(cpp),
                         original_source=relative(original_source), original_source_sha256=sha(original_source),
                         dependency_sha256={relative(p): sha(p) for p in (primitive, header, cpp)}))
    proof = RUN / 'proof-before-compile.json'
    write(proof, dict(schema=1, original_sha256=SHA, instructions=instruction_rows, edits=edits,
                     canonical_owners=0, wip_owners=0, ownership_wip_sources=wip,
                     boundary='Caller/width evidence only; full x87/ABI/body/data acceptance remains open'))
    pin(proof)
    prior = json.loads(pin(RUNS / '192-scalar-slice-objects/summary.json').read_bytes())
    compiler = pin(Path(prior['batches'][0]['command'][0]), prior['compiler_sha256'])
    for name in ('c1xx.dll', 'c2.dll'):
        pin(compiler.parent / name)
    flags = [f for f in prior['batches'][0]['command'][1:] if f.startswith('/') and not f.startswith('/Fo')]
    assert all(x in flags for x in ('/c', '/Od', '/Gy', '/TP', '/MP6'))
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    objects = OUT / 'objects'
    objects.mkdir()
    response = OUT / 'compile.rsp'
    response.write_text('\n'.join('"' + str(ROOT / r['generated_source']) + '"' for r in rows) + '\n', encoding='utf8', newline='\n')
    pin(response)
    for path, expected in pins.items():
        assert sha(path) == expected, ('input changed before compile', path)
    command = [str(compiler), *flags, '/Fo' + str(objects) + os.sep, '@' + str(response)]
    start = time.perf_counter()
    process = subprocess.run(command, cwd=OUT, capture_output=True, timeout=120, env={**os.environ, 'VSLANG': '1033'})
    seconds = round(time.perf_counter() - start, 3)
    log = OUT / 'compile.log'
    log.write_bytes(process.stdout + process.stderr)
    # Persist measured process evidence before parsing/attribution.
    write(OUT / 'batch-exit.json', dict(command=command, compiler_exit_code=process.returncode, seconds=seconds,
                                      log=relative(log), log_sha256=sha(log)))
    assert process.returncode == 0, log.read_text(errors='replace')
    assert not re.search(rb'\b(?:error|warning) C\d+', log.read_bytes())
    for row in rows:
        obj = objects / (row['va'] + '.obj')
        symbols = coff.coff_symbols(obj)
        row.update(compiled=True, compiler_exit_code=0, object=relative(obj), object_sha256=sha(obj), symbols=symbols)
    for path, expected in pins.items():
        assert sha(path) == expected, ('input changed after compile', path)
    summary = dict(schema=1, original_sha256=SHA, compiler_sha256=sha(compiler), objects_compiled=len(rows),
                   actual_compiler_batches=1, warnings=0, compiler_exit_code=process.returncode, seconds=seconds,
                   batch_command=command, compiler_log=relative(log), compiler_log_sha256=sha(log),
                   results=rows, input_sha256={relative(p): h for p, h in pins.items()},
                   original_instructions_verified=sum(map(len, instruction_rows.values())),
                   limits=['No native original differential execution or full body acceptance',
                           '004012b0 x87 intermediate rounding and overflow remain open',
                           '004032d0 receiver/stack contract proven at caller only; actual callee behavior open',
                           'No global allocation, game target, production registry or existing packet edits'])
    write(RUN / 'summary.json', summary)
    write(RUN / 'validation.json', dict(summary_sha256=sha(RUN / 'summary.json'), input_guards_before_after=True,
                                      objects_compiled=len(rows), actual_compiler_batches=1, actual_original_instructions_verified=summary['original_instructions_verified']))
    print(json.dumps(dict(objects=len(rows), seconds=seconds, original_instructions=summary['original_instructions_verified'])))


if __name__ == '__main__':
    main()
