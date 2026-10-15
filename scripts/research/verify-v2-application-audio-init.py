"""Original-x86 differential proof for Porsche.exe 004a66b0 audio init."""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE = 0x400000
ENTRY = 0x4a66b0
BODY_BYTES = 398
POST_SETUP = 0x4ab470
POST_SETUP_BYTES = 63
MODE_DATA_VA = 0x5b4ac0
MODE_DATA_BYTES = 0x80
STACK = 0x2210000
EXIT = 0x220fff0
MODE = 0x657c98
GATE = 0x657c9c
DEVICE_FOUND = 0x655d40
BUFFER = 0x655d44
POST_68 = 0x656868
RATE = 0x5deb48
CALLERS = ['004a68a2', '004a6af9']

# mode, gate, config-query HRESULT, device HRESULT, initial configured flag,
# timer rate, and descriptor pattern. Query fills all 124 output bytes.
CASES = [
    (0, 1, 0, 0, 0, 101, 0),
    (1, 1, 0, 0, 0, 100, 1),
    (2, 0, 0, 0, 1, 99, 0),
    (3, 0, -1, 0, 1, 100, 0),
    (3, 0, 0, -7, 1, 100, 0),
    (4, 0, 0, 1, 1, 100, 0),
    (0, 1, 0, 0, 0, 0xfffffffe, 0),
    (0, 1, 0, 0, 0, 0xffffffff, 0),
]


def read_va(image, module, va, size):
    rva = va - int(module['image_base'], 16)
    section = next(s for s in module['sections']
                   if s['rva'] <= rva and rva + size <= s['rva'] + s['raw_size'])
    offset = section['raw_offset'] + rva - section['rva']
    return image[offset:offset + size]


def descriptor_pattern(kind):
    value = bytearray((i * 37 + 11) & 0xff for i in range(124))
    value[8] = 0 if kind == 2 else 4
    value[0x0a] = 4
    value[0x0b:0x0f] = bytes((0x01, 0x02 if kind == 1 else 0x91, 0x30, 0))
    value[2:4] = bytes((0x44, 0xac))
    return value


def original(module, image, case_id):
    sys.path.insert(0, str(ROOT / 'local/tools/python-unicorn'))
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBP,
        UC_X86_REG_EBX, UC_X86_REG_EDI, UC_X86_REG_EIP, UC_X86_REG_ESP,
        UC_X86_REG_ESI)

    mode, gate, query_result, device_result, initial_found, rate, pattern = CASES[case_id]
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(BASE, 0x300000)
    for section in module['sections']:
        if section['raw_size']:
            start = section['raw_offset']
            uc.mem_write(BASE + section['rva'], image[start:start + section['raw_size']])
    uc.mem_map(0x2200000, 0x100000)
    uc.mem_map(0x710000, 0x10000)

    def put(address, value):
        uc.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def word(address):
        return struct.unpack('<I', uc.mem_read(address, 4))[0]

    def ret(machine, eax=0):
        esp = machine.reg_read(UC_X86_REG_ESP)
        return_address = word(esp)
        machine.reg_write(UC_X86_REG_EAX, eax & 0xffffffff)
        machine.reg_write(UC_X86_REG_ESP, esp + 4)
        machine.reg_write(UC_X86_REG_EIP, return_address)

    put(STACK, EXIT)
    regs = {UC_X86_REG_EBX: 0x11223344, UC_X86_REG_ESI: 0x22334455,
            UC_X86_REG_EDI: 0x33445566, UC_X86_REG_EBP: 0x44556677}
    for register, value in regs.items():
        uc.reg_write(register, value)
    uc.reg_write(UC_X86_REG_ESP, STACK)
    put(MODE, mode)
    put(GATE, gate)
    put(DEVICE_FOUND, initial_found)
    put(BUFFER, 0x22004000)
    put(POST_68, 0x0000aa55)
    put(RATE, rate)

    events = []
    applied = []
    query_calls = 0
    device_calls = 0
    local = STACK - 0x7c
    table_data = read_va(image, module, MODE_DATA_VA, MODE_DATA_BYTES)
    if hashlib.sha256(table_data).hexdigest() != '1971f9131f19a90589aa38b61716f75b521469ab8ef7799874f5de89f991ef01':
        raise AssertionError('audio mode table source bytes changed')

    def handle(machine, address, _size, _user):
        nonlocal query_calls, device_calls
        if address == EXIT:
            uc.emu_stop()
            return
        esp = uc.reg_read(UC_X86_REG_ESP)
        if address == 0x565950:
            events.append('prepare:00565950')
            ret(uc)
        elif address == 0x565680:
            output = word(esp + 4)
            events.append('query:00565680:124')
            query_calls += 1
            uc.mem_write(output, bytes(descriptor_pattern(pattern)))
            ret(uc, query_result)
        elif address == 0x5656d0:
            output = word(esp + 4)
            applied.append(bytes(uc.mem_read(output, 124)).hex())
            events.append('apply:005656d0:' + applied[-1])
            ret(uc)
        elif address == 0x565720:
            buffer, size, flags = word(esp + 4), word(esp + 8), word(esp + 12)
            events.append(f'device:00565720:{buffer:08x}:{size:08x}:{flags:08x}')
            device_calls += 1
            ret(uc, device_result)
        elif address == 0x53c380:
            interval = word(esp + 4)
            events.append(f'wait:0053c380:{interval:08x}')
            ret(uc)
        elif address == 0x565c70:
            args = [word(esp + 4 + 4 * i) for i in range(5)]
            events.append('period:00565c70:' + ':'.join(f'{arg:08x}' for arg in args))
            ret(uc)

    uc.hook_add(UC_HOOK_CODE, handle)
    try:
        uc.emu_start(ENTRY, 0, count=50000)
    except Exception as error:
        raise AssertionError(f'case {case_id}: original fault at EIP={uc.reg_read(UC_X86_REG_EIP):08x}') from error
    if uc.reg_read(UC_X86_REG_EIP) != EXIT:
        raise AssertionError(f'case {case_id}: original did not return')
    if uc.reg_read(UC_X86_REG_ESP) != STACK + 4:
        raise AssertionError(f'case {case_id}: caller stack cleanup mismatch')
    for register, expected in regs.items():
        if uc.reg_read(register) != expected:
            raise AssertionError(f'case {case_id}: callee-saved register changed')
    state = [f'{uc.reg_read(UC_X86_REG_EAX) & 0xff:x}', f'{word(DEVICE_FOUND):x}',
             f'{uc.mem_read(POST_68, 2)[0]:x}', f'{uc.mem_read(POST_68 + 1, 1)[0]:x}',
             f'{word(MODE):x}', f'{word(GATE):x}', f'{word(BUFFER):x}', f'{word(RATE):x}']
    return {'state': state, 'trace': events, 'descriptor': applied[-1] if applied else None,
            'query_calls': query_calls, 'device_calls': device_calls}


