"""Exact original readonly float cells; one data object, zero function recovery."""
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
RUN = RUNS / '221-readonly-scalar-storage'
OUT = ROOT / 'local/experiments/v2-readonly-scalars-221'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
TARGETS = {'005b242c': bytes.fromhex('0000c842'), '005b24a8': bytes.fromhex('0000803f')}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sections(data):
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    count = struct.unpack_from('<H', data, pe + 6)[0]
    optional = struct.unpack_from('<H', data, pe + 20)[0]
    base = struct.unpack_from('<I', data, pe + 52)[0]
    result = []
    for index in range(count):
        at = pe + 24 + optional + index * 40
        name, size, rva, rawsize, raw = struct.unpack_from('<8sIIII', data, at)
        flags = struct.unpack_from('<I', data, at + 36)[0]
        result.append(dict(name=name.rstrip(b'\0').decode(), va=base+rva,
                           size=size, rawsize=rawsize, raw=raw, flags=flags))
    return result


def main():
    import capstone
    assert not OUT.exists() and not (RUN / 'summary.json').exists(), 'fresh221 output required'
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
            assert digest(path) == expected, ('input changed', path)

    pin(Path(__file__))
    evidence_path = pin(RUNS / '219-readonly-scalar-owners/summary.json')
    evidence = json.loads(evidence_path.read_bytes())
    assert evidence['original_sha256'] == SHA
    for path, expected in evidence['input_sha256'].items():
        pin(ROOT / path, expected)
    original = pin(ROOT / 'local/game/Porsche.exe', SHA)
    image = original.read_bytes()
    pe_sections = sections(image)
    corpus = pin(ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    pin(Path(capstone.__file__))
    references = {va: [] for va in TARGETS}
    for line in corpus.read_text(encoding='utf8').splitlines():
        selected = [va for va in TARGETS if '0x' + va in line.lower()]
        if not selected:
            continue
        m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)', line)
        assert m, line
        address, raw = int(m[1],16), bytes.fromhex(m[2])
        section = next(s for s in pe_sections if s['va'] <= address < s['va']+s['rawsize'])
        offset = section['raw'] + address - section['va']
        assert image[offset:offset+len(raw)] == raw
        decoded = list(decoder.disasm(raw, address))
        assert len(decoded) == 1 and decoded[0].size == len(raw)
        ins = decoded[0]
        for va in selected:
            operands = [op for op in ins.operands if op.type == capstone.x86.X86_OP_MEM and
                        (op.mem.disp & 0xffffffff) == int(va,16)]
            assert len(operands) == 1 and operands[0].size == 4
            assert operands[0].access & capstone.CS_AC_READ and not operands[0].access & capstone.CS_AC_WRITE
            assert ins.mnemonic in ('fld','fadd','fsub','fsubr','fmul','fdivr','fcom','fcomp')
            references[va].append(dict(pc=m[1],bytes=m[2],mnemonic=ins.mnemonic,width=4,read=True,write=False))
    assert {va:len(rows) for va,rows in references.items()} == {'005b242c':55,'005b24a8':683}
    for va, expected in TARGETS.items():
        address = int(va,16)
        section = next(s for s in pe_sections if s['va'] <= address < s['va']+s['rawsize'])
        assert section['name'] == '.rdata' and not section['flags'] & 0x80000000
        offset = section['raw'] + address - section['va']
        assert image[offset:offset+4] == expected and address % 4 == 0
        assert evidence['pe_sections']['target_ranges'][va]['relocations_in_range'] == 0
    prior = json.loads(pin(RUNS / '202-float-bit-stores/summary.json').read_bytes())
    compiler = pin(ROOT / 'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86/cl.exe', prior['compiler_sha256'])
    for name in ('c1xx.dll','c2.dll'):
        pin(compiler.parent / name)
    link = pin(compiler.parent / 'link.exe')
    kernel = pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    source = pin(RUN / 'original_scalars.cpp')
    fixture = pin(RUN / 'scalar_fixture.cpp')
    coff = module('coff221', pin(ROOT / 'scripts/research/build-v2-compile-corpus.py'))
    proof = RUN / 'proof-before-compile.json'
    write(proof, dict(original_sha256=SHA, indexed_reads=references,
                      storage=[dict(va=va,bytes=4,alignment=4,original_bytes=data.hex(),readonly=True,
                                    formal_byte_alias='DAT_'+va,private_native_symbol='?_DAT_'+va+'@@3MA') for va,data in TARGETS.items()],
                      scope='Two isolated original readonly cells in experimental union; no production or whole-program storage acceptance'))
    pin(proof)
    objects = OUT / 'objects'
    objects.mkdir()
    flags = ['/nologo','/c','/std:c++17','/Od','/GS-','/GR-','/Zl','/W4','/utf-8','/MP6']
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    command = [str(compiler),*flags,'/Fo'+str(objects)+os.sep,str(source),str(fixture)]
    guard()
    write(OUT / 'prepare.json', dict(command=command,input_sha256={relative(p):h for p,h in pins.items()}))
    env = {**os.environ,'VSLANG':'1033'}

    def run(command,name):
        start = time.perf_counter()
        process = subprocess.run(list(map(str,command)),cwd=OUT,env=env,capture_output=True,timeout=120)
        elapsed = round(time.perf_counter()-start,6)
        log = OUT / (name+'.log')
        log.write_bytes(process.stdout+process.stderr)
        receipt = dict(command=list(map(str,command)),exit_code=process.returncode,seconds=elapsed,log=relative(log),log_sha256=digest(log))
        write(OUT/(name+'.execution.json'),receipt)
        return receipt

    compiled = run(command,'compile')
    assert compiled['exit_code'] == 0, (OUT/'compile.log').read_text(errors='replace')
    assert not re.search(rb'\b(?:warning|error) C\d+', (OUT/'compile.log').read_bytes())
    obj = objects / 'original_scalars.obj'
    symbols = coff.coff_symbols(obj)
    expected_symbols = ['?_DAT_'+va+'@@3MA' for va in TARGETS]
    assert sorted(symbols['defined']) == sorted(expected_symbols) and not symbols['undefined']
    data = obj.read_bytes()
    count = struct.unpack_from('<H',data,2)[0]
    storage_sections = []
    for index in range(count):
        at = 20+index*40
        name = data[at:at+8].rstrip(b'\0').decode()
        length,offset,_,_,relocs,_,flags = struct.unpack_from('<IIIIHHI',data,at+16)
        if name == '.orig$fc':
            bits = data[offset:offset+length]
            assert flags & 0x40000000 and not flags & 0x80000000 and relocs == 0
            assert bits == b''.join(TARGETS.values()), bits.hex()
            storage_sections.append(dict(name=name,bytes=bits.hex(),flags=f'{flags:08x}',relocations=relocs))
    assert len(storage_sections) == 1
    exe = OUT/'scalar_fixture.exe'
    linked = run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objects/'scalar_fixture.obj',kernel],'fixture-link')
    assert linked['exit_code'] == 0
    native = run([exe],'fixture-native')
    assert native['exit_code'] == 0
    exe_sections = sections(exe.read_bytes())
    actual_readonly = next(s for s in exe_sections if s['name'] == '.orig')
    assert actual_readonly['flags'] & 0x40000000 and not actual_readonly['flags'] & 0x80000000
    guard()
    summary = dict(schema=1,kind='original-readonly-data',original_sha256=SHA,compiler_sha256=digest(compiler),
                   functions_added=0,defined_data_symbols=expected_symbols,actual_compiler_batches=1,compiled=compiled,fixture_link=linked,native_fixture=native,
                   support_objects=[dict(id='readonly-float-cells-221',compiled=True,compiler_exit_code=0,
                     generated_source=relative(source),generated_source_sha256=digest(source),object=relative(obj),object_sha256=digest(obj),
                     symbols=symbols,dependency_sha256={relative(source):digest(source)},readonly_sections=storage_sections)],
                   input_sha256={relative(p):h for p,h in pins.items()},
                   original_indexed_memory_reads_verified=738,
                   limits=['Only exact readonly scalar bits for current native consumer00485100; no algorithm change',
                           'Future formal byte aliases must share these cells; no separate byte allocation',
                           'Whole original section address relationships, indirect uses and production ownership remain open'])
    write(RUN/'summary.json',summary)
    write(RUN/'validation.json',dict(summary_sha256=digest(RUN/'summary.json'),input_guards_before_after=True,
                                    data_symbols=2,functions_added=0,actual_compiler_batches=1,native_fixture_exit=0,readonly_object_and_PE_pass=True))
    print(json.dumps(dict(data_symbols=2,functions_added=0,original_reads=738,compile_seconds=compiled['seconds'],native_exit=0)))


if __name__ == '__main__':
    main()
