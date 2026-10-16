"""Bounded PE/index/native-consumer preflight for one signed/unsigned DWORD cell."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT/'iterations/v2/001-original-recovery/runs'
RUN = RUNS/'242-shared-scalar-views'
VA = 0x0060c95c
NAMES = {'?DAT_0060c95c@@3HA','?DAT_0060c95c@@3IA'}


def main():
    import capstone
    hp = ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'
    spec = importlib.util.spec_from_file_location('h242',hp)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    pins = {}
    def pin(path,expected=None):
        path = Path(path).resolve()
        actual = h.digest(path)
        assert expected is None or expected==actual,path
        pins[path] = actual
        return path
    pin(Path(__file__))
    pin(hp)
    pin(Path(capstone.__file__))
    for dll in Path(capstone.__file__).parent.rglob('*capstone*.dll'):
        pin(dll)
    RUN.mkdir(parents=True,exist_ok=True)
    assert not (RUN/'preflight.json').exists(), 'Fresh242 preflight required'
    selection = json.loads(pin(RUNS/'238-data-owner-clusters/summary.json').read_bytes())
    baseline_path = pin(RUNS/'233-initialized-and-nested-union/summary.json')
    baseline = json.loads(baseline_path.read_bytes())
    rows = [r for r in baseline['frontier'] if r.get('va')=='0060c95c']
    assert len(rows)==2 and {r['symbol'] for r in rows}==NAMES
    for row in rows:
        for variant in row['ghidra_variants']:
            symbol = variant['symbol']
            assert symbol['bytes']==4 and symbol['storage']=='0060c95c:4'
            assert symbol['type']['path'] in ('/int','/undefined4')
            assert symbol['storage_detail']['memory'] and not symbol['storage_detail']['compound']
    blockers = []
    overlaps = []
    for row in baseline['frontier']:
        va = row.get('va')
        if not va or va=='0060c95c' or row.get('category')!='data':
            continue
        for variant in row.get('ghidra_variants',[]):
            symbol = variant['symbol']
            n = symbol.get('bytes')
            if isinstance(n,int) and n>0 and int(va,16)<VA+4 and int(va,16)+n>VA:
                overlaps.append(dict(va=va,symbol=row['symbol'],bytes=n))
    if overlaps:
        blockers.append('Overlapping cross-VA current native view')
    image = pin(ROOT/'local/game/Porsche.exe',h.SHA).read_bytes()
    sections = h.sections(image)
    sec = next(s for s in sections if s['va']<=VA and VA+4<=s['va']+s['size'])
    assert sec['name']=='.data' and sec['flags']&0x40000000 and sec['flags']&0x80000000 and not sec['flags']&0x20000000
    backed = VA+4<=sec['va']+sec['rawsize']
    assert not backed, 'Expected virtual zero-fill cell; re-evaluate initialization'
    def offset(va):
        s = next(s for s in sections if s['va']<=va<s['va']+s['rawsize'])
        return s['raw']+va-s['va']
    pe = struct.unpack_from('<I',image,0x3c)[0]
    base = struct.unpack_from('<I',image,pe+52)[0]
    rva,size = struct.unpack_from('<II',image,pe+24+96+5*8)
    pos,end = offset(base+rva),offset(base+rva)+size
    targets, interior, in_cell = [],[],[]
    while pos<end:
        page,length = struct.unpack_from('<II',image,pos)
        assert length>=8 and length%2==0 and pos+length<=end
        for i in range(pos+8,pos+length,2):
            word = struct.unpack_from('<H',image,i)[0]
            if word>>12!=3:
                continue
            site = base+page+(word&0xfff)
            value = struct.unpack_from('<I',image,offset(site))[0]
            if site<VA+4 and site+4>VA:
                in_cell.append(f'{site:08x}')
            if VA<=value<VA+4:
                if value!=VA:
                    interior.append(dict(site=f'{site:08x}',target=f'{value:08x}'))
                else:
                    targets.append(site)
        pos += length
    decoder = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    decoder.detail = True
    refs,covered,address_taking = [],[],[]
    listing = pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    for line in listing.read_text(encoding='utf8').splitlines():
        if '0x0060c95c' not in line.lower():
            continue
        m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        assert m,line
        pc,raw = int(m[1],16),bytes.fromhex(m[2])
        assert image[offset(pc):offset(pc)+len(raw)]==raw
        ins = list(decoder.disasm(raw,pc))
        assert len(ins)==1 and ins[0].size==len(raw)
        ins = ins[0]
        mem = [o for o in ins.operands if o.type==capstone.x86.X86_OP_MEM and (o.mem.disp&0xffffffff)==VA]
        if len(mem)!=1 or mem[0].size!=4 or mem[0].mem.base or mem[0].mem.index or ins.mnemonic!='mov':
            address_taking.append(dict(pc=m[1],bytes=m[2],instruction=m[3]))
            continue
        assert mem[0].access in (capstone.CS_AC_READ,capstone.CS_AC_WRITE) and ins.disp_size==4
        site = pc+ins.disp_offset
        assert site in targets
        covered.append(site)
        refs.append(dict(pc=m[1],bytes=m[2],instruction=m[3],width=4,
            read=bool(mem[0].access&capstone.CS_AC_READ),write=bool(mem[0].access&capstone.CS_AC_WRITE),HIGHLOW_site=f'{site:08x}'))
    gaps = sorted(set(targets)-set(covered))
    if gaps or address_taking or interior or in_cell:
        blockers.append('Relocation/address-taking/layout proof is incomplete')
    parserpath = pin(ROOT/'scripts/research/build-v2-compile-corpus.py')
    parser = h.module('coff242',parserpath)
    consumers = []
    for row in rows:
        for va in row['referring_object_vas']:
            r = next(r for r in baseline['results'] if r.get('va')==va)
            path = pin(ROOT/r['object'],r['object_sha256'])
            actual = parser.coff_symbols(path)
            assert row['symbol'] in actual['undefined'] and not any('0060c95c' in s for s in actual['defined'])
            for name in r['include_closure']:
                pin(ROOT/name,baseline['input_sha256'][name])
            consumers.append(dict(va=va,object=r['object'],object_sha256=r['object_sha256'],actual_undefined=row['symbol']))
    registry = json.loads(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    assert not any(r['module']=='Porsche.exe' and r['entry_va']=='0060c95c' for r in registry)
    rg = pin(Path(shutil.which('rg')))
    command = [str(rg),'-n','-i','0060c95c',str(ROOT/'iterations/v2/001-original-recovery/source')]
    start = time.perf_counter()
    p = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60)
    elapsed = round(time.perf_counter()-start,6)
    log = RUN/'source-owner-scan.log'
    log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
    receipt = dict(command=command,exit_code=p.returncode,seconds=elapsed,log=h.relative(log),log_sha256=h.digest(log))
    h.write(RUN/'source-owner-scan.execution.json',receipt)
    if p.returncode!=1 or log.read_bytes():
        blockers.append('Existing canonical/WIP source occurrence requires ownership review')
    for path,sha in pins.items():
        assert h.digest(path)==sha, ('Input mutation',path)
    report = dict(schema=1,kind='shared-scalar-views-preflight',original_sha256=h.SHA,va='0060c95c',
        baseline=h.relative(baseline_path),baseline_sha256=h.digest(baseline_path),original_section=sec,
        initial_bits='00000000',file_backed=False,virtual_zero_fill=True,current_native_views=rows,
        original_memory_instructions=refs,reads=sum(r['read'] for r in refs),writes=sum(r['write'] for r in refs),
        complete_HIGHLOW_target_sites=[f'{s:08x}' for s in targets],unindexed_target_sites=[f'{s:08x}' for s in gaps],
        address_taking_or_nonscalar_instructions=address_taking,interior_target_relocations=interior,in_cell_relocations=in_cell,
        current_crossVA_overlap_views=overlaps,native_consumer_objects=consumers,source_owner_scan=receipt,
        safe_for_bounded_storage_pilot=not blockers,blockers=blockers,input_sha256={h.relative(p):sha for p,sha in pins.items()},
        generated_CXX=0,compiler_commands=0,native_execution_commands=0,
        limits=['Current direct signed/unsigned4-byte views only; no meaning/algorithm, whole-program alias/computed-pointer/layout/lifetime claim'])
    h.write(RUN/'preflight.json',report)
    print(json.dumps(dict(refs=len(refs),reads=report['reads'],writes=report['writes'],HIGHLOW_targets=len(targets),
        gaps=len(gaps),address_taking=len(address_taking),overlaps=len(overlaps),safe=not blockers,blockers=blockers,pins=len(pins))))


if __name__=='__main__':
    main()
