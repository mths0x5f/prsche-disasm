"""Bounded, read-only coverage census of Run245 original-body queue against Run246 translator."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

import capstone

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def relative(path):
    path=Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
def load(path):return json.loads(Path(path).read_bytes())
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
def write(path,obj):Path(path).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')

def main():
    RUN.mkdir(parents=True,exist_ok=True)
    if (RUN/'summary.json').exists():
        old=load(RUN/'summary.json')
        assert old['kind']=='bounded-x86-cpp-generator-coverage-census' and old['queue_original_body_trace_required']==85
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();sha=digest(path)
        assert expected is None or sha==expected,(path,sha,expected)
        pins[relative(path)]=sha
        return path
    def guard():
        for name,sha in pins.items():
            p=Path(name)
            if not p.is_absolute():p=ROOT/p
            assert digest(p)==sha,('input drift',name)
    pin(Path(__file__))
    driver=module('translate252',pin(ROOT/'scripts/research/experiment-v2-x86-cpp-246.py'))
    pin(Path(capstone.__file__))
    for dll in Path(capstone.__file__).parent.rglob('*capstone*.dll'):pin(dll)
    queue=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/245-automated-frontier-queue/summary.json'))
    pin(ROOT/queue['union_summary'],queue['union_summary_sha256'])
    compiled246=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/246-x86-cpp-pilot/summary.json'))
    compiled247=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/247-canonical-reuse-batch/summary.json'))
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'))
    catalog_path=pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl')
    catalog={r['entry_va']:r for r in (json.loads(line) for line in catalog_path.read_text(encoding='utf-8-sig').splitlines() if line.strip())}
    original=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes()
    assert queue['original_sha256']==compiled246['original_sha256']==compiled247['original_sha256']==SHA
    pe=struct.unpack_from('<I',original,0x3c)[0]
    assert original[pe:pe+4]==b'PE\0\0'
    nsec=struct.unpack_from('<H',original,pe+6)[0]
    optional=struct.unpack_from('<H',original,pe+20)[0]
    base=struct.unpack_from('<I',original,pe+24+28)[0]
    sections=[]
    for i in range(nsec):
        at=pe+24+optional+40*i
        name=original[at:at+8].split(b'\0',1)[0].decode('ascii')
        virtual,start,rawsize,raw=struct.unpack_from('<IIII',original,at+8)
        sections.append(dict(name=name,virtual=virtual,start=start,rawsize=rawsize,raw=raw))
    def pe_bytes(start,size):
        rva=start-base
        s=next((s for s in sections if s['start']<=rva and rva+size<=s['start']+s['rawsize'] and rva+size<=s['start']+s['virtual']),None)
        if s is None:return None
        return original[s['raw']+rva-s['start']:s['raw']+rva-s['start']+size]
    queue_rows=[r for r in queue['tasks'] if r['action']=='original_body_trace_required']
    assert len(queue_rows)==85
    registered={r.get('entry_va') for r in registry['functions'] if r.get('module')=='Porsche.exe'}
    existing=set(compiled246['experimental_vas'])|set(compiled247['compiled_vas'])
    excluded=[];rows=[]
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    for task in queue_rows:
        va=task['original_va']
        reasons=[]
        if va in registered:reasons.append('accepted_registry_owner')
        if va in existing:reasons.append('compiled_246_or_247_owner')
        if task.get('accepted_owners') or task.get('exact_source_definition_candidates'):reasons.append('accepted_or_WIP_source_owner')
        if task.get('compiled_entry'):reasons.append('compiled_queue_entry')
        if reasons:
            excluded.append(dict(va=va,reasons=reasons))
            continue
        entry=catalog.get(va)
        if not entry:
            rows.append(dict(va=va,rank=task['rank'],fanout=task['fanout'],classification='missing_index_entry'))
            continue
        ranges=entry['ranges']
        if len(ranges)!=1 or int(ranges[0][0],16)!=int(va,16):
            rows.append(dict(va=va,rank=task['rank'],fanout=task['fanout'],classification='noncontiguous_ranges',ranges=ranges))
            continue
        start,end=(int(x,16) for x in ranges[0]);size=end-start+1
        raw=pe_bytes(start,size)
        assert size==entry['body_bytes']==task['original_body_bytes'],(va,size,entry['body_bytes'],task['original_body_bytes'])
        if raw is None:
            rows.append(dict(va=va,rank=task['rank'],fanout=task['fanout'],classification='not_file_backed_PE_span',body_bytes=size))
            continue
        instructions=list(decoder.disasm(raw,start))
        decoded=sum(i.size for i in instructions)
        counts=collections.Counter(i.mnemonic for i in instructions)
        first_unsupported=None;classification='fullspan_supported';detail=''
        try:
            generated,witness=driver.translate(raw,start)
            assert sum(len(bytes.fromhex(w['bytes'])) for w in witness)==size
            assert len(witness)==len(instructions)
            assert generated.startswith('#include "machine246.h"')
        except ValueError as error:
            detail=str(error)
            if decoded!=size:classification='undecoded_tail'
            elif detail.startswith('Unsupported opcode'):
                classification='unsupported_opcode'
                first_unsupported=detail.split(':',1)[0].split()[-1]
            elif detail.startswith(('Unsupported operand','Unsupported destination','Unsupported register','Unsupported address register','Unsupported arithmetic width','Segment override unsupported')):
                classification='unsupported_operand'
            elif 'Branch target' in detail:classification='unsupported_branch_boundary'
            elif 'Open fallthrough' in detail:classification='unsupported_fallthrough'
            else:classification='other_translate_rejection'
        if decoded!=size and classification=='fullspan_supported':raise AssertionError(('partial decode accepted',va))
        rows.append(dict(va=va,rank=task['rank'],fanout=task['fanout'],native_symbols=task['native_symbols'],body_bytes=size,body_sha256=hashlib.sha256(raw).hexdigest(),decoded_bytes=decoded,decoded_instructions=len(instructions),classification=classification,first_rejection=detail,first_unsupported_address=first_unsupported,opcode_counts=dict(sorted(counts.items()))))
    guard()
    classes=collections.Counter(r['classification'] for r in rows)
    opcode_all=collections.Counter()
    opcode_rejected=collections.Counter()
    supported_mnemonics={'mov','lea','xor','and','test','cmp','sbb','neg','jl','jge','je','jz','ret'}
    missing_isa_bodies=collections.Counter()
    for row in rows:
        opcode_all.update(row.get('opcode_counts',{}))
        if row['classification']!='fullspan_supported':opcode_rejected.update(row.get('opcode_counts',{}))
        missing_isa_bodies.update(set(row.get('opcode_counts',{}))-supported_mnemonics)
    small=sorted((r for r in rows if r['classification']!='fullspan_supported' and r.get('body_bytes',999999)<=64),key=lambda r:(r['body_bytes'],-r['fanout'],r['va']))
    no_call_x87=[r['va'] for r in rows if r.get('opcode_counts') and 'call' not in r['opcode_counts'] and not any(op.startswith('f') for op in r['opcode_counts'])]
    report=dict(schema=1,kind='bounded-x86-cpp-generator-coverage-census',source_queue=relative(ROOT/'iterations/v2/001-original-recovery/runs/245-automated-frontier-queue/summary.json'),original_sha256=SHA,queue_original_body_trace_required=85,excluded=excluded,analyzed=len(rows),classifications=dict(sorted(classes.items())),total_decoded_opcode_counts=dict(sorted(opcode_all.items(),key=lambda x:(-x[1],x[0]))),rejected_body_opcode_counts=dict(sorted(opcode_rejected.items(),key=lambda x:(-x[1],x[0]))),missing_isa_body_counts=dict(sorted(missing_isa_bodies.items(),key=lambda x:(-x[1],x[0]))),no_call_or_x87_vas=no_call_x87,next_bounded_batch=dict(vas=no_call_x87,prerequisite='Trace external JMP target and canonical ABI/provider for each thunk before any backend expansion; external control transfer cannot be represented by current in-body gotos',note='PUSH/POP/ADD/SUB alone closes zero of these 85 full bodies because 80 include CALL and the remaining no-CALL/non-x87 bodies tail-JMP outside their span'),top_small_rejections=[dict(va=r['va'],body_bytes=r['body_bytes'],fanout=r['fanout'],classification=r['classification'],reason=r['first_rejection']) for r in small[:15]],rows=rows,input_sha256=pins,before_after_guards=True,compiler_commands=0,native_commands=0,new_accepted_functions=0,limits=['Full PE span required; any unsupported part rejects the entire body','Opcode counts include every Capstone-decoded instruction in each bounded body, even after first translation rejection','Coverage is syntax/subset capability only, not ABI, semantic equivalence, original-data fidelity or acceptance'])
    write(RUN/'summary.json',report)
    print(json.dumps(dict(queue=85,excluded=len(excluded),analyzed=len(rows),classes=dict(classes),top_small=[(r['va'],r['first_rejection']) for r in small[:5]])))

if __name__=='__main__':main()
