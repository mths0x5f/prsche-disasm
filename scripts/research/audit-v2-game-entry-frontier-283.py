"""Read-only cached normal-entry link feasibility; no compiler/linker/Ghidra."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/283-game-entry-frontier'
OUT=ROOT/'local/experiments/v2-game-entry-frontier-283'
BUILD=ROOT/'local/builds/v2/original-game-link-098'
REPORT=ROOT/'iterations/v2/001-original-recovery/runs/173-float-transport-integration/original-game-link/link-report.json'
NAMES={'porsche_original.lib','porsche_recovered_links.lib','porsche_window_links.lib','win32_window_bindings.lib','porsche_platform_win32.lib'}
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def archive_members(data):
    assert data[:8]==b'!<arch>\n';p=8;count=0
    while p<len(data):
        h=data[p:p+60];assert len(h)==60 and h[58:60]==b'`\n'
        size=int(h[48:58]);name=h[:16].strip();assert p+60+size<=len(data)
        if name not in (b'/',b'//',b'/SYM64/'):count+=1
        p+=60+size+(size&1)
    assert p==len(data);return count


def directives(path):
    data=Path(path).read_bytes();count=int.from_bytes(data[2:4],'little');out=[]
    for i in range(count):
        p=20+i*40
        if data[p:p+8].rstrip(b'\0')==b'.drectve':
            size=int.from_bytes(data[p+16:p+20],'little');offset=int.from_bytes(data[p+20:p+24],'little');out.append(data[offset:offset+size].decode('ascii'))
    return out


def main():
    assert not(RUN/'summary.json').exists(),'completed283 immutable'
    RUN.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);pins={}
    def pin(p,expected=None):
        p=Path(p).resolve();h=digest(p);assert expected is None or h==expected,('pin',p);pins[relative(p)]=h;return p
    graph=module('graph283','scripts/research/v2_build_graph.py');coff=module('coff283','scripts/research/build-v2-compile-corpus.py')
    for p in [__file__,ROOT/'scripts/research/v2_build_graph.py',ROOT/'scripts/research/build-v2-compile-corpus.py',
              ROOT/'scripts/research/verify-v2-original-game-link.py',ROOT/'iterations/v2/001-original-recovery/CMakeLists.txt',
              ROOT/'iterations/v2/001-original-recovery/source/recovered/sources.cmake',
              ROOT/'iterations/v2/001-original-recovery/runs/102-original-game-link/CMakeLists.txt',
              ROOT/'iterations/v2/001-original-recovery/runs/102-original-game-link/host-entry.cpp',BUILD/'CMakeCache.txt']:
        pin(p)
    report=load(pin(REPORT));pin(ROOT/report['raw_log'],report['raw_log_sha256'])
    assert report['unresolved_symbol_count']==267 and report['unresolved_reference_count']==303 and report['game_executable_executed'] is False
    source_matches=[];source_drift=[]
    for name,h in report['source_sha256'].items():
        path=ROOT/name;actual=digest(pin(path));(source_matches if h==actual else source_drift).append(name)
    projects=graph.projects(BUILD,'porsche_original_game_link');compiled=graph.compiled_sources(BUILD,'porsche_original_game_link')
    assert len(compiled)==146
    ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};project_rows=[]
    for project in projects:
        pin(project);xml=ET.parse(project);sources=[e.get('Include') for e in xml.iter() if e.tag.endswith('}ClCompile') and e.get('Include')]
        project_rows.append(dict(project=relative(project),compile_roots=len(sources),references=[relative(project.parent/e.get('Include')) for e in xml.iter() if e.tag.endswith('}ProjectReference') and e.get('Include')]))
    target=ET.parse(BUILD/'porsche_original_game_link.vcxproj')
    group=next(g for g in target.findall('m:ItemDefinitionGroup',ns) if "=='Release|Win32'" in g.get('Condition',''))
    release_link={e.tag.split('}')[-1]:e.text for e in group.find('m:Link',ns)}
    deps=release_link['AdditionalDependencies'].split(';');libs=[BUILD/Path(v) for v in deps if v.startswith('common')]
    assert len(libs)==5 and all(p.is_file() for p in libs) and release_link['SubSystem']=='Windows'
    assert not any('WHOLEARCHIVE' in str(v).upper() or 'NOENTRY' in str(v).upper() for v in release_link.values())
    host=BUILD/'porsche_original_game_link.dir/Release/host-entry.obj'
    roots=[]
    for path in [host,BUILD/'common/porsche_original.dir/Release/startup.obj',BUILD/'common/porsche_original.dir/Release/application_main.obj']:
        pin(path);roots.append(dict(object=relative(path),sha256=digest(path),symbols=coff.coff_symbols(path),directives=directives(path)))
    assert roots[0]['symbols']['defined']==['_WinMain@16'] and roots[0]['symbols']['undefined']==['?win_main_004b6710@porsche@@YGHPAX0PADH@Z']
    assert '?win_main_004b6710@porsche@@YGHPAX0PADH@Z' in roots[1]['symbols']['defined']
    assert '?app_main_004b6a50@porsche@@YAHHPAPAD@Z' in roots[1]['symbols']['undefined'] and '?app_main_004b6a50@porsche@@YAHHPAPAD@Z' in roots[2]['symbols']['defined']
    # File inventory only, nineteen matching libraries; no recursive content hash.
    names=subprocess.check_output(['rg','--files','--no-ignore','local/builds/v2'],cwd=ROOT,text=True).splitlines()
    cache=[]
    for name in names:
        p=ROOT/name
        if p.name not in NAMES:continue
        pin(p);data=p.read_bytes();cache.append(dict(path=relative(p),name=p.name,bytes=len(data),members=archive_members(data),sha256=digest(p),
             mtime_utc=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()))
    selected=[]
    for p in libs:
        row=next(r for r in cache if r['path']==relative(p));newest=max((r for r in cache if r['name']==p.name),key=lambda r:r['mtime_utc'])
        selected.append(dict(**row,newest_available_by_mtime=row['path']==newest['path'],newest_path=newest['path']))
    write(OUT/'library-cache-inventory.json',cache);pin(OUT/'library-cache-inventory.json')
    proposal=load(pin(OUT/'entry-link-proposal.json'));pin(OUT/'entry-link-proposal.rsp')
    assert proposal['executed'] is False and Path(proposal['linker']).is_file();pin(proposal['linker'])
    assert not any(v.upper().startswith(('/WHOLEARCHIVE','/NOENTRY','/ENTRY:')) for v in proposal['args'])
    assert [Path(v) for v in proposal['args'] if v.endswith('.obj')]==[host]
    assert all(str(p) in proposal['args'] for p in libs)
    union_path=ROOT/'iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json';union=load(pin(union_path))
    entry_vas=['005a2d1a','005a2441','005a0f45','004035e0','004b6710','004b6a50']
    assert not any(r.get('va') in entry_vas for r in union['results'])
    audit284=pin(ROOT/'iterations/v2/001-original-recovery/runs/284-original-entry-audit/summary.json','89c1c5604dadcdb53e2c07672e21b7d4211c1fab598c7d763b85e45a66491f09')
    main_symbol='?app_main_004b6a50@porsche@@YAHHPAPAD@Z'
    direct=[r['symbol'] for r in report['unresolved_frontier'] if any(x['caller']==main_symbol for x in r['references'])]
    members={}
    for r in report['unresolved_frontier']:
        for ref in r['references']:
            members.setdefault(ref['object'],set()).add(r['symbol'])
    assert len(members)==58 and len(direct)==20
    for name,h in pins.items():assert digest(ROOT/name)==h,('input drift',name)
    summary=dict(schema=1,kind='read-only-game-entry-link-frontier',target='porsche_original_game_link',build_tree=relative(BUILD),
      target_definition='iterations/v2/001-original-recovery/runs/102-original-game-link/CMakeLists.txt',
      target_host='iterations/v2/001-original-recovery/runs/102-original-game-link/host-entry.cpp',
      normal_CMake_command=['cmake','--build',relative(BUILD),'--target','porsche_original_game_link','--config','Release'],
      project_graph=project_rows,compiled_source_roots=146,release_link=release_link,normal_entry_coff_chain=roots,
      libraries=selected,library_cache_variants=cache,source_report173_matching_pins=len(source_matches),source_report173_drift=source_drift,
      recorded_entry_link=dict(report=relative(REPORT),raw_log=report['raw_log'],unresolved_names=267,unresolved_references=303,
        diagnostic_archive_members=58,member_unresolved_counts=[dict(member=k,unresolved_names=len(v)) for k,v in sorted(members.items())],
        direct_app_main_missing_symbols=direct,game_executable_executed=False),
      comparison274=dict(unresolved_names=414,mode='DLL NOENTRY WHOLEARCHIVE',entry_VAs_present=[],not_same_dependency_root=True),
      original_entry_audit=relative(audit284),original_PE_entry='005a2d1a',host_bypasses_original_pre_WinMain_initializers=True,
      original_startup_blocks=['005a940c environmentcopy','005a91bf','005a9106','005a2441 constructorwalker','005a0f45 initialcallback','004035e0 firstconstructor'],
      feasible_next_step=dict(kind='cached normal-entry diagnostic replay, not current1125union or faithfulgame launch',
        response_file=relative(OUT/'entry-link-proposal.rsp'),command=[proposal['linker'],'@'+proposal['rsp']],
        change_output_to_new_owned_run=True,compilation_required=False,linker_execution_here=False,
        note='RSP derives actualReleaseproject dependencies; adds explicitOPTREF/ICF andVERBOSELIB andnewOUT/MAP. No capturedhistorical linkercommand is available (tlog empty).'),
      runtime_blocks=['Originalpre-WinMain callback/constructortable state/order missing; modernMSVCCRT startup is not a proof of originalinitialization.',
        '267entry-induced unresolved canonical contracts remain, including20fromapp_main; rawcandidatearchive uses differentnames/ABI and contains no entry chain.',
        'Firstreal nativeexecution needs original constructors/sharedstate/resource/render/provider contracts; no PE-byte fallback or fakebootstrap is authorized.'],
      map_file_bytes=(BUILD/'porsche_original_game_link.map').stat().st_size,game_executable_present=(BUILD/'bin/Release/porsche_original_game_link.exe').exists(),
      compiler_commands=0,linker_commands=0,native_game_execution_commands=0,source_or_index_modified=False,input_sha256=pins,before_after_guards=True)
    write(RUN/'summary.json',summary)
    write(RUN/'validation.json',dict(passed=True,summary_sha256=digest(RUN/'summary.json'),input_pins=len(pins),projects=len(projects),source_roots=146,
          cached_libraries=len(selected),cache_variants=len(cache),actual_entry_coff_symbols=True,recorded_entry_frontier267=True,
          recorded_members58=True,compiler_commands=0,linker_commands=0,native_game_execution_commands=0))
    print(json.dumps(dict(libraries=[{k:r[k] for k in ['path','bytes','members','mtime_utc','newest_available_by_mtime']} for r in selected],
      source_drift=len(source_drift),pins=len(pins),entry_frontier=267,diagnostic_members=58,executed=False)))


if __name__=='__main__':main()
