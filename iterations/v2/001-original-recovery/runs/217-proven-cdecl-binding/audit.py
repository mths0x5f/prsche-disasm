"""Read-only exact binding/native fixture proof audit; no compiler/linker rerun."""
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]; RUN=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('experiment217audit',ROOT/'scripts/research/experiment-v2-proven-cdecl-binding-217.py'); experiment=importlib.util.module_from_spec(spec); spec.loader.exec_module(experiment)
spec=importlib.util.spec_from_file_location('coff217audit',ROOT/'scripts/research/build-v2-compile-corpus.py'); coff=importlib.util.module_from_spec(spec); spec.loader.exec_module(coff)
summary_path=RUN/'summary.json'; report=json.loads(summary_path.read_bytes()); validation=json.loads((RUN/'validation.json').read_bytes())
assert validation['summary_sha256']==sha(summary_path)
def verify(item):
    name,expected=item; path=Path(name) if Path(name).is_absolute() else ROOT/name; assert sha(path)==expected,('input drift',name)
with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(verify,report['input_sha256'].items()))
assert report['kind']=='proven-link-contract' and report['new_function_count']==0
assert len(report['support_objects'])==len(report['aliases'])==1
support=report['support_objects'][0]; alias=report['aliases'][0]
assert support['id']==alias['support_object_id']=='cdecl-binding-00590290'
assert alias['from']=='?FUN_00590290@@YAIII@Z' and alias['to']=='?FUN_00590290@@YAIXZ' and alias['va']=='00590290'
assert alias['directive']=='/alternatename:'+alias['from']+'='+alias['to']
source=ROOT/support['generated_source']; obj=ROOT/support['object']
assert sha(source)==support['generated_source_sha256'] and sha(obj)==support['object_sha256']
assert coff.coff_symbols(obj)==support['symbols'] and all(not v for v in support['symbols'].values())
sections=experiment.coff_sections(obj); directives=[bytes.fromhex(s['bytes']).decode().strip() for s in sections if s['name']=='.drectve']
assert directives==[alias['directive']] and not any(s['bytes'] for s in sections if s['name'].startswith('.text'))
assert source.read_text().count('#pragma comment(linker,')==1
for name,expected in support['dependency_sha256'].items():assert sha(ROOT/name)==expected
target=report['cached_target']; target_obj=ROOT/target['object']
assert sha(target_obj)==target['object_sha256'] and coff.coff_symbols(target_obj)==target['symbols']
texts=[s for s in experiment.coff_sections(target_obj) if s['name'].startswith('.text') and s['bytes']]
assert len(texts)==1 and texts[0]['bytes']=='558bec33c05dc3' and texts[0]['relocations']==0
assert target['symbols']['defined']==[alias['to']] and not target['symbols']['undefined']
assert alias['proof']['original_body_hex']=='33c0c3' and alias['proof']['unused_stack_offsets']==[4,8]
assert alias['proof']['caller_passed_bytes']==alias['proof']['caller_cleanup_bytes']==8 and alias['proof']['callee_ret_pop_bytes']==0
assert alias['proof']['cached_object_sha256']==target['object_sha256']
fixture=report['fixture']; fixture_source=ROOT/fixture['source'];fixture_obj=ROOT/fixture['object']
assert fixture_source.read_text()==experiment.FIXTURE and sha(fixture_source)==fixture['source_sha256']
assert sha(fixture_obj)==fixture['object_sha256'] and coff.coff_symbols(fixture_obj)==fixture['symbols']
assert alias['from'] in fixture['symbols']['undefined'] and alias['to'] in fixture['symbols']['undefined']
# Bind the exact assembly reference symbol to its own native section, not merely
# any equal byte sequence in the fixture object.
raw=fixture_obj.read_bytes(); _,n,_,symoff,count,optional,_=struct.unpack_from('<HHIIIHH',raw);strings=raw[symoff+count*18:];i=0;reference=[]
while i<count:
    off=symoff+i*18;name=raw[off:off+8]
    if name[:4]==b'\0'*4:
        start=struct.unpack_from('<I',name,4)[0];text=strings[start:strings.index(b'\0',start)].decode()
    else:text=name.rstrip(b'\0').decode()
    value,section,_,storage,aux=struct.unpack_from('<IhHBB',raw,off+8)
    if text=='?original_reference@@YAXXZ' and storage==2 and section>0:
        sec=20+(section-1)*40;size,at=struct.unpack_from('<II',raw,sec+16);reference.append(raw[at+value:at+size].hex())
    i+=1+aux
assert reference==['33c0c3']
assert sha(ROOT/fixture['exe'])==fixture['exe_sha256'] and sha(ROOT/fixture['map'])==fixture['map_sha256']
assert fixture['cases']==1088 and fixture['checks']==18497
for label,result in report['native_commands'].items():
    assert result['observed_exit_code']==0 and result['seconds']>=0
    assert sha(ROOT/result['log'])==result['log_sha256']
    capture=ROOT/result['log'];capture=capture.parent.parent/(label+'-capture.json')
    assert json.loads(capture.read_bytes())==result
    log=(ROOT/result['log']).read_text()
    assert not re.search(r'\b(?:fatal error|error)\s+[CLD]\d+',log,re.I)
    warnings=re.findall(r'\bwarning\s+([CLD]\d+):',log,re.I)
    assert warnings==(['C4731','C4731'] if label=='compile' else []),warnings
assert not report['ownership']['canonical_exact_or_interior'] and not report['ownership']['wip_implementations']
for path in (RUN/'README.md',summary_path,Path(__file__),ROOT/'scripts/research/experiment-v2-proven-cdecl-binding-217.py',source,fixture_source,ROOT/report['compiler_response']): assert b'\r' not in path.read_bytes()
validation.update(read_only_audit_sha256=sha(Path(__file__)),readme_sha256=sha(RUN/'README.md'),actual_support_no_function_symbols_pass=True,
    exact_one_actual_directive_pass=True,actual_cached_target_body_pass=True,actual_original_reference_symbol_bytes_pass=True,
    actual_compile_link_native_capture_chain_pass=True,new_text_LF_pass=True,support_id_interface_pass=True,
    fixture_warning_codes={'C4731':2},fixture_ebp_seed_warning_preserved=True,support_source_warning_count=0)
(RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in validation.items() if not k.endswith('sha256')},indent=2))
