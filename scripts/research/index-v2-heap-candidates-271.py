"""Publish four unproved entry candidates without promoting them to functions."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import capstone
from capstone.x86 import X86_OP_IMM,X86_OP_MEM

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/271-heap-candidate-index'
INDEX=ROOT/'research/binary-index/supplemental/heap-consumers-271.jsonl'
SOURCE=ROOT/'iterations/v2/001-original-recovery/runs/270-heap-consumer-index/preflight.json'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
SOURCE_SHA='c53bf19e7713a27a8457b7dc6914e0f49298eaaf23daee0526ff3e3fbf3394f9'
SPANS=(('005697d0','005697e6',23),('00569a40','00569a6a',43),('00569b10','00569b3b',44),('0056a1f0','0056a37f',400))
ROLES={'005697d0':('005697d4','push-address'),'00569a40':('00569a48','indexed-MEM4-read'),
       '00569b10':('00569b1b','indexed-MEM4-read'),'0056a1f0':('0056a221','CMP-immediate')}
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def validate_record(row,image,pe_bytes):
    if 'entry_va' in row:raise ValueError('Authoritative function entry key forbidden')
    if row.get('module')!='Porsche.exe' or row.get('module_sha256')!=SHA:raise ValueError('Original identity mismatch')
    if row.get('entry_status')!='unproved' or row.get('recovery_status')!='navigation-only':raise ValueError('Candidate status promotion forbidden')
    if row.get('accepted_function') is not False or row.get('storage_approval') is not False:raise ValueError('Acceptance promotion forbidden')
    entry=row.get('candidate_entry_va');known={a:(b,n) for a,b,n in SPANS}
    if entry not in known or (row.get('candidate_end_va'),row.get('body_bytes'))!=known[entry]:raise ValueError('Candidate span identity mismatch')
    raw=pe_bytes(image,entry,row['body_bytes'])
    if raw.hex()!=row['body_hex'] or hashlib.sha256(raw).hexdigest()!=row['body_sha256']:raise ValueError('Candidate PE/hash mismatch')
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    instructions=list(decoder.disasm(raw,int(entry,16)))
    actual=[dict(va=f'{i.address:08x}',bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in instructions]
    if actual!=row['instructions'] or sum(i.size for i in instructions)!=len(raw):raise ValueError('Instruction stream mismatch')
    text='; CANDIDATE '+entry+' navigation only, no function entry accepted\n'+'\n'.join(
        f'{i.address:08x}  {i.bytes.hex()}  {i.mnemonic.upper()} {i.op_str}' for i in instructions)+'\n'
    if hashlib.sha256(text.encode('utf8')).hexdigest()!=row['source_instruction_sha256']:raise ValueError('Focused instruction source hash mismatch')
    if row['source_preflight_sha256']!=SOURCE_SHA:raise ValueError('Frozen preflight identity mismatch')
    if row['incoming_indexed_entry_refs']!=[] or row['incoming_HIGHLOW_entry_refs']!=[]:raise ValueError('Unexpected authoritative entry evidence')
    if row['authoritative_external_entry_proved'] is not False:raise ValueError('Function entry proof not available')
    expected_pc,kind=ROLES[entry];role=row['table_operand_role']
    if role['pc']!=expected_pc or role['role']!=kind or role['table_base_va']!='006b4f20':raise ValueError('Table role identity mismatch')
    ins=next(i for i in instructions if i.address==int(expected_pc,16))
    if kind=='push-address':
        if not(ins.mnemonic=='push' and ins.operands[0].type==X86_OP_IMM and ins.operands[0].imm==0x6b4f20):raise ValueError('Not table address PUSH')
    elif kind=='indexed-MEM4-read':
        mem=[o for o in ins.operands if o.type==X86_OP_MEM and o.mem.disp==0x6b4f20]
        if not(ins.mnemonic=='mov' and len(mem)==1 and mem[0].size==4 and mem[0].access==capstone.CS_AC_READ and mem[0].mem.index and mem[0].mem.scale==4):raise ValueError('Not indexed table MEM4 read')
    elif not(ins.mnemonic=='cmp' and ins.operands[1].type==X86_OP_IMM and ins.operands[1].imm==0x6b4f20):raise ValueError('Not table-base CMP immediate')


def build_records(source,image,pe_bytes):
    rows=[]
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    for original,(entry,end,n) in zip(source['rows'],SPANS):
        assert original['candidate_entry']==entry and original['candidate_end']==end and original['bytes']==n
        raw=pe_bytes(image,entry,n);assert raw.hex()==original['hex']
        ins=list(decoder.disasm(raw,int(entry,16)))
        pc,kind=ROLES[entry]
        row=dict(schema=1,module='Porsche.exe',module_sha256=SHA,candidate_entry_va=entry,candidate_end_va=end,
                 entry_status='unproved',recovery_status='navigation-only',accepted_function=False,storage_approval=False,
                 body_bytes=n,body_hex=raw.hex(),body_sha256=original['body_sha256'],source_instruction_sha256=original['source_instruction_sha256'],
                 source_preflight=relative(SOURCE),source_preflight_sha256=SOURCE_SHA,
                 instructions=[dict(va=f'{i.address:08x}',bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins],
                 calls=original['calls'],internal_branches=original['branches'],
                 table_operand_role=dict(pc=pc,role=kind,table_base_va='006b4f20',storage_extent_inferred=False),
                 boundary_evidence={k:original[k] for k in ['preceding32_hex','preceding_padding_bytes','preceding_raw_pc','preceding_raw_byte',
                     'following16_hex','trailing_padding_bytes','nearest_prior_indexed_range','nearest_next_indexed_range','closed_internal_instruction_graph']},
                 incoming_indexed_entry_refs=original['incoming_indexed_edges'],incoming_HIGHLOW_entry_refs=original['incoming_HIGHLOW'],
                 known_raw_incoming_calls=original['incoming_raw_E8_E9_candidates'],authoritative_external_entry_proved=False,
                 limits=['No executable function-entry or liveness claim; padding/closed CFG remain structural evidence.',
                         'Raw CALL candidates have unproved instruction boundaries; no guessed calling convention or prototype.',
                         'No heap-table allocation/coalescing/alias authorization; frozen Run267 HOLD remains.'])
        validate_record(row,image,pe_bytes);rows.append(row)
    assert len(rows)==4 and len({r['candidate_entry_va'] for r in rows})==4
    assert sum(r['body_bytes'] for r in rows)==510 and sum(len(r['instructions']) for r in rows)==167
    return rows


def guards(rows,image,pe_bytes):
    tests=[]
    mutations=[('body byte tamper',lambda r:r.update(body_hex='90'+r['body_hex'][2:])),
               ('body hash tamper',lambda r:r.update(body_sha256='0'*64)),
               ('original SHA mismatch',lambda r:r.update(module_sha256='0'*64)),
               ('authoritative entry key',lambda r:r.update(entry_va=r['candidate_entry_va'])),
               ('status promotion',lambda r:r.update(entry_status='proved')),
               ('storage approval promotion',lambda r:r.update(storage_approval=True)),
               ('instruction tamper',lambda r:r['instructions'][0].update(bytes='90'))]
    for name,mutate in mutations:
        row=json.loads(json.dumps(rows[0]));mutate(row)
        try:validate_record(row,image,pe_bytes)
        except (ValueError,AssertionError):tests.append(name)
        else:raise AssertionError(('candidate guard accepted tamper',name))
    return tests


README='''# Supplemental candidate navigation index

`heap-consumers-271.jsonl` preserves four omitted heap-consumer **candidate** spans
from original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Run270 supplies the source evidence; Run271 rechecks all 510 PE bytes and167
instructions. Each record uses `candidate_entry_va`, `entry_status: unproved`
and `recovery_status: navigation-only`. There is deliberately no `entry_va` field.
Do not import these records as authoritative functions or accepted implementations.

Candidate ranges:005697d0..005697e6,00569a40..00569a6a,00569b10..00569b3b,
0056a1f0..0056a37f. Exact instruction bytes, hashes, nearby boundaries and known
raw incoming CALL candidates are included. No indexed incoming entry references
or relocated entry pointers are known. RET/NOP padding, closed CFG and indexed
twins support navigation, not an executable entry/liveness claim.

Table operand roles are PUSH address, indexed DWORD reads and CMP immediate.
These records do not prove allocation extent, authorize heap storage/coalescing,
repair native ABI contracts or supply a provider. **Run267 HOLD remains.**
The existing manual-functions.jsonl and full corpus remain byte-for-byte unchanged.

Next trace: establish raw incoming CALL boundaries0056a1c1/0056a483 and their
entry/control-flow context; examine0053c290 fill-dispatch consumers as needed.
The first three candidates have no known incoming direct/relocated entry evidence.

Generate once: `py -3 scripts/research/index-v2-heap-candidates-271.py`.
Read-only validation: `py -3 scripts/research/index-v2-heap-candidates-271.py --validate`.
No compiler, native execution or Ghidra is invoked; seven tamper/promotion guards
protect the candidate boundary. Run271 README/summary/validation contain provenance.
'''


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--validate',action='store_true');args=parser.parse_args()
    if not args.validate:assert not (RUN/'summary.json').exists() and not INDEX.exists(),'fresh271 output required'
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('input identity',path);pins[relative(path)]=h;return path
    source=load(pin(SOURCE,SOURCE_SHA))
    for name,h in source['input_sha256'].items():pin(ROOT/name,h)
    for p in [__file__,ROOT/'scripts/research/audit-v2-x86-call-chain-258.py',ROOT/'iterations/v2/001-original-recovery/runs/270-heap-consumer-index/candidate-listing.asm']:
        pin(p)
    assert digest(ROOT/'iterations/v2/001-original-recovery/runs/270-heap-consumer-index/candidate-listing.asm')==source['focused_listing_sha256']
    pe_bytes=module('pe271','scripts/research/audit-v2-x86-call-chain-258.py').original_bytes
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes();records=build_records(source,image,pe_bytes);rejected=guards(records,image,pe_bytes)
    encoded=''.join(json.dumps(r,separators=(',',':'))+'\n' for r in records).encode('utf8')
    if args.validate:
        assert INDEX.read_bytes()==encoded and (INDEX.parent/'README.md').read_bytes()==README.encode('utf8')
        summary=load(RUN/'summary.json');assert summary['index_sha256']==digest(INDEX) and summary['input_sha256']==pins
    else:
        RUN.mkdir(parents=True,exist_ok=True);INDEX.parent.mkdir(parents=True,exist_ok=True)
        assert not (INDEX.parent/'README.md').exists(),'do not overwrite another supplemental README owner'
        INDEX.write_bytes(encoded);(INDEX.parent/'README.md').write_text(README,encoding='utf8',newline='\n')
    for name,h in pins.items():assert digest(ROOT/name)==h,('before/after mutation',name)
    summary=dict(schema=1,kind='navigation-only-heap-candidate-index',original_sha256=SHA,index=relative(INDEX),index_sha256=digest(INDEX),
                 supplemental_readme_sha256=digest(INDEX.parent/'README.md'),candidate_spans=4,original_bytes=510,instructions=167,
                 candidate_entry_vas=[r['candidate_entry_va'] for r in records],entry_status='unproved',recovery_status='navigation-only',
                 authoritative_functions_added=0,accepted_functions_added=0,heap_storage_approved=False,run267_hold=True,
                 old_index_modified=False,compiler_commands=0,native_commands=0,input_sha256=pins,before_after_guards=True,
                 rejected_tamper_tests=rejected,next_trace=['rawincoming0056a1c1','rawincoming0056a483','0053c290filldispatchconsumer'])
    if not args.validate:write(RUN/'summary.json',summary)
    else:assert summary==load(RUN/'summary.json')
    write(RUN/'validation.json',dict(passed=True,summary_sha256=digest(RUN/'summary.json'),index_sha256=digest(INDEX),input_pins=len(pins),
                                   original_bytes=510,instructions=167,guards=rejected,authoritative_functions_added=0,run267_hold=True,
                                   compiler_commands=0,native_commands=0))
    print(json.dumps(dict(passed=True,candidates=4,bytes=510,instructions=167,pins=len(pins),guards=len(rejected),accepted_functions=0,hold=True)))


if __name__=='__main__':main()
