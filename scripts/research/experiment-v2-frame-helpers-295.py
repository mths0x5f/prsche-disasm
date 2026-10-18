"""Build and compare typed frame helpers with exact original PE body bytes."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/295-frame-helpers'
PE = ROOT / 'local/game/Porsche.exe'
ORIGINAL_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
sys.path.insert(0, str(ROOT / 'scripts/research'))
from v2_shared_manifests import ManifestReader, write_manifest


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    p = Path(path).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + '\n', encoding='utf8', newline='\n')


def load(path):
    return json.loads(Path(path).read_bytes())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def pe_read(raw, address, size):
    pe = struct.unpack_from('<I', raw, 0x3c)[0]
    count = struct.unpack_from('<H', raw, pe + 6)[0]
    opt_size = struct.unpack_from('<H', raw, pe + 20)[0]
    image = struct.unpack_from('<I', raw, pe + 24 + 28)[0]
    for i in range(count):
        sec = pe + 24 + opt_size + i * 40
        vsize, rva, rsize, offset = struct.unpack_from('<IIII', raw, sec + 8)
        start = image + rva
        if start <= address and address + size <= start + rsize:
            return raw[offset + address - start:offset + address - start + size]
    raise ValueError('PE bytes outside raw section')


def run(out, command, name):
    receipt = out / (name + '.receipt.json')
    log = out / (name + '.log')
    if receipt.exists() or log.exists():
        raise FileExistsError('Attempt receipt is immutable: ' + name)
    start = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, env={**os.environ, 'CL':'', '_CL_':'', 'INCLUDE':''},
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_bytes(result.stdout)
    row = dict(command=command, cwd=str(ROOT), exit_code=result.returncode,
               seconds=time.perf_counter()-start, log=relative(log), log_sha256=digest(log))
    save(receipt, row)
    return row


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument('--attempt', required=True)
    args = arg.parse_args()
    if not args.attempt.isdigit() or len(args.attempt) != 3:
        raise ValueError('Use a three-digit immutable attempt')
    out = ROOT / ('local/experiments/v2-frame-helpers-295/' + args.attempt)
    if out.exists():
        raise FileExistsError('Attempt directory is immutable')
    if (RUN / 'summary.json').exists():
        raise FileExistsError('Finalized run is immutable')
    out.mkdir(parents=True)
    (out / 'objects').mkdir()
    (out / 'dependencies').mkdir()
    raw = PE.read_bytes()
    if digest(PE) != ORIGINAL_SHA:
        raise ValueError('Original SHA drift')
    body = {0x423840:pe_read(raw, 0x423840, 67), 0x482e50:pe_read(raw, 0x482e50, 69)}
    if pe_read(raw, 0x5b47d8, 4) != struct.pack('<f', 8000.0) or pe_read(raw, 0x5b2764, 4) != struct.pack('<f', 10000.0):
        raise ValueError('Original float cells changed')
    header = RUN / 'original_bytes_295.hpp'
    header_text = '#pragma once\n' + ''.join(
        'static const unsigned char original_%08x[] = {%s};\n' %
        (va, ','.join('0x%02x' % byte for byte in value)) for va,value in body.items())
    if header.exists():
        if header.read_text(encoding='ascii') != header_text:
            raise ValueError('Original body header drift')
    else:
        header.write_text(header_text, encoding='ascii', newline='\n')
    baseline = load(RUN.parent / '290-frame-service-cluster/summary.json')
    compiler = Path(baseline['compiler_command'][0]); linker=compiler.with_name('link.exe')
    roots=[ROOT / p if not Path(p).is_absolute() else Path(p) for p in baseline['results'][0]['include_directories']]
    sources=[RUN/'00423840.cpp', RUN/'00482e50.cpp', RUN/'fixture.cpp']
    objects=[out/'objects'/(p.stem+'.obj') for p in sources]
    kernel=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')
    index=ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl'
    registry=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'
    repo_inputs=[*sources,header,RUN.parent/'290-frame-service-cluster/frame_service_290.hpp',
                 Path(__file__),PE,compiler,linker,index,registry]
    pins={relative(p):digest(p) for p in repo_inputs}
    external_tools={relative(kernel):digest(kernel)}
    shared=write_manifest(ROOT,pins,'raw')
    reader=ManifestReader(ROOT)
    reader.verify({'input_manifest':shared},expected_hash_mode='raw')
    command=[str(compiler),'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GS-','/GR-','/EHsc',
             '/W4','/utf-8','/MP6','/Zl','/sourceDependencies',str(out/'dependencies'),
             *[x for p in roots for x in ('/I',str(p))],'/Fo'+str(out/'objects')+os.sep,*map(str,sources)]
    save(out/'before.json',dict(schema=1,input_manifest=shared,external_tools_sha256=external_tools,
                                body_hex={f'{k:08x}':v.hex() for k,v in body.items()},
                                compiler_command=command, original_sha256=ORIGINAL_SHA))
    compiled=run(out,command,'compile')
    if compiled['exit_code']:
        raise RuntimeError('Compiler failed; receipt retained')
    # Compiler dependencies become a separate immutable pin layer after compilation.
    deps={};external_dependencies={}
    for src in sources:
        path=out/'dependencies'/(src.name+'.json')
        deps[relative(path)]=digest(path)
        for name in load(path)['Data']['Includes']:
            target=deps if Path(name).resolve().is_relative_to(ROOT) else external_dependencies
            target[relative(name)]=digest(name)
    dep_ref=write_manifest(ROOT,deps,'raw')
    reader.verify({'source_manifest':dep_ref},scope='source',expected_hash_mode='raw')
    exe=out/'fixture.exe'
    link=[str(linker),'/nologo','/MACHINE:X86','/NODEFAULTLIB','/ENTRY:entry','/SUBSYSTEM:CONSOLE',
          '/OUT:'+str(exe),*map(str,objects),str(kernel)]
    linked=run(out,link,'link')
    if linked['exit_code']:
        raise RuntimeError('Link failed; receipt retained')
    native=run(out,[str(exe)],'native')
    if native['exit_code']:
        raise RuntimeError('Native comparison failed; receipt retained')
    if load(out/'native.log') != dict(cases=11,failures=0):
        raise ValueError('Native case report mismatch')
    coff=module('coff295',ROOT/'scripts/research/build-v2-compile-corpus.py')
    symbols=[coff.coff_symbols(p) for p in objects[:2]]
    if 'advance_00423840' not in symbols[0]['defined'][0] or 'invoke_00482e50' not in symbols[1]['defined'][0]:
        raise ValueError('Typed symbol mismatch')
    if symbols[0]['undefined'] or set(symbols[1]['undefined']) != {
            '?frame_limit_005b47d8@porsche@@3MB','?frame_step_005b2764@porsche@@3MB'}:
        raise ValueError('Unexpected provider symbols')
    reader.verify({'input_manifest':shared},expected_hash_mode='raw')
    reader.verify({'source_manifest':dep_ref},scope='source',expected_hash_mode='raw')
    output_pins={relative(p):digest(p) for p in [*objects,exe,*out.glob('*.receipt.json'),*out.glob('*.log')]}
    summary=dict(schema=1,kind='typed-frame-helpers',original_sha256=ORIGINAL_SHA,
                 original_bodies={f'{k:08x}':dict(size=len(v),hex=v.hex()) for k,v in body.items()},
                 game_sources=[relative(p) for p in sources[:2]],
                 game_objects=[dict(path=relative(p),sha256=digest(p)) for p in objects[:2]],
                 symbols=symbols,compiler_batches=1,native_cases=11,attempt=args.attempt,
                 input_manifest=shared,source_manifest=dep_ref,external_tools_sha256=external_tools,
                 external_dependencies_sha256=external_dependencies,output_sha256=output_pins,
                 limitations=['The two original float data cells need a game storage owner',
                              'Finite native cases do not establish complete game behavior'])
    save(RUN/'summary.json',summary)
    save(RUN/'validation.json',dict(passed=True,summary_sha256=digest(RUN/'summary.json'),
                                    original_bytes=136,native_cases=11,compiler_batches=1))
    print(json.dumps(dict(passed=True,native_cases=11,original_bytes=136)))


if __name__=='__main__':
    main()
