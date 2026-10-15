"""Bounded original-address representation/declaration delta on frozen190 leaves."""
from __future__ import annotations
from collections import Counter
import hashlib, importlib.util, json, os, re, struct, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta'
OUT = ROOT/'local/experiments/v2-thiscall-leaf-delta-196'
PRIOR = ROOT/'iterations/v2/001-original-recovery/runs/190-thiscall-declaration-delta/summary.json'
EXPORT = ROOT/'iterations/v2/001-original-recovery/runs/179-ghidra-declarations/export'
spec = importlib.util.spec_from_file_location('leaves187', ROOT/'scripts/research/experiment-v2-thiscall-leaves-187.py')
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
dspec = importlib.util.spec_from_file_location('decl184', ROOT/'scripts/research/experiment-v2-declarations-184.py')
decl = importlib.util.module_from_spec(dspec); dspec.loader.exec_module(decl)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative = lambda p: Path(p).resolve().relative_to(ROOT).as_posix()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf8', newline='\n')


class OriginalPE:
    def __init__(self, image):
        self.image = image; nt = struct.unpack_from('<I', image, 0x3c)[0]
        optional = nt+24; self.base = struct.unpack_from('<I', image, optional+28)[0]
        assert struct.unpack_from('<H', image, optional)[0] == 0x10b
        count = struct.unpack_from('<H', image, nt+6)[0]
        size = struct.unpack_from('<H', image, nt+20)[0]; self.sections = []
        for i in range(count):
            off = optional+size+40*i
            virtual_size, rva, raw_size, raw = struct.unpack_from('<IIII', image, off+8)
            self.sections.append((self.base+rva, self.base+rva+raw_size, raw))
        reloc_rva, reloc_size = struct.unpack_from('<II', image, optional+96+5*8)
        data = self.bytes(self.base+reloc_rva, reloc_size); off = 0; self.highlow = set()
        while off < len(data):
            page, size = struct.unpack_from('<II', data, off)
            if size == 0: break
            assert size >= 8 and off+size <= len(data)
            for at in range(off+8, off+size, 2):
                entry = struct.unpack_from('<H', data, at)[0]
                if entry >> 12 == 3: self.highlow.add(self.base+page+(entry & 4095))
            off += size

    def bytes(self, va, size):
        matches = [(start, raw) for start, end, raw in self.sections if start <= va and va+size <= end]
        assert len(matches) == 1, (hex(va), size)
        start, raw = matches[0]; return self.image[raw+va-start:raw+va-start+size]


def selected_variant(records, name, va):
    matches = [(record, v) for record in records for v in record['variants']
               if v['symbol'].get('name') == name and va in v['consumer_vas']]
    assert len(matches) == 1, (name, va, len(matches))
    record, variant = matches[0]; symbol = variant['symbol']; storage = symbol['storage_detail']
    assert symbol['namespace'] == 'Global' and storage['memory'] and not storage['compound']
    assert len(storage['varnodes']) == 1 and storage['varnodes'][0]['bytes'] == symbol['bytes']
    return record, variant


