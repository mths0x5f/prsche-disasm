"""Read-only actual332 COFF/proof triage; no compile/link/native process."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/337-game-frontier-triage'
R=ROOT/'iterations/v2/001-original-recovery/runs'
def read(p):return json.loads(p.read_text())
def sha(p,normalized=False):
    b=p.read_bytes();return hashlib.sha256(b.replace(b'\r\n',b'\n') if normalized else b).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(p):pins[rel(p)]=sha(p);return p
    pin(Path(__file__).resolve());build=read(pin(R/'332-resource-chain-game-integration/build-001.json'))
    frontier={x['symbol']:x for x in build['frontier']}
    assert (len(frontier),sum(len(x['references']) for x in frontier.values()))==(261,286)
    parser=pin(ROOT/'scripts/research/build-v2-compile-corpus.py')
    spec=importlib.util.spec_from_file_location('coff337',parser);coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    objects={rel(pin(p)):coff.coff_symbols(p) for p in (ROOT/'local/builds/v2/resource-chain-game-integration-332').rglob('*.obj')}
    definitions={s for v in objects.values() for s in v['defined']}
    index=pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl')
    functions={x['entry_va']:x for x in map(json.loads,index.read_text().splitlines())}
    listing=pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    pin(ROOT/'research/binary-index/README.md');pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')
    def candidate(rank,filename,symbols,targets,proofpath,status,next_step,holds):
        source=pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'/filename)
        path=pin(R/proofpath);proof=read(path);matches=0
        for name,expected in proof['source_sha256'].items():
            assert sha(pin(ROOT/name),True)==expected,f'proof input drift:{name}'
            matches+=1
        views={p:v for p,v in objects.items() if Path(p).stem==source.stem}
        assert len(views)==1
        view=next(iter(views.values()))
        assert set(targets)<=set(view['defined'])
        assert all(s in frontier for s in symbols)
        vas=sorted({va for s in targets for va in re.findall(r'_([0-9a-f]{8})@',s)})
        return dict(rank=rank,source=rel(source),source_sha256=sha(source),status=status,missing_symbols=symbols,canonical_symbols=targets,closed_names_if_bound=len(symbols),closed_references_if_bound=sum(len(frontier[s]['references']) for s in symbols),new_names_if_bound=[],actual_objects=views,object_undefined_without_current_provider=sorted(set(view['undefined'])-definitions),proof=dict(path=rel(path),sha256=sha(path),native_cases=proof['cases'],current_normalized_pins=matches,native_equal=proof['native_cpp_equal_original_x86']),indexed_entries={va:functions.get(va) for va in vas},next_step=next_step,holds=holds)
    candidates=[
      candidate(1,'formatter_search.cpp',['?compare_005ae3c0@porsche@@YAHPBD0@Z','?render_settings_read_config_005a1e10@porsche@@YAHPADPBD@Z'],['?formatter_search_compare_005ae3c0@porsche@@YAHPBD0@Z','?formatter_search_substring_005a1e10@porsche@@YAPBDPBD0@Z'],'172-formatter-search/production-verification.json','READY bounded ABI-binding packet; canonical whole-TU closure already complete','Add two transport-only bridges; preserve substring pointer bits in int32 EAX and verify transport without rerunning9374 cases.',['Existing locale/EOF domain holds remain; this is not a new algorithm.']),
      candidate(2,'timer_setup.cpp',['?startup_capacity_00565030@porsche@@YAXI@Z'],['?timer_setup_00565030@porsche@@YAXI@Z'],'173-float-transport-integration/formatter-timer-integration/timer-setup/verification.json','MECHANICAL alias candidate; existing diagnostic boundary remains','Typed cdecl void(uint32) forwarding is a bounded follow-up; verify original004a5444 argument0x80 and bridge transport.',['timer_diagnostic_boundary is already unresolved; live asynchronous scheduling is not accepted.']),
      candidate(3,'context_effects.cpp',['?game_setup_movie_delta_004237d0@porsche@@YAXPAXII@Z'],['?application_context_clear_004237d0@porsche@@YAXPAXII@Z'],'143-runtime-network-integration/context-effects/verification.json','MECHANICAL alias candidate; context state HOLD retained','Use exact void(void*,uint32,uint32) forwarding only after bounded argument/ABI review.',['application_context_heap_state005e4fe8 and context_selector_pointer005e4fec have no current provider; do not invent them.']),
      candidate(4,'formatter_text.cpp',['?startup_drive_character_005a2c24@porsche@@YAHH@Z'],['?formatter_text_alpha_005a2c24@porsche@@YAHH@Z'],'169-vtable-output-integration/formatter-text/verification.json','NOT READY for full caller domain','Resolve initial ctype EOF/negative-input storage before admitting signed filename bytes from004a5c30.',['Run236 initial ctype predecessor storage gap remains; startup caller sign-extends filename[0].'])
    ]
    # Exact stdio names exist, but raw format VAs are not native pointers.
    stdio=next((p,v) for p,v in objects.items() if Path(p).name=='formatter_stdio.obj')
    candidates.append(dict(rank=5,source='iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_stdio.cpp',status='NOT READY: format-address relocation and ABI adapter proof required',missing_symbols=['?startup_sequence_report_005a177b@porsche@@YAXII@Z','?render_display_texture_report_005a177b@porsche@@YAXPBDI@Z'],canonical_symbols=['?formatter_stdio_printf_005a177b@porsche@@YAHPBDZZ'],closed_names_if_bound=2,closed_references_if_bound=3,actual_object=stdio[0],object_undefined_without_current_provider=sorted(set(stdio[1]['undefined'])-definitions),holds=['Startup consumers pass original005d6e3c/005d1400 integers. A raw pointer cast would not relocate those literals.','Void fixed-argument views versus variadic int return require an explicit transport proof.','No new behavioral/native acceptance is established by this triage.']))
    compiled=set(build['compiled_source_roots'])
    outside=[rel(pin(p)) for p in (ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe').glob('*.cpp') if rel(p) not in compiled]
    corpus=read(pin(R/'274-shared-heap-union/summary.json'))
    rejects=[dict(symbol='input_negative_index00532e10/input_unmapped_index00532e10',reason='These are explicit outside-storage-domain seams inside fe_input_getstate00532e10; aliasing to the same function recurses and does not recover adjacent storage.'),dict(symbol='resource_invalid_module_path0059d650',reason='Error boundary inside same-VA resource_paths function; self-alias would recurse.'),dict(symbol='render_event_invoke_callback005debec',reason='Same VA is a mutable callback-pointer data cell, not an implementation entry.'),dict(symbol='network_group_text005e8e50',reason='Multiple same-VA storage views already exist; shared extent/identity is unresolved. Do not select a name by address alone.')]
    windows=[]
    for line in listing.read_text().splitlines():
        m=re.match(r'^([0-9a-f]{8})  ',line)
        if m and any(a<=int(m[1],16)<=b for a,b in [(0x44eab3,0x44eac8),(0x44eb0d,0x44eb1d),(0x4a543f,0x4a544e)]):windows.append(line)
    for path,h in pins.items():assert sha(ROOT/path)==h,f'input drift:{path}'
    result=dict(schema=1,run=337,status='read-only-triage-complete',baseline=dict(run=332,names=261,references=286,compiled_sources=171,objects_read=len(objects)),candidates=candidates,uncompiled_canonical_sources=outside,uncompiled_source_decision='No whole-TU mechanical intake matching330 remains: audio init/context destructor/context candidate/RTTI each retain explicit holds.',rejected_same_va_shortcuts=rejects,original_caller_windows=windows,corpus274=dict(objects=corpus['objects'],limits=corpus['limits'],decision='Existing raw compile-candidate corpus is not native acceptance; no corpus compile or raw-body import performed.'),inputs_sha256=pins,subprocesses=0,native_rerun=False,game_graph_modified=False)
    write(RUN/'summary.json',result)
    write(RUN/'validation.json',dict(status='PASS',baseline_names=261,baseline_references=286,candidate_count=5,existing_proof_pins_current=True,no_compile_link_native=True))
    print('Run337 PASS:5 ranked modules; search2 names fully closed dependencies; timer/context retain existing boundaries; ctype/stdio not ready.')
if __name__=='__main__':main()
