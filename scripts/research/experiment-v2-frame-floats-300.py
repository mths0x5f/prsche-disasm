"""Compile exact original frame float cells as read-only data, with captured pins."""
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

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/300-frame-float-data'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VALUES={'005b47d8':('.p3lim','0000fa45','?frame_limit_005b47d8@porsche@@3MB'),
        '005b2764':('.p3step','00401c46','?frame_step_005b2764@porsche@@3MB')}
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_shared_manifests import ManifestReader,write_manifest

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def load(path):return json.loads(Path(path).read_bytes())
def save(path,data):Path(path).write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value

def sections(object_path):
    raw=Path(object_path).read_bytes();machine,count,_,symtab,syms,opt,_=struct.unpack_from('<HHLLLHH',raw)
    if machine!=0x14c or opt!=0:raise ValueError('Expected ordinary x86 COFF')
    result={}
    for index in range(count):
        at=20+index*40
        name=raw[at:at+8].rstrip(b'\0').decode('ascii')
        size,start,_,_,relocs,_,flags=struct.unpack_from('<IIIIHHI',raw,at+16)
        result[name]=dict(bytes=raw[start:start+size].hex(),size=size,relocations=relocs,flags=f'{flags:08x}')
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True);args=parser.parse_args()
    if not args.attempt.isdigit() or len(args.attempt)!=3:raise ValueError('Expected three-digit attempt')
    out=ROOT/('local/experiments/v2-frame-floats-300/'+args.attempt)
    if out.exists() or (RUN/'summary.json').exists():raise FileExistsError('Immutable output exists')
    out.mkdir(parents=True);(out/'dependencies').mkdir()
    source=RUN/'frame_floats_300.cpp';evidence=RUN/'original-evidence.json'
    summary295=ROOT/'iterations/v2/001-original-recovery/runs/295-frame-helpers/summary.json'
    baseline=load(ROOT/'iterations/v2/001-original-recovery/runs/290-frame-service-cluster/summary.json')
    compiler=Path(baseline['compiler_command'][0])
    obj295=ROOT/next(row['path'] for row in load(summary295)['game_objects'] if row['path'].endswith('00482e50.obj'))
    inputs=[source,evidence,summary295,obj295,Path(__file__),
            ROOT/'scripts/research/probe-v2-frame-floats-300.py',
            ROOT/'scripts/research/build-v2-compile-corpus.py',
            ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
            ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',
            ROOT/'local/game/Porsche.exe',compiler]
    pins={relative(path):digest(path) for path in inputs}
    reference=write_manifest(ROOT,pins,'raw')
    reader=ManifestReader(ROOT);reader.verify({'input_manifest':reference},expected_hash_mode='raw')
    proof=load(evidence)
    if proof['original_sha256']!=SHA or pins['local/game/Porsche.exe']!=SHA or proof['cross_boundary_direct_operands']:
        raise ValueError('Original evidence drift')
    for address,(section,bits,symbol) in VALUES.items():
        cell=proof['cells'][address]
        if (cell['section']!='.rdata' or int(cell['section_flags'],16)&0x80000000 or
            cell['original_bits']!=bits or cell['relocations_inside_cell'] or
            any(cell['interior_literals'].values()) or
            len(cell['literal_occurrences'])!=len(cell['index_refs']) or
            len(cell['indexed_instructions'])!=len(cell['index_refs']) or
            any(not row['HIGHLOW'] or len(row['indexed_instruction'])!=1 for row in cell['literal_occurrences']) or
            any(row['width']!=4 or not row['read'] or row['write'] for row in cell['indexed_instructions']) or
            any(row['type']!='READ' for row in cell['index_refs'])):
            raise ValueError('Unproved isolated read-only cell '+address)
    object_path=out/'frame_floats_300.obj'
    command=[str(compiler),'/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/EHsc',
             '/W4','/utf-8','/MP6','/Zl','/sourceDependencies',str(out/'dependencies'),
             '/Fo'+str(object_path),str(source)]
    save(out/'before.json',dict(schema=1,input_manifest=reference,command=command,original_sha256=SHA))
    start=time.perf_counter()
    result=subprocess.run(command,cwd=ROOT,env={**os.environ,'CL':'','_CL_':'','INCLUDE':''},
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=out/'compile.log';log.write_bytes(result.stdout)
    receipt=out/'compile.receipt.json'
    save(receipt,dict(command=command,cwd=str(ROOT),exit_code=result.returncode,
                      seconds=time.perf_counter()-start,log=relative(log),log_sha256=digest(log)))
    if result.returncode:raise RuntimeError('Compile failed; receipt retained')
    dep=out/'dependencies/frame_floats_300.cpp.json'
    deps={relative(dep):digest(dep)}
    for name in load(dep)['Data']['Includes']:
        path=Path(name).resolve()
        if not path.is_relative_to(ROOT):raise ValueError('Unexpected external dependency')
        deps[relative(path)]=digest(path)
    dep_ref=write_manifest(ROOT,deps,'raw')
    reader.verify({'source_manifest':dep_ref},scope='source',expected_hash_mode='raw')
    coff=module('coff300',ROOT/'scripts/research/build-v2-compile-corpus.py')
    symbols=coff.coff_symbols(object_path)
    expected=sorted(item[2] for item in VALUES.values())
    if symbols['defined']!=expected or symbols['undefined'] or symbols['common'] or symbols['weak']:
        raise ValueError('Data-only COFF symbol mismatch')
    storage=sections(object_path)
    for _,(section,bits,_) in VALUES.items():
        row=storage[section]
        if row['bytes']!=bits or row['size']!=4 or row['relocations']!=0 or not int(row['flags'],16)&0x40000000 or int(row['flags'],16)&0x80000000:
            raise ValueError('Native data bits or read-only section mismatch')
    reader.verify({'input_manifest':reference},expected_hash_mode='raw')
    reader.verify({'source_manifest':dep_ref},scope='source',expected_hash_mode='raw')
    summary=dict(schema=1,kind='exact-frame-float-data',original_sha256=SHA,
                 source=relative(source),game_object=dict(path=relative(object_path),sha256=digest(object_path)),
                 symbols=symbols,storage={name:storage[name] for name,_,_ in VALUES.values()},
                 original_read_sites={address:len(proof['cells'][address]['index_refs']) for address in VALUES},
                 compiler_batches=1,input_manifest=reference,source_manifest=dep_ref,
                 compile_receipt=dict(path=relative(receipt),sha256=digest(receipt)),
                 output_sha256={relative(path):digest(path) for path in (object_path,log,receipt)},
                 limits=['Only two isolated read-only cells; original whole-section layout is not reproduced',
                         'Unindexed indirect access and full game behavior remain outside this bounded proof'])
    save(RUN/'summary.json',summary)
    save(RUN/'validation.json',dict(passed=True,summary_sha256=digest(RUN/'summary.json'),
                                    native_coff_bits=8,readonly_data_symbols=2,indexed_reads=35,
                                    compiler_batches=1))
    print(json.dumps(dict(passed=True,native_coff_bits=8,indexed_reads=35,game_objects=1)))

if __name__=='__main__':main()
