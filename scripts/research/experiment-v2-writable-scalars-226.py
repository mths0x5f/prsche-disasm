"""Two exact original writable scalar cells; no new function implementation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '226-writable-scalar-storage'
OUT = ROOT / 'local/experiments/v2-writable-scalars-226'


def main():
    import capstone
    spec = importlib.util.spec_from_file_location('scalar_helpers226', ROOT / 'scripts/research/experiment-v2-readonly-scalars-221.py')
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    write, digest, relative = h.write, h.digest, h.relative
    assert not OUT.exists() and not (RUN/'summary.json').exists(), 'Fresh226 capture required'
    OUT.mkdir(parents=True)
    pins = {}

    def pin(path, expected=None):
        path = Path(path).resolve()
        actual = digest(path)
        assert expected is None or actual == expected, path
        pins[path] = actual
        return path

    def guard():
        for path, expected in pins.items():
            assert digest(path) == expected, ('Input changed', path)

    pin(Path(__file__))
    pin(Path(h.__file__))
    pin(Path(capstone.__file__))
    selection = json.loads(pin(RUNS/'225-writable-scalar-selection/summary.json').read_bytes())
    for path, expected in selection['input_sha256'].items():
        pin(ROOT/path, expected)
    selected = {r['va']: r for r in selection['eligible']}
    assert set(selected) == {'005e25d0','005e25d4'}
    image = pin(ROOT/'local/game/Porsche.exe', h.SHA).read_bytes()
    image_sections = h.sections(image)

    def offset(address):
        section = next(s for s in image_sections if s['va'] <= address < s['va']+s['rawsize'])
        return section['raw']+address-section['va']

    pe = struct.unpack_from('<I', image, 0x3c)[0]
    base = struct.unpack_from('<I', image, pe+52)[0]
    reloc_rva, reloc_size = struct.unpack_from('<II', image, pe+24+96+5*8)
    pos, end = offset(base+reloc_rva), offset(base+reloc_rva)+reloc_size
    target_sites = {va: [] for va in selected}
    in_cell = []
    while pos < end:
        page, length = struct.unpack_from('<II', image, pos)
        assert length >= 8 and length % 2 == 0
        for at in range(pos+8,pos+length,2):
            word = struct.unpack_from('<H', image, at)[0]
            if word >> 12 != 3:
                continue
            site = base+page+(word&0xfff)
            value = struct.unpack_from('<I', image, offset(site))[0]
            for va in selected:
                if int(va,16) <= site < int(va,16)+4:
                    in_cell.append(site)
                if value == int(va,16):
                    target_sites[va].append(site)
        pos += length
    assert not in_cell
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    proof_rows = {va: [] for va in selected}
    covered_sites = {va: [] for va in selected}
    listing = pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    for line in listing.read_text(encoding='utf8').splitlines():
        targets = [va for va in selected if '0x'+va in line.lower()]
        if not targets:
            continue
        m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)', line)
        assert m, line
        pc, data = int(m[1],16), bytes.fromhex(m[2])
        assert image[offset(pc):offset(pc)+len(data)] == data
        instructions = list(decoder.disasm(data,pc))
        assert len(instructions) == 1 and instructions[0].size == len(data)
        ins = instructions[0]
        for va in targets:
            operands = [op for op in ins.operands if op.type == capstone.x86.X86_OP_MEM and (op.mem.disp&0xffffffff) == int(va,16)]
            assert len(operands) == 1 and operands[0].size == 4
            assert ins.disp_size == 4 and (pc+ins.disp_offset) in target_sites[va]
            assert ins.mnemonic == 'mov' and operands[0].access in (capstone.CS_AC_READ,capstone.CS_AC_WRITE)
            covered_sites[va].append(pc+ins.disp_offset)
            proof_rows[va].append(dict(pc=m[1],bytes=m[2],assembly=m[3],width=4,
                                      read=bool(operands[0].access&capstone.CS_AC_READ),write=bool(operands[0].access&capstone.CS_AC_WRITE)))
    for va, rows in proof_rows.items():
        assert sorted(covered_sites[va]) == sorted(target_sites[va]), ('Unindexed or address-taking reference',va)
        assert len(rows) == selected[va]['exact_indexed_refs']
        assert sum(r['read'] for r in rows) == selected[va]['reads']
        assert sum(r['write'] for r in rows) == selected[va]['writes']
        section = next(s for s in image_sections if s['va']<=int(va,16)<s['va']+s['rawsize'])
        assert section['name']=='.data' and section['flags']&0x80000000
        assert image[offset(int(va,16)):offset(int(va,16))+4] == b'\0'*4
    baseline = json.loads(pin(RUNS/'222-native-support-union/summary.json').read_bytes())
    for va in selected:
        rows = [r for r in baseline['frontier'] if r.get('va') == va]
        assert len(rows) == 1 and rows[0]['symbol'] == selected[va]['symbol'], ('Conflicting native views',va)
    toolroot = ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86'
    compiler = pin(toolroot/'cl.exe', baseline['ordinary_summaries'] and
                   json.loads(pin(RUNS/'202-float-bit-stores/summary.json').read_bytes())['compiler_sha256'])
    for name in ('c1xx.dll','c2.dll'):
        pin(toolroot/name)
    link = pin(toolroot/'link.exe')
    kernel = pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    source, fixture = pin(RUN/'original_scalars.cpp'), pin(RUN/'scalar_fixture.cpp')
    coff = h.module('coff226', pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    proof = RUN/'proof-before-compile.json'
    write(proof, dict(original_sha256=h.SHA,original_memory_instructions=proof_rows,
                     complete_HIGHLOW_sites={va:[f'{x:08x}' for x in sites] for va,sites in target_sites.items()},
                     in_cell_relocations=0,initial_bytes='0000000000000000',relative_separation=4,writable=True,
                     limits=['No whole-program computed-pointer/section-layout/alias/lifetime acceptance','Only current native views are supplied']))
    pin(proof)
    objects = OUT/'objects'
    objects.mkdir()
    flags = ['/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/Zl','/W4','/utf-8','/MP6']
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    command = [str(compiler),*flags,'/Fo'+str(objects)+os.sep,str(source),str(fixture)]
    guard()
    write(OUT/'prepare.json',dict(command=command,input_sha256={relative(p):h for p,h in pins.items()}))

    def run(command,name):
        start = time.perf_counter()
        p = subprocess.run(list(map(str,command)),cwd=OUT,capture_output=True,timeout=120,env={**os.environ,'VSLANG':'1033'})
        elapsed = round(time.perf_counter()-start,6)
        log = OUT/(name+'.log')
        log.write_bytes(p.stdout+p.stderr)
        receipt = dict(command=list(map(str,command)),exit_code=p.returncode,seconds=elapsed,log=relative(log),log_sha256=digest(log))
        write(OUT/(name+'.execution.json'),receipt)
        return receipt

    compiled = run(command,'compile')
    assert compiled['exit_code']==0, (OUT/'compile.log').read_text(errors='replace')
    assert not re.search(rb'\b(?:warning|error) C\d+', (OUT/'compile.log').read_bytes())
    obj = objects/'original_scalars.obj'
    symbols = coff.coff_symbols(obj)
    assert sorted(symbols['defined']) == sorted(r['symbol'] for r in selected.values()) and not symbols['undefined']
    data = obj.read_bytes()
    storage = []
    for i in range(struct.unpack_from('<H',data,2)[0]):
        at=20+40*i
        name=data[at:at+8].rstrip(b'\0').decode()
        size,raw,_,_,relocs,_,flags=struct.unpack_from('<IIIIHHI',data,at+16)
        if name=='.ogw$sc':
            assert size==8 and data[raw:raw+size]==b'\0'*8 and relocs==0
            assert flags&0x40000000 and flags&0x80000000 and not flags&0x20000000
            storage.append(dict(name=name,bytes=data[raw:raw+size].hex(),flags=f'{flags:08x}',relocations=0))
    assert len(storage)==1
    exe=OUT/'scalar_fixture.exe'
    linked=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objects/'scalar_fixture.obj',kernel],'fixture-link')
    assert linked['exit_code']==0
    native=run([exe],'fixture-native')
    assert native['exit_code']==0
    exe_section=next(s for s in h.sections(exe.read_bytes()) if s['name']=='.ogw')
    assert exe_section['flags']&0x40000000 and exe_section['flags']&0x80000000
    guard()
    summary=dict(schema=1,kind='original-writable-data',original_sha256=h.SHA,compiler_sha256=digest(compiler),functions_added=0,
                 data_symbols=2,actual_compiler_batches=1,compiled=compiled,fixture_link=linked,native_fixture=native,
                 support_objects=[dict(id='writable-scalar-cells-226',compiled=True,compiler_exit_code=0,
                     generated_source=relative(source),generated_source_sha256=digest(source),object=relative(obj),object_sha256=digest(obj),
                     dependency_sha256={relative(source):digest(source)},symbols=symbols,storage_sections=storage)],
                 input_sha256={relative(p):h for p,h in pins.items()},original_memory_instructions_verified=15,
                 limits=['Two current native scalar views only; no new algorithm or game function',
                         'Signed/unsigned cells preserve original zero bits and four-byte separation',
                         'Whole original.data layout/computed references/aliases/lifetime/production integration deferred'])
    write(RUN/'summary.json',summary)
    write(RUN/'validation.json',dict(summary_sha256=digest(RUN/'summary.json'),input_guards_before_after=True,
                                    data_symbols=2,functions_added=0,native_fixture_exit=0,writable_PE_and_object_pass=True))
    print(json.dumps(dict(data_symbols=2,functions_added=0,original_instructions=15,compile_seconds=compiled['seconds'],native_exit=0)))


if __name__=='__main__':
    main()
