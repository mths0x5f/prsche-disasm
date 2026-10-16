"""Read-only, independent acceptance audit of the frozen Run246 pilot."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/246-x86-cpp-pilot'
OUT=ROOT/'local/experiments/v2-x86-cpp-pilot-246'
VAS=('00590290','004930f0','00590070')

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''): h.update(block)
    return h.hexdigest()

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def load(path): return json.loads(Path(path).read_bytes())

def original_bytes(image,va,n):
    pe=struct.unpack_from('<I',image,0x3c)[0]
    assert image[pe:pe+4]==b'PE\0\0'
    sections=struct.unpack_from('<H',image,pe+6)[0]
    optional=struct.unpack_from('<H',image,pe+20)[0]
    base=struct.unpack_from('<I',image,pe+24+28)[0]
    rva=int(va,16)-base
    for i in range(sections):
        p=pe+24+optional+40*i
        size,start,rawsize,offset=struct.unpack_from('<IIII',image,p+8)
        if start<=rva and rva+n<=start+rawsize:
            assert rva+n<=start+size
            return image[offset+rva-start:offset+rva-start+n]
    raise AssertionError(('PE bytes not file backed',va))

def main():
    summary=load(RUN/'summary.json')
    proof=load(RUN/'proof-before-compile.json')
    driver=module('driver246_audit',ROOT/'scripts/research/experiment-v2-x86-cpp-246.py')
    coff=module('coff246_audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
    oracle_parser=module('oracle246_audit',ROOT/'scripts/research/audit-v2-nested-calls-229.py')
    assert summary['kind']=='isolated-static-x86-to-cpp-pilot'
    assert tuple(summary['experimental_vas'])==VAS and set(proof['original_hex'])==set(VAS)
    assert summary['new_accepted_functions']==0 and summary['production_or_union_changed'] is False
    assert summary['actual_compiler_batches']==1 and summary['existing_owner_regressions']==3
    assert summary['game_algorithm_reimplementations']==0
    for name,sha in summary['input_sha256'].items():
        path=Path(name)
        if not path.is_absolute(): path=ROOT/path
        assert digest(path)==sha,(name,'input hash drift')
    assert summary['input_sha256']['iterations/v2/001-original-recovery/runs/246-x86-cpp-pilot/proof-before-compile.json']==digest(RUN/'proof-before-compile.json')
    image=(ROOT/'local/game/Porsche.exe').read_bytes()
    assert digest(ROOT/'local/game/Porsche.exe')==summary['original_sha256']==proof['original_sha256']
    assert (OUT/'machine246.h').read_text(encoding='utf8')==driver.HEADER
    assert (OUT/'state-fixture.cpp').read_text(encoding='utf8')==driver.FIXTURE
    assert driver.FIXTURE.count('cases246!=375808u')==1
    assert 1024+4**3*6*16+10*6*3*2*256*4==summary['state_comparisons']==375808
    witnessed=0
    for va in VAS:
        raw=bytes.fromhex(proof['original_hex'][va])
        assert original_bytes(image,va,len(raw))==raw,('original PE bytes',va)
        generated,witness=driver.translate(raw,int(va,16))
        assert (OUT/(va+'.cpp')).read_text(encoding='utf8')==generated,('generated C++ drift',va)
        assert witness==proof['instruction_lowering'][va],('lowering drift',va)
        assert b''.join(bytes.fromhex(w['bytes']) for w in witness)==raw
        assert witness[-1]['mnemonic']=='ret'
        assert proof['existing_owners'][va]['object_sha256']==digest(ROOT/proof['existing_owners'][va]['object'])
        assert proof['existing_owners'][va]['generated_source_sha256']==digest(ROOT/proof['existing_owners'][va]['generated_source'])
        native=coff.coff_symbols(OUT/'objects'/(va+'.obj'))
        assert native['defined']==[f'?translated_{va}@@YAXAAUMachine246@@@Z'] and not native['common']
        witnessed+=len(witness)
    assert witnessed==summary['translated_original_instructions']==28
    assert sum(len(bytes.fromhex(proof['original_hex'][va])) for va in VAS)==summary['translated_original_bytes']==76
    assert set(summary['unsupported_inputs_rejected'])=={'unsupported INT3','truncated instruction','branch into missing instruction boundary'}
    for raw in (b'\xcc',b'\x8b',b'\x74\x01\xc3'):
        try: driver.translate(raw,0x1000)
        except ValueError: pass
        else: raise AssertionError(('unsupported input accepted',raw.hex()))
    fixture_symbols=coff.coff_symbols(OUT/'objects/state-fixture.obj')
    for va in VAS:
        assert f'?original_{va}_246@@YAXXZ' in fixture_symbols['defined']
    assert '?count246@@3IA' in fixture_symbols['defined']
    assert '?table246@@3IA' in fixture_symbols['defined']
    for row in summary['oracle']:
        va=row['va']
        assert va in VAS and row['normalized_exact'] and row['bytes']==len(bytes.fromhex(proof['original_hex'][va]))
        body,relocs=oracle_parser.coff_function(OUT/'objects/state-fixture.obj',f'?original_{va}_246@@YAXXZ')
        expected=bytearray.fromhex(proof['original_hex'][va])
        expected_relocs=([dict(offset=10,symbol='?count246@@3IA',type=6),dict(offset=28,symbol='?table246@@3IA',type=6)] if va=='00590070' else [])
        assert relocs==row['relocations']==expected_relocs
        for reloc in relocs: expected[reloc['offset']:reloc['offset']+4]=bytes(4)
        assert body==bytes(expected),('actual fixture oracle bytes',va)
    compile_receipt=load(OUT/'compile.execution.json')
    first_link=load(OUT/'first-fixture-link.execution.json')
    link=load(OUT/'fixture-link.execution.json')
    native=load(OUT/'fixture-native.execution.json')
    assert compile_receipt['exit_code']==0 and abs(compile_receipt['elapsed_seconds']-summary['compile_seconds'])<1e-9
    assert compile_receipt['command']==summary['command'] and '/MP6' in compile_receipt['command']
    assert len([x for x in compile_receipt['command'] if x.lower().endswith('.cpp')])==4
    assert not re.search(rb'(?:warning|error) [CD]\d+', (OUT/'compile.log').read_bytes())
    assert first_link['exit_code']!=0 and b'memcpy' in (OUT/'first-fixture-link.log').read_bytes()
    assert link['exit_code']==0 and native['exit_code']==summary['native_fixture_exit_code']==0
    assert abs(native['elapsed_seconds']-summary['native_seconds'])<1e-9
    assert {Path(x).name.lower() for x in link['command'] if x.lower().endswith('.lib')} >= {'libcmt.lib','libvcruntime.lib','libucrt.lib','kernel32.lib'}
    assert [x for x in first_link['command'] if x.lower().endswith('.obj')]==[x for x in link['command'] if x.lower().endswith('.obj')]
    assert summary['resumed_existing_compile'] is True
    assert digest(OUT/'captured-compile-driver.py')==summary['input_sha256']['local/experiments/v2-x86-cpp-pilot-246/captured-compile-driver.py']
    print(json.dumps(dict(passed=True,original_bytes=76,instructions=28,oracle_functions=3,native_comparisons=375808,compiler_batches=1,existing_owner_regressions=3,accepted_functions=0,pins=len(summary['input_sha256']))))

if __name__=='__main__': main()
