"""Read-only actual PE/COFF/directive/pin audit; no native tools or rerun."""
import importlib.util
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
RUN = ROOT/'iterations/v2/001-original-recovery/runs/242-shared-scalar-views'
OUT = ROOT/'local/experiments/v2-shared-scalar-views-242'
SIGNED,UNSIGNED = '?DAT_0060c95c@@3HA','?DAT_0060c95c@@3IA'


def main():
    import capstone
    path = ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py'
    spec = importlib.util.spec_from_file_location('a242',path)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    s = json.loads((RUN/'summary.json').read_bytes())
    b = json.loads((RUN/'binding-summary.json').read_bytes())
    v = json.loads((RUN/'validation.json').read_bytes())
    p = json.loads((RUN/'preflight.json').read_bytes())
    assert h.digest(RUN/'summary.json')==v['summary_sha256']
    assert h.digest(RUN/'binding-summary.json')==v['binding_summary_sha256']
    assert s['kind']=='original-writable-data' and b['kind']=='proven-link-contract'
    assert s['physical_data_cells']==1 and b['physical_data_cells_added']==0
    assert s['input_sha256']==b['input_sha256']
    for name,sha in s['input_sha256'].items():
        assert h.digest(ROOT/name)==sha,name
    dr,ar = s['support_objects'][0],b['support_objects'][0]
    data,alias = h.coff(ROOT/dr['object']),h.coff(ROOT/ar['object'])
    assert data['sha256']==dr['object_sha256'] and alias['sha256']==ar['object_sha256']
    sec = next(x for x in data['sections'] if x['name']=='.ogw$sv')
    assert sec['size']==4 and data['bytes'][sec['raw']:sec['raw']+4]==b'\0'*4
    assert sec['chars']&0x40000000 and sec['chars']&0x80000000 and not sec['chars']&0x20000000
    assert all(not x['reloc_count'] and not (x['size'] and x['chars']&0x20000000) for x in data['sections'])
    ds = next(x for x in alias['sections'] if x['name']=='.drectve')
    directive = alias['bytes'][ds['raw']:ds['raw']+ds['size']].decode('ascii').strip()
    assert directive=='/alternatename:'+UNSIGNED+'='+SIGNED
    assert all(not x['reloc_count'] and not x['chars']&0xa0000000 and
               (not x['size'] or x['name'] in ('.drectve','.debug$S','.chks64')) for x in alias['sections'])
    assert dr['symbols']['defined']==[SIGNED] and not dr['symbols']['undefined']
    assert not ar['symbols']['defined'] and not ar['symbols']['undefined']
    assert b['aliases'][0]['from']==UNSIGNED and b['aliases'][0]['to']==SIGNED
    original = h.pe(ROOT/'local/game/Porsche.exe')
    assert original['sha256']==s['original_sha256']
    va = 0x60c95c
    rva = va-original['image_base']
    os = next(x for x in original['sections'] if x['va']<=rva and rva+4<=x['va']+x['vsize'])
    assert os['name']=='.data' and os['chars']&0x40000000 and os['chars']&0x80000000 and not os['chars']&0x20000000
    assert rva>=os['va']+os['raw_size']
    def offset(address):
        r = address-original['image_base']
        sec = next(x for x in original['sections'] if x['va']<=r<x['va']+x['raw_size'])
        return sec['raw']+r-sec['va']
    sites = []
    for r in original['reloc_rvas']:
        site = original['image_base']+r
        assert not (site<va+4 and site+4>va)
        value = struct.unpack_from('<I',original['bytes'],offset(site))[0]
        if va<=value<va+4:
            assert value==va
            sites.append(f'{site:08x}')
    assert sites==p['complete_HIGHLOW_target_sites'] and len(sites)==125
    decoder = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    decoder.detail = True
    covered = []
    for entry in p['original_memory_instructions']:
        pc,raw = int(entry['pc'],16),bytes.fromhex(entry['bytes'])
        assert original['bytes'][offset(pc):offset(pc)+len(raw)]==raw
        ins = list(decoder.disasm(raw,pc))
        assert len(ins)==1 and ins[0].size==len(raw) and ins[0].mnemonic=='mov'
        mem = [o for o in ins[0].operands if o.type==capstone.x86.X86_OP_MEM and (o.mem.disp&0xffffffff)==va]
        assert len(mem)==1 and mem[0].size==4 and not mem[0].mem.base and not mem[0].mem.index
        assert bool(mem[0].access&capstone.CS_AC_READ)==entry['read']
        assert bool(mem[0].access&capstone.CS_AC_WRITE)==entry['write']
        covered.append(f'{pc+ins[0].disp_offset:08x}')
    assert sorted(covered)==sorted(sites)
    assert sum(e['read'] for e in p['original_memory_instructions'])==122
    assert sum(e['write'] for e in p['original_memory_instructions'])==3
    fixture = h.pe(ROOT/s['fixture_executable'])
    assert fixture['sha256']==s['fixture_executable_sha256']
    fs = next(x for x in fixture['sections'] if x['name']=='.ogw')
    assert fs['vsize']==4 and fs['chars']&0x40000000 and fs['chars']&0x80000000 and not fs['chars']&0x20000000
    assert fixture['bytes'][fs['raw']:fs['raw']+4]==b'\0'*4
    assert not any(fs['va']<=r<fs['va']+4 for r in fixture['reloc_rvas'])
    outputs = json.loads((OUT/'fixture-before-execution.json').read_bytes())
    assert outputs['executable_sha256']==fixture['sha256']
    for name,sha in s['fixture_object_sha256'].items():
        assert h.digest(ROOT/name)==sha==outputs['object_sha256'][name]
    for name,key in [('compile','compiled'),('fixture-link','fixture_link'),('fixture-native','native_fixture')]:
        receipt = json.loads((OUT/(name+'.execution.json')).read_bytes())
        assert receipt==s[key] and receipt==b[key] and receipt['exit_code']==0
        assert h.digest(ROOT/receipt['log'])==receipt['log_sha256']
    assert s['finalized_existing_compile'] and s['actual_compiler_batches']==1
    print(json.dumps(dict(passed=True,summary_sha256=v['summary_sha256'],binding_summary_sha256=v['binding_summary_sha256'],
        audit_sha256=h.digest(Path(__file__)),guarded_inputs=len(s['input_sha256']),original_PE_MEM4_refs=125,
        original_reads=122,original_writes=3,physical_cells=1,exact_COFF_drectve=directive,
        data_object_sha256=data['sha256'],alias_object_sha256=alias['sha256'],fixture_sha256=fixture['sha256'],
        compiler_batches=1,compiler_exit=s['compiled']['exit_code'],native_exit=s['native_fixture']['exit_code'],new_functions=0),indent=2))


if __name__=='__main__':
    main()
