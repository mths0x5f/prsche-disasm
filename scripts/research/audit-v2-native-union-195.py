"""Audit frozen 192/190 x86 COFF union and diagnostic whole-archive DLL link.

No compilation, symbol bridges, source repair, storage allocation or game target.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
DEFAULT_OUT = ROOT / 'local/experiments/v2-native-union-195'
RUN = RUNS / '195-native-union'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('coff195', ROOT / 'scripts/research/build-v2-compile-corpus.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def pe_sections(data):
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    assert data[pe:pe+4] == b'PE\0\0'
    machine, count, _, _, _, optional, _ = struct.unpack_from('<HHIIIHH', data, pe+4)
    assert machine == 0x14c
    image_base = struct.unpack_from('<I', data, pe+24+28)[0]
    result = []
    for index in range(count):
        start = pe + 24 + optional + index * 40
        name, virtual_size, rva, raw_size, raw_offset = struct.unpack_from('<8sIIII', data, start)
        flags = struct.unpack_from('<I', data, start+36)[0]
        result.append(dict(name=name.rstrip(b'\0').decode('ascii'), va=image_base+rva,
                           virtual_bytes=virtual_size, raw_bytes=raw_size, raw_offset=raw_offset,
                           flags=hex(flags), readable=bool(flags & 0x40000000),
                           writable=bool(flags & 0x80000000), executable=bool(flags & 0x20000000)))
    return result


def comdat_evidence(path, wanted):
    """Read section-selection auxiliaries for repeated compiler constants."""
    data = Path(path).read_bytes()
    machine, count, _, offset, symbols, optional, _ = struct.unpack_from('<HHIIIHH', data)
    assert machine == 0x14c and optional == 0
    strings = offset + symbols * 18
    entries, selections = {}, {}
    index = 0
    while index < symbols:
        start = offset + index * 18
        raw, value, section, kind, storage, auxiliary = struct.unpack_from('<8sIhHBB', data, start)
        if raw[:4] == b'\0'*4:
            at = strings + struct.unpack_from('<I',raw,4)[0]
            name = data[at:data.index(b'\0',at)].decode('ascii')
        else:
            name = raw.rstrip(b'\0').decode('ascii')
        if storage == 3 and section > 0 and auxiliary:
            selections[section] = data[start+18+14]
        if storage == 2 and section > 0 and name in wanted:
            entries[name] = section
        index += 1 + auxiliary
    result = {}
    for name, section in entries.items():
        start = 20 + (section-1)*40
        length, raw = struct.unpack_from('<II',data,start+16)
        flags = struct.unpack_from('<I',data,start+36)[0]
        result[name] = dict(section=section, comdat=bool(flags & 0x1000), selection=selections.get(section),
                            section_bytes=length, section_sha256=hashlib.sha256(data[raw:raw+length]).hexdigest())
    return result


def memory_evidence(va, original, sections):
    address = int(va, 16)
    section = next((s for s in sections if s['va'] <= address < s['va']+max(s['raw_bytes'], s['virtual_bytes'])), None)
    if section is None:
        return dict(va=va, status='not_in_original_PE_section')
    delta = address - section['va']
    length = max(0, min(16, section['raw_bytes']-delta))
    return dict(va=va, section=section, initialized_file_bytes=length,
                first_file_bytes_hex=original[section['raw_offset']+delta:section['raw_offset']+delta+length].hex(),
                boundary='Original section/initial file bytes only; no native owner/type/alias allocation inferred')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--finalize-existing', action='store_true', help='Reparse pinned195 archive/logs; never repeat lib/link.')
    args = parser.parse_args()
    out = args.output.resolve()
    assert out == DEFAULT_OUT.resolve() or out.parent == DEFAULT_OUT.resolve(), 'output restricted to195 experiment'
    prior195 = None
    if args.finalize_existing:
        prior_bytes = (RUN/'summary.json').read_bytes()
        prior195 = json.loads(prior_bytes)
        assert prior195['library']['path']==relative(out/'porsche_native_union_candidates.lib')
        saved = out/'first-parser-summary.json'
        assert not saved.exists(), 'finalize existing outputs only once'
        saved.write_bytes(prior_bytes)
    else:
        assert not out.exists() or not any(out.iterdir()), 'fresh output directory required'
        assert not (RUN / 'summary.json').exists(), 'do not overwrite completed195 snapshot'
    out.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        expected = expected or digest(path)
        assert path not in pins or pins[path] == expected, ('inconsistent expected input hash', path)
        pins[path] = expected
        return path

    ordinary_path = pin(RUNS / '192-scalar-slice-objects/summary.json')
    leaf_path = pin(RUNS / '190-thiscall-declaration-delta/summary.json')
    ordinary, leaves = (json.loads(p.read_bytes()) for p in (ordinary_path, leaf_path))
    assert ordinary['original_sha256'] == leaves['original_sha256'] == SHA
    for summary in (ordinary, leaves):
        assert summary['input_sha256'], 'missing recorded closure'
        for key in ('input_sha256', 'source_sha256'):
            for name, expected in summary.get(key, {}).items():
                pin(name, expected)
    ordinary_rows = [r for r in ordinary['results'] if r.get('compiler_exit_code') == 0]
    leaf_rows = [r for r in leaves['results'] if r.get('compiled')]
    assert len(ordinary_rows) == 924 and len(leaf_rows) == 130
    assert not ({r['va'] for r in ordinary_rows} & {r['va'] for r in leaf_rows})
    rows = []
    for cohort, selected in (('ordinary192', ordinary_rows), ('thiscall190', leaf_rows)):
        for r in selected:
            source = pin(r['generated_source'], r['generated_source_sha256'])
            obj = pin(r['object'], r['object_sha256'])
            for name, expected in r.get('dependency_sha256', {}).items():
                pin(name, expected)
            for name in r.get('forced_headers', []):
                resolved = Path(name).resolve()
                assert resolved in pins, ('forced header missing from pinned closure', name)
            # Walk the actual quoted native include closure, including transitive helpers.
            pending, visited = [source], set()
            while pending:
                current = pending.pop()
                if current in visited:
                    continue
                visited.add(current)
                assert current in pins, ('native dependency absent from recorded closure', current)
                for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"', current.read_text(encoding='utf8'), re.M):
                    include = Path(name)
                    include = include.resolve() if include.is_absolute() else (current.parent / include).resolve()
                    assert include.is_file(), ('missing quoted include', include)
                    pending.append(include)
            symbols = base.coff_symbols(obj)
            expected_symbols = r.get('symbols') or dict(defined=r['defined_external_symbols'], undefined=r['undefined_external_symbols'], common=[], weak=[])
            assert symbols == expected_symbols, ('COFF symbol snapshot drift', r['va'])
            rows.append(dict(va=r['va'], cohort=cohort, object=relative(obj), object_sha256=r['object_sha256'],
                             generated_source=relative(source), generated_source_sha256=r['generated_source_sha256'],
                             include_closure=sorted(relative(p) for p in visited), symbols=symbols))
    registry_path = pin('iterations/v2/001-original-recovery/source/recovered/functions.json')
    declarations = RUNS / '179-ghidra-declarations/export'
    globals_path = pin(declarations / 'globals.jsonl')
    functions_path = pin(declarations / 'functions.jsonl')
    catalog_path = pin('research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl')
    original_path = pin('local/game/Porsche.exe', SHA)
    pin('scripts/research/audit-v2-native-union-195.py')
    pin('scripts/research/build-v2-compile-corpus.py')
    if prior195:
        pin(out/'first-parser-summary.json')
    toolroot = ROOT / 'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
    libtool, linktool = (pin(toolroot / 'bin/Hostx64/x86' / name) for name in ('lib.exe', 'link.exe'))
    assert digest(toolroot / 'bin/Hostx64/x86/cl.exe') == ordinary['compiler_sha256'] == leaves['compiler_sha256']
    libpaths = [toolroot / 'lib/x86', Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/ucrt/x86'), Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86')]
    assert all(p.is_dir() for p in libpaths)
    # Pin every library eligible for the linker search rather than relying on ambient x64 LIB.
    for folder in libpaths:
        for path in folder.glob('*.lib'):
            pin(path)

    def verify(item):
        path, expected = item
        actual = digest(path)
        return None if actual == expected else dict(path=str(path), expected=expected, actual=actual)

    def guards():
        with ThreadPoolExecutor(max_workers=8) as pool:
            errors = [r for r in pool.map(verify, pins.items()) if r]
        assert not errors, ('input mutation/hash mismatch', errors[:5])

    guards()
    print(json.dumps(dict(stage='inputs_verified', objects=len(rows), unique_pins=len(pins))), flush=True)
    definitions, refs = defaultdict(list), defaultdict(list)
    by_va = {r['va']: r for r in rows}
    for row in rows:
        for name in row['symbols']['defined'] + row['symbols']['common']:
            definitions[name].append(row['va'])
        for name in row['symbols']['undefined']:
            refs[name].append(row['va'])
    unresolved = {name: sorted(set(v)) for name, v in sorted(refs.items()) if name not in definitions}
    assert len(unresolved) == 387 and sum(map(len, unresolved.values())) == 763
    duplicates = {s:v for s,v in definitions.items() if len(v)>1}
    repeated = {}
    for name, vas in duplicates.items():
        entries = [{**comdat_evidence(ROOT/by_va[va]['object'],{name})[name], 'va':va} for va in vas]
        assert all(e['comdat'] and e['selection']==2 for e in entries), ('unexpected repeated non-select-any definition',name,entries)
        assert len({e['section_sha256'] for e in entries}) == 1, ('different compiler-constant contents',name)
        repeated[name] = entries
    env = {**os.environ, 'VSLANG':'1033', 'LIB':os.pathsep.join(map(str,libpaths)), 'LINK':'', '_LINK_':''}
    archive = out / 'porsche_native_union_candidates.lib'
    response = out / 'objects.rsp'
    response.write_text('\n'.join('"'+str(ROOT / r['object'])+'"' for r in rows)+'\n', encoding='utf8', newline='\n')

    def run_tool(command, filename):
        before = time.perf_counter()
        p = subprocess.run(command, cwd=out, capture_output=True, env=env, timeout=180)
        raw = p.stdout+p.stderr
        try:
            log = raw.decode('utf8')
        except UnicodeDecodeError:
            log = raw.decode('cp1251')
        log = log.replace('\r\n','\n')
        logpath = out / filename
        logpath.write_text(log, encoding='utf8', newline='\n')
        return dict(command=command, exit_code=p.returncode, seconds=round(time.perf_counter()-before,3), log=relative(logpath), log_sha256=digest(logpath)), log

    if prior195:
        library = prior195['library']
        assert digest(archive)==library['sha256'] and digest(ROOT/library['log'])==library['log_sha256']
    else:
        library, library_log = run_tool([str(libtool),'/nologo','/MACHINE:X86','/OUT:'+str(archive),'@'+str(response)],'library.log')
        assert library['exit_code'] == 0 and archive.is_file(), library_log
    library.update(path=relative(archive), bytes=archive.stat().st_size, sha256=digest(archive), members=len(rows))
    dll = out / 'diagnostic_union.dll'
    command = [str(linktool),'/nologo','/DLL','/NOENTRY','/MACHINE:X86','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(dll),'/WHOLEARCHIVE:'+str(archive)]
    command += ['/LIBPATH:'+str(p) for p in libpaths]
    command += ['/VERBOSE:LIB','libcmt.lib','libvcruntime.lib','libucrt.lib','kernel32.lib']
    if prior195:
        diagnostic_link = {k:prior195['diagnostic_link'][k] for k in ('command','exit_code','seconds','log','log_sha256')}
        assert diagnostic_link['command']==command
        assert digest(ROOT/diagnostic_link['log'])==diagnostic_link['log_sha256']
        link_log = (ROOT/diagnostic_link['log']).read_text(encoding='utf8')
    else:
        diagnostic_link, link_log = run_tool(command,'diagnostic-link.log')
    link_names = Counter()
    diagnostic_codes = Counter(re.findall(r'\b(LNK\d+)\b',link_log))
    for line in link_log.splitlines():
        if not re.search(r'\bLNK(?:2001|2019)\b',line):
            continue
        # VSLANG can be ignored when only Russian resources are installed.
        # Parenthesized decorated symbol is first, before the referring function.
        tail = re.split(r'\bLNK(?:2001|2019):\s*',line,maxsplit=1)[1]
        match = re.search(r'\(([_@?][^()\s]+)\)',tail)
        if match:
            name = match[1]
        else:
            known = [s for s in unresolved if re.search(r'(?<!\S)'+re.escape(s)+r'(?!\S)',tail)]
            if len(known)==1:
                name = known[0]
            else:
                # Additional CRT imports are outside the raw candidate union.
                match = re.search(r'(?<!\S)([_@?][A-Za-z0-9_@$?]+)(?![A-Za-z0-9_@$?])',tail)
                assert match, ('cannot parse localized link diagnostic',line)
                name = match[1]
        link_names[name] += 1
    assert link_names and diagnostic_link['exit_code'] != 0 and not dll.exists()
    diagnostic_link.update(dll_created=False, unresolved_symbol_names=len(link_names), diagnostic_occurrences=sum(link_names.values()),
                           unresolved_symbols=dict(sorted(link_names.items())), diagnostic_codes=dict(sorted(diagnostic_codes.items())),
                           names_outside_raw_union=sorted(set(link_names)-set(unresolved)), raw_union_names_resolved_by_platform_libraries=sorted(set(unresolved)-set(link_names)))
    registry = json.loads(registry_path.read_bytes())['functions']
    owners = defaultdict(list)
    for row in registry:
        if row['module']=='Porsche.exe':
            owners[row['entry_va'].lower()].append({k:row[k] for k in ('entry_va','source','status','calling_convention') if k in row})
    inferred = {r['entry_va']:r for r in map(json.loads,functions_path.read_text().splitlines())}
    catalog = {r['entry_va']:r for r in map(json.loads,catalog_path.read_text().splitlines())}
    globals_by_name = defaultdict(list)
    globals_by_va = defaultdict(list)
    for row in map(json.loads,globals_path.read_text().splitlines()):
        for variant in row['variants']:
            symbol = variant['symbol']
            entry = dict(identity=row['identity'], conflict=row['conflict'], symbol=symbol, consumer_vas=variant['consumer_vas'])
            globals_by_name[symbol.get('name')].append(entry)
            for node in symbol['storage_detail']['varnodes']:
                if node['space']=='ram':
                    globals_by_va[f"{int(node['offset']):08x}"].append(entry)
    original = original_path.read_bytes()
    sections = pe_sections(original)
    frontier = []
    for name, consumers in unresolved.items():
        row = dict(symbol=name, referring_object_vas=consumers, object_references=len(consumers),
                   diagnostic_link_unresolved=name in link_names, diagnostic_link_occurrences=link_names.get(name,0))
        function = re.search(r'FUN_([0-9a-fA-F]{8})',name)
        data_name = re.match(r'^\?([^@]+)@@3',name)
        if function:
            va = function[1].lower()
            compiled = by_va.get(va)
            row.update(category='function', va=va, canonical_owners=owners.get(va,[]), original_catalog=catalog.get(va),
                       inferred_signature=inferred.get(va,{}).get('inferred_signature'))
            if compiled:
                row.update(classification='compiled_VA_symbol_contract_mismatch', compiled_cohort=compiled['cohort'], available_defined_symbols=compiled['symbols']['defined'])
            elif owners.get(va):
                row.update(classification='canonical_recovered_owner_outside_candidate_union')
            else:
                row.update(classification='no_compiled_union_body_or_canonical_owner')
        elif data_name:
            stem = data_name[1]
            va_match = re.search(r'([0-9a-fA-F]{8})$',stem)
            va = va_match[1].lower() if va_match else None
            matches = globals_by_name.get(stem,[])
            kind = 'exact_HighSymbol_name' if matches else None
            if not matches and stem.startswith('_'):
                matches = globals_by_name.get(stem[1:],[])
                kind = 'printed_leading_underscore_candidate' if matches else None
            if not matches and va:
                matches = globals_by_va.get(va,[])
                kind = 'address_candidate_only' if matches else None
            row.update(category='data', printed_name=stem, va=va, classification='native_storage_definition_absent',
                       ghidra_match_kind=kind, ghidra_variants=matches,
                       observed_conflict=any(m['conflict'] for m in matches),
                       original_memory=memory_evidence(va,original,sections) if va else None,
                       boundary='Name/address matches retain inferred variants and consumers; do not prove a native owner or permit guessed storage')
        else:
            row.update(category='other',classification='platform_CRT_resolved' if name not in link_names else 'unresolved_runtime_or_printed_name_contract')
        frontier.append(row)
    counts = Counter(r['category'] for r in frontier)
    classifications = Counter(r['classification'] for r in frontier)
    assert counts == dict(function=145,data=225,other=17)
    assert all(r['diagnostic_link_unresolved'] for r in frontier if r['category'] in ('function','data')), 'platform libs must not appear to resolve Porsche-named functions/data'
    guards()
    report = dict(schema=1, module='Porsche.exe', original_sha256=SHA, objects=1054, ordinary_objects=924, thiscall_objects=130,
                  overlapping_vas=0, new_compilations=0, duplicate_non_COMDAT_definitions={}, repeated_identical_select_any_COMDAT=repeated,
                  raw_union_unresolved_names=len(unresolved),raw_union_object_references=sum(map(len,unresolved.values())),
                  categories=dict(counts),classifications=dict(classifications),library=library,diagnostic_link=diagnostic_link,
                  input_guard=dict(unique_pins=len(pins), before=True, after=True),
                  input_sha256={str(p.relative_to(ROOT)).replace('\\','/') if p.is_relative_to(ROOT) else str(p):s for p,s in sorted(pins.items(),key=lambda x:str(x[0]))},
                  objects_response=dict(path=relative(response),sha256=digest(response)), results=rows, frontier=frontier,
                  finalize_existing=bool(prior195), actual_library_commands_this_pass=0 if prior195 else 1,
                  actual_link_commands_this_pass=0 if prior195 else 1,
                  elapsed_seconds=round(time.perf_counter()-start,3),
                  limits=['Compile candidates only: no EXE, startup, original behavior or fidelity acceptance.',
                          'DLL /NOENTRY /WHOLEARCHIVE diagnostic forces all bodies; counts are not complete game dependency closure.',
                          'No source repair, ABI bridge, dummy implementation, storage allocation or accepted registry change.',
                          'Data evidence is read-only original PE/179 inference; overlapping/conflicting views remain explicit.',
                          'Historical178/181 compiler binary identity remains unproven; current tools and recorded closure are checked.'])
    write(RUN/'summary.json',report)
    write(out/'result.json',{k:v for k,v in report.items() if k not in ('input_sha256','results','frontier')})
    print(json.dumps({k:report[k] for k in ('objects','raw_union_unresolved_names','raw_union_object_references','categories','classifications','elapsed_seconds')}),flush=True)
    print(json.dumps({k:diagnostic_link[k] for k in ('exit_code','dll_created','unresolved_symbol_names','diagnostic_occurrences','diagnostic_codes','names_outside_raw_union','raw_union_names_resolved_by_platform_libraries')}),flush=True)


if __name__ == '__main__':
    main()
