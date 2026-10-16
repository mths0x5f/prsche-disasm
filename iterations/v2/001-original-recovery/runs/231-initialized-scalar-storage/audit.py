"""Independent read-only PE/COFF audit; no compiler, linker, or fixture execution."""
import importlib.util
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[5]
RUN = ROOT/'iterations/v2/001-original-recovery/runs/231-initialized-scalar-storage'
EXP = ROOT/'local/experiments/v2-initialized-scalars-231'
TARGETS = {'005ccb34':'80000000', '005d0608':'01000000', '005e5f4c':'0a000000'}


def main():
    import capstone
    spec = importlib.util.spec_from_file_location('audit226', ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py')
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    s = json.loads((RUN/'summary.json').read_bytes())
    v = json.loads((RUN/'validation.json').read_bytes())
    proof = json.loads((RUN/'proof-before-compile.json').read_bytes())
    assert h.digest(RUN/'summary.json')==v['summary_sha256']
    assert s['kind']=='original-writable-data' and s['functions_added']==0 and s['data_symbols']==3
    for name, sha in s['input_sha256'].items():
        assert h.digest(ROOT/name)==sha, name
    row = s['support_objects'][0]
    assert row['id']=='initialized-scalar-cells-231' and row['compiled'] and row['compiler_exit_code']==0
    assert h.digest(ROOT/row['generated_source'])==row['generated_source_sha256']
    assert h.digest(ROOT/row['object'])==row['object_sha256']
    obj = h.coff(ROOT/row['object'])
    storage = next(x for x in obj['sections'] if x['name']=='.ogw$ns')
    assert storage['size']==12 and storage['chars']&0x40000000 and storage['chars']&0x80000000
    assert not storage['chars']&0x20000000 and all(x['reloc_count']==0 for x in obj['sections'])
    assert not any(x['size'] and x['chars']&0x20000000 for x in obj['sections'])
    actual = {}
    for va, bits in TARGETS.items():
        name = f'?DAT_{va}@@3HA'
        symbol = next(x for x in obj['symbols'] if x['name']==name)
        assert obj['sections'][symbol['section']-1]['name']=='.ogw$ns'
        actual[va] = obj['bytes'][storage['raw']+symbol['value']:storage['raw']+symbol['value']+4].hex()
        assert actual[va]==bits
    assert set(row['symbols']['defined'])=={f'?DAT_{va}@@3HA' for va in TARGETS}
    assert not row['symbols']['undefined']
    original = h.pe(ROOT/'local/game/Porsche.exe')
    assert original['sha256']==s['original_sha256']

    def offset(address):
        rva = address-original['image_base']
        sec = next(x for x in original['sections'] if x['va']<=rva<x['va']+x['raw_size'])
        return sec['raw']+rva-sec['va']

    sites = {va:[] for va in TARGETS}
    for rva in original['reloc_rvas']:
        site = original['image_base']+rva
        value = struct.unpack_from('<I', original['bytes'], offset(site))[0]
        for va in TARGETS:
            address = int(va,16)
            assert not (site<address+4 and site+4>address)
            if address<=value<address+4:
                assert value==address
                sites[va].append(f'{site:08x}')
    assert sites==proof['complete_HIGHLOW_sites']
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    counts = {}
    for va, bits in TARGETS.items():
        section, data = h.cell(original,int(va,16))
        assert data.hex()==bits and section['name']=='.data'
        assert section['chars']&0x40000000 and section['chars']&0x80000000 and not section['chars']&0x20000000
        entries = proof['original_memory_instructions'][va]
        covered = []
        for entry in entries:
            pc, raw = int(entry['pc'],16), bytes.fromhex(entry['bytes'])
            assert original['bytes'][offset(pc):offset(pc)+len(raw)]==raw
            ins = list(decoder.disasm(raw,pc))
            assert len(ins)==1 and ins[0].size==len(raw) and ins[0].mnemonic=='mov'
            mem = [x for x in ins[0].operands if x.type==capstone.x86.X86_OP_MEM and (x.mem.disp&0xffffffff)==int(va,16)]
            assert len(mem)==1 and mem[0].size==4
            assert bool(mem[0].access&capstone.CS_AC_READ)==entry['read']
            assert bool(mem[0].access&capstone.CS_AC_WRITE)==entry['write']
            covered.append(f'{pc+ins[0].disp_offset:08x}')
        assert sorted(covered)==sorted(sites[va])
        counts[va] = dict(reads=sum(x['read'] for x in entries), writes=sum(x['write'] for x in entries))
    assert counts=={'005ccb34':dict(reads=2,writes=0),'005d0608':dict(reads=2,writes=1),'005e5f4c':dict(reads=2,writes=0)}
    fixture = h.pe(EXP/'scalar_fixture.exe')
    fs = next(x for x in fixture['sections'] if x['name']=='.ogw')
    assert fs['chars']&0x40000000 and fs['chars']&0x80000000 and not fs['chars']&0x20000000
    assert fixture['bytes'][fs['raw']:fs['raw']+12].hex()=='80000000010000000a000000'
    assert not any(fs['va']<=r<fs['va']+12 for r in fixture['reloc_rvas'])
    receipts = {}
    for name, key in [('compile','compiled'),('fixture-link','fixture_link'),('fixture-native','native_fixture')]:
        receipt = json.loads((EXP/(name+'.execution.json')).read_bytes())
        assert receipt==s[key] and receipt['exit_code']==0
        assert h.digest(ROOT/receipt['log'])==receipt['log_sha256']
        assert b'\r' not in (ROOT/receipt['log']).read_bytes()
        receipts[name] = dict(exit_code=receipt['exit_code'], seconds=receipt['seconds'])
    assert not s['original_relative_layout_claim'] and not proof['original_relative_layout_claim']
    print(json.dumps(dict(passed=True, summary_sha256=h.digest(RUN/'summary.json'),
        audit_sha256=h.digest(Path(__file__)), guarded_inputs=len(s['input_sha256']),
        actual_cells=actual, actual_original_ref_counts=counts, complete_HIGHLOW_sites=sites,
        data_object_sha256=obj['sha256'], fixture_sha256=fixture['sha256'],
        compiler_link_native_receipts=receipts, new_functions=0, original_relative_layout_claim=False),indent=2))


if __name__=='__main__':
    main()
