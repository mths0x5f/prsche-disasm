"""Read-only196 source/ABI/PE/COFF provenance audit; no compiler/oracle reruns."""
from collections import Counter
import hashlib, importlib.util, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('delta196', ROOT/'scripts/research/experiment-v2-thiscall-leaf-delta-196.py')
experiment = importlib.util.module_from_spec(spec); spec.loader.exec_module(experiment)
sha = experiment.sha
summary_path = RUN/'summary.json'; report = json.loads(summary_path.read_bytes())
prior = json.loads((ROOT/report['prior_summary']).read_bytes())
assert sha(ROOT/report['prior_summary']) == report['prior_summary_sha256']
assert report['selected_unique_vas'] == 159 and report['reused_objects'] == 130
assert report['changed_tus'] == 19 and report['actual_compiler_batches'] == 1
assert report['compiler_flags'] == prior['compiler_flags'] and '/MP6' in report['compiler_flags']
for name, expected in report['input_sha256'].items(): assert sha(ROOT/name) == expected, ('input mutation', name)
assert sha(ROOT/report['compiler_response']) == report['compiler_response_sha256']
assert sha(ROOT/report['compiler_log']) == report['compiler_log_sha256']
binary = next(r for r in experiment.base.abi.rows(ROOT/'research/binary-index/static/binaries.jsonl') if r['file'] == 'Porsche.exe')
original_path = ROOT/'local/game'/binary['path']; assert sha(original_path) == report['original_sha256']
pe = experiment.OriginalPE(original_path.read_bytes())
records = experiment.base.abi.rows(experiment.EXPORT/'globals.jsonl')
catalog = {r['entry_va']: r for r in experiment.base.abi.rows(experiment.base.abi.CORPUS/'functions.jsonl')}
index = experiment.base.abi.instruction_index()
oldmap = {r['va']: r for r in prior['results']}; undefined = Counter(); objects = matches = address_edits = declaration_tus = 0
new_vas = []; failures = []; changed_vas = []; changed_output_paths = set()
assert len({r['va'] for r in report['results']}) == 159
for row in report['results']:
    va = row['va']; old = oldmap[va]
    assert row['original_contract'] == old['original_contract'] and row['method_contract'] == old['method_contract']
    assert row['original_contract']['ret_agrees']
    actual = b''.join(pe.bytes(int(a, 16), int(b, 16)-int(a, 16)+1) for a, b in row['original_body_ranges'])
    assert actual.hex() == row['original_instruction_bytes_hex']
    assert hashlib.sha256(actual).hexdigest() == row['original_instruction_bytes_sha256']
    source = ROOT/row['generated_source']; assert sha(source) == row['generated_source_sha256']
    for name, expected in row['dependency_sha256'].items(): assert sha(ROOT/name) == expected
    if row['changed_196']:
        changed_vas.append(va); assert not old['compiled']; changed_output_paths.add(source)
        expected = (ROOT/old['generated_source']).read_text(encoding='utf8')
        for edit in row['edits_196']:
            if edit['kind'] == 'original_mov_imm32_address_representation':
                assert expected.count(edit['before']) == 1
                name = re.fullmatch(r'  \*param_1 = &(PTR_(?:LAB|FUN)_[0-9a-f]{8});', edit['before'])[1]
                assert edit['after'] == '  *param_1 = reinterpret_cast<undefined4>(&'+name+');'
                assert edit['proof'] == experiment.address_store_evidence(old, name, records, pe, catalog, index)
                expected = expected.replace(edit['before'], edit['after'])
                expected = expected.replace('#line 1 ', 'static_assert(sizeof(void*)==4 && sizeof(undefined4)==4, "original MOV address width");\n#line 1 ', 1)
                address_edits += 1
            else:
                assert edit['kind'] == 'consumer_specific_179_declarations'; h = ROOT/edit['header']
                assert sha(h) == edit['header_sha256']; changed_output_paths.add(h)
                assert h.read_text(encoding='utf8') == experiment.decl.header(edit['records'])
                for record in edit['records']:
                    identity, variant = experiment.selected_variant(records, record['symbol']['name'], va)
                    assert record['identity'] == identity['identity'] and record['symbol'] == variant['symbol']
                    assert record['consumer_vas'] == variant['consumer_vas']
                    assert record['original_identity_conflict'] == identity['conflict']
                scalar = re.search(r'^#include "[^\n]*ghidra-scalars-syntax-only\.h"\n', expected, re.M); assert scalar
                expected = expected[:scalar.end()]+'#include "'+h.as_posix()+'"\n'+expected[scalar.end():]
                declaration_tus += 1
        assert source.read_text(encoding='utf8') == expected, ('unapproved body/context change', va)
    else:
        assert row['generated_source'] == old['generated_source'] and row['generated_source_sha256'] == old['generated_source_sha256']
    if row['compiled']:
        obj = ROOT/row['object']; assert sha(obj) == row['object_sha256']
        symbols = experiment.base.coff_symbols(obj); assert symbols['machine'] == 'i386'
        assert symbols['defined_external_symbols'] == row['defined_external_symbols']
        assert symbols['undefined_external_symbols'] == row['undefined_external_symbols']
        assert any('Thiscall_'+va in name for name in symbols['defined_external_symbols'])
        sections = experiment.base.abi.text_sections(obj); assert sections == row['native_text_sections']
        exact = any(s['relocations'] == 0 and s['bytes'] == actual.hex() for s in sections)
        assert exact == row['exact_original_body_bytes_match']; matches += exact; objects += 1
        undefined.update(symbols['undefined_external_symbols'])
        if row['cache_reused']:
            assert old['compiled'] and row['object_sha256'] == old['object_sha256']
            assert row['exact_original_body_bytes_match'] == old['exact_original_body_bytes_match']
        else: new_vas.append(va)
    else:
        assert not (ROOT/row['object']).exists()
        assert any('error' in d['severity'] for d in row['diagnostics'])
        failures.append({'va': va, 'changed_196': row['changed_196'], 'diagnostics': row['diagnostics'], 'next_group': experiment.blocker_group(row)})
