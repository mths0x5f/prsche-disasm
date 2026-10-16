"""Read-only36-owner source/native COFF/ABI census; no tool execution."""
from collections import Counter, defaultdict
import bisect, hashlib, importlib.util, json, re, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'224-canonical-owner-bindings'; OUT=ROOT/'local/experiments/v2-canonical-owner-bindings-224'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def signatures(text,va,ending):
    pattern=r'(?m)^[ \t]*([^;{}\n]*\b([A-Za-z_]\w*_'+va+r')\s*\([^;{}]*\)\s*(?:noexcept\s*)?)'+ending
    return [dict(signature=' '.join(m[1].split()),name=m[2],line=text[:m.start()].count('\n')+1,
                 body_start=m.end() if ending==r'\{' else None) for m in re.finditer(pattern,text)]


def split_parameters(text):
    result=[]; start=0; depth=0
    for i,c in enumerate(text):
        if c in '(<[':depth+=1
        elif c in ')>]':depth-=1
        elif c==',' and depth==0:result.append(text[start:i].strip());start=i+1
    tail=text[start:].strip()
    if tail and tail!='void':result.append(tail)
    return result


def shape(type_,return_=False):
    text=type_.strip(); text=re.sub(r'\[\[.*?\]\]|__declspec\([^)]*\)','',text).strip()
    text=re.sub(r'\b(?:__cdecl|__stdcall|__fastcall|const|volatile|register)\b','',text).strip()
    if text=='...':return dict(kind='varargs',bytes=None,location='variable')
    if '*' in text:return dict(kind='pointer',bytes=4,location='EAX' if return_ else 'stack4',spelling=text)
    if text in ('void',''):return dict(kind='void',bytes=0,location='none')
    text=re.sub(r'\bstd::','',text)
    unsigned={'uint','undefined4','uint32_t','uintptr_t','size_t','U','unsigned int','unsigned long'}
    signed={'int','int32_t','I','long','signed int','int32'}
    if text in unsigned:return dict(kind='unsigned32',bytes=4,location='EAX' if return_ else 'stack4')
    if text in signed:return dict(kind='signed32',bytes=4,location='EAX' if return_ else 'stack4')
    if text in ('char','signed char','int8_t','I8'):return dict(kind='signed8',bytes=1,location='AL' if return_ else 'stack4')
    if text in ('undefined1','byte','uint8_t','unsigned char','U8','bool'):return dict(kind='unsigned8',bytes=1,location='AL' if return_ else 'stack4')
    if text in ('short','int16_t'):return dict(kind='signed16',bytes=2,location='AX' if return_ else 'stack4')
    if text in ('ushort','undefined2','uint16_t'):return dict(kind='unsigned16',bytes=2,location='AX' if return_ else 'stack4')
    return dict(kind='unresolved_type',bytes=None,location='unknown',spelling=text)


def signature_shape(signature,name):
    before,after=signature.split(name,1); parameters=after.strip()[1:after.rfind(')')]
    result=shape(before,True); params=[]
    for p in split_parameters(parameters):
        if p=='...':params.append(shape(p));continue
        if '(*' in p or re.search(r'\(\s*__\w+\s*\*',p):params.append(dict(kind='function_pointer',bytes=4,location='stack4',spelling=p));continue
        p=re.sub(r'\s*=.*$','',p)
        p=re.sub(r'(?<=[\s*])(?:param_\d+|[a-z_]\w*)\s*$','',p).strip()
        params.append(shape(p))
    return dict(return_=result,parameters=params,varargs=any(p['kind']=='varargs' for p in params),
                calling_convention='fastcall' if '__fastcall' in before else 'stdcall' if '__stdcall' in before else 'cdecl')


