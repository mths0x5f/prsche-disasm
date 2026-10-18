"""Compile the 21 PE-derived frame-loop and shutdown cluster bodies and run the physical x86 differential fixture."""
import argparse, hashlib, importlib.util, json, os, re, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/400-frame-loop-clusters'
OUT = ROOT / 'local/experiments/v2-frame-loop-clusters-400'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

SPANS = [
    ('00412030', 91, 'application_main_function_00412030'),
    ('005338d0', 53, 'frame_control_slot_release_005338d0'),
    ('00425780', 135, 'application_main_function_00425780'),
    ('004acb80', 141, 'application_main_function_004acb80'),
    ('00565d60', 106, 'audio_channel_stop_00565d60'),
    ('00414eb0', 196, 'application_main_function_00414eb0'),
    ('00467740', 141, 'application_main_function_00467740'),
    ('004b7140', 16, 'render_teardown_prefix_004b7140'),
    ('00465e20', 29, 'render_teardown_secondary_00465e20'),
    ('00538d80', 20, 'destroy_00538d80'),
    ('00539eb0', 14, 'release_00539eb0'),
    ('00540420', 24, 'destroy_00540420'),
    ('0047f190', 119, 'render_teardown_registry_0047f190'),
    ('00514990', 1, 'render_registry_item_noop_00514990'),
    ('00563d30', 222, 'application_main_function_00563d30'),
    ('00564700', 70, 'stream_slot_cancel_00564700'),
    ('00564750', 61, 'stream_slot_resolve_00564750'),
    ('00563bd0', 93, 'stream_completion_pump_00563bd0'),
    ('00563c70', 68, 'stream_queue_pop_00563c70'),
    ('00563c30', 64, 'stream_queue_push_00563c30'),
    ('00563cc0', 105, 'stream_slot_finalize_00563cc0'),
]
VAS = [va for va, _, _ in SPANS]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rel(p):
    p = Path(p).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()

def write(p, v):
    p.write_bytes((json.dumps(v, indent=2, ensure_ascii=False) + '\n').encode('utf8'))

