"""Three exact initialized writable int32 cells, one data-only support object."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT/'iterations/v2/001-original-recovery/runs'
RUN = RUNS/'231-initialized-scalar-storage'
OUT = ROOT/'local/experiments/v2-initialized-scalars-231'
TARGETS = {'005ccb34': '80000000', '005d0608': '01000000', '005e5f4c': '0a000000'}


def main():
    import capstone
    hp = ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'
    spec = importlib.util.spec_from_file_location('helpers231', hp)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    write, digest, relative = h.write, h.digest, h.relative
    assert not OUT.exists() and not (RUN/'summary.json').exists(), 'Fresh231 output required'
    OUT.mkdir(parents=True)
    pins = {}

    def pin(path, expected=None):
        path = Path(path).resolve()
        actual = digest(path)
        assert expected is None or expected == actual, path
        pins[path] = actual
        return path

    def guard():
        for path, expected in pins.items():
            assert digest(path) == expected, ('Input mutation', path)

    def run(command, name):
        command = list(map(str, command))
        start = time.perf_counter()
        p = subprocess.run(command, cwd=OUT, capture_output=True, timeout=120,
                           env={**os.environ, 'VSLANG': '1033'})
        elapsed = round(time.perf_counter()-start, 6)
        log = OUT/(name+'.log')
        log.write_bytes((p.stdout+p.stderr).replace(b'\r\n', b'\n'))
        receipt = dict(command=command, exit_code=p.returncode, seconds=elapsed,
                       log=relative(log), log_sha256=digest(log))
        write(OUT/(name+'.execution.json'), receipt)
        return receipt

    pin(Path(__file__))
    pin(hp)
    audit = h.module('audit226_for231', pin(RUNS/'226-writable-scalar-storage/audit.py'))
    pin(ROOT/'scripts/research/experiment-v2-writable-scalars-226.py')
    pin(Path(capstone.__file__))
    # Pin the actual decoder DLL as well as its Python wrapper.
    for dll in Path(capstone.__file__).parent.rglob('*capstone*.dll'):
        pin(dll)
    selection = json.loads(pin(RUNS/'230-initialized-scalar-selection/summary.json').read_bytes())
    for path, expected in selection['input_sha256'].items():
        pin(ROOT/path, expected)
    selected = {r['va']: r for r in selection['eligible']}
    assert set(selected) == set(TARGETS)
    assert all(r['type']=='int32' and r['pe_bytes']==TARGETS[va] and
               not r['overlap_views'] and not r['owner_definitions'] for va,r in selected.items())
    image = pin(ROOT/'local/game/Porsche.exe', h.SHA).read_bytes()
    sections = h.sections(image)

    def offset(address):
        s = next(s for s in sections if s['va'] <= address < s['va']+s['rawsize'])
        return s['raw']+address-s['va']

    pe = struct.unpack_from('<I', image, 0x3c)[0]
    base = struct.unpack_from('<I', image, pe+52)[0]
    rva, size = struct.unpack_from('<II', image, pe+24+96+5*8)
    pos, end = offset(base+rva), offset(base+rva)+size
    sites = {va: [] for va in TARGETS}
    in_cell, interior_targets = [], []
    while pos < end:
        page, length = struct.unpack_from('<II', image, pos)
        assert length >= 8 and length % 2 == 0 and pos+length <= end
        for at in range(pos+8, pos+length, 2):
            word = struct.unpack_from('<H', image, at)[0]
            if word >> 12 != 3:
                continue
            site = base+page+(word&0xfff)
            value = struct.unpack_from('<I', image, offset(site))[0]
            for va in TARGETS:
                address = int(va, 16)
                if site < address+4 and site+4 > address:
                    in_cell.append(site)
                if address <= value < address+4:
                    if value != address:
                        interior_targets.append(dict(site=f'{site:08x}', target=f'{value:08x}'))
                    else:
                        sites[va].append(site)
        pos += length
    assert not in_cell and not interior_targets
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    proof_rows, covered = {va: [] for va in TARGETS}, {va: [] for va in TARGETS}
    listing = pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    for line in listing.read_text(encoding='utf8').splitlines():
        targets = [va for va in TARGETS if '0x'+va in line.lower()]
        if not targets:
            continue
        m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)', line)
        assert m, line
        pc, raw = int(m[1],16), bytes.fromhex(m[2])
        assert image[offset(pc):offset(pc)+len(raw)] == raw
        decoded = list(decoder.disasm(raw,pc))
        assert len(decoded)==1 and decoded[0].size==len(raw)
        ins = decoded[0]
        for va in targets:
            ops = [op for op in ins.operands if op.type==capstone.x86.X86_OP_MEM and
                   (op.mem.disp&0xffffffff)==int(va,16)]
            assert len(ops)==1 and ops[0].size==4 and ins.mnemonic=='mov'
            assert ops[0].access in (capstone.CS_AC_READ, capstone.CS_AC_WRITE)
            assert ins.disp_size==4 and pc+ins.disp_offset in sites[va]
            covered[va].append(pc+ins.disp_offset)
            proof_rows[va].append(dict(pc=m[1], bytes=m[2], assembly=m[3], width=4,
                read=bool(ops[0].access&capstone.CS_AC_READ), write=bool(ops[0].access&capstone.CS_AC_WRITE)))
    for va, rows in proof_rows.items():
        assert sorted(covered[va])==sorted(sites[va]) and len(rows)==selected[va]['highlow_refs']
        assert sum(r['read'] for r in rows)==selected[va]['reads']
        assert sum(r['write'] for r in rows)==selected[va]['writes']
        s = next(s for s in sections if s['va']<=int(va,16)<s['va']+s['rawsize'])
        assert s['name']=='.data' and s['flags']&0x40000000 and s['flags']&0x80000000
        assert not s['flags']&0x20000000
        assert image[offset(int(va,16)):offset(int(va,16))+4].hex()==TARGETS[va]
    baseline = json.loads(pin(RUNS/'228-writable-and-callee-union/summary.json').read_bytes())
    coff = h.module('coff231', pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    consumer_proof = {}
    for va, selected_row in selected.items():
        views = [r for r in baseline['frontier'] if r.get('va')==va]
        assert len(views)==1 and views[0]['symbol']==selected_row['symbol']==f'?DAT_{va}@@3HA'
        assert not views[0]['observed_conflict']
        consumer_proof[va] = []
        for caller in views[0]['referring_object_vas']:
            row = next(r for r in baseline['results'] if r['va']==caller)
            obj = pin(ROOT/row['object'], row['object_sha256'])
            native = coff.coff_symbols(obj)
            assert selected_row['symbol'] in native['undefined']
            assert not any(va in symbol for symbol in native['defined'])
            for path in row['include_closure']:
                pin(ROOT/path, baseline['input_sha256'][path])
            consumer_proof[va].append(dict(va=caller, object=relative(obj), object_sha256=digest(obj),
                                           actual_undefined_symbol=selected_row['symbol']))
        for view in baseline['frontier']:
            other_va = view.get('va')
            if not other_va or other_va==va or view.get('category')!='data':
                continue
            address = int(other_va,16)
            for variant in view.get('ghidra_variants',[]):
                n = variant['symbol'].get('bytes')
                assert not (isinstance(n,int) and n>0 and address<int(va,16)+4 and address+n>int(va,16)), ('Overlapping native view',va,other_va)
    registry = json.loads(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())
    assert not any(r.get('module')=='Porsche.exe' and r.get('entry_va') in TARGETS for r in registry['functions'])
    rg = pin(Path(shutil.which('rg')))
    ownership = run([rg, '-n', '-i', '005ccb34|005d0608|005e5f4c',
        ROOT/'iterations/v2/001-original-recovery/source/recovered',
        ROOT/'iterations/v2/001-original-recovery/source/include'], 'source-owner-scan')
    assert ownership['exit_code']==1 and not (OUT/'source-owner-scan.log').read_bytes(), 'Existing canonical/WIP source match; review before allocation'
    toolroot = ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86'
    tool_summary = json.loads(pin(RUNS/'202-float-bit-stores/summary.json').read_bytes())
    compiler = pin(toolroot/'cl.exe', tool_summary['compiler_sha256'])
    for name in ('c1xx.dll', 'c2.dll'):
        pin(toolroot/name)
    link = pin(toolroot/'link.exe')
    kernel = pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    source, fixture = pin(RUN/'original_scalars.cpp'), pin(RUN/'scalar_fixture.cpp')
    proof = RUN/'proof-before-compile.json'
    write(proof, dict(original_sha256=h.SHA, selected_cells=selected, original_memory_instructions=proof_rows,
        complete_HIGHLOW_sites={va:[f'{site:08x}' for site in rows] for va,rows in sites.items()},
        in_cell_relocations=0, interior_target_relocations=0, native_consumer_symbols=consumer_proof,
        original_initial_bytes=TARGETS, original_writable=True, source_owner_scan=ownership,
        original_relative_layout_claim=False, current_native_overlap_views=0,
        limits=['Current direct views only; computed pointers/aliases/whole-data layout/lifetime deferred']))
    pin(proof)
    objects = OUT/'objects'
    objects.mkdir()
    flags = ['/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/Zl','/W4','/utf-8','/MP6']
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    command = [compiler, *flags, '/Fo'+str(objects)+os.sep, source, fixture]
    guard()
    write(OUT/'prepare.json', dict(command=list(map(str,command)), input_sha256={relative(p):sha for p,sha in pins.items()}))
    compiled = run(command, 'compile')
    assert compiled['exit_code']==0, (OUT/'compile.log').read_text(errors='replace')
    assert not re.search(rb'\b(?:warning|error) C\d+', (OUT/'compile.log').read_bytes())
    obj = objects/'original_scalars.obj'
    symbols = coff.coff_symbols(obj)
    assert set(symbols['defined'])=={r['symbol'] for r in selected.values()} and not symbols['undefined']
    parsed = audit.coff(obj)
    storage = next(s for s in parsed['sections'] if s['name']=='.ogw$ns')
    assert storage['size']==12 and storage['chars']&0x40000000 and storage['chars']&0x80000000
    assert not storage['chars']&0x20000000 and all(s['reloc_count']==0 for s in parsed['sections'])
    assert not any(s['size'] and s['chars']&0x20000000 for s in parsed['sections'])
    native_cells = []
    for va, row in selected.items():
        sym = next(s for s in parsed['symbols'] if s['name']==row['symbol'])
        assert parsed['sections'][sym['section']-1]['name']=='.ogw$ns'
        bits = parsed['bytes'][storage['raw']+sym['value']:storage['raw']+sym['value']+4].hex()
        assert bits==TARGETS[va]
        native_cells.append(dict(va=va, symbol=row['symbol'], native_offset=sym['value'], initial_bytes=bits))
    assert sorted(r['native_offset'] for r in native_cells)==[0,4,8]
    # These offsets describe this COFF only, never separation in the original image.
    storage_report = dict(name='.ogw$ns', bytes=parsed['bytes'][storage['raw']:storage['raw']+12].hex(),
        flags=f"{storage['chars']:08x}", relocations=0, cells=native_cells)
    exe = OUT/'scalar_fixture.exe'
    linked = run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB',
        '/OUT:'+str(exe),obj,objects/'scalar_fixture.obj',kernel], 'fixture-link')
    assert linked['exit_code']==0
    fixture_image = exe.read_bytes()
    fs = next(s for s in h.sections(fixture_image) if s['name']=='.ogw')
    assert fs['flags']&0x40000000 and fs['flags']&0x80000000 and not fs['flags']&0x20000000
    assert fixture_image[fs['raw']:fs['raw']+12].hex()==storage_report['bytes']
    native = run([exe], 'fixture-native')
    assert native['exit_code']==0
    guard()
    summary = dict(schema=1, kind='original-writable-data', original_sha256=h.SHA,
        compiler_sha256=digest(compiler), functions_added=0, data_symbols=3, actual_compiler_batches=1,
        compiled=compiled, fixture_link=linked, native_fixture=native,
        support_objects=[dict(id='initialized-scalar-cells-231', compiled=True, compiler_exit_code=0,
            generated_source=relative(source), generated_source_sha256=digest(source),
            object=relative(obj), object_sha256=digest(obj), dependency_sha256={relative(source):digest(source)},
            symbols=symbols, storage_sections=[storage_report])],
        input_sha256={relative(p):sha for p,sha in pins.items()}, original_memory_instructions_verified=7,
        original_relative_layout_claim=False, native_fixture_patterns=6,
        native_fixture_checks='Initial bits; distinct cells; six raw patterns per cell including high-bit values; cross-cell independence; restore128/1/10',
        limits=['Three initialized int32 current native views only; zero new game functions',
                'Native COFF offsets do not claim original separation between nonadjacent cells',
                'Computed-pointer/alias/whole-data-layout/lifetime/production integration deferred'])
    write(RUN/'summary.json', summary)
    write(RUN/'validation.json', dict(summary_sha256=digest(RUN/'summary.json'), input_guards_before_after=True,
        guarded_inputs=len(pins), data_symbols=3, functions_added=0, native_fixture_exit=native['exit_code'],
        writable_PE_and_object_pass=True, exact_COFF_initial_bytes=storage_report['bytes'],
        data_object_relocations=0, original_HIGHLOW_operand_sites=7, in_cell_relocations=0,
        original_relative_layout_claim=False, compiler_exit_code=compiled['exit_code']))
    print(json.dumps(dict(data_symbols=3, functions_added=0, original_instructions=7,
        compile_exit=compiled['exit_code'], compile_seconds=compiled['seconds'], native_exit=native['exit_code'])))


if __name__=='__main__':
    main()
