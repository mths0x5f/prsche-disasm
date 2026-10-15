"""Check the bounded storage correction against original instructions and high IR.

Consumes existing four-function captures; never recompiles or opens Ghidra.
"""
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/193-abi-storage-pilot'
EXPORT = RUN / 'export/attempt-002'
CORPUS = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS = ['00482f70', '00483290', '00489370', '00489530']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    result = load(EXPORT / 'result.json')
    provenance = load(EXPORT / 'provenance.json')
    assert result['original_sha256'] == SHA
    assert provenance['original_project_unchanged']
    assert provenance['headless_exit_code'] == 0
    assert provenance['original_project_before'] == provenance['original_project_after']
    assert '-readOnly' in provenance['command'] and '-noanalysis' in provenance['command']
    assert set(result['modified_functions']) == {'00482f70', '00489530'}
    pins = {}
    for record in provenance['files']:
        path = ROOT / record['path']
        assert digest(path) == record['sha256'], path
        pins[record['path']] = record['sha256']
    for path in [Path(__file__), CORPUS / 'disassembly.asm', CORPUS / 'functions.jsonl',
                 ROOT / 'local/game/Porsche.exe', *EXPORT.iterdir()]:
        if path.is_file():
            pins[path.relative_to(ROOT).as_posix()] = digest(path)

    raw = (ROOT / 'local/game/Porsche.exe').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    pe = struct.unpack_from('<I', raw, 0x3c)[0]
    assert raw[pe:pe+4] == b'PE\0\0'
    machine, nsections, _, _, _, optional, _ = struct.unpack_from('<HHIIIHH', raw, pe+4)
    assert machine == 0x14c
    image_base = struct.unpack_from('<I', raw, pe+24+28)[0]
    sections = []
    for i in range(nsections):
        off = pe+24+optional+40*i
        virtual_size, rva, size, offset = struct.unpack_from('<IIII', raw, off+8)
        sections.append((rva, size, offset))

    def original_bytes(va, size):
        rva = int(va, 16) - image_base
        for start, length, offset in sections:
            if start <= rva and rva+size <= start+length:
                return raw[offset+rva-start:offset+rva-start+size].hex()
        raise AssertionError(('unbacked address', va))

    catalog = {r['entry_va']: r for r in map(json.loads, (CORPUS / 'functions.jsonl').read_text().splitlines())}
    indexed = {}
    for line in (CORPUS / 'disassembly.asm').read_text().splitlines():
        m = re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)', line)
        if m:
            indexed[m[1]] = {'va': m[1], 'bytes': m[2], 'instruction': m[3]}
    instructions = {}
    for va in VAS:
        ranges = catalog[va]['ranges']
        body = [r for pc, r in indexed.items() if any(int(a, 16) <= int(pc, 16) <= int(b, 16) for a, b in ranges)]
        assert body
        for r in body:
            assert original_bytes(r['va'], len(r['bytes'])//2) == r['bytes'], r
        instructions[va] = body

    # These instructions establish the two hardware contracts, independently of getC.
    expected = {'00483298': '8b09', '004832a1': 'e8cafcffff',
                '00489372': '8bf9', '00489382': '53', '00489383': '56',
                '00489384': '8bcf', '00489386': 'e8a5010000',
                '00489530': '81ec28010000', '00489547': '8b9c243c010000',
                '004895eb': '8bbc2440010000', '0048971f': '8bbc2440010000',
                '0048305e': '33c0', '00483065': '33c0'}
    for va, code in expected.items():
        assert indexed[va]['bytes'] == original_bytes(va, len(code)//2) == code
    contracts = {}
    for va, words in [('00489530', 2), ('00482f70', 3)]:
        rets = [i for i in instructions[va] if i['instruction'].startswith('RET')]
        assert rets and all(r['bytes'] == 'c2' + struct.pack('<H', words*4).hex() for r in rets)
        after = load(EXPORT / f'after-callees-{va}.json')
        params = after['database']['parameters']
        assert len(params) == words+1
        assert params[0]['storage']['display'] == 'ECX:4'
        assert [p['storage']['varnodes'][0]['offset'] for p in params[1:]] == list(range(4, words*4+1, 4))
        assert all(p['bytes'] == 4 for p in params)
        assert after['database']['stack_purge_bytes'] == words*4
        contracts[va] = {'receiver': 'ECX:4', 'stack_slots': list(range(4, words*4+1, 4)),
                         'original_ret_sites': rets, 'semantic_types_recovered': False}

    calls = []
    for caller, callee, pc in [('00489370', '00489530', '00489386'), ('00483290', '00482f70', '004832a1')]:
        before = load(EXPORT / f'before-{caller}.json')
        after = load(EXPORT / f'after-callees-{caller}.json')
        bc, ac = before['calls'][0], after['calls'][0]
        assert len(before['calls']) == len(after['calls']) == 1
        assert bc['instruction_va'] == ac['instruction_va'] == pc
        assert bc['inputs'][0]['address'] == ac['inputs'][0]['address'] == callee
        assert len(ac['inputs']) == len(bc['inputs'])+1
        recv = ac['inputs'][1]
        if caller == '00489370':
            assert recv['input'] and recv['address'] == 'register:00000004'
            assert [n['address'] for n in ac['inputs'][2:]] == ['register:00000018', 'Stack[0x4]']
            assert ac['inputs'][2]['defined_by'] == 'MULTIEQUAL'
            equation = 'ECX_call=ECX_entry; stack+4=ESI loop index; stack+8=entry stack+4'
        else:
            assert recv['defined_by'] == 'LOAD'
            base = recv['producer_inputs'][1]
            assert base['input'] and base['address'] == 'register:00000004'
            assert [n['address'] for n in ac['inputs'][2:]] == ['Stack[0x4]', 'Stack[0x8]', 'Stack[0xc]']
            assert after['inferred']['parameters'][0]['storage']['display'] == 'ECX:4 (auto)'
            equation = 'ECX_call=DWORD[ECX_entry]; three original entry stack slots preserved'
        calls.append({'caller_va': caller, 'callee_va': callee, 'call_pc': pc,
                      'before_input_count_without_target': len(bc['inputs'])-1,
                      'after_input_count_without_target': len(ac['inputs'])-1,
                      'original_equation': equation, 'high_ir_input_producers_checked': True})
    for name, expected_sha in pins.items():
        assert digest(ROOT / name) == expected_sha, ('input mutation', name)
    summary = {'schema': 1, 'original_sha256': SHA, 'functions_decompiled_per_stage': 4,
               'stages': 2, 'modified_callee_signatures': 2, 'restored_call_sites': calls,
               'original_instruction_bytes_checked': sum(len(v) for v in instructions.values()),
               'contracts': contracts, 'original_project_unchanged': True,
               'automatic_caller_reinference': True, 'autoanalysis': False,
               'input_sha256': pins,
               'boundary': ['Two raw32 storage contracts only, not class/type/lifetime reconstruction.',
                            '00489530 inferred void return is retained for this experiment; complete return/hidden-register ABI is not accepted.',
                            'No native compile/execution, game integration, new accepted functions or blanket correction of the42 mismatches.',
                            '00482f70 stack+c is unused locally but caller pushes it and both original RET12 consume it.']}
    (RUN / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps({k: summary[k] for k in ['functions_decompiled_per_stage', 'modified_callee_signatures', 'original_instruction_bytes_checked', 'original_project_unchanged']}))


if __name__ == '__main__':
    main()
