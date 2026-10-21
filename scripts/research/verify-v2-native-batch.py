"""Small config-driven x86 original/native batch runner.

The fixture owns the oracle and fail-closed callback boundaries. This runner
pins source/PE inputs, compiles the same sources at /Od and /O2, and preserves
full command logs in an immutable local attempt directory.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time
import struct

ROOT = Path(__file__).resolve().parents[2]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()

def relative(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')

def pe_at(image, va, count):
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    assert image[pe:pe+4] == b'PE\0\0'
    sections = struct.unpack_from('<H', image, pe+6)[0]
    optional = struct.unpack_from('<H', image, pe+20)[0]
    base = struct.unpack_from('<I', image, pe+52)[0]
    for i in range(sections):
        off = pe+24+optional+i*40
        virtual_size, rva, raw_size, raw = struct.unpack_from('<IIII', image, off+8)
        if rva <= va-base and va-base+count <= rva+min(virtual_size,raw_size):
            start = raw+va-base-rva
            return image[start:start+count]
    raise ValueError(f'VA {va:08x} is outside PE file-backed section')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--attempt', type=int, required=True)
    args = parser.parse_args()
    config_path = (ROOT / args.config).resolve()
    cfg = json.loads(config_path.read_text(encoding='utf-8'))
    assert args.attempt > 0
    out = (ROOT / cfg['experiment'] / f'{args.attempt:03d}').resolve()
    assert not out.exists(), f'immutable attempt exists: {out}'
    out.mkdir(parents=True)
    pe = ROOT / cfg['original_pe']
    assert digest(pe) == cfg['original_sha256']
    src = [ROOT / item for item in cfg['sources']]
    fixture_template = ROOT / cfg['fixture']
    replacements = {}
    for item in cfg.get('original_bodies', []):
        data = pe_at(pe.read_bytes(),int(item['va'],16),item['bytes'])
        assert digest_bytes(data) == item['sha256']
        replacements[item['token']] = ','.join(map(str,data))
    fixture = out/'native_fixture.cpp'
    content = fixture_template.read_text(encoding='utf-8')
    for token, data in replacements.items():
        assert content.count(token)==1
        content = content.replace(token,data)
    fixture.write_text(content,encoding='utf-8',newline='\n')
    dependency_helper_path = ROOT/'scripts/research/audio_recovery_provenance.py'
    helper_spec = importlib.util.spec_from_file_location('native_dependencies', dependency_helper_path)
    dependency_helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(dependency_helper)
    vc = ROOT / 'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
    sdk = Path('C:/Program Files (x86)/Windows Kits/10')
    kit = '10.0.26100.0'
    cl = vc / 'bin/Hostx64/x86/cl.exe'
    link = cl.parent / 'link.exe'
    includes = [ROOT / item for item in cfg.get('include_dirs', [])]
    includes += [vc / 'include', *(sdk / 'Include' / kit / item for item in ('ucrt', 'shared', 'um'))]
    libs = [vc / 'lib/x86/libcmt.lib', vc / 'lib/x86/libvcruntime.lib',
            vc / 'lib/x86/oldnames.lib', sdk / 'Lib' / kit / 'ucrt/x86/libucrt.lib',
            sdk / 'Lib' / kit / 'um/x86/kernel32.lib']
    pins = {p.resolve(): digest(p) for p in [Path(__file__), dependency_helper_path, config_path, pe, *src, fixture_template,fixture,
                                              cl, link, cl.parent/'c1xx.dll', cl.parent/'c2.dll', *libs]}
    for item in cfg.get('headers', []):
        p = (ROOT / item).resolve()
        pins[p] = digest(p)
    def local_includes(path, found):
        path = path.resolve()
        if path in found:
            return
        found.add(path)
        for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"',
                               path.read_text(encoding='utf-8'), re.M):
            match = next((candidate.resolve() for candidate in
                          [path.parent/name, *(directory/name for directory in includes)]
                          if candidate.is_file()), None)
            if match is None:
                raise ValueError(f'unpinned quoted include {name} from {path}')
            local_includes(match, found)
    dependencies = set()
    for source in [*src, fixture_template]:
        local_includes(source, dependencies)
    for path in dependencies:
        pins[path] = digest(path)
    def guard():
        for p, expected in pins.items():
            assert digest(p) == expected, f'input drift: {p}'
    receipts = {}
    def run(name, command, expected_codes=(0,)):
        guard()
        start = time.perf_counter()
        try:
            proc = subprocess.run(list(map(str, command)), cwd=out, capture_output=True,
                                  env={**os.environ, 'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},
                                  timeout=cfg.get('timeout_seconds',180))
            data = proc.stdout + proc.stderr
            code = proc.returncode
        except subprocess.TimeoutExpired as error:
            data = (error.stdout or b'') + (error.stderr or b'')
            code = -1
        log = out / (name + '.log')
        log.write_bytes(data)
        receipt = {'command':list(map(str, command)), 'exit_code':code,
                   'seconds':round(time.perf_counter()-start, 6), 'log':relative(log),
                   'log_sha256':digest(log)}
        save(out/(name+'.execution.json'), receipt)
        receipts[name] = receipt
        guard()
        if code not in expected_codes:
            raise RuntimeError(f'{name} failed ({code}):\n{log.read_text(errors="replace")[-4000:]}')
        return log.read_text(errors='replace')
    common = [cl, '/nologo','/c','/TP','/std:c++17','/Oi','/Gy','/GR-','/EHsc','/W4','/utf-8',
              *(part for inc in includes for part in ('/I', inc))]
    dependency_dir = out/'dependencies'
    dependency_dir.mkdir()
    def compile_unit(name, source, flags, obj):
        dep_record = dependency_dir/f'{name}.json'
        command = [*common,*flags,'/sourceDependencies',dep_record,f'/Fo{obj}',source]
        run(f'dependency-probe-{name}',command)
        closure = dependency_helper.dependency_paths(out)
        for path in closure:
            pins.setdefault(path,digest(path))
        guard()
        run(f'{name}-compile',command)
        assert dependency_helper.dependency_paths(out)==closure, f'{name}: compiler dependency drift'
        pins[obj.resolve()] = digest(obj)
        pins[dep_record.resolve()] = digest(dep_record)
        guard()
    objects = {}
    for variant, flags in [('od',['/Od','/Oy-','/GS-']),('o2',['/O2','/GS'])]:
        variant_objects = []
        for index, source in enumerate(src):
            obj = out / f'{variant}-{index}.obj'
            compile_unit(f'{variant}-{index}',source,flags,obj)
            variant_objects.append(obj)
        objects[variant] = variant_objects
    fixture_obj = out/'fixture.obj'
    compile_unit('fixture',fixture,['/Od','/Oy-','/GS-'],fixture_obj)
    main_dependencies = dependency_helper.dependency_paths(out)
    results = {}
    for variant in ('od','o2'):
        exe = out/f'{variant}.exe'
        run(f'{variant}-link',[link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE',
                              '/INCREMENTAL:NO','/OPT:REF',
                              '/NODEFAULTLIB',f'/OUT:{exe}',
                              *objects[variant],fixture_obj,*libs])
        pins[exe.resolve()] = digest(exe)
        output = run(f'{variant}-native',[exe,pe])
        marker = cfg['pass_marker']
        assert marker in output, f'{variant} did not report {marker!r}'
        results[variant] = {'marker':marker,'output_sha256':digest(out/f'{variant}-native.log')}
    mutations = []
    for item in cfg.get('mutations',[]):
        name = item['name']
        source = (ROOT/item['source']).resolve()
        assert source in [path.resolve() for path in src]
        source_index = next(i for i,path in enumerate(src) if path.resolve()==source)
        original_text = source.read_text(encoding='utf-8')
        old, new = item['old'], item['new']
        assert original_text.count(old)==1, f'{name}: mutation anchor not unique'
        mutation_source = out/f'mutation-{name}.cpp'
        mutation_source.write_text(original_text.replace(old,new),encoding='utf-8',newline='\n')
        pins[mutation_source.resolve()] = digest(mutation_source)
        mutation_obj = out/f'mutation-{name}.obj'
        compile_unit(f'mutation-{name}',mutation_source,['/O2','/GS'],mutation_obj)
        mutation_objects = list(objects['o2'])
        mutation_objects[source_index] = mutation_obj
        mutation_exe = out/f'mutation-{name}.exe'
        run(f'mutation-{name}-link',[link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE',
            '/INCREMENTAL:NO','/OPT:REF','/NODEFAULTLIB',f'/OUT:{mutation_exe}',
            *mutation_objects,fixture_obj,*libs])
        pins[mutation_exe.resolve()] = digest(mutation_exe)
        failure_code = item.get('expected_exit',10)
        output = run(f'mutation-{name}-native',[mutation_exe,pe],expected_codes=(failure_code,))
        assert item.get('failure_marker','divergence ') in output, f'{name}: no differential failure marker'
        mutations.append({'name':name,'source':relative(source),'detected':True,
                          'exit_code':failure_code,'log_sha256':digest(out/f'mutation-{name}-native.log')})
    guard()
    outputs = {relative(path):digest(path) for path in out.rglob('*') if path.is_file()}
    assert all(digest(ROOT/path)==sha for path,sha in outputs.items())
    report = {'schema':1,'run':cfg['run'],'status':'PASS','original_sha256':digest(pe),
              'original_bodies':cfg.get('original_bodies',[]),
              'config':relative(config_path),'attempt_dir':relative(out),'variants':results,
              'inputs_sha256':{relative(p):h for p,h in pins.items()},
              'outputs_sha256':outputs,
              'actual_dependencies':sorted(map(relative,dependency_helper.dependency_paths(out))),
              'main_dependencies':sorted(map(relative,main_dependencies)),
              'receipts':receipts,
              'mutation_controls':mutations}
    save(out/'receipt.json',report)
    print(f"Run{cfg['run']} native PASS: {relative(out/'receipt.json')}")

if __name__ == '__main__':
    main()
