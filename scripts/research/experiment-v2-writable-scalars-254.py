"""Build one data-only native object for Run254's screened virtual-zero DWORD cells."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'254-writable-scalar-batch'
OUT=ROOT/'local/experiments/v2-writable-scalars-254'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
def main(finalize):
    helper=module('helper254build',ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py')
    coff=module('coff254build',ROOT/'scripts/research/build-v2-compile-corpus.py')
    audit=module('audit254build',RUNS/'226-writable-scalar-storage/audit.py')
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();sha=helper.digest(path)
        assert expected is None or sha==expected,(path,sha,expected)
        pins[path]=sha;return path
    def guard():
        for path,sha in pins.items():assert helper.digest(path)==sha,('input drift',path)
    def run(command,name):
        command=list(map(str,command));start=time.perf_counter()
        p=subprocess.run(command,cwd=OUT,capture_output=True,timeout=120,env={**os.environ,'VSLANG':'1033'})
        log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
        receipt=dict(command=command,exit_code=p.returncode,seconds=round(time.perf_counter()-start,6),log=helper.relative(log),log_sha256=helper.digest(log))
        helper.write(OUT/(name+'.execution.json'),receipt)
        return receipt
    assert not (RUN/'summary.json').exists()
    if finalize:assert (OUT/'compile.execution.json').exists()
    else:
        assert not OUT.exists(),'Fresh254 capture required'
        OUT.mkdir(parents=True)
    pin(Path(__file__));pin(ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py')
    pin(ROOT/'scripts/research/screen-v2-writable-scalars-254.py')
    pin(ROOT/'scripts/research/build-v2-compile-corpus.py')
    pin(RUNS/'226-writable-scalar-storage/audit.py')
    screen=load= json.loads(pin(RUN/'screening.json').read_bytes())
    for name,sha in screen['input_sha256'].items():pin(ROOT/name,sha)
    assert screen['before_after_guards'] and screen['screened']==24 and len(screen['safe_vas'])==17
    safe=[r for r in screen['rows'] if r['safe']]
    assert [r['va'] for r in safe]==screen['safe_vas']
    assert all(r['symbol'] in (f"?DAT_{r['va']}@@3HA",f"?DAT_{r['va']}@@3IA") and r['initial_bits']=='00000000' for r in safe)
    assert all(len(r['direct_MEM4'])==len(r['complete_HIGHLOW_sites']) and r['native_consumers'] for r in safe)
    assert all(abs(int(a['va'],16)-int(b['va'],16))>=4 for a in safe for b in safe if a is not b)
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes()
    sections=helper.sections(image)
    for row in safe:
        n=int(row['va'],16)
        sec=next(s for s in sections if s['va']<=n and n+4<=s['va']+s['size'])
        assert sec['name']=='.data' and sec['flags']&0xc0000000==0xc0000000 and not sec['flags']&0x20000000
        assert n>=sec['va']+sec['rawsize']
    toolroot=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86'
    compiler_report=json.loads(pin(RUNS/'202-float-bit-stores/summary.json').read_bytes())
    compiler=pin(toolroot/'cl.exe',compiler_report['compiler_sha256'])
    for name in ('c1xx.dll','c2.dll'):pin(toolroot/name)
    linker=pin(toolroot/'link.exe')
    kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    data_source=RUN/'original_scalars.cpp';fixture_source=RUN/'scalar_fixture.cpp'
    data_text='// Original Porsche.exe SHA256 '+SHA+'; independent zero DWORD cells.\n#pragma section(".ogw$zc", read, write)\n'
    for row in safe:
        typ='unsigned int' if row['symbol'].endswith('3IA') else 'int'
        data_text+=f'__declspec(allocate(".ogw$zc")) {typ} DAT_{row["va"]} = 0;\n'
    data_text+='static_assert(sizeof(int)==4 && sizeof(unsigned int)==4,"DWORD");\n'
    fixture=''.join(f'extern {"unsigned int" if r["symbol"].endswith("3IA") else "int"} DAT_{r["va"]};\n' for r in safe)
    fixture+='extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned int);\n'
    fixture+='static unsigned int raw_word(const void*p){const unsigned char*b=static_cast<const unsigned char*>(p);return b[0]|(static_cast<unsigned int>(b[1])<<8)|(static_cast<unsigned int>(b[2])<<16)|(static_cast<unsigned int>(b[3])<<24);}\n'
    fixture+='static void store_word(void*p,unsigned int v){unsigned char*b=static_cast<unsigned char*>(p);for(unsigned int i=0;i<4;++i)b[i]=static_cast<unsigned char>(v>>(8*i));}\n'
    fixture+='extern "C" void __cdecl entry(){\n'
    fixture+=f' void*cells[{len(safe)}]={{'+','.join('&DAT_'+r['va'] for r in safe)+'};\n'
    fixture+=' const unsigned int patterns[6]={0,1,0x7fffffffu,0x80000000u,0x80000001u,0xffffffffu};\n'
    fixture+=f' for(unsigned int i=0;i<{len(safe)};++i){{if(raw_word(cells[i])!=0)ExitProcess(1);for(unsigned int j=i+1;j<{len(safe)};++j)if(cells[i]==cells[j])ExitProcess(2);}}\n'
    fixture+=f' for(unsigned int i=0;i<{len(safe)};++i){{for(unsigned int p=0;p<6;++p){{store_word(cells[i],patterns[p]);if(raw_word(cells[i])!=patterns[p])ExitProcess(3);for(unsigned int j=0;j<{len(safe)};++j)if(j!=i&&raw_word(cells[j])!=0)ExitProcess(4);}}store_word(cells[i],0);}}\n'
    fixture+=f' for(unsigned int i=0;i<{len(safe)};++i)if(raw_word(cells[i])!=0)ExitProcess(5);ExitProcess(0);}}\n'
    for path,text in ((data_source,data_text),(fixture_source,fixture)):
        if finalize:assert path.read_text(encoding='utf8')==text,('source drift',path)
        else:path.write_text(text,encoding='utf8',newline='\n')
        pin(path)
    objdir=OUT/'objects'
    if not finalize:objdir.mkdir()
    flags=['/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/Zl','/W4','/utf-8','/MP6']
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    command=[compiler,*flags,'/Fo'+str(objdir)+os.sep,data_source,fixture_source]
    if finalize:
        captured=json.loads(pin(OUT/'prepare.json').read_bytes())
        for name,sha in captured['input_sha256'].items():pin(ROOT/name,sha)
        compiled=json.loads(pin(OUT/'compile.execution.json').read_bytes())
        assert compiled['command']==list(map(str,command))
        pin(ROOT/compiled['log'],compiled['log_sha256'])
    else:
        guard()
        helper.write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={helper.relative(p):sha for p,sha in pins.items()}))
        compiled=run(command,'compile')
    assert compiled['exit_code']==0,(OUT/'compile.log').read_text(errors='replace')
    assert not re.search(rb'\b(?:warning|error) C\d+',(OUT/'compile.log').read_bytes())
    obj=objdir/'original_scalars.obj'
    symbols=coff.coff_symbols(obj)
    assert set(symbols['defined'])=={r['symbol'] for r in safe} and not symbols['undefined'] and not symbols['common']
    parsed=audit.coff(obj)
    storage=next(s for s in parsed['sections'] if s['name']=='.ogw$zc')
    size=4*len(safe)
    assert storage['size']==size and storage['chars']&0xc0000000==0xc0000000 and not storage['chars']&0x20000000
    assert not any(s['reloc_count'] or (s['size'] and s['chars']&0x20000000) for s in parsed['sections'])
    assert parsed['bytes'][storage['raw']:storage['raw']+size]==bytes(size)
    cells=[]
    for row in safe:
        sym=next(s for s in parsed['symbols'] if s['name']==row['symbol'])
        assert parsed['sections'][sym['section']-1]['name']=='.ogw$zc' and sym['value']%4==0
        cells.append(dict(va=row['va'],symbol=row['symbol'],native_offset=sym['value'],initial_bytes='00000000'))
    assert sorted(c['native_offset'] for c in cells)==list(range(0,size,4))
    exe=OUT/'scalar_fixture.exe'
    if finalize:linked=json.loads(pin(OUT/'fixture-link.execution.json').read_bytes())
    else:linked=run([linker,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objdir/'scalar_fixture.obj',kernel],'fixture-link')
    assert linked['exit_code']==0
    pe=audit.pe(exe);section=next(s for s in pe['sections'] if s['name']=='.ogw')
    assert section['chars']&0xc0000000==0xc0000000 and not section['chars']&0x20000000
    assert pe['bytes'][section['raw']:section['raw']+size]==bytes(size)
    assert not any(section['va']<=r<section['va']+size for r in pe['reloc_rvas'])
    if finalize:native=json.loads(pin(OUT/'fixture-native.execution.json').read_bytes())
    else:native=run([exe],'fixture-native')
    assert native['exit_code']==0
    guard()
    report=dict(schema=1,kind='original-writable-data',original_sha256=SHA,functions_added=0,data_symbols=len(safe),physical_data_cells=len(safe),screened=screen['screened'],deferred_vas=screen['deferred_vas'],actual_compiler_batches=1,actual_compiled_TUs=2,compiled=compiled,fixture_link=linked,native_fixture=native,fixture_executable=helper.relative(exe),fixture_executable_sha256=helper.digest(exe),support_objects=[dict(id='writable-virtual-zero-cells-254',compiled=True,compiler_exit_code=0,generated_source=helper.relative(data_source),generated_source_sha256=helper.digest(data_source),object=helper.relative(obj),object_sha256=helper.digest(obj),dependency_sha256={helper.relative(data_source):helper.digest(data_source)},symbols=symbols,storage_sections=[dict(name='.ogw$zc',bytes='00'*size,flags=f"{storage['chars']:08x}",relocations=0,cells=cells)])],input_sha256={helper.relative(p):sha for p,sha in pins.items()},screening=helper.relative(RUN/'screening.json'),screening_sha256=helper.digest(RUN/'screening.json'),original_memory_instructions_verified=sum(len(r['direct_MEM4']) for r in safe),original_relative_layout_claim=False,finalized_existing_compile=finalize,limits=['Current direct MEM4/native symbol views only; no data meaning, array or function recovery','Seven screened cells deferred: see screening.json for actual HIGHLOW/WIP gaps','Computed aliases/whole original layout/lifetime and production integration remain open'])
    helper.write(RUN/'summary.json',report)
    helper.write(RUN/'validation.json',dict(passed=True,summary_sha256=helper.digest(RUN/'summary.json'),guarded_inputs=len(pins),input_guards_before_after=True,screened=24,physical_data_cells=len(safe),deferred=7,original_MEM4_HIGHLOW_sites=report['original_memory_instructions_verified'],compiler_exit_code=compiled['exit_code'],link_exit_code=linked['exit_code'],native_exit_code=native['exit_code'],original_relative_layout_claim=False))
    print(json.dumps(dict(cells=len(safe),deferred=7,refs=report['original_memory_instructions_verified'],compile_exit=compiled['exit_code'],compile_seconds=compiled['seconds'],link_exit=linked['exit_code'],native_exit=native['exit_code'],pins=len(pins))))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--finalize-existing',action='store_true')
    main(parser.parse_args().finalize_existing)