def main():
    RUN.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);pins={}
    def read(path):
        path=Path(path).resolve();raw=path.read_bytes();pins[path]=hashlib.sha256(raw).hexdigest();return raw
    read(Path(__file__))
    baseline_path=RUNS/'216-sound-consumer-union/summary.json'; baseline=json.loads(read(baseline_path))
    assert baseline['original_sha256']==SHA
    selected=[r for r in baseline['frontier'] if r['classification']=='canonical_recovered_owner_outside_candidate_union'];assert len(selected)==36
    registry_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json';registry=json.loads(read(registry_path))['functions']
    owners={r['entry_va']:r for r in registry if r['module']=='Porsche.exe'}
    catalog_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl';catalog={r['entry_va']:r for r in map(json.loads,read(catalog_path).decode().splitlines())}
    manual_path=ROOT/'research/binary-index/manual-functions.jsonl'
    for r in map(json.loads,read(manual_path).decode().splitlines()):
        if r['module']=='Porsche.exe':catalog[r['entry_va']]=r
    ranges=sorted((int(a,16),int(b,16),r['va']) for r in selected for a,b in catalog[r['va']]['ranges']);starts=[a for a,b,v in ranges]
    original={r['va']:dict(call_sites=[],ret_sites=[],indirect_branches=[]) for r in selected}
    asm_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm'
    for line in read(asm_path).decode().splitlines():
        m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        if not m:continue
        address=int(m[1],16);i=bisect.bisect_right(starts,address)-1
        if i<0 or address>ranges[i][1]:continue
        entry=dict(va=m[1],bytes=m[2],instruction=m[3]);va=ranges[i][2]
        if m[3].startswith('CALL'):original[va]['call_sites'].append(entry)
        if m[3].startswith('RET'):original[va]['ret_sites'].append(entry)
        if m[3].startswith('JMP') and not re.fullmatch(r'JMP 0x[0-9a-f]+',m[3]):original[va]['indirect_branches'].append(entry)
    parserpath=ROOT/'scripts/research/build-v2-compile-corpus.py';read(parserpath)
    spec=importlib.util.spec_from_file_location('coff224',parserpath);coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    source_paths=sorted({ROOT/owners[r['va']]['source'] for r in selected});source_text={p:read(p).decode() for p in source_paths}
    include_root=ROOT/'iterations/v2/001-original-recovery/source/include'
    headers={}
    for path,text in source_text.items():
        actual=[]
        for name in re.findall(r'^#include "(porsche/[^\n]+)"',text,re.M):
            h=include_root/name
            if h.exists():headers[h]=read(h).decode();actual.append(h)
        headers[path]=actual
    # Basenames only narrow inventory; actual i386 symbols and recorded source
    # command are independently inspected before accepting an object candidate.
    buildroot=ROOT/'local/builds/v2'; basenames={p.stem for p in source_paths}; candidates=defaultdict(list)
    for p in buildroot.rglob('*.obj'):
        stem=p.name.removesuffix('.obj').removesuffix('.cpp')
        if stem in basenames:candidates[stem].append(p)
    object_rows={}; rejected=[]
    for path in source_paths:
        ordered=sorted(candidates[path.stem],key=lambda p:('trace' in str(p).lower(),not p.is_relative_to(buildroot/'001-original-recovery'),'Release' not in p.parts,-p.stat().st_mtime_ns,len(str(p))))
        chosen=None
        for obj in ordered:
            raw=obj.read_bytes()
            if raw[:2]!=b'\x4c\x01':rejected.append(dict(path=relative(obj),reason='not ordinary i386 COFF'));continue
            try:symbols=coff.coff_symbols(obj)
            except Exception as exc:rejected.append(dict(path=relative(obj),reason=type(exc).__name__));continue
            wanted={r['va'] for r in selected if owners[r['va']]['source']==relative(path)}
            if not any(any(va in symbol for va in wanted) for symbol in symbols['defined']):
                # A partial owner can lack the requested exact entry entirely;
                # keep its native object to prove absence rather than fabricate it.
                if not all(r['va']=='00534480' for r in selected if owners[r['va']]['source']==relative(path)):continue
            read(obj);command_records=[]
            for log in obj.parent.glob('*.tlog/CL.command.1.tlog'):
                data=log.read_bytes()
                try:text=data.decode('utf-16')
                except UnicodeError:continue
                chunks=re.split(r'(?m)^\^',text)
                matching=[c for c in chunks if str(path).upper() in c.upper()]
                if matching:
                    read(log);command_records.append(dict(path=relative(log),sha256=pins[log.resolve()],records=matching))
            chosen=dict(object=relative(obj),object_sha256=pins[obj.resolve()],machine='i386',symbols=symbols,
                candidate_paths=len(ordered),native_command_records=command_records,
                revision_limit='Current source/header hashes and actual native symbol identity are pinned separately; no new compile or historical source-revision attestation inferred')
            break
        object_rows[relative(path)]=chosen
    rows=[]
    for row in selected:
        va=row['va'];owner=owners[va];path=ROOT/owner['source'];text=source_text[path];defs=signatures(text,va,r'\{');public=[]
        for header in headers[path]:
            for declaration in signatures(headers[header],va,';'):public.append(dict(path=relative(header),sha256=pins[header.resolve()],**declaration))
        native=object_rows[owner['source']];native_symbols=[]
        if native:
            names={d['name'] for d in defs};native_symbols=[s for s in native['symbols']['defined'] if any(s.startswith('?'+name+'@') for name in names)]
        inferred=row['inferred_signature'];missing_name='FUN_'+va;missing_shape=signature_shape(inferred.rstrip(';'),missing_name)
        comparisons=[]
        for d in defs:
            actual_shape=signature_shape(d['signature'],d['name'])
            same_public=(actual_shape==missing_shape)
            raw_match=(not actual_shape['varargs'] and actual_shape['calling_convention']=='cdecl' and missing_shape['calling_convention']=='cdecl'
                and actual_shape['return_']['location']==missing_shape['return_']['location']
                and len(actual_shape['parameters'])==len(missing_shape['parameters'])
                and all(a['location']==b['location']!='unknown' for a,b in zip(actual_shape['parameters'],missing_shape['parameters'])))
            comparisons.append(dict(name=d['name'],actual_shape=actual_shape,normalized_type_categories_match=same_public,raw_abi_shape_candidate=raw_match,
                boundary='Width/return-location comparison only; actual original callers/providers/native binding not accepted'))
        blockers=[]
        if 'partial' in owner['status']:blockers.append('canonical owner explicitly partial; original complete entry is not established')
        if not defs:blockers.append('No exact VA function definition in actual canonical owner source')
        if not native_symbols:blockers.append('No exact VA canonical exported native symbol found')
        if original[va]['call_sites']:blockers.append('Original body is not leaf; callee/provider/state closure remains required')
        if any(c['actual_shape']['varargs'] for c in comparisons):blockers.append('Variadic canonical ABI vs fixed inferred declaration')
        if comparisons and not any(c['normalized_type_categories_match'] for c in comparisons):blockers.append('Public typed signature differs from missing getC declaration; raw representation alone is not binding approval')
        if native and native['symbols']['undefined']:blockers.append('Selected owner TU has unresolved native dependencies; symbol list supplied, provider object closure open')
        rows.append(dict(va=va,missing_symbol=row['symbol'],referring_object_vas=row['referring_object_vas'],inferred_signature=inferred,
            original_registry_contract=owner,source=owner['source'],source_sha256=pins[path.resolve()],source_definitions=defs,public_header_declarations=public,
            original_index=original[va],original_body_bytes=catalog[va]['body_bytes'],original_catalog_contract=catalog[va],
            original_abi_status='Original CALL/RET sites inventoried; hardware inputs/return contract not independently re-proved. Registry proof boundary remains authoritative.',
            source_type_alias_declarations=[dict(line=i+1,text=line.strip()) for i,line in enumerate(text.splitlines()) if re.search(r'\busing\s+\w+\s*=|\btypedef\b',line)],
            native_object=native,native_exact_definition_symbols=native_symbols,
            native_decorated_calling_conventions=[dict(symbol=s,calling_convention='cdecl' if '@@YA' in s else 'unclassified') for s in native_symbols],
            shape_comparisons=comparisons,blockers=blockers,immediate_binding_approved=False))
    # Conditional review shortlist only: matching scalar categories, existing native
    # symbols, full canonical owner. None qualifies as a simple leaf.
    preferred=['005366e0','0053aa60','005a2248'];shortlist=[]
    for va in preferred:
        r=next(r for r in rows if r['va']==va)
        if r['native_exact_definition_symbols'] and any(c['normalized_type_categories_match'] for c in r['shape_comparisons']):
            shortlist.append(dict(va=va,native_symbols=r['native_exact_definition_symbols'],source=r['source'],object=r['native_object']['object'],
                original_calls=len(r['original_index']['call_sites']),status='Conditional review only; provider/object/state closure and native binding fixture required',blockers=r['blockers']))
    counts=dict(owners=36,source_files=len(source_paths),native_owner_objects=sum(o is not None for o in object_rows.values()),
        functions_with_actual_native_definition=sum(bool(r['native_exact_definition_symbols']) for r in rows),
        partial_owners=sum('partial' in r['original_registry_contract']['status'] for r in rows),
        matching_normalized_public_scalar_shapes=sum(any(c['normalized_type_categories_match'] for c in r['shape_comparisons']) for r in rows),
        raw_abi_shape_candidates=sum(any(c['raw_abi_shape_candidate'] for c in r['shape_comparisons']) for r in rows),
        original_leaf_bodies=sum(not r['original_index']['call_sites'] and not r['original_index']['indirect_branches'] for r in rows),
        immediate_binding_candidates=0)
    report=dict(schema=1,kind='read-only-canonical-owner-binding-census',original_sha256=SHA,frontier_summary=relative(baseline_path),frontier_summary_sha256=sha(baseline_path),
        scope_vas=[r['va'] for r in rows],counts=counts,conditional_review_shortlist=shortlist,rows=rows,
        input_sha256={relative(p):h for p,h in pins.items()},native_object_inventory_rejections=rejected,
        compiler_commands=0,native_execution_commands=0,ghidra_commands=0,union_commands=0,
        limits=['Exactly36 canonical owners in216; no additional bodies, aliases, compilation or storage allocation.',
                'Actual object/symbol/type/RET inventory is not new native binding/fidelity acceptance.',
                'Every original body has CALLs; no simple leaf found. Conditional review targets require closure and fixture proof.',
                'Normalized scalar category equality includes undefined4/uint/u32; it is not identical C++ type, original input/return proof, or binding approval.',
                'Only directly included project headers are inventoried; cached objects are not attested against the current full historical include closure.'])
    assert all(sha(p)==h for p,h in pins.items()), 'Input mutation during read-only census'
    write(OUT/'object-inventory.json',object_rows);write(RUN/'summary.json',report)
    write(RUN/'validation.json',dict(schema=1,passed=True,original_sha256=SHA,
        summary_sha256=sha(RUN/'summary.json'),script_sha256=sha(Path(__file__)),
        guarded_inputs=len(pins),input_mutation_guard_passed=True,
        selected_frontier_rows=36,unique_owner_sources=len(source_paths),
        actual_i386_objects=sum(o is not None for o in object_rows.values()),
        actual_native_definition_rows=counts['functions_with_actual_native_definition'],
        original_nonleaf_rows=sum(bool(r['original_index']['call_sites']) for r in rows),
        native_command_log_rows=sum(bool(r['native_object'] and r['native_object']['native_command_records']) for r in rows),
        immediate_binding_candidates=0,compiler_commands=0,native_execution_commands=0,
        ghidra_commands=0,union_commands=0))
    print(json.dumps(dict(counts=counts,shortlist=shortlist),indent=2))


if __name__=='__main__':main()