def native(probe, case_id):
    result = subprocess.run([str(probe), str(case_id)], text=True,
        capture_output=True, check=True)
    lines = result.stdout.splitlines()
    if len(lines) != 2 or not lines[0].startswith('state=') or not lines[1].startswith('trace='):
        raise AssertionError(f'case {case_id}: malformed native output {result.stdout!r}')
    trace = [] if not lines[1][6:] else lines[1][6:].split(';')
    apply = next((item[len('apply:005656d0:'):] for item in trace
                  if item.startswith('apply:005656d0:')), None)
    return {'state': lines[0][6:].split(','), 'trace': trace, 'descriptor': apply,
            'query_calls': sum(item.startswith('query:') for item in trace),
            'device_calls': sum(item.startswith('device:') for item in trace)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--report-dir', type=Path, required=True)
    args = parser.parse_args()
    args.report_dir.mkdir(parents=True, exist_ok=True)
    module = next(json.loads(line) for line in
        (ROOT / 'research/binary-index/static/binaries.jsonl').read_text().splitlines()
        if json.loads(line).get('file') == 'Porsche.exe')
    image = (ROOT / 'local/game' / module['path']).read_bytes()
    if hashlib.sha256(image).hexdigest() != SHA:
        raise AssertionError('original Porsche.exe SHA mismatch')
    functions = [json.loads(line) for line in
        (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
    by_va = {row['entry_va']: row for row in functions}
    for va, body_bytes, ranges in (
            ('004a66b0', BODY_BYTES, [['004a66b0', '004a683d']]),
            ('004ab470', POST_SETUP_BYTES, [['004ab470', '004ab4ae']])):
        row = by_va[va]
        if row['body_bytes'] != body_bytes or row['ranges'] != ranges:
            raise AssertionError(f'{va} index boundary changed: {row}')
    calls = [json.loads(line) for line in
        (ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl').read_text().splitlines()]
    edges = {(row.get('from_va'), row.get('to_va')) for row in calls}
    for caller in CALLERS:
        if (caller, '004a66b0') not in edges:
            raise AssertionError(f'caller edge missing: {caller} -> 004a66b0')
    expected_edges = {
        ('004a66bb', '00565950'), ('004a66c5', '00565680'),
        ('004a67ee', '005656d0'), ('004a6801', '00565720'),
        ('004a6829', '0053c380'), ('004a6831', '004ab470'),
        ('004ab486', '00565c70'), ('004ab498', '00565c70'),
    }
    if expected_edges - edges:
        raise AssertionError(f'callee edges missing: {sorted(expected_edges - edges)}')

    original_records = []
    for va, length, abi in (
            ('004a66b0', BODY_BYTES, 'cdecl, no arguments, AL boolean return tested by caller 004a6840'),
            ('004ab470', POST_SETUP_BYTES, 'cdecl, no arguments, caller ignores EAX')):
        body = read_va(image, module, int(va, 16), length)
        original_records.append({'va': va, 'body_bytes': length,
            'body_sha256': hashlib.sha256(body).hexdigest(), 'abi': abi})
    boundaries = []
    for va in ('00565950', '00565680', '005656d0', '00565720', '0053c380', '00565c70'):
        row = by_va[va]
        begin, end = row['ranges'][0]
        length = int(end, 16) - int(begin, 16) + 1
        body = read_va(image, module, int(va, 16), length)
        boundaries.append({'va': va, 'ranges': row['ranges'], 'body_bytes': length,
            'body_sha256': hashlib.sha256(body).hexdigest(), 'status': 'typed controlled boundary'})

    details = []
    for case_id in range(len(CASES)):
        expected = original(module, image, case_id)
        actual = native(args.probe, case_id)
        if expected != actual:
            raise AssertionError(f'case {case_id} mismatch\noriginal={expected}\nnative={actual}')
        details.append({'case': case_id, 'calls': len(expected['trace']), 'equal': True})

    compiled = [ROOT / 'iterations/v2/001-original-recovery/source/recovered/application_audio_init_probe.cpp',
        ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/application_audio_init.cpp',
        ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/application_state.cpp']
    paths = [
        'iterations/v2/001-original-recovery/runs/131-application-audio-init/CMakeLists.txt',
        'iterations/v2/001-original-recovery/runs/131-application-audio-init/README.md',
        'iterations/v2/001-original-recovery/source/include/porsche/application_audio_init.hpp',
        'iterations/v2/001-original-recovery/source/include/porsche/application_services.hpp',
        'iterations/v2/001-original-recovery/source/include/porsche/application_state.hpp',
        'iterations/v2/001-original-recovery/source/include/porsche/file_events.hpp',
        'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/application_services.cpp',
        'iterations/v2/001-original-recovery/source/recovered/application_audio_init_probe.cpp',
        'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/application_audio_init.cpp',
        'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/application_state.cpp',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/static/binaries.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/defined-data.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'scripts/research/v2_source_dependencies.py',
        'scripts/research/verify-v2-application-audio-init.py',
    ]
    table_data = read_va(image, module, MODE_DATA_VA, MODE_DATA_BYTES)
    report = {
        'schema': 1, 'module': 'Porsche.exe', 'sha256': SHA, 'module_sha256': SHA,
        'function_vas': ['004a66b0', '004ab470'],
        'full_function_vas': ['004ab470'], 'partial_function_vas': ['004a66b0'],
        'partial_reasons': {
            '004a66b0': 'the original has no negative-mode guard; -9 is within the pinned table window, but -10 reads before it. Caller 004e48b4 passes an opaque virtual-method result as mode without a proven range contract, so lower signed values remain outside the modeled input domain'
        },
        'cases': len(CASES), 'native_cpp_equal_original_x86': True,
        'original_functions': original_records, 'callee_boundaries': boundaries,
        'caller_edges': CALLERS,
        'state_vas': ['00657c98', '00657c9c', '00655d40', '00655d44',
                      '00656868', '00656869', '005deb48'],
        'original_mode_table': {'va': '005b4ac0', 'bytes': MODE_DATA_BYTES,
            'sha256': hashlib.sha256(table_data).hexdigest(),
            'note': 'raw source bytes retained for exact indexed stride reads; no field names inferred'},
        'boundary_contracts': [
            '00565950 pre-initialization body is external and its return is ignored',
            '00565680 controls the signed query result and copies all 31 dwords (124 bytes) into the local descriptor before the caller reads it',
            '005656d0 observes the final 124-byte descriptor; its return is ignored',
            '00565720 is the device creation boundary; original branches on signed EAX',
            '0053c380 timing wait and 00565c70 device-control effects are controlled; returns ignored',
            'the original has no negative-mode guard; -9 is covered by the pinned bytes, -10 is not, and the opaque caller-supplied signed mode has no proven range contract',
        ],
        'cases_detail': details,
        'source_sha256': source_hashes(paths, compiled_sources=compiled),
        'compiled_translation_units': [str(path) for path in compiled],
    }
    output = args.report_dir / 'verification.json'
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'verified {len(CASES)} original x86 application audio-init cases; report={output.resolve().relative_to(ROOT)}')


if __name__ == '__main__':
    main()
