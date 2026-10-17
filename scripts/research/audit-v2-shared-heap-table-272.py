"""Read-only acceptance audit of the Run272 heap-table storage packet."""
import hashlib, importlib.util, json, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/272-shared-heap-table'
OUT = ROOT / 'local/experiments/v2-shared-heap-table-272'
RAW = '?DAT_006b4f20@@3IA'
CAN = '?heaps_006b4f20@porsche@@3PAPAUOriginalHeap@1@A'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(Path(path).read_bytes())

def local(name):
    p = Path(name)
    return p if p.is_absolute() else ROOT / p

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    a = load(RUN / 'summary.json')
    b = load(RUN / 'bindings/summary.json')
    p = load(RUN / 'preflight.json')
    assert a['kind'] == 'original-writable-data' and b['kind'] == 'proven-link-contract'
    assert a['functions_added'] == b['new_function_count'] == 0
    assert a['storage_va'] == p['storage_va'] == '006b4f20'
    assert a['storage_bytes'] == p['storage_bytes'] == 64
    assert a['initial_bytes'] == p['initial_hex'] == '00' * 64
    assert p['one_past_va'] == '006b4f60' and p['highlow_sites'] == 30
    assert len(p['entry_liveness_unproved']) == 4
    assert b['ordinary_summary_sha256'] == sha(RUN / 'summary.json')
    assert b['aliases'][0]['from'] == RAW and b['aliases'][0]['to'] == CAN
    assert b['aliases'][0]['va'] == '006b4f20'
    assert a['data_symbols'] == a['physical_data_cells'] == 1
    assert len(a['support_objects']) == len(b['support_objects']) == 1
    assert a['compiler_sha256'] == b['compiler_sha256']
    assert '/MP6' in a['compiler_command'] and a['actual_compiler_batches'] == 1
    assert a['compiler_execution_receipt'] == b['compiler_execution_receipt']
    for report in (a, b):
        for name, expected in report['input_sha256'].items():
            assert sha(local(name)) == expected, name
    assert sha(ROOT / 'local/game/Porsche.exe') == a['original_sha256']
    assert sha(local(p['canonical_source'])) == p['canonical_source_sha256']
    assert sha(local(p['canonical_header'])) == p['canonical_header_sha256']
    assert p['canonical_declaration'].encode() in local(p['canonical_source']).read_bytes()
    assert ('extern ' + p['canonical_declaration']).encode() in local(p['canonical_header']).read_bytes()
    image = (ROOT / 'local/game/Porsche.exe').read_bytes()
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    assert image[pe:pe+4] == b'PE\0\0'
    n, oh = struct.unpack_from('<H', image, pe+6)[0], struct.unpack_from('<H', image, pe+20)[0]
    rva = 0x6b4f20 - 0x400000
    matches = []
    for i in range(n):
        q = pe+24+oh+i*40
        name = image[q:q+8].split(b'\0')[0]
        vs, va, rs, rp = struct.unpack_from('<IIII', image, q+8)
        chars = struct.unpack_from('<I', image, q+36)[0]
        if va <= rva and rva+64 <= va+vs:
            matches.append((name, va, rs, chars))
    assert len(matches) == 1
    name, va, rs, chars = matches[0]
    assert name == b'.data' and rva >= va+rs
    assert chars & 0x80000000 and not chars & 0x20000000
    coff = module('coff272audit', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    parser = module('parse272audit', ROOT / 'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py')
    drow, brow = a['support_objects'][0], b['support_objects'][0]
    assert drow['symbols'] == coff.coff_symbols(local(drow['object']))
    assert brow['symbols'] == coff.coff_symbols(local(brow['object']))
    assert drow['symbols'] == {'defined':[CAN], 'undefined':[], 'common':[], 'weak':[]}
    assert brow['symbols'] == {'defined':[], 'undefined':[], 'common':[], 'weak':[]}
    d = parser.coff(local(drow['object']))
    sym = next(x for x in d['symbols'] if x['name'] == CAN)
    section = d['sections'][sym['section']-1]
    assert sym['value'] == 0 and section['size'] == 64 and section['reloc_count'] == 0
    assert section['chars'] & 0x80000000 and not section['chars'] & 0x20000000
    assert drow['storage_sections'] == [dict(name=section['name'],size=section['size'],chars=section['chars'],reloc_count=section['reloc_count'])]
    assert local(drow['generated_source']).read_text() == '#include "porsche/heap.hpp"\nnamespace porsche {\nOriginalHeap* heaps_006b4f20[16];\n}\n'
    directive = '/alternatename:' + RAW + '=' + CAN
    binding = parser.coff(local(brow['object']))
    ds = next(x for x in binding['sections'] if x['name'] == '.drectve')
    assert binding['bytes'][ds['raw']:ds['raw']+ds['size']].decode('ascii').strip() == directive
    assert brow['directive'] == b['aliases'][0]['directive'] == directive
    assert all(not (x['chars'] & 0x20000000) for x in binding['sections'])
    receipt = load(local(a['compiler_execution_receipt']))
    assert receipt['exit_code'] == 0 and receipt['command'] == a['compiler_command']
    roots = [str(local(x).resolve()) for x in drow['include_directories']]
    actual_roots = [receipt['command'][i+1] for i, x in enumerate(receipt['command'][:-1]) if x == '/I']
    assert roots == actual_roots and len(roots) == 5
    for row in (drow, brow):
        assert row['compiler_command'] == receipt['command']
        assert row['include_directories'] == drow['include_directories']
        assert row['compiler_execution_receipt'] == a['compiler_execution_receipt']
        assert sha(local(row['generated_source'])) == row['generated_source_sha256']
        assert sha(local(row['object'])) == row['object_sha256']
        assert sha(local(row['source_dependencies'])) == row['source_dependencies_sha256']
        for path, h in row['dependency_sha256'].items():
            assert sha(local(path)) == h, path
    for consumer in p['raw_consumers']:
        assert sha(local(consumer['object'])) == consumer['object_sha256']
        body, relocs = module('fn272audit', ROOT / 'scripts/research/audit-v2-nested-calls-229.py').coff_function(local(consumer['object']),consumer['defined'])
        refs = [x for x in relocs if x['symbol'] == RAW]
        assert len(refs) == len(consumer['views'])
        for ref, view in zip(refs, consumer['views']):
            assert ref == view['relocation'] and ref['type'] == 6
            i = view['instruction_offset']
            assert body[i-3:i] == bytes.fromhex('83e00f')
            assert body[i:i+7] == bytes.fromhex('8b0c8500000000')
            assert ref['offset'] == i+3 and view['effective_slots'] == '0..15'
    for label in ('fixture-link-001','fixture-native-001'):
        r = load(OUT / (label+'.execution.json'))
        assert r['exit_code'] == 0 and sha(local(r['log'])) == r['log_sha256']
    assert sha(local(a['native_fixture']['executable'])) == a['native_fixture']['executable_sha256']
    assert a['native_fixture']['exit_code'] == 0 and a['native_fixture']['slots'] == 16
    assert a['native_fixture']['zero_bytes'] == 64 and a['native_fixture']['crosswrites']
    validation = dict(schema=1,status='pass',summary_sha256=sha(RUN/'summary.json'),binding_summary_sha256=sha(RUN/'bindings/summary.json'),audit_script_sha256=sha(__file__),original_sha256=a['original_sha256'],physical_allocations=1,slots=16,raw_consumer_relocations=3,native_exit_code=0,limits=['preceding 006b4b20..006b4f1f relative adjacency not provided','candidate function entry liveness and fill algorithms unproved','x86 COFF raw scalar-array alias is not a portable C++ type contract'])
    (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
    binding_validation = {**validation, 'summary_sha256':sha(RUN/'bindings/summary.json'), 'ordinary_summary_sha256':sha(RUN/'summary.json')}
    (RUN/'bindings/validation.json').write_text(json.dumps(binding_validation,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status='pass',actual_PE=True,actual_COFF=True,raw_sites=3,slots=16,native_exit=0)))

if __name__ == '__main__':
    main()