assert len(new_vas) == report['new_objects'] == 16 and new_vas == report['new_object_vas']
assert objects == report['real_coff_objects'] == 146 and matches == report['exact_original_body_byte_matches'] == 27
assert address_edits == report['original_highlow_stores_proved'] == 14 and declaration_tus == 5
assert len(failures) == report['remaining_compiler_failures'] == 13
assert dict(undefined) == report['undefined_symbols']
rsp = ROOT/report['compiler_response']; log = ROOT/report['compiler_log']
response = [s.strip('"') for s in rsp.read_text(encoding='utf-8-sig').splitlines()]
assert response[:len(report['compiler_flags'])] == report['compiler_flags']
assert response[len(report['compiler_flags'])+1:] == [str(ROOT/r['generated_source']) for r in report['results'] if r['changed_196']]
markers = re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$', log.read_text(encoding='utf8'))
assert Counter(markers) == Counter(changed_vas), 'One unique compiler filename marker per changed TU'
changed_output_paths.update((rsp, log, summary_path, Path(__file__), RUN/'README.md', Path(spec.origin)))
for path in changed_output_paths: assert b'\r' not in path.read_bytes(), ('new artifact not LF before hash', path)
validation = {'schema': 1, 'summary_sha256': sha(summary_path), 'audit_source_sha256': sha(Path(__file__)), 'readme_sha256': sha(RUN/'README.md'),
              'input_pins_pass': True, 'actual_original_pe_bytes_pass': True, 'original_highlow_receiver_stores_pass': True,
              'exact_consumer_179_declarations_pass': True, 'only_proved_source_changes_pass': True, 'original_abi_ret_contracts_preserved': True,
              'cached_objects_preserved': 130, 'changed_tus': len(changed_vas), 'compiler_filename_markers_pass': True, 'new_output_lf_pass': True,
              'real_coff_objects': objects, 'new_objects': len(new_vas), 'exact_body_byte_matches': matches,
              'undefined_unique_symbols': len(undefined), 'undefined_references': sum(undefined.values()), 'remaining_failures': failures,
              'boundary': 'Read-only provenance/PE/COFF validation, no compiler rerun, original execution, native ABI oracle or semantic acceptance.'}
(RUN/'validation.json').write_text(json.dumps(validation, indent=2)+'\n', encoding='utf8', newline='\n')
print(json.dumps({k: v for k, v in validation.items() if k != 'remaining_failures'}, indent=2))
