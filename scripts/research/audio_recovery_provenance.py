"""Input/output integrity for the standalone Run421/422 research fixtures."""
import hashlib
import importlib.util
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dependency_paths(out):
    paths = set()
    for p in (out / 'dependencies').glob('*.json'):
        data = json.loads(p.read_text(encoding='utf-8-sig'))['Data']
        paths.add(Path(data['Source']).resolve())
        paths.update(Path(x).resolve() for x in data['Includes'])
    assert paths, 'missing compiler dependency records'
    return paths


def verify(root, run, out, summary, expected_defined, optional_defined, expected_undefined):
    manifest_path = out / 'provenance-001.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert digest(manifest_path) == summary['provenance_sha256'], 'provenance drift'
    for name, expected in manifest['input_sha256'].items():
        p = Path(name)
        if not p.is_absolute(): p = root / p
        assert digest(p) == expected, f'input drift: {name}'
    for name, expected in manifest['output_sha256'].items():
        p = root / name
        assert digest(p) == expected, f'output drift: {name}'
    for key, path in [('source', run / manifest['source_file']), ('header', run / manifest['header_file']), ('fixture', out / manifest['fixture_file'])]:
        assert digest(path) == summary[key + '_sha256'], f'{key} SHA mismatch'
    spec = importlib.util.spec_from_file_location('coff_audio_audit', root / 'scripts/research/build-v2-compile-corpus.py')
    coff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(coff)
    view = coff.coff_symbols(out / 'objects' / manifest['object_file'])
    assert view == summary['symbols'], 'actual COFF differs from summary'
    defined = set(view['defined'])
    assert expected_defined <= defined and defined - expected_defined <= optional_defined, 'unexpected COFF definitions'
    assert set(view['undefined']) == expected_undefined, 'unexpected COFF undefined symbols'
    for name, recorded in [('compile-001', summary['compile']), ('fixture-link-001', summary['link']), ('fixture-native-001', summary['native_fixture']['execution'])]:
        receipt = json.loads((out / (name + '.execution.json')).read_text())
        assert receipt == recorded and receipt['exit_code'] == 0, f'receipt mismatch: {name}'
        assert digest(root / receipt['log']) == receipt['log_sha256'], f'log drift: {name}'
    expected = set(manifest['dependency_input_paths'])
    assert {str(x) for x in dependency_paths(out)} == expected, 'dependency closure drift'
    assert manifest['guards_before_and_after_compile_link_native'] is True