def module(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def resolve_compiler(baseline):
    cand = Path(baseline['compiler_command'][0])
    if cand.exists():
        return cand, baseline['compiler_sha256']
    local_cl = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x86/cl.exe')
    assert local_cl.exists(), f'Compiler not found: {cand} or {local_cl}'
    return local_cl, sha(local_cl)

def resolve_roots(baseline, compiler):
    roots = []
    for x in baseline['results'][0]['include_directories']:
        p = (ROOT / x).resolve() if not Path(x).is_absolute() else Path(x)
        if not p.is_dir() and 'MSVC' in str(x):
            p = (compiler.parents[3] / 'include').resolve()
        roots.append(p)
    roots.append(RUN)
    assert len(roots) == 6 and all(x.is_dir() for x in roots), roots
    return roots

def main(finalize, attempt):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'objects').mkdir(exist_ok=True)
    (OUT / 'dependencies').mkdir(exist_ok=True)
    suffix = f'{attempt:03d}'
    compile_name = 'compile-' + suffix
    link_name = 'fixture-link-' + suffix
    native_name = 'fixture-native-' + suffix
    if not finalize:
        assert not (OUT / (compile_name + '.execution.json')).exists()
    pins = {}

    def pin(p, expected=None):
        p = Path(p).resolve()
        h = sha(p)
        assert expected is None or h == expected, (p, h, expected)
        pins[p] = h
        return p

    def guard():
        assert all(sha(p) == h for p, h in pins.items()), 'input drift'

    def run(cmd, name):
        cmd = list(map(str, cmd))
        started = time.perf_counter()
        process = subprocess.run(
            cmd,
            cwd=OUT,
            env={**os.environ, 'VSLANG': '1033', 'CL': '', '_CL_': '', 'INCLUDE': ''},
            capture_output=True,
            timeout=120,
        )
        log = OUT / (name + '.log')
        log.write_bytes((process.stdout + process.stderr).replace(b'\r\n', b'\n'))
        receipt = dict(
            command=cmd,
            exit_code=process.returncode,
            seconds=round(time.perf_counter() - started, 6),
            log=rel(log),
            log_sha256=sha(log),
        )
        write(OUT / (name + '.execution.json'), receipt)
        return receipt

    baseline = json.loads(pin(ROOT / 'iterations/v2/001-original-recovery/runs/276-file-operation-reuse/summary.json').read_bytes())
    original = pin(ROOT / 'local/game/Porsche.exe', SHA)
    for p in [
        __file__,
        ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',
        ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json',
        ROOT / 'iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json',
        RUN / 'frame_loop_clusters_400.hpp',
        RUN / 'bridge-sources-400.cmake',
    ]:
        pin(p)

    union = json.loads((ROOT / 'iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json').read_bytes())
    if (ROOT / union['objects_response']['path']).exists() and (ROOT / union['library']['path']).exists():
        union_rsp = pin(ROOT / union['objects_response']['path'], union['objects_response']['sha256'])
        union_lib = pin(ROOT / union['library']['path'], union['library']['sha256'])
        assert all(v not in union_rsp.read_text() and v.encode() not in union_lib.read_bytes() for v in VAS)

    registry = json.loads((ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    assert all(x['entry_va'] not in VAS for x in registry)

    index = {x['entry_va']: x['body_bytes'] for x in map(json.loads, (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
    assert [(va, index[va]) for va in VAS] == [(va, sz) for va, sz, _ in SPANS]
    assert sum(sz for _, sz, _ in SPANS) == 1769

    sources = [pin(RUN / (va + '.cpp')) for va in VAS]
    fixture = pin(OUT / 'frame_loop_fixture.cpp')
    compiler_path, compiler_expected_sha = resolve_compiler(baseline)
    compiler = pin(compiler_path, compiler_expected_sha)
    linker = pin(compiler.with_name('link.exe'))
    kernel = pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    roots = resolve_roots(baseline, compiler)

    flags = [
        '/nologo', '/c', '/std:c++17', '/Od', '/Oi', '/Gy', '/GS-', '/GR-',
        '/EHsc', '/TP', '/W4', '/utf-8', '/diagnostics:column', '/MP6', '/Zl',
        '/sourceDependencies', str(OUT / 'dependencies'),
    ]
    command = [
        compiler, *flags,
        *[item for root in roots for item in ('/I', root)],
        '/Fo' + str(OUT / 'objects') + os.sep,
        *sources, fixture,
    ]

    if finalize:
        prepared = json.loads(pin(OUT / ('prepare-' + suffix + '.json')).read_bytes())
        for name, h in prepared['input_sha256'].items():
            pin(ROOT / name if not Path(name).is_absolute() else Path(name), h)
        compiled = json.loads(pin(OUT / (compile_name + '.execution.json')).read_bytes())
        assert compiled['command'] == list(map(str, command))
    else:
        guard()
        write(OUT / ('prepare-' + suffix + '.json'), dict(command=list(map(str, command)), input_sha256={rel(p): h for p, h in pins.items()}))
        compiled = run(command, compile_name)

    assert compiled['exit_code'] == 0, (OUT / (compile_name + '.log')).read_text(errors='replace')
    assert not re.search(rb'warning [CD]\d+|error [CD]\d+', (OUT / (compile_name + '.log')).read_bytes()), (OUT / (compile_name + '.log')).read_text(errors='replace')

    for src in [*sources, fixture]:
        dep = pin(OUT / 'dependencies' / (src.name + '.json'))
        data = json.loads(dep.read_bytes())
        assert Path(data['Data']['Source']).resolve() == src
        for x in data['Data']['Includes']:
            include = Path(x).resolve()
            assert any(include.is_relative_to(root) for root in roots), include
            pin(include)

    coff = module('coff400', ROOT / 'scripts/research/build-v2-compile-corpus.py')
    objects = [pin(OUT / 'objects' / (src.stem + '.obj')) for src in [*sources, fixture]]
    views = [coff.coff_symbols(obj) for obj in objects]
    assert all(not v['common'] and not v['weak'] for v in views[:len(SPANS)])
    for idx, (va, _, sym_sub) in enumerate(SPANS):
        assert any(sym_sub in s for s in views[idx]['defined']), (va, sym_sub, views[idx]['defined'])

    exe = OUT / 'native-fixture.exe'
    mapfile = OUT / 'native-fixture.map'
    link = [
        linker, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/ENTRY:entry',
        '/NODEFAULTLIB', '/INCREMENTAL:NO', '/OPT:NOREF',
        '/OUT:' + str(exe), '/MAP:' + str(mapfile),
        *objects, kernel,
    ]
    if finalize and (OUT / (link_name + '.execution.json')).exists():
        linked = json.loads(pin(OUT / (link_name + '.execution.json')).read_bytes())
    else:
        linked = run(link, link_name)
    assert linked['exit_code'] == 0, (OUT / (link_name + '.log')).read_text(errors='replace')

    if finalize and (OUT / (native_name + '.execution.json')).exists():
        native = json.loads(pin(OUT / (native_name + '.execution.json')).read_bytes())
    else:
        native = run([exe], native_name)
    assert native['exit_code'] == 0, (OUT / (native_name + '.log')).read_text(errors='replace')

    for p in [exe, mapfile, *OUT.glob('*.log'), *OUT.glob('*.execution.json')]:
        pin(p)
    guard()

    results = []
    for (va, sz, _), src, obj, view in zip(SPANS, sources, objects[:len(SPANS)], views[:len(SPANS)]):
        results.append(dict(
            va=va,
            body_bytes=sz,
            generated_source=rel(src),
            generated_source_sha256=sha(src),
            object=rel(obj),
            object_sha256=sha(obj),
            symbols=view,
            compiler_command=list(map(str, command)),
            compiler_execution_receipt=rel(OUT / (compile_name + '.execution.json')),
            include_directories=[rel(x) for x in roots],
            source_dependencies=rel(OUT / 'dependencies' / (src.name + '.json')),
            source_dependencies_sha256=sha(OUT / 'dependencies' / (src.name + '.json')),
            compiled=True,
            compiler_exit_code=0,
            actual_i386_coff_validated=True,
        ))

    summary = dict(
        schema=1,
        kind='original-frame-loop-and-shutdown-clusters',
        module='Porsche.exe',
        original_sha256=SHA,
        original_vas=VAS,
        original_selected_bytes=1769,
        new_distinct_function_VAs=21,
        objects_compiled=21,
        real_coff_objects=21,
        results=results,
        game_objects=[dict(path=rel(o), sha256=sha(o)) for o in objects[:len(SPANS)]],
        compiler_sha256=sha(compiler),
        compiler_batch_exit_code=0,
        actual_compiler_batches=attempt,
        actual_MP6_requested=True,
        compile_seconds=compiled['seconds'],
        compiler_command=list(map(str, command)),
        compiler_execution_receipt=rel(OUT / (compile_name + '.execution.json')),
        native_fixture=dict(
            executable=rel(exe),
            sha256=sha(exe),
            exit_code=native['exit_code'],
            seconds=native['seconds'],
            case_count=34,
            clusters=6,
        ),
        sourceDependencies_format='MSVC1.2',
        input_sha256={rel(p): h for p, h in pins.items()},
        input_guards_before=True,
        input_guards_after=True,
        production_ready=False,
        limits=[
            'External leaf callees and unrecovered global storage owners remain explicit extern boundaries',
            'Fixture providers and executable PE slab harness are excluded from game_objects',
            'No full game startup or interactive frame loop execution is claimed',
        ],
    )
    write(RUN / 'summary.json', summary)
    print(json.dumps(dict(compile=compiled['exit_code'], native=native['exit_code'], cases=34, game_objects=21, bytes=1769)))

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--finalize-existing', action='store_true')
    a.add_argument('--attempt', type=int, default=1)
    args = a.parse_args()
    main(args.finalize_existing, args.attempt)