def address_store_evidence(old, name, records, pe, catalog, index):
    record, variant = selected_variant(records, name, old['va']); symbol = variant['symbol']
    target = int(symbol['storage_detail']['varnodes'][0]['address'], 16)
    assert target == int(name.rsplit('_', 1)[1], 16) and symbol['bytes'] == 4
    instructions = base.abi.function_instructions(catalog[old['va']], index); candidates = []
    for row in instructions:
        raw = bytes.fromhex(row['bytes']); va = int(row['va'], 16)
        assert pe.bytes(va, len(raw)) == raw
        # Precisely C7 /0 mod=00, no displacement/SIB: MOV dword ptr [GPR], imm32.
        if len(raw) == 6 and raw[0] == 0xc7 and raw[1] & 0xf8 == 0 and raw[1] & 7 not in (4, 5):
            if struct.unpack_from('<I', raw, 2)[0] == target:
                assert va+2 in pe.highlow, ('missing original HIGHLOW', old['va'], row)
                candidates.append({**row, 'immediate_va': f'{va+2:08x}', 'table_va': f'{target:08x}',
                                   'highlow_relocation': True, 'receiver_store_bytes': 4,
                                   'table_identity': record['identity'], 'table_variant': variant})
    assert len(candidates) == 1, (old['va'], name, candidates)
    assert old['original_contract']['ret_agrees']
    # Prove that the memory operand still carries entry ECX, rather than
    # merely finding an unrelated address constant inside the same function.
    registers = {'ECX': True}; trace = []
    full_register = {'AL': 'EAX', 'AH': 'EAX', 'AX': 'EAX', 'BL': 'EBX', 'BH': 'EBX', 'BX': 'EBX',
                     'CL': 'ECX', 'CH': 'ECX', 'CX': 'ECX', 'DL': 'EDX', 'DH': 'EDX', 'DX': 'EDX',
                     'SI': 'ESI', 'DI': 'EDI', 'BP': 'EBP', 'SP': 'ESP'}
    for instruction in instructions:
        if instruction['va'] == candidates[0]['va']:
            raw = bytes.fromhex(instruction['bytes']); receiver = ['EAX', 'ECX', 'EDX', 'EBX', 'ESP', 'EBP', 'ESI', 'EDI'][raw[1] & 7]
            assert registers.get(receiver), ('store receiver not entry ECX', old['va'], receiver)
            candidates[0]['receiver_register'] = receiver; candidates[0]['entry_ecx_copy_trace'] = trace
            break
        assembly = instruction['instruction']; op = assembly.split(' ', 1)[0]
        assert not op.startswith('J') and op not in ('CALL', 'RET'), ('nonlinear pre-store trace', old['va'])
        copy = re.fullmatch(r'MOV (E[A-Z]{2}),([E][A-Z]{2})', assembly)
        dest = re.match(r'\w+ ([A-Z]+)(?:,|$)', assembly)
        if copy:
            registers[copy[1]] = registers.get(copy[2], False)
            if registers[copy[1]]: trace.append(instruction)
        elif dest and op not in ('CMP', 'TEST', 'PUSH'):
            reg = full_register.get(dest[1], dest[1])
            if reg in ('EAX', 'EBX', 'ECX', 'EDX', 'ESI', 'EDI', 'EBP', 'ESP'): registers[reg] = False
    return candidates[0]


def blocker_group(row):
    errors = [d for d in row.get('diagnostics', []) if 'error' in d['severity']]
    if any(d['code'] == 'C2440' for d in errors): return 'pointer_to_raw32_storage'
    if any(d['code'] == 'C2228' for d in errors): return 'partial_scalar_field'
    if any('uint3' in d['message'] for d in errors): return 'uint3_vocabulary'
    return 'missing_global_or_printed_alias'


