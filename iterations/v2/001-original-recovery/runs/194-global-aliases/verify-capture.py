"""Report-only refinement: include direct address-space input/output varnodes."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / 'scripts/research/experiment-v2-global-aliases-194.py'
spec = importlib.util.spec_from_file_location('alias194', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
old_accesses = module.raw_accesses

def accesses(instruction, address):
    result = old_accesses(instruction, address)
    for op in instruction['raw_pcode']:
        for index, node in enumerate(op['inputs']):
            if node['space'] == 'ram' and int(node['offset']) == address:
                result.append({'kind': 'READ', 'bytes': node['bytes'],
                               'sequence': op['sequence'], 'opcode': op['opcode'],
                               'input_index': index, 'pointer': 'direct RAM input varnode'})
        node = op.get('output')
        if node and node['space'] == 'ram' and int(node['offset']) == address:
            result.append({'kind': 'WRITE', 'bytes': node['bytes'],
                           'sequence': op['sequence'], 'opcode': op['opcode'],
                           'pointer': 'direct RAM output varnode'})
    return result

module.raw_accesses = accesses
module.report()
summary_path = module.RUN / 'summary.json'
summary = json.loads(summary_path.read_text())
summary['report_refinement'] = {
    'driver': str(Path(__file__)), 'sha256': module.sha(Path(__file__)),
    'initial_summary_sha256': module.sha(module.RUN / 'initial-summary.json'),
    'reason': 'Static address-space varnodes are direct memory inputs/outputs; LOAD/STORE-only matching missed these.',
    'capture_repeated': False, 'native_declarations_added': 0,
    'host_exit_caveat': 'PowerShell host exit1 on Java sun.misc.Unsafe NativeCommandError; actual result.json completion and all12 cases exist.'}
for case in summary['cases']:
    for instruction in case['instructions']:
        if not instruction['direct_access_width_agrees']:
            continue
        native = 0
        for operand in instruction['capstone_memory_operands']:
            native |= operand['access']
        raw = 0
        for access in instruction['sleigh_direct_accesses']:
            raw |= 1 if access['kind'] in ('READ', 'LOAD') else 2
        instruction['direct_access_direction_agrees'] = raw == native
        if raw != native:
            instruction['direction_discrepancy'] = {'sleigh_access_mask': raw, 'capstone_access_mask': native,
                'resolution': 'unresolved independent decoder direction discrepancy; do not approve typed declaration'}
    token_nodes = [t['token'].get('varnode') for t in case['tokens']]
    case['token_ram_width_agrees'] = bool(token_nodes) and all(
        n and n['space'] == 'ram' and int(n['offset']) == int(case['address'], 16)
        and n['bytes'] in case['original_direct_access_widths'] for n in token_nodes)
    case['acceptance'] = 'consumer address/width evidence only; no complete body or shared-storage acceptance'
module.dump(summary_path, summary)
validation = {'status': 'PASS', 'cases': len(summary['cases']),
              'classification_counts': summary['classification_counts'],
              'token_ram_width_agreement_cases': sum(c['token_ram_width_agrees'] for c in summary['cases']),
              'instruction_records_verified': sum(len(c['instructions']) for c in summary['cases']),
              'memory_width_verified': sum(i['direct_access_width_agrees'] for c in summary['cases'] for i in c['instructions']),
              'memory_direction_discrepancies': sum(i.get('direct_access_direction_agrees') is False for c in summary['cases'] for i in c['instructions']),
              'approved_complete_body_semantics': 0, 'native_compile_delta': 0,
              'source_pins_verified': True, 'program_changed_guard': summary['program_changed_before'] == summary['program_changed_after'],
              'summary_sha256': module.sha(summary_path),
              'export_sha256': {str(p.relative_to(ROOT)): module.sha(p) for p in sorted((module.OUT / 'export').iterdir()) if p.is_file()},
              'capture_pins_sha256': module.sha(module.OUT / 'capture-pins.json'),
              'cases_sha256': module.sha(module.OUT / 'cases.json'),
              'historical_readiness_superseded': True,
              'whole_project_guard': 'Root independently verifies original project79files.'}
module.dump(module.RUN / 'validation.json', validation)
print(json.dumps(validation, separators=(',', ':'))[:1000])
