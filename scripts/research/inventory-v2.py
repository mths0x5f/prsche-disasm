"""Audit every local executable against its input SHA and v2 export results.

Listing, automatic pseudo-C, recovered source and binary matches are distinct.
No source module is excluded merely because it is a driver/installer/16-bit NE.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
ITERATION = ROOT / 'iterations/v2/001-original-recovery'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from v2_manual_index import records as manual_records
from v2_proof_cache import ProofCache


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-listing', action='store_true')
    parser.add_argument('--require-decompile-attempts', action='store_true')
    parser.add_argument('--write-verification', action='store_true')
    parser.add_argument('--verification-output', type=Path,
                        default=ITERATION/'runs/169-vtable-output-integration/corpus-verification.json',
                        help='Current checkpoint report; historical run hashes are preserved')
    args = parser.parse_args()
    verification_output = args.verification_output if args.verification_output.is_absolute() else ROOT / args.verification_output
    original = ROOT / 'local/game'
    old = load(ROOT / 'research/binary-index/coverage.json')
    known = {entry['sha256']: entry for entry in old['binaries']}
    binaries = {}
    for path in sorted(original.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.exe','.dll','.asi','.ocx'):
            continue
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        relative = path.relative_to(original).as_posix()
        if sha in binaries:
            binaries[sha]['paths'].append(relative)
            continue
        offset = struct.unpack_from('<I',data,0x3c)[0] if data[:2] == b'MZ' and len(data)>=64 else None
        signature = data[offset:offset+4] if offset is not None else b''
        kind = 'PE' if signature == b'PE\0\0' else 'NE' if signature[:2] == b'NE' else 'unknown'
        entry = {'sha256':sha,'paths':[relative],'bytes':len(data),'format':kind,
                 'role':'unclassified','recovered_functions':0,'matched_functions':0,'matched_binary':False}
        if kind == 'PE':
            entry.update(machine=hex(struct.unpack_from('<H',data,offset+4)[0]),
                         coff_timestamp=hex(struct.unpack_from('<I',data,offset+8)[0]),
                         linker_version=f'{data[offset+26]}.{data[offset+27]}',
                         compiler='unconfirmed; linker version alone is insufficient')
        expected = known.get(sha)
        if not expected:
            raise RuntimeError(f'{relative}: SHA is absent from the original inventory; investigate before reuse')
        export = ROOT/'research/v2/binaries'/f'{path.name}-{sha[:12]}'
        listing, decompile = load(export/'listing.json'), load(export/'decompilation.json')
        for record in (listing,decompile):
            if record and record['sha256'] != sha:
                raise RuntimeError(f'{relative}: stale export SHA')
        if listing:
            for name in ('disassembly.asm','functions.jsonl','defined-data.jsonl','unclassified-executable.jsonl'):
                if not (export/name).is_file():
                    raise RuntimeError(f'{relative}: completed listing is missing {name}')
            if sum(1 for _ in (export/'functions.jsonl').open(encoding='utf-8')) != listing['functions']:
                raise RuntimeError(f'{relative}: listing function count mismatch')
        if decompile:
            statuses = [json.loads(line) for line in (export/'decompile-status.jsonl').read_text(encoding='utf-8').splitlines()]
            if len(statuses) != decompile['functions'] or not (export/'decompiled.c').is_file():
                raise RuntimeError(f'{relative}: incomplete decompile output despite completion marker')
            failed = [s for s in statuses if s['status'] in ('failed','timeout')]
            if len(failed) != decompile['failed']:
                raise RuntimeError(f'{relative}: decompile failure count mismatch')
            text = (export/'decompiled.c').read_text(encoding='utf-8')
            bodies = re.split(r'/\* VA [^*]+\*/', text)[1:]
            decompile['warning_functions'] = sum(bool(re.search(r'/\* WARNING:|// WARNING:',body)) for body in bodies)
            decompile['diagnostic_functions'] = sum(bool(s.get('message')) for s in statuses)
            entry['decompile_failures'] = failed
        entry['export_directory'] = export.relative_to(ROOT).as_posix()
        entry['original_analysis'] = expected.get('ghidra',{})
        entry['listing'] = listing or {'status':'not-exported'}
        entry['automatic_decompilation'] = decompile or {'status':'not-exported'}
        binaries[sha] = entry
    manual = manual_records()
    manual_addresses = {}
    for record in manual:
        manual_addresses.setdefault(record['sha256'], set()).add(record['entry_va'].lower())
    recovered = load(ITERATION/'source/recovered/functions.json') or {'functions': []}
    seen = set()
    proof_cache = ProofCache()
    indexed_by_sha = {
        sha: {json.loads(line)['entry_va'].lower() for line in
              (ROOT/entry['export_directory']/'functions.jsonl').read_text(encoding='utf8').splitlines()}
             | manual_addresses.get(sha, set())
        for sha, entry in binaries.items()
    }
    for function in recovered['functions']:
        key = (function['sha256'], function['entry_va'])
        if key in seen or key[0] not in binaries:
            raise RuntimeError(f'Duplicate or unknown recovered function: {key}')
        seen.add(key)
        source = ROOT/function['source']
        if not source.is_file():
            raise RuntimeError(f'Recovered source is missing: {source}')
        entry = binaries[key[0]]
        indexed = indexed_by_sha[key[0]]
        if key[1].lower() not in indexed:
            raise RuntimeError(f'Recovered function is absent from corpus: {key}')
        if function['status'] in ('native-differential-verified', 'partial-native-differential-verified'):
            verification = proof_cache.document(ROOT/function['verification_report'])
            source_sha = proof_cache.digest(source)
            verified_vas = verification.get('function_vas', verification.get('full_function_vas', []) + verification.get('partial_function_vas', []) or [verification.get('function_va')]) if verification else []
            if not verification or verification['sha256'] != key[0] or key[1] not in verified_vas or not verification['native_cpp_equal_original_x86'] or verification['source_sha256'].get(function['source']) != source_sha:
                raise RuntimeError(f'Missing/stale native verification: {key}')
            for relative, expected_sha in verification['source_sha256'].items():
                dependency = ROOT/relative
                if not dependency.is_file() or proof_cache.digest(dependency) != expected_sha:
                    raise RuntimeError(f'Stale verified source dependency: {relative}')
            if function['status'] == 'native-differential-verified':
                if key[1] in verification.get('partial_function_vas', []):
                    raise RuntimeError(f'Partial proof cannot count as full function: {key}')
                entry['recovered_functions'] += 1
        if function.get('integration_verification_report'):
            integration = proof_cache.document(ROOT/function['integration_verification_report'])
            if not integration or integration['sha256'] != key[0] or key[1] not in integration.get('function_vas', integration.get('entry_vas', [])) or not integration['native_cpp_equal_original_x86']:
                raise RuntimeError(f'Missing joint verification: {key}')
            for relative, expected_sha in integration['source_sha256'].items():
                dependency = ROOT/relative
                if not dependency.is_file() or proof_cache.digest(dependency) != expected_sha:
                    raise RuntimeError(f'Stale joint source dependency: {relative}')
        if function.get('binary_matched'):
            raise RuntimeError('Binary-match evidence validation has not been implemented; do not count unchecked claims')
    proof_cache.check_stable()
    print(json.dumps({'proof_audit_cache': proof_cache.counts}))
    automatic_addresses = {}
    for sha, entry in binaries.items():
        export_functions = ROOT / entry['export_directory'] / 'functions.jsonl'
        automatic_addresses[sha] = {json.loads(line)['entry_va'].lower() for line in
                                    export_functions.read_text(encoding='utf-8').splitlines()}
        entry['supplementary_functions'] = []
    for record in manual:
        sha = record['sha256']
        if sha not in binaries:
            raise RuntimeError(f'Manual function references unknown binary SHA: {sha}')
        address = record['entry_va'].lower()
        if address in automatic_addresses[sha]:
            raise RuntimeError(f'Manual function overlaps automatic catalog: {(sha, address)}')
        binaries[sha]['supplementary_functions'].append({
            'entry_va': record['entry_va'], 'name': record['name'],
            'status': record['status'], 'reason': record['reason'],
            'body_bytes': record['body_bytes'], 'ranges': record['ranges'],
        })
    for entry in binaries.values():
        entry['supplementary_function_count'] = len(entry['supplementary_functions'])
    entries = list(binaries.values())
    listing_done = sum(bool(e['listing'].get('complete_listing_of_analyzed_instructions')) for e in entries)
    decompile_done = sum(bool(e['automatic_decompilation'].get('attempted_all_functions')) for e in entries)
    counts = {'input_paths':sum(len(e['paths']) for e in entries),'unique_modules':len(entries),
              'listing_modules':listing_done,'decompile_attempted_modules':decompile_done,
              'instructions':sum(e['listing'].get('instructions',0) for e in entries),
              'analyzed_functions':sum(e['listing'].get('functions',0) for e in entries),
              'unclassified_executable_bytes':sum(e['listing'].get('unclassified_executable_bytes',0) for e in entries),
              'automatic_pseudo_c_functions':sum(e['automatic_decompilation'].get('pseudo_c_functions',0) for e in entries),
              'supplementary_manual_functions':sum(e['supplementary_function_count'] for e in entries),
              'indexed_functions':sum(e['listing'].get('functions',0) for e in entries) + sum(e['supplementary_function_count'] for e in entries),
              'decompile_failures':sum(e['automatic_decompilation'].get('failed',0) for e in entries),
              'pseudo_c_warning_functions':sum(e['automatic_decompilation'].get('warning_functions',0) for e in entries),
              'recovered_functions':sum(e['recovered_functions'] for e in entries),
              'partially_verified_functions':sum(f['status']=='partial-native-differential-verified' for f in recovered['functions']),
              'matched_functions':0,'matched_modules':0}
    output = {'schema':1,'snapshot_date':'2026-10-09','generation':'v2',
              'v1_checkpoint':'dc6b9d8','original_data':'local/game (read-only)',
              'reference_method':'matching source recovery; native Windows/x86 baseline before portable adaptation',
              'counts':counts,'binaries':entries,
              'boundary':'Exported instructions and automatic pseudo-C are not complete code discovery or compilable recovered source.'}
    target = ITERATION/'reference/binaries.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(counts))
    if args.require_listing and listing_done != len(entries):
        raise SystemExit('Missing full listings; inspect reference/binaries.json')
    if args.require_decompile_attempts and decompile_done != len(entries):
        raise SystemExit('Missing decompilation attempts; inspect reference/binaries.json')
    if args.write_verification:
        if listing_done != len(entries) or decompile_done != len(entries):
            raise SystemExit('Cannot record complete export verification before every module is attempted')
        catalog = load(ITERATION/'source/catalog/modules.json')
        if not catalog or catalog['function_count'] != counts['indexed_functions']:
            raise RuntimeError('Stale source catalog; run structure-v2.py after inventory-v2.py')
        for module in catalog['modules']:
            sha = module['source_sha256']
            rows = [json.loads(line) for line in (ROOT/module['catalog']).read_text(encoding='utf8').splitlines()]
            addresses = {row['va'].lower() for row in rows}
            expected = automatic_addresses[sha] | manual_addresses.get(sha, set())
            if addresses != expected or len(rows) != len(expected):
                raise RuntimeError(f'Stale/duplicate source catalog addresses: {module["catalog"]}')
        hashes = {}
        original_resources = {}
        paths = list((ROOT/'research/v2/binaries').rglob('*')) + [target]
        paths += [ROOT/p for p in ('scripts/research/export-v2.ps1',
                  'scripts/research/inventory-v2.py','scripts/research/ghidra/ExportRecoveryCorpus.java',
                  'scripts/build-v2.ps1','scripts/research/structure-v2.py',
                  'scripts/research/trace-v2-startup.py','scripts/research/verify-v2-startup.py',
                  'scripts/research/export-v2-fe-tables.py','scripts/research/verify-v2-fe-stream.py',
                  'scripts/research/verify-v2-heap.py')]
        paths += [ROOT/'scripts/research/index-v2-clock-worker.py']
        paths += [ROOT/'scripts/research/v2_proof_cache.py', ROOT/'scripts/research/test_v2_proof_cache.py', ROOT/'scripts/research/audit-v2-proofs.py', ROOT/'scripts/research/refresh-v2-proofs.py', ROOT/'scripts/research/audit-v2-global-aliases.py', ROOT/'scripts/research/audit-v2-link-frontier.py', ROOT/'scripts/research/v2_manual_index.py', ROOT/'scripts/research/verify-v2-files.py', ROOT/'scripts/research/verify-v2-file-device.py', ROOT/'research/binary-index/manual-functions.jsonl', ROOT/'research/binary-index/README.md']
        run005 = ITERATION/'runs/005-original-files'
        if run005.exists():
            paths += [path for path in run005.rglob('*') if path.resolve() != verification_output.resolve()]
        paths += [path for path in (ITERATION/'runs/006-file-device').rglob('*') if path.resolve() != verification_output.resolve()]
        paths += [ROOT/'scripts/research/index-v2-worker.py', ROOT/'scripts/research/verify-v2-file-worker.py']
        paths += [path for path in (ITERATION/'runs/007-file-worker').rglob('*') if path.resolve() != verification_output.resolve()]
        paths += [ROOT/'scripts/research/verify-v2-file-wait.py']
        paths += [path for path in (ITERATION/'runs/008-file-scheduler').rglob('*') if path.resolve() != verification_output.resolve()]
        paths += [ROOT/'scripts/research/verify-v2-file-events.py', ROOT/'scripts/research/index-binaries.py', ROOT/'scripts/research/test_index_binaries.py', ROOT/'research/binary-index/static/imports.jsonl']
        paths += [path for path in (ITERATION/'runs/009-file-events').rglob('*') if path.resolve() != verification_output.resolve()]
        paths += [ROOT/'scripts/research/index-v2-threads.py', ROOT/'scripts/research/verify-v2-file-threads.py']
        paths += [path for path in (ITERATION/'runs/010-file-threads').rglob('*') if path.resolve() != verification_output.resolve()]
        paths += [ROOT/'scripts/research/verify-v2-file-disk.py', ROOT/'scripts/research/verify-v2-fe-callbacks.py']
        for run_name in ('011-file-disk','012-fe-callbacks','013-input-state','014-heap-locks','015-joint-disk','017-input-modes','018-lock-bootstrap','016-disk-open','019-input-buffer','020-thread-bootstrap','022-startup-services','023-resource-paths','024-render-startup','025-application-heap','026-render-objects','027-window-runtime','030-startup-integration','028-render-loader','029-window-create','031-application-alloc','033-application-heap-init','034-window-procedure','036-native-window','032-render-display','035-window-worker','037-application-pool','038-window-handlers','039-window-state','040-application-bootstrap','041-startup-chain','042-render-registry','043-startup-subsystems','044-window-thread-start','045-window-messages','046-startup-input','047-application-fe','048-window-position','049-render-activate','050-application-instance','051-render-window','052-exit-registry','053-crt-shutdown','054-thread-shutdown','055-native-platform','056-render-driver-calls','057-native-thread-chain','059-window-keys','060-render-event-route','061-startup-platform-integration','058-application-main','063-render-mode','064-window-callback-bindings','065-window-callback-integration','067-main-callback-integration','066-render-settings','068-application-state','069-window-event-queue','070-native-window-bindings','071-render-state-init','072-window-links','073-render-state-integration','074-application-arena','075-recovered-links','076-global-alias-audit','077-native-window-chain','078-shared-runtime-integration','079-window-channels','080-shared-diagnostic-storage','081-bss-fallback-audit','082-window-scheduler','083-window-shutdown','084-window-support','085-window-exit-cleanup','086-native-window-lifecycle','087-window-notifications','088-object-cleanup','089-mouse-input','090-native-window-integration','091-window-event-translation','092-object-update','093-game-setup','094-movie-header','095-splash-progress','096-input-snapshot','097-startup-sequence','098-startup-integration','099-startup-service','100-startup-service','101-frame-pump','102-original-game-link','103-engine-service','104-link-alias-audit','105-frame-services','106-resource-predicate','107-frame-integration','110-clock-worker-index','108-formatter-entry','109-resource-leaf','111-runtime-integration','112-clock-worker','113-resource-dispatch','115-process-exit','116-install-paths','117-install-integration','120-application-main-storage','118-timer-setup','119-formatter-original','121-formatter-timer-integration','122-auxiliary-wait','125-native-shutdown','123-event-lifecycle','126-event-integration','127-thread-wait','128-application-services','130-event-thread-integration','129-application-context','124-formatter-parser','132-formatter-cleanup','133-application-audio-device','134-formatter-integration','135-application-context-base','136-formatter-context-integration','137-formatter-runtime','138-formatter-runtime-storage','139-context-effects','140-formatter-bootstrap','141-application-services-next','142-audio-lifecycle','143-runtime-network-integration','144-crt-strings','145-network-lifecycle','147-float-helpers','148-network-services','149-context-ranges','150-context-services','151-network-cleanup','153-services-integration','152-crt-lowio','154-context-move','155-network-session','156-lowio-memory-integration','157-crt-runtime','158-formatter-text','159-network-workers-members','160-crt-text-workers-integration','161-small-heap','162-formatter-locale','163-network-groups','165-heap-locale-groups-integration','164-network-vtables','166-formatter-output','169-vtable-output-integration'):
            paths += [path for path in (ITERATION/'runs'/run_name).rglob('*') if path.resolve() != verification_output.resolve()]
        paths += [ROOT/'scripts/research/verify-v2-input-state.py', ROOT/'scripts/research/verify-v2-heap-locks.py', ROOT/'scripts/research/verify-v2-joint-disk.py', ROOT/'scripts/research/verify-v2-original-game-link.py']
        paths += [ROOT/'scripts/research/verify-v2-disk-open.py', ROOT/'scripts/research/verify-v2-input-buffer.py', ROOT/'scripts/research/verify-v2-thread-bootstrap.py']
        paths += [ROOT/('scripts/research/verify-v2-'+name+'.py') for name in ('startup-services','resource-paths','application-heap','render-startup','render-objects','window-runtime','render-loader','window-create','application-alloc','application-heap-init','window-procedure')]
        # Pending parallel work is excluded until its dependency hashes are accepted.
        paths += list((ITERATION/'source/catalog').rglob('*'))
        paths += [ITERATION/'source/recovered/functions.json', ITERATION/'source/recovered/sources.cmake']
        source_reports = {f['verification_report'] for f in recovered['functions']}
        source_reports.add('iterations/v2/001-original-recovery/runs/039-window-state/verification.json')
        source_reports.add('iterations/v2/001-original-recovery/runs/067-main-callback-integration/window-callback-bindings/verification.json')
        source_reports.update(f['integration_verification_report'] for f in recovered['functions'] if f.get('integration_verification_report'))
        # Fresh layout, storage and platform proofs also pin modern infrastructure.
        for path in (ITERATION/'runs/169-vtable-output-integration').rglob('*.json'):
            document = load(path)
            if isinstance(document, dict) and 'source_sha256' in document:
                source_reports.add(path.relative_to(ROOT).as_posix())
        for report_path in sorted(source_reports):
            paths += [ROOT/p for p in load(ROOT/report_path)['source_sha256']]
        # Native OS fixtures have dependency pins, separately from differential proofs.
        for name in ('native-core','native-thread','native-window','native-window-lifecycle','native-formatter-error','native-formatter-lowio','native-formatter-crt','native-formatter-locale-heap','native-formatter-output'):
            native = load(ITERATION/'runs/169-vtable-output-integration'/(name+'-result.json'))
            if not native:
                raise RuntimeError(f'Missing current native fixture report: {name}-result.json')
            for relative, expected in native['source_sha256'].items():
                dep = ROOT/relative
                if hashlib.sha256(dep.read_bytes().replace(b'\r\n',b'\n')).hexdigest() != expected:
                    raise RuntimeError(f'Stale native fixture dependency: {relative}')
                paths.append(dep)
        # The separate Run102 link frontier is evidence for the entrypoint's
        # unresolved surface; keep its inputs and verifier in the modern report.
        paths += [ROOT/'iterations/v2/001-original-recovery/runs/102-original-game-link'/name
                  for name in ('link-report.json','host-entry.cpp','CMakeLists.txt')]
        paths += [ITERATION/'CMakeLists.txt', ITERATION/'reference/startup.json']
        paths += [ROOT/p for p in sorted({f['verification_report'] for f in recovered['functions']} | {f['verification'] for f in recovered['functions']})]
        paths += [ITERATION/'runs/003-fe-stream'/name for name in
                  ('tables.json', 'resource-inventory.json', 'source-functions.jsonl', 'source-calls.jsonl')]
        paths += [ITERATION/'runs/004-original-heap'/name for name in
                  ('source-functions.jsonl', 'source-calls.jsonl', 'heap-table-references.jsonl', 'toolchain.json', 'globals.json')]
        for path in sorted(paths):
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if path.is_file():
                data = path.read_bytes()
                if path.is_relative_to(original):
                    # Immutable game inputs are pinned separately, never staged
                    # as recovered sources or redistributed with the corpus.
                    original_resources[path.relative_to(ROOT).as_posix()] = {
                        'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                    continue
                source_script = path.relative_to(ROOT).as_posix().startswith('scripts/')
                if source_script:
                    data = data.replace(b'\r\n', b'\n')
                hashes[path.relative_to(ROOT).as_posix()] = {
                    'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                    'hash_text_normalization':'CRLF to LF' if source_script else 'none; corpus stored as LF'}
        verification = {'schema':1,'date':'2026-10-12','counts':counts,
            'original_input_hashes_verified':True,'all_listing_files_present':True,
            'all_function_status_counts_verified':True,'ghidra':'12.1.3',
            'pe_export':'cached analyzed project, noanalysis/readOnly',
            'ne_export':'separate NeLoader project, subsequent readOnly decompile',
            'exporter_compilation_check':'drvmgt.dll full listing succeeded after SHA/resume guards',
            'new_v2_game_executable':False,'recovered_compilable_source':counts['recovered_functions'] > 0,
            'original_native_behavior_acceptance':False,'files':hashes,
            'original_resource_inputs':original_resources,
            'limitations':['Automatic pseudo-C is not recovered compilable source.',
                'Four functions failed/timed out; details remain in the manifest.',
                'Warnings and unclassified executable bytes remain unresolved.',
                'Exact original compiler/CRT/flags/layout are not confirmed.']}
        verification_output.parent.mkdir(parents=True,exist_ok=True)
        verification_output.write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    main()
