"""Config-driven x86 ABI transport proof for aliases to previously proved bodies."""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path, normalized=False):
    data = Path(path).read_bytes()
    return hashlib.sha256(data.replace(b'\r\n', b'\n') if normalized else data).hexdigest()


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--attempt', type=int, required=True)
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    config_path = args.config.resolve()
    cfg = load(config_path)
    source, header, fixture = (ROOT / cfg[key] for key in ('source', 'header', 'fixture'))
    out = ROOT / cfg['experiment'] / f'{args.attempt:03d}'
    assert not out.exists(), f'immutable attempt: {out}'
    out.mkdir(parents=True)
    (out / 'dependencies').mkdir()
    pins = {}

    def pin(path):
        path = Path(path).resolve()
        value = sha(path)
        assert path not in pins or pins[path] == value, f'input drift: {path}'
        pins[path] = value
        return path

    def guard():
        for path, value in pins.items():
            assert sha(path) == value, f'input drift: {path}'

    for path in (Path(__file__), config_path, source, header, fixture):
        pin(path)
    pe = pin(ROOT / 'local/game/Porsche.exe')
    assert sha(pe) == 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
    coff = module('abi_coff', pin(ROOT / 'scripts/research/build-v2-compile-corpus.py'))
    provenance = module('abi_provenance', pin(ROOT / 'scripts/research/audio_recovery_provenance.py'))
    utility = module('abi_pe', pin(ROOT / 'scripts/research/verify-v2-pr9-resource-313.py'))
    original = pe.read_bytes()
    proofs = []
    for entry in cfg['proofs']:
        path = pin(ROOT / entry['path'])
        proof = load(path)
        assert proof['native_cpp_equal_original_x86'] and proof['cases'] == entry['cases']
        assert proof['sha256'] == sha(pe)
        for name, value in proof['source_sha256'].items():
            assert sha(pin(ROOT / name), True) == value, f'old proof drift: {name}'
        regions = [region for body in proof.get('original_body_pins', [])
                   if body['entry_va'] == entry['entry_va'] for region in body['ranges']]
        assert regions or not proof.get('original_body_pins'), entry['entry_va']
        for region in regions:
            assert hashlib.sha256(utility.pe_at(original, int(region['start_va'], 16),
                                                  region['bytes'])).hexdigest() == region['sha256']
        proofs.append({'path': rel(path), 'sha256': sha(path), 'cases': proof['cases'],
                       'source_pins': len(proof['source_sha256']), 'entry_va': entry['entry_va'],
                       'body_regions_rechecked': len(regions), 'rerun': False})
    triage = pin(ROOT / 'iterations/v2/001-original-recovery/runs/337-game-frontier-triage/summary.json')
    candidates = load(triage)['candidates']
    for symbol in cfg['expected_defined']:
        assert any(symbol in candidate.get('missing_symbols', []) for candidate in candidates)
    vc = ROOT / 'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
    sdk = Path('C:/Program Files (x86)/Windows Kits/10')
    kit = '10.0.26100.0'
    compiler = vc / 'bin/Hostx64/x86/cl.exe'
    linker = compiler.parent / 'link.exe'
    includes = [source.parent, ROOT / 'iterations/v2/001-original-recovery/source/include',
                vc / 'include', *(sdk / 'Include' / kit / part for part in ('ucrt', 'shared', 'um'))]
    libs = [vc / 'lib/x86/libcmt.lib', vc / 'lib/x86/libvcruntime.lib',
            vc / 'lib/x86/oldnames.lib', sdk / 'Lib' / kit / 'ucrt/x86/libucrt.lib',
            sdk / 'Lib' / kit / 'um/x86/kernel32.lib']
    for path in (compiler, linker, compiler.parent / 'c1xx.dll', compiler.parent / 'c2.dll', *libs):
        pin(path)
    for path in (source, fixture):
        for dependency in utility.local_includes(path):
            pin(dependency)
    receipts = {}

    def run(name, command):
        guard()
        start = time.perf_counter()
        process = subprocess.run(list(map(str, command)), cwd=out,
                                 env={**os.environ, 'VSLANG': '1033', 'CL': '', '_CL_': '', 'INCLUDE': ''},
                                 capture_output=True, timeout=120)
        log = out / (name + '.log')
        log.write_bytes(process.stdout + process.stderr)
        result = {'command': list(map(str, command)), 'exit_code': process.returncode,
                  'seconds': round(time.perf_counter() - start, 6), 'log': rel(log),
                  'log_sha256': sha(log)}
        write(out / (name + '.execution.json'), result)
        receipts[name] = result
        guard()
        return result

    common = [compiler, '/nologo', '/c', '/TP', '/std:c++17', '/Oy-', '/GS-',
              '/GR-', '/EHsc', '/W4', '/utf-8',
              *(arg for inc in includes for arg in ('/I', inc))]
    game_obj, fixture_obj = out / 'game.obj', out / 'fixture.obj'

    def compile_all(tag):
        for name, path, opt, obj in (('game', source, '/O2', game_obj),
                                     ('fixture', fixture, '/Od', fixture_obj)):
            result = run(tag + '-' + name, [*common, opt, '/sourceDependencies',
                         out / 'dependencies', f'/Fo{obj}', path])
            assert result['exit_code'] == 0, (out / (tag + '-' + name + '.log')).read_text(errors='replace')

    compile_all('probe')
    dependencies = provenance.dependency_paths(out)
    for path in dependencies:
        pin(path)
    compile_all('compile')
    assert provenance.dependency_paths(out) == dependencies
    pin(game_obj)
    pin(fixture_obj)
    symbols = coff.coff_symbols(game_obj)
    assert set(symbols['defined']) == set(cfg['expected_defined']), symbols
    assert set(symbols['undefined']) == set(cfg['expected_undefined']), symbols

    def link(name, obj, target):
        result = run(name, [linker, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE',
                           '/INCREMENTAL:NO', '/NODEFAULTLIB', f'/OUT:{target}', obj,
                           fixture_obj, *libs])
        assert result['exit_code'] == 0, (out / (name + '.log')).read_text(errors='replace')

    exe = out / 'native_fixture.exe'
    link('link', game_obj, exe)
    pin(exe)
    result = run('native', [exe])
    assert result['exit_code'] == 0, (out / 'native.log').read_text(errors='replace')
    assert f"cases={cfg['cases']} failures=0" in (out / 'native.log').read_text()
    negatives = []
    if args.negative_controls:
        text = source.read_text()
        for mutation in cfg['mutations']:
            name, old, new = (mutation[key] for key in ('name', 'old', 'new'))
            assert text.count(old) == 1, name
            path = out / (name + '.cpp')
            path.write_text(text.replace(old, new), encoding='utf8', newline='\n')
            pin(path)
            obj, target = out / (name + '.obj'), out / (name + '.exe')
            result = run(name + '-compile', [*common, '/O2', f'/Fo{obj}', path])
            assert result['exit_code'] == 0, (out / (name + '-compile.log')).read_text(errors='replace')
            link(name + '-link', obj, target)
            result = run(name + '-native', [target])
            assert result['exit_code'] == 10, (out / (name + '-native.log')).read_text(errors='replace')
            negatives.append({'name': name, 'detected': True, 'exit_code': 10})
    guard()
    outputs = {rel(path): sha(path) for path in out.rglob('*') if path.is_file()}
    report = {'schema': 1, 'run': cfg['run'], 'status': 'PASS', 'kind': 'existing-body ABI bindings',
              'new_original_functions': 0, 'native_cases_passed': cfg['cases'],
              'source_sha256': {rel(path): sha(path) for path in (source, header, fixture)},
              'inputs_sha256': {rel(path): value for path, value in pins.items()},
              'outputs_sha256': outputs, 'receipts': receipts, 'coff_symbols': symbols,
              'original_body_proofs': proofs, 'negative_controls': negatives,
              'actual_dependencies': sorted(map(rel, dependencies)),
              'guards_before_after': True, 'optimization': 'bridge/O2;fixture/Od'}
    receipt = out / 'receipt.json'
    write(receipt, report)
    write(ROOT / cfg['summary'], {'schema': 1, 'run': cfg['run'], 'status': 'PASS',
          'new_original_functions': 0, 'native_cases_passed': cfg['cases'],
          'native_attemptdir': rel(out), 'native_receipt_sha256': sha(receipt),
          'source_sha256': report['source_sha256'], 'coff_symbols': symbols,
          'original_body_proofs': proofs, 'negative_controls': negatives,
          'predicted_closed_names': cfg['expected_defined'], 'predicted_closed_references': 2,
          'new_dependencies': []})
    print(f"Run{cfg['run']} PASS: {cfg['cases']} O2 transport cases, {len(negatives)} mutations")


if __name__ == '__main__':
    main()
