"""Read-only211 PE/prototype/body/native-call cleanup audit; no tool execution."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]; RUN=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('coff211audit',ROOT/'scripts/research/build-v2-compile-corpus.py'); coff=importlib.util.module_from_spec(spec); spec.loader.exec_module(coff)
report=json.loads((RUN/'summary.json').read_bytes()); validation=json.loads((RUN/'validation.json').read_bytes())
assert validation['summary_sha256']==sha(RUN/'summary.json')
def verify(item):
    name,expected=item; assert sha(ROOT/name)==expected,('changed input',name)
with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(verify,report['input_sha256'].items()))
assert report['compiled_vas']==['00565cd0','00565e70'] and report['objects_compiled']==2 and not report['failed_vas']
assert report['actual_compiler_batches']==1 and report['observed_compiler_batch_exit_code']==0
assert report['compile_seconds']==1.122785 and not report['warning_codes']
capture_path=ROOT/report['native_capture']; assert sha(capture_path)==report['native_capture_sha256']; capture=json.loads(capture_path.read_bytes())
assert capture['observed_compiler_batch_exit_code']==0 and capture['compile_seconds']==report['compile_seconds']
assert capture['log_sha256']==report['compiler_log_sha256']==sha(ROOT/report['compiler_log'])
assert capture['response_sha256']==report['compiler_response_sha256']==sha(ROOT/report['compiler_response'])
prepare_path=ROOT/capture['prepare']; assert sha(prepare_path)==capture['prepare_sha256']; prepare=json.loads(prepare_path.read_bytes())
assert prepare['before_guard_pass'] and prepare['input_sha256']==report['input_sha256']
evidence_path=ROOT/report['evidence']; assert sha(evidence_path)==report['evidence_sha256']; evidence=json.loads(evidence_path.read_bytes())
assert evidence['bounded_body_bytes']==277 and sum(len(rows) for rows in evidence['instructions'].values())==127
assert ''.join(r['bytes'] for r in evidence['instructions']['00590290'])=='33c0c3'
assert all(not r['canonical_exact_or_interior'] and not r['wip_implementations'] for r in evidence['ownership'].values())


def native_call_cleanup(path,target):
    data=path.read_bytes(); machine,section_count,_,symoff,nsyms,optional,_=struct.unpack_from('<HHIIIHH',data)
    assert machine==0x14c and optional==0; strings=data[symoff+nsyms*18:]; names={}; i=0
    while i<nsyms:
        off=symoff+i*18; raw=data[off:off+8]
        if raw[:4]==b'\0'*4:
            start=struct.unpack_from('<I',raw,4)[0]; name=strings[start:strings.index(b'\0',start)].decode()
        else: name=raw.rstrip(b'\0').decode()
        names[i]=name; auxiliary=data[off+17]; i+=1+auxiliary
    found=[]
    for n in range(section_count):
        off=20+n*40; size,raw,reloc=struct.unpack_from('<III',data,off+16); count=struct.unpack_from('<H',data,off+32)[0]
        body=data[raw:raw+size]
        for i in range(count):
            at,index,typ=struct.unpack_from('<IIH',data,reloc+i*10)
            if names[index]==target:
                assert typ==0x14 and at>0 and body[at-1]==0xe8
                assert body[at+4:at+7]==bytes.fromhex('83c408'),('native cleanup not8',path,target,body[at+4:at+12].hex())
                found.append(dict(target=target,section=n+1,call_section_offset=at-1,cleanup_bytes='83c408',call_and_cleanup_hex=body[at-1:at+7].hex()))
    assert len(found)==1; return found[0]


native_evidence=[]
for row in report['results']:
    source=ROOT/row['generated_source']; original=ROOT/row['baseline_generated_source']
    assert sha(source)==row['generated_source_sha256'] and sha(original)==row['baseline_generated_source_sha256']
    text=original.read_text(encoding='utf8'); assert text.count(row['prototype_before'])==1
    assert source.read_text(encoding='utf8')==text.replace(row['prototype_before'],row['prototype_after'])
    marker='/* VA '+row['va']+' */'; assert source.read_bytes().split(marker.encode(),1)[1]==original.read_bytes().split(marker.encode(),1)[1]
    obj=ROOT/row['object']; assert sha(obj)==row['object_sha256'] and coff.coff_symbols(obj)==row['symbols']
    assert row['compiler_exit_code']==row['observed_compiler_batch_exit_code']==0 and row['owned_error_count']==row['owned_warning_count']==0
    assert row['actual_i386_coff_validated'] and row['compiled']
    callee=row['direct_call_contract']['callee']; target=next(name for name in row['symbols']['undefined'] if name.startswith('?FUN_'+callee+'@@'))
    native_evidence.append(dict(caller=row['va'],**native_call_cleanup(obj,target)))
for path in (RUN/'README.md',RUN/'summary.json',Path(__file__),ROOT/'scripts/research/experiment-v2-direct-call-contracts-211.py',ROOT/report['compiler_response'],ROOT/report['compiler_log'],capture_path): assert b'\r' not in path.read_bytes()
validation.update(read_only_audit_sha256=sha(Path(__file__)),readme_sha256=sha(RUN/'README.md'),prepare_capture_chain_pass=True,
    exact_two_prototype_edits_pass=True,byte_identical_caller_bodies_pass=True,actual_two_native_coff_pass=True,
    actual_native_call_cleanup8_pass=True,native_call_relocations=native_evidence,new_text_LF_pass=True)
(RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in validation.items() if not k.endswith('sha256')},indent=2))