def main():
    start = time.perf_counter()
    for p in (RUN, OUT, OUT/'sources', OUT/'headers', OUT/'objects', OUT/'logs'): p.mkdir(parents=True, exist_ok=True)
    prior = json.loads(PRIOR.read_bytes()); validation_path = PRIOR.parent/'validation.json'
    validation = json.loads(validation_path.read_bytes())
    assert validation['summary_sha256'] == sha(PRIOR) and validation['input_pins_pass']
    assert prior['real_coff_objects'] == 130 and prior['remaining_compiler_failures'] == 29
    assert prior['exact_original_body_byte_matches'] == 27 and prior['selected_unique_vas'] == 159
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    pins = {ROOT/name: expected for name, expected in prior['input_sha256'].items()}
    for p in (Path(__file__), PRIOR, validation_path, Path(spec.origin), Path(dspec.origin), EXPORT/'globals.jsonl', EXPORT/'types.jsonl'):
        pins[p.resolve()] = sha(p)
    for name in ('cl.exe', 'c1xx.dll', 'c2.dll'):
        p = base.abi.COMPILER.parent/name; pins[p] = sha(p)
    assert sha(base.abi.COMPILER) == prior['compiler_sha256']
    for old in prior['results']:
        pins[ROOT/old['generated_source']] = old['generated_source_sha256']
        pins.update({ROOT/name: expected for name, expected in old['dependency_sha256'].items()})
        if old['compiled']: pins[ROOT/old['object']] = old['object_sha256']
    for p, expected in pins.items(): assert sha(p) == expected, ('stale input', p)
    binary = next(r for r in base.abi.rows(ROOT/'research/binary-index/static/binaries.jsonl') if r['file'] == 'Porsche.exe')
    original = ROOT/'local/game'/binary['path']; pins[original] = base.abi.SHA
    assert sha(original) == base.abi.SHA; pe = OriginalPE(original.read_bytes())
    records = base.abi.rows(EXPORT/'globals.jsonl'); types = {r['path']: r for r in base.abi.rows(EXPORT/'types.jsonl')}
    # Exact DefaultDataType primitive metadata omitted by DataTypeManager iteration.
    for record in records:
        for v in record['variants']:
            t = v['symbol']['type']
            if t['path'] not in types and t['name'] in decl.PRIMITIVES and (t['length'], t['alignment']) == decl.PRIMITIVES[t['name']]: types[t['path']] = t
    catalog = {r['entry_va']: r for r in base.abi.rows(base.abi.CORPUS/'functions.jsonl')}; index = base.abi.instruction_index()
    # Only TUs whose complete missing declarations have exact per-consumer179 types.
    declaration_vas = {'0040e5a0', '0041b100', '004bd3c0', '00525c30', '005a0c50'}
    results = []; changed = []; evidence = []; census = Counter()
    for old in prior['results']:
        row = json.loads(json.dumps(old)); row['cache_reused'] = bool(old['compiled']); row['changed_196'] = False
        row['input_190_source'] = old['generated_source']; row['input_190_source_sha256'] = old['generated_source_sha256']
        if old['compiled']: results.append(row); continue
        census[blocker_group(old)] += 1; va = old['va']; text = (ROOT/old['generated_source']).read_text(encoding='utf8'); edits = []
        match = re.search(r'(?m)^  \*param_1 = &(PTR_(?:LAB|FUN)_[0-9a-f]{8});$', text)
        if match and blocker_group(old) == 'pointer_to_raw32_storage':
            assert 'undefined4 * param_1 = reinterpret_cast<undefined4 *>(this);' in text
            name = match[1]; proof = address_store_evidence(old, name, records, pe, catalog, index)
            before = match[0]; after = '  *param_1 = reinterpret_cast<undefined4>(&'+name+');'
            text = text[:match.start()]+after+text[match.end():]
            text = text.replace('#line 1 ', 'static_assert(sizeof(void*)==4 && sizeof(undefined4)==4, "original MOV address width");\n#line 1 ', 1)
            edits.append({'kind': 'original_mov_imm32_address_representation', 'before': before, 'after': after, 'proof': proof}); evidence.append({'va': va, **proof})
        if va in declaration_vas:
            missing = sorted({d['message'].split(':', 1)[0] for d in old['diagnostics'] if d['code'] == 'C2065' and 'error' in d['severity']})
            accepted = []
            for name in missing:
                record, variant = selected_variant(records, name, va); scoped = {**record, 'conflict': False, 'variants': [variant]}
                a, e = decl.declarations(types, [scoped]); assert len(a) == 1 and not e, (va, name, e)
                a[0]['original_identity_conflict'] = record['conflict']; accepted += a
            h = OUT/'headers'/(va+'-globals.h'); h.write_text(decl.header(accepted), encoding='utf8', newline='\n')
            scalar = re.search(r'^#include "[^\n]*ghidra-scalars-syntax-only\.h"\n', text, re.M); assert scalar
            text = text[:scalar.end()]+'#include "'+h.as_posix()+'"\n'+text[scalar.end():]
            edits.append({'kind': 'consumer_specific_179_declarations', 'header': relative(h), 'header_sha256': sha(h), 'records': accepted})
            row['dependency_sha256'].update(base.headers_closure([h], pins))
        if edits:
            source = OUT/'sources'/(va+'.cpp'); source.write_text(text, encoding='utf8', newline='\n'); obj = OUT/'objects'/(va+'.obj')
            if obj.exists(): obj.unlink()  # Exact known196 output only.
            row.update({'generated_source': relative(source), 'generated_source_sha256': sha(source), 'object': relative(obj), 'changed_196': True, 'edits_196': edits})
            pins[source] = sha(source); changed.append(row)
        results.append(row)
    assert census['pointer_to_raw32_storage'] == len(evidence) == 14 and len(changed) == 19
    flags = prior['compiler_flags']; assert '/MP6' in flags and '/O2' in flags
    assert not any(r['forced_headers'] for r in changed), 'Do not silently merge forced-include contracts'
    rsp = OUT/'logs/changed-19.rsp'; log = OUT/'logs/changed-19.log'
    rsp.write_text('\n'.join('"'+s+'"' for s in flags+['/Fo'+(OUT/'objects').as_posix()+'/']+[str(ROOT/r['generated_source']) for r in changed])+'\n', encoding='utf-8-sig', newline='\n')
    before = time.perf_counter(); p = subprocess.run([str(base.abi.COMPILER), '@'+str(rsp)], cwd=OUT, capture_output=True, encoding='utf8', errors='replace', env=base.abi.ENV, timeout=180)
    compile_seconds = time.perf_counter()-before; raw_log = p.stdout+p.stderr; log.write_text(raw_log, encoding='utf8', newline='\n')
    diagnostics = {r['va']: [] for r in changed}
    for m in re.finditer(r'porsche_method_([0-9a-f]{8})\((\d+),(\d+)\):\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)', raw_log):
        va, line, column, severity, code, message = m.groups(); assert va in diagnostics
        diagnostics[va].append({'line': int(line), 'column': int(column), 'severity': severity, 'code': code, 'message': message})
    for row in changed:
        obj = ROOT/row['object']; row['compiled'] = obj.exists(); row['diagnostics'] = diagnostics[row['va']]
        assert obj.exists() == (not any('error' in d['severity'] for d in row['diagnostics'])), row['va']
        if obj.exists():
            row.update({'object_sha256': sha(obj), 'object_bytes': obj.stat().st_size, 'compiler_exit_code': 0, **base.coff_symbols(obj)})
            sections = base.abi.text_sections(obj); row['native_text_sections'] = sections
            row['exact_original_body_bytes_match'] = any(s['relocations'] == 0 and s['bytes'] == row['original_instruction_bytes_hex'] for s in sections)
            assert any('Thiscall_'+row['va'] in s for s in row['defined_external_symbols'])
            row.pop('failure', None)
        else: row['failure'] = 'Additional exact diagnostics remain; no guessed casts, aliases, types or storage supplied.'
    for path, expected in pins.items(): assert sha(path) == expected, ('input mutation', path)
    oldmap = {r['va']: r for r in prior['results']}
    for row in results:
        assert row['original_contract'] == oldmap[row['va']]['original_contract'] and row['method_contract'] == oldmap[row['va']]['method_contract']
        if row['cache_reused']: assert row['object_sha256'] == oldmap[row['va']]['object_sha256']
    new = [r for r in changed if r['compiled']]; undefined = Counter(s for r in results if r['compiled'] for s in r['undefined_external_symbols'])
    report = {'schema': 1, 'module': 'Porsche.exe', 'original_sha256': base.abi.SHA, 'prior_summary': relative(PRIOR), 'prior_summary_sha256': sha(PRIOR),
              'input_sha256': {relative(k): v for k, v in sorted(pins.items(), key=lambda x: str(x[0]))}, 'compiler_sha256': sha(base.abi.COMPILER),
              'compiler_flags': flags, 'jobs': 6, 'initial_failure_groups': dict(census), 'selected_unique_vas': 159, 'reused_objects': 130,
              'changed_tus': len(changed), 'unmodified_failure_tus': 29-len(changed), 'original_highlow_stores_proved': len(evidence), 'actual_compiler_batches': 1,
              'new_objects': len(new), 'new_object_vas': [r['va'] for r in new], 'real_coff_objects': 130+len(new), 'remaining_compiler_failures': 29-len(new),
              'preserved_cached_body_byte_matches': 27, 'new_exact_original_body_byte_matches': sum(r['exact_original_body_bytes_match'] for r in new),
              'exact_original_body_byte_matches': sum(r.get('exact_original_body_bytes_match', False) for r in results if r['compiled']),
              'undefined_unique_symbols': len(undefined), 'undefined_references': sum(undefined.values()), 'undefined_symbols': dict(undefined),
              'compiler_response': relative(rsp), 'compiler_response_sha256': sha(rsp), 'compiler_log': relative(log), 'compiler_log_sha256': sha(log),
              'compiler_batch_exit_code': p.returncode, 'compile_seconds': round(compile_seconds, 3), 'elapsed_seconds': round(time.perf_counter()-start, 3), 'results': results,
              'boundary': 'Isolated compile candidates. Explicit address-to-raw32 stores proven by original MOV/PE HIGHLOW/tableVA and exact consumer179 declarations; unchanged186/187 method ABI/RET contracts. No class/lifetime proof, storage definitions, original execution, new ABI oracle or production changes.'}
    write_json(RUN/'summary.json', report)
    print(json.dumps({k: report[k] for k in ('initial_failure_groups', 'changed_tus', 'new_objects', 'new_object_vas', 'real_coff_objects', 'remaining_compiler_failures', 'exact_original_body_byte_matches', 'compile_seconds', 'elapsed_seconds')}, indent=2))


if __name__ == '__main__': main()
