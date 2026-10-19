"""Audit the isolated REA Windows/x86 CLI pilot without starting Ghidra."""
import hashlib
import json
from pathlib import Path
import subprocess

from v2_shared_manifests import ManifestReader, externalize

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/302-rea-pilot'
EXPERIMENT = ROOT / 'local/experiments/v2-rea-pilot-302'
TOOL = ROOT / 'local/tools/rea-pilot-302'
INDEX = ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
ORIGINAL_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
SOURCE_COMMIT = 'cee95b2ae6a19122de95103b2d23bc6f8c9c4428'
NODE_ZIP_SHA = '50efaf01a08c520b4bbe499c09a8c5a5c370002c419c0d9da2c6815d3066a453'
PACKAGE_SHA = '20958a66dba1a011e50a486beb9463a343128ed368c984f94065362c13f51f90'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def records(name):
    return [json.loads(line) for line in (INDEX / name).read_text(encoding='utf8').splitlines()]


def immutable_json(path, value):
    data = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf8')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ValueError('Existing audit result differs: ' + str(path))


def main():
    assert digest(ROOT / 'local/game/Porsche.exe') == ORIGINAL_SHA
    assert digest(EXPERIMENT / 'Porsche.exe') == ORIGINAL_SHA
    assert digest(TOOL / '.pilot/downloads/node-v26.12.0-win-x64.zip') == NODE_ZIP_SHA
    assert digest(TOOL / '.pilot/downloads/rea-agents-6.7.0.tgz') == PACKAGE_SHA
    commit = subprocess.check_output(['git', '-C', str(TOOL), 'rev-parse', 'HEAD'], text=True).strip()
    assert commit == SOURCE_COMMIT

    phases = ('pack-001', 'pack-002', 'pack-003', 'verify-package-001',
              'copy-target-001', 'install-001', 'install-002', 'help-001',
              'doctor-001', 'providers-001', 'function-001', 'function-002',
              'xrefs-001')
    receipts = {}
    for phase in phases:
        path = EXPERIMENT / phase / 'receipt.json'
        receipt = json.loads(path.read_bytes())
        log = EXPERIMENT / phase / 'output.log'
        assert receipt['log_sha256'] == digest(log)
        assert receipt['source_commit'] == SOURCE_COMMIT
        assert receipt['phase'] + '-' + receipt['attempt'] == phase
        receipts[phase] = dict(path=relative(path), sha256=digest(path),
                               exit_code=receipt['exit_code'], seconds=receipt['seconds'])
    for phase in ('pack-003', 'verify-package-001', 'copy-target-001', 'install-002',
                  'help-001', 'providers-001', 'function-002', 'xrefs-001'):
        assert receipts[phase]['exit_code'] == 0
    assert receipts['function-001']['exit_code'] != 0
    assert receipts['doctor-001']['exit_code'] != 0
    assert (EXPERIMENT / 'extract-001/output.log').read_text().strip() == 'extracted'
    assert not (EXPERIMENT / 'extract-001/receipt.json').exists()

    function = json.loads((EXPERIMENT / 'function-002/output.log').read_bytes())
    xrefs = json.loads((EXPERIMENT / 'xrefs-001/output.log').read_bytes())
    for item in (function, xrefs):
        assert item['subject']['digest']['sha256'] == ORIGINAL_SHA
        assert item['subject']['format'] == 'pe' and item['subject']['architecture'] == 'x86'
        assert item['provider']['id'] == 'ghidra' and item['provider']['version'] == '12.1.3'
    assert function['operation'] == 'analyze_function'
    assert xrefs['operation'] == 'xrefs' and xrefs['normalized_result'] == ['0x487e4d']
    normal = function['normalized_result']
    proc = normal['procedure']
    assert proc['address'] == '0x476170'
    assert proc['body']['ranges'] == [{'start': '0x476170', 'end': '0x476218'}]
    assert proc['body']['total_bytes'] == 169
    assert [p['address'] for p in normal['callers']] == ['0x487e20']
    assert [p['address'] for p in normal['callees']] == ['0x476710']
    assert [r['source_address'] for r in normal['incoming_references']] == xrefs['normalized_result']
    unresolved = [r['address'] for r in normal['unresolved_calls']]
    assert unresolved == ['0x4761c0', '0x4761f1']
    assert function['relationship_coverage']['status'] == 'partial'

    funcs = {r['entry_va']: r for r in records('functions.jsonl')}
    assert funcs['00476170']['ranges'] == [['00476170', '00476218']]
    assert funcs['00476170']['body_bytes'] == 169
    assert funcs['00487e20']['ranges'] == [['00487e20', '00487e76']]
    assert funcs['00476710']['ranges'] == [['00476710', '00476797']]
    direct = [r for r in records('calls.jsonl') if r.get('from_function') == '00476170' or r.get('to_function') == '00476170']
    assert [(r['from_va'], r['to_va']) for r in direct] == [('0047619b', '00476710'), ('00487e4d', '00476170')]
    index_unresolved = [r['va'] for r in records('unresolved-calls.jsonl') if r.get('function') == '00476170']
    assert index_unresolved == [address[2:].zfill(8) for address in unresolved]
    entry_refs = [r for r in records('references.jsonl') if r.get('to_va') == '00476170' and r.get('from_va') == '00487e4d']
    assert len(entry_refs) == 1 and entry_refs[0]['type'] == 'UNCONDITIONAL_CALL'

    doctor = json.loads((EXPERIMENT / 'doctor-001/output.log').read_bytes())
    checks = {item['name']: item['ok'] for item in doctor['scope_checks']}
    assert all(checks[name] for name in ('node', 'ghidra', 'ghidra-headless', 'ghidra-version'))

    inputs = [ROOT / 'local/game/Porsche.exe'] + [INDEX / name for name in
              ('functions.jsonl', 'calls.jsonl', 'references.jsonl', 'unresolved-calls.jsonl')]
    sources = [ROOT / 'scripts/research/rea-pilot-302.py', Path(__file__),
               ROOT / 'scripts/research/v2_shared_manifests.py']
    pin_doc = externalize(ROOT, {'input_sha256': {relative(p): digest(p) for p in inputs}}, 'input')
    pin_doc = externalize(ROOT, {**pin_doc, 'source_sha256': {relative(p): digest(p) for p in sources}}, 'source')
    reader = ManifestReader(ROOT)
    reader.verify(pin_doc, 'input', expected_hash_mode='raw')
    reader.verify(pin_doc, 'source', expected_hash_mode='raw')

    result = dict(schema=1, kind='rea-windows-x86-pilot', status='PASS',
                  original_sha256=ORIGINAL_SHA, source_commit=SOURCE_COMMIT,
                  package_version='6.7.0', node_version='26.12.0',
                  node_zip_sha256=NODE_ZIP_SHA, package_tarball_sha256=PACKAGE_SHA,
                  provider='Ghidra 12.1.3', target='00476170',
                  function_range=['00476170', '00476218'], bytes=169,
                  callers=['00487e20'], call_sites=['00487e4d'],
                  callees=['00476710'], callee_call_sites=['0047619b'],
                  unresolved_call_sites=index_unresolved,
                  relationship_coverage='partial', xrefs=['00487e4d'],
                  cached_index_match=True, receipts=receipts,
                  input_manifest=pin_doc['input_manifest'],
                  source_manifest=pin_doc['source_manifest'],
                  limitations=['Two indirect call targets remain unresolved',
                               'Ghidra 12.1.3 is accepted by REA but its verified build is 12.1.4',
                               'Doctor overall fails broad Hopper/agent checks despite healthy Ghidra scope',
                               'extract-001 completed but runner crashed before receipt; verify-package-001 independently matched 1775 files'])
    immutable_json(RUN / 'audit.json', result)
    print('PASS REA302: native Windows/x86 function + xrefs; cached index match; partial indirect calls')


if __name__ == '__main__':
    main()
