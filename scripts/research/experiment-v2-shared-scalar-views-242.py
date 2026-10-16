"""One original DWORD, two native integer views, exact data-link alias."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT/'iterations/v2/001-original-recovery/runs'
RUN = RUNS/'242-shared-scalar-views'
OUT = ROOT/'local/experiments/v2-shared-scalar-views-242'
SIGNED = '?DAT_0060c95c@@3HA'
UNSIGNED = '?DAT_0060c95c@@3IA'
DIRECTIVE = '/alternatename:'+UNSIGNED+'='+SIGNED


def main(finalize_existing=False):
    hp = ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'
    spec = importlib.util.spec_from_file_location('h242build',hp)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    write,digest,relative = h.write,h.digest,h.relative
    assert not (RUN/'summary.json').exists(), 'Fresh242 summary required'
    if finalize_existing:
        assert (OUT/'compile.execution.json').exists()
    else:
        assert not OUT.exists(), 'Fresh242 native capture required'
        OUT.mkdir(parents=True)
    pins = {}
    def pin(path,expected=None):
        path = Path(path).resolve()
        actual = digest(path)
        assert expected is None or actual==expected,path
        pins[path] = actual
        return path
    def guard():
        for path,sha in pins.items():
            assert digest(path)==sha, ('Input mutation',path)
    def run(command,name):
        command = list(map(str,command))
        start = time.perf_counter()
        p = subprocess.run(command,cwd=OUT,capture_output=True,timeout=120,env={**os.environ,'VSLANG':'1033'})
        elapsed = round(time.perf_counter()-start,6)
        log = OUT/(name+'.log')
        log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
        receipt = dict(command=command,exit_code=p.returncode,seconds=elapsed,log=relative(log),log_sha256=digest(log))
        write(OUT/(name+'.execution.json'),receipt)
        return receipt
    pin(Path(__file__))
    pin(hp)
    preflight_path = pin(RUN/'preflight.json')
    preflight = json.loads(preflight_path.read_bytes())
    assert preflight['safe_for_bounded_storage_pilot'] and not preflight['blockers']
    assert preflight['initial_bits']=='00000000' and preflight['virtual_zero_fill']
    assert len(preflight['complete_HIGHLOW_target_sites'])==125 and len(preflight['original_memory_instructions'])==125
    for path,sha in preflight['input_sha256'].items():
        pin(ROOT/path,sha)
    audit = h.module('audit226_for242',pin(RUNS/'226-writable-scalar-storage/audit.py'))
    coff = h.module('coff242build',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    tools = ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86'
    compiler_report = json.loads(pin(RUNS/'202-float-bit-stores/summary.json').read_bytes())
    compiler = pin(tools/'cl.exe',compiler_report['compiler_sha256'])
    for name in ('c1xx.dll','c2.dll'):
        pin(tools/name)
    link = pin(tools/'link.exe')
    kernel = pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    sources = [pin(RUN/(name+'.cpp')) for name in ['original_cell','data_alias','signed_view_fixture','unsigned_view_fixture','scalar_fixture']]
    objects = OUT/'objects'
    if not finalize_existing:
        objects.mkdir()
    flags = ['/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/Zl','/W4','/utf-8','/MP6']
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    command = [compiler,*flags,'/Fo'+str(objects)+os.sep,*sources]
    if finalize_existing:
        captured = json.loads(pin(OUT/'prepare.json').read_bytes())
        for path,sha in captured['input_sha256'].items():
            pin(OUT/'captured-compile-driver.py' if path==relative(Path(__file__)) else ROOT/path,sha)
        compiled = json.loads(pin(OUT/'compile.execution.json').read_bytes())
        assert compiled['command']==list(map(str,command))
        pin(ROOT/compiled['log'],compiled['log_sha256'])
        pin(OUT/'postcompile-attribution-failure.log')
        guard()
    else:
        guard()
        write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={relative(p):sha for p,sha in pins.items()}))
        compiled = run(command,'compile')
    assert compiled['exit_code']==0,(OUT/'compile.log').read_text(errors='replace')
    assert not re.search(rb'\b(?:warning|error) C\d+',(OUT/'compile.log').read_bytes())
    data_obj,alias_obj = objects/'original_cell.obj',objects/'data_alias.obj'
    data_symbols,alias_symbols = coff.coff_symbols(data_obj),coff.coff_symbols(alias_obj)
    assert data_symbols['defined']==[SIGNED] and not data_symbols['undefined']
    assert not alias_symbols['defined'] and not alias_symbols['undefined']
    data,alias = audit.coff(data_obj),audit.coff(alias_obj)
    storage = next(s for s in data['sections'] if s['name']=='.ogw$sv')
    assert storage['size']==4 and data['bytes'][storage['raw']:storage['raw']+4]==b'\0'*4
    assert storage['chars']&0x40000000 and storage['chars']&0x80000000 and not storage['chars']&0x20000000
    assert not any(s['reloc_count'] or (s['size'] and s['chars']&0x20000000) for s in data['sections'])
    directive_section = next(s for s in alias['sections'] if s['name']=='.drectve')
    directive = alias['bytes'][directive_section['raw']:directive_section['raw']+directive_section['size']].decode('ascii').strip()
    assert directive==DIRECTIVE
    assert all(not s['reloc_count'] and not s['chars']&0xa0000000 and
               (not s['size'] or s['name'] in ('.drectve','.debug$S','.chks64')) for s in alias['sections'])
    signed_native = coff.coff_symbols(objects/'signed_view_fixture.obj')
    unsigned_native = coff.coff_symbols(objects/'unsigned_view_fixture.obj')
    assert signed_native['undefined']==[SIGNED] and unsigned_native['undefined']==[UNSIGNED]
    exe = OUT/'scalar_fixture.exe'
    linked = run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB',
        '/OUT:'+str(exe),*[objects/(p.stem+'.obj') for p in sources],kernel],'fixture-link')
    assert linked['exit_code']==0
    pe = audit.pe(exe)
    section = next(s for s in pe['sections'] if s['name']=='.ogw')
    assert section['chars']&0x40000000 and section['chars']&0x80000000 and not section['chars']&0x20000000
    assert pe['bytes'][section['raw']:section['raw']+4]==b'\0'*4
    assert not any(section['va']<=r<section['va']+4 for r in pe['reloc_rvas'])
    output_hashes = {relative(objects/(p.stem+'.obj')):digest(objects/(p.stem+'.obj')) for p in sources}
    write(OUT/'fixture-before-execution.json',dict(executable=relative(exe),executable_sha256=digest(exe),object_sha256=output_hashes))
    native = run([exe],'fixture-native')
    assert native['exit_code']==0
    assert digest(exe)==pe['sha256'] and all(digest(ROOT/path)==sha for path,sha in output_hashes.items())
    guard()
    input_pins = {relative(p):sha for p,sha in pins.items()}
    storage_report = dict(name='.ogw$sv',bytes='00000000',flags=f"{storage['chars']:08x}",relocations=0,
                          cells=[dict(va='0060c95c',symbol=SIGNED,native_offset=0,initial_bytes='00000000')])
    common = dict(schema=1,original_sha256=preflight['original_sha256'],compiler_sha256=digest(compiler),functions_added=0,
        actual_compiler_batches=1,compiled=compiled,fixture_link=linked,native_fixture=native,
        fixture_executable=relative(exe),fixture_executable_sha256=digest(exe),fixture_object_sha256=output_hashes,
        finalized_existing_compile=finalize_existing,
        compile_provenance='Original durable execution receipt and captured driver/inputs retained; no compiler rerun after metadata attribution correction' if finalize_existing else 'Fresh single compiler batch',
        input_sha256=input_pins,preflight=relative(preflight_path),preflight_sha256=digest(preflight_path),
        limits=['One physical original DWORD with current signed/unsigned views; no inferred data meaning or algorithm',
                'Original direct HIGHLOW/index coverage does not prove whole-program computed aliases/layout/lifetime',
                'No game function, production or union change'])
    summary = dict(**common,kind='original-writable-data',data_symbols=1,physical_data_cells=1,
        support_objects=[dict(id='shared-scalar-cell-0060c95c-242',compiled=True,compiler_exit_code=0,
            generated_source=relative(sources[0]),generated_source_sha256=digest(sources[0]),
            object=relative(data_obj),object_sha256=digest(data_obj),dependency_sha256={relative(sources[0]):digest(sources[0])},
            symbols=data_symbols,storage_sections=[storage_report])])
    binding = dict(**common,kind='proven-link-contract',physical_data_cells_added=0,
        support_objects=[dict(id='signed-unsigned-cell-binding-0060c95c-242',compiled=True,compiler_exit_code=0,
            generated_source=relative(sources[1]),generated_source_sha256=digest(sources[1]),
            object=relative(alias_obj),object_sha256=digest(alias_obj),dependency_sha256={relative(sources[1]):digest(sources[1])},
            symbols=alias_symbols,drectve=directive)],
        aliases=[dict(from_=UNSIGNED,to=SIGNED,va='0060c95c',support_object_id='signed-unsigned-cell-binding-0060c95c-242',
            directive=DIRECTIVE,proof=dict(original_span='0060c95c:4',original_MEM4_references=125,
                original_HIGHLOW_targets_complete=True,initial_bits='00000000',type_views=['int32','uint32'],
                native_separate_TU_views=True,native_address_identity=True,native_highbit_crosswrites_and_restore=True))])
    binding['aliases'][0]['from'] = binding['aliases'][0].pop('from_')
    write(RUN/'summary.json',summary)
    write(RUN/'binding-summary.json',binding)
    write(RUN/'validation.json',dict(passed=True,summary_sha256=digest(RUN/'summary.json'),binding_summary_sha256=digest(RUN/'binding-summary.json'),
        guarded_inputs=len(pins),input_mutation_guards_before_after=True,functions_added=0,physical_data_cells=1,
        exact_data_aliases=1,support_objects=2,actual_compiler_batches=1,actual_compiled_TUs=5,
        compiler_exit_code=compiled['exit_code'],fixture_link_exit=linked['exit_code'],native_fixture_exit=native['exit_code'],
        actual_COFF_drectve=directive,original_index_MEM4_references=125,original_HIGHLOW_targets=125,
        native_fixture='Initialzero/addressidentity; six signed and six unsigned cross-view patterns including highbits; restorezero'))
    print(json.dumps(dict(physical_cells=1,aliases=1,functions=0,compiled_TUs=5,compile_exit=compiled['exit_code'],
        compile_seconds=compiled['seconds'],link_exit=linked['exit_code'],native_exit=native['exit_code'],pins=len(pins))))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--finalize-existing',action='store_true')
    main(parser.parse_args().finalize_existing)
