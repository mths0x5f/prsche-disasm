"""Compare real C++ fill dispatch and all backends with the complete PE chain."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import traceback

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'iterations/v2/001-original-recovery/runs'
RUN = RUNS / '321-simd-fill-game-integration'
OUT = ROOT / 'local/experiments/v2-fill-chain-321'
spec = importlib.util.spec_from_file_location('native317', ROOT / 'scripts/research/verify-v2-scalar-fill-317.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
sha, write, pe_body = helpers.sha, helpers.write, helpers.pe_body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'\d{3}', args.attempt)
    work = OUT / ('attempt-' + args.attempt)
    work.mkdir(parents=True, exist_ok=False)
    receipt = dict(schema=1, attempt=args.attempt, status='started', commands=[])
    try:
        def run(argv, name):
            value = subprocess.run(list(map(str, argv)), cwd=work, capture_output=True, text=True, timeout=90)
            log = work / (name + '.log')
            write(log, value.stdout + value.stderr)
            receipt['commands'].append(dict(argv=list(map(str, argv)), exit_code=value.returncode,
                                            log=log.name, log_sha256=sha(log)))
            if value.returncode:
                raise RuntimeError(f'{name}: exit {value.returncode}; see {log}')
            return value.stdout

        pe = ROOT / 'local/game/Porsche.exe'
        assert sha(pe) == helpers.PE_SHA
        image = pe.read_bytes()
        generated = '#pragma once\n'
        original = {}
        for name, address, size in [('dispatcher', 0x53c290, 77), ('scalar', 0x5b0980, 186),
                                    ('mmx', 0x5b0a40, 176), ('sse', 0x5b0b00, 242)]:
            body = pe_body(image, address, size)
            path = work / (name + '.bin')
            path.write_bytes(body)
            original[path.name] = sha(path)
            generated += 'static const unsigned char ' + name + '_bytes[]={' + ','.join(map(str, body)) + '};\n'
        write(work / 'original_bodies.hpp', generated)
        sources = [RUNS / '312-pr7-fill-dispatch/0053c290.cpp', RUNS / '317-scalar-fill-backend/005b0980.cpp',
                   RUNS / '319-mmx-fill-backend/005b0a40.cpp', RUNS / '320-sse-fill-backend/005b0b00.cpp',
                   ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/shared_runtime_globals.cpp',
                   RUN / 'fill_chain_fixture.cpp']
        vc, sdk = helpers.VC, helpers.SDK
        tools = [vc / 'bin/Hostx64/x86' / (name + '.exe') for name in ('cl', 'link', 'dumpbin')]
        includes = [work, RUNS / '312-pr7-fill-dispatch', ROOT / 'iterations/v2/001-original-recovery/source/include',
                    vc / 'include', *[sdk / 'Include/10.0.26100.0' / name for name in ('ucrt', 'shared', 'um')]]
        quoted = set()
        for source in sources:
            helpers.quoted_inputs(source.resolve(), includes, quoted)
        quoted.update({Path(__file__).resolve(), Path(helpers.__file__).resolve(), pe})
        receipt['inputs_sha256'] = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(quoted)}
        receipt['inputs_sha256'].update(original)
        receipt['tools_sha256'] = {p.relative_to(ROOT).as_posix(): sha(p) for p in tools}
        libraries = [vc / 'lib/x86/libcmt.lib', vc / 'lib/x86/libvcruntime.lib',
                     sdk / 'Lib/10.0.26100.0/ucrt/x86/libucrt.lib', sdk / 'Lib/10.0.26100.0/um/x86/kernel32.lib']
        receipt['link_libraries_sha256'] = {str(p): sha(p) for p in libraries}
        run([tools[0], '/nologo', '/c', '/std:c++17', '/Od', '/Oy-', '/MT', '/GS-', '/EHsc', '/TP', '/W4',
             '/utf-8', *['/I' + str(p) for p in includes], '/Fo' + str(work) + '\\', *sources], 'compile')
        objects = [work / (p.stem + '.obj') for p in sources]
        receipt['objects_sha256'] = {p.name: sha(p) for p in objects}
        for stem in ('0053c290', '005b0980', '005b0a40', '005b0b00'):
            run([tools[2], '/symbols', work / (stem + '.obj')], 'symbols-' + stem)
        exe = work / 'fixture.exe'
        run([tools[1], '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/NODEFAULTLIB',
             '/OUT:' + str(exe), *objects, *libraries], 'link')
        receipt['exe_sha256'] = sha(exe)
        output = run([exe], 'native')
        match = re.fullmatch(r'cases=(\d+) checks=(\d+) failures=(\d+)\s*', output)
        assert match and int(match[1]) == 27648 and int(match[3]) == 0, output
        receipt.update(status='pass', native_cases_passed=int(match[1]), native_checks=int(match[2]),
                       scope='4 flag masks, 32 offsets, 36 lengths 0..4097, 3 DWORD patterns, 2 x87 seeds; actual chain')
        for name, expected in receipt['inputs_sha256'].items():
            path = ROOT / name
            if not path.exists():
                path = work / name
            assert sha(path) == expected, 'Input changed during fixture: ' + name
    except Exception as error:
        receipt.update(status='fail', error=str(error))
        write(work / 'error.log', traceback.format_exc())
    finally:
        write(work / 'receipt.json', json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({k: receipt[k] for k in ('status', 'attempt')}, ensure_ascii=True))
        print(work / 'receipt.json')
    if receipt['status'] != 'pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
