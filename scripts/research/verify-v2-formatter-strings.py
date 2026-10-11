"""Compare CRT string memory accesses and lazy dialog state against original x86."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys

from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE, MEM, EXIT, ARENA = 0x400000, 0x2200000, 0x220f000, 0x2202000
VAS = (0x5aa4e0, 0x5aa4f0, 0x5a28a0, 0x5acfb9)
sys.path.insert(0, str(ROOT / 'local/tools/python-unicorn'))
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ESI,
                              UC_X86_REG_EDI, UC_X86_REG_ESP, UC_X86_REG_EIP)


def mapped(image, module, va, size):
    rva = va - BASE
    s = next(s for s in module['sections']
             if s['rva'] <= rva and rva + size <= s['rva'] + max(s['raw_size'], s['vsize']))
    rel = rva - s['rva']
    count = max(0, min(size, s['raw_size'] - rel))
    off = s['raw_offset'] + rel
    return image[off:off + count] + bytes(size - count)


def make_uc(image, module):
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(BASE, 0x300000)
    for s in module['sections']:
        if s['raw_size']:
            uc.mem_write(BASE + s['rva'], image[s['raw_offset']:s['raw_offset'] + s['raw_size']])
    uc.mem_map(MEM, 0x10000)
    return uc


def start(uc, va, args):
    sp = MEM + 0xe000
    uc.mem_write(sp, struct.pack('<' + 'I' * (len(args) + 1), EXIT, *args))
    uc.reg_write(UC_X86_REG_ESP, sp)
    for reg in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI): uc.reg_write(reg, 0x12345678)
    uc.emu_start(va, 0, count=100000)
    assert uc.reg_read(UC_X86_REG_EIP) == EXIT
    assert uc.reg_read(UC_X86_REG_ESP) == sp + 4
    for reg in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI): assert uc.reg_read(reg) == 0x12345678
    return uc.reg_read(UC_X86_REG_EAX)


def content(length, salt):
    # Includes80/81/ff and the magic predicate's nonzero high-byte false positives.
    return bytes(((i * 73 + salt * 19) % 255) + 1 for i in range(length))


def string_cases():
    for operation, sa, da, length in itertools.product((0, 1), range(4), range(4),
                                                       (0, 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 31, 63, 127)):
        data = bytearray([0x8d] * 1024)
        source, destination = 128 + sa, 512 + da
        data[source:source + length + 1] = content(length, sa) + b'\0'
        if operation == 1:
            prefix = content((length * 3 + sa) % 9, da + 2)
            data[destination:destination + len(prefix) + 1] = prefix + b'\0'
        yield {'name': f'string_{operation}_{sa}_{da}_{length}', 'operation': operation,
               'destination': destination, 'source': source, 'count': 0, 'initial': bytes(data)}
    for sa, da, length, count in itertools.product(range(4), range(4),
                  (0, 1, 2, 3, 4, 7, 8, 15, 31, 63), (0, 1, 2, 3, 4, 5, 7, 8, 9, 15, 16, 17, 32, 65)):
        data = bytearray([0xa5] * 1024)
        source, destination = 128 + sa, 512 + da
        data[source:source + length + 1] = content(length, sa) + b'\0'
        yield {'name': f'bounded_{sa}_{da}_{length}_{count}', 'operation': 2,
               'destination': destination, 'source': source, 'count': count, 'initial': bytes(data)}
    # Machine-defined overlap domains, separately labelled; no memmove claim.
    for operation, sa, delta, length in itertools.product((0, 2), range(4), (0, -1, -2, -3, -4, -7), (0, 1, 3, 7, 15, 31)):
        data = bytearray([0xc3] * 1024)
        source = 256 + sa
        data[source:source + length + 1] = content(length, sa) + b'\0'
        yield {'name': f'overlap_down_{operation}_{sa}_{delta}_{length}', 'operation': operation,
               'destination': source + delta, 'source': source, 'count': length + 5, 'initial': bytes(data)}
    # A bounded copy reads a complete aligned DWORD before writing; forward
    # overlap may propagate those original word snapshots instead of bytes.
    for sa, delta, count in itertools.product(range(4), (1, 2, 3, 4, 5), (1, 3, 4, 7, 8, 17, 32)):
        data = bytearray([0xf1] * 1024)
        source = 256 + sa
        data[source:source + 65] = content(64, sa) + b'\0'
        yield {'name': f'overlap_forward_bounded_{sa}_{delta}_{count}', 'operation': 2,
               'destination': source + delta, 'source': source, 'count': count, 'initial': bytes(data)}
    for sa in range(4):
        data = bytearray([0xa5] * 1024)
        source, destination = 256 + sa, 256 + sa
        data[source] = 0
        yield {'name': f'concat_empty_self_{sa}', 'operation': 1,
               'destination': destination, 'source': source, 'count': 0, 'initial': bytes(data)}
    yield {'name': 'zero_count_one_past', 'operation': 2, 'destination': 1024,
           'source': 1024, 'count': 0, 'initial': bytes([0xa5] * 1024)}


def original_string(uc, case):
    uc.mem_write(ARENA, case['initial'])
    trace = []
    def memory(m, access, address, size, value, _data):
        if ARENA <= address < ARENA + 1024:
            assert address + size <= ARENA + 1024
            # Unicorn callbacks run before writes and before reads.
            if access == 16: value = int.from_bytes(m.mem_read(address, size), 'little')
            trace.append(f'{"r" if access == 16 else "w"}:{address - ARENA}:{size}:{value}')
    handles = [uc.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, memory),
               uc.hook_add(UC_HOOK_CODE, lambda m, p, _s, _d: m.emu_stop() if p == EXIT else None)]
    operation = case['operation']
    args = [ARENA + case['destination'], ARENA + case['source']]
    if operation == 2: args.append(case['count'])
    value = start(uc, VAS[operation], args)
    for handle in handles: uc.hook_del(handle)
    return {'kind': 'string', 'return_offset': value - ARENA,
            'arena': bytes(uc.mem_read(ARENA, 1024)).hex(), 'events': trace}


def dialog_cases():
    for seed, mask, active, popup in itertools.product((0, 1, 3, 5, 7), range(8), (0, 0x4000), (0, 0x5000)):
        yield (seed, mask, active, popup, -7, 0, 2, 0)
    for seed in (0, 2, 4, 6): yield (seed, 7, 0x4000, 0x5000, 29, 1, 2, 0)
    for mutation in (1, 2, 3):
        yield (0, 7, 0x4000, 0x5000, 39, 0, 2, mutation)
        yield (7, 0, 0x4000, 0x5000, 39, 0, 2, mutation)


def original_dialog(uc, case):
    seed, mask, active, popup, result, load_fail, repeat, mutation = case
    load, proc, box, get_active, get_popup, alternate = [MEM + 0x1000 + i * 0x100 for i in range(6)]
    put = lambda p, v: uc.mem_write(p, struct.pack('<I', v & 0xffffffff))
    word = lambda p: struct.unpack('<I', uc.mem_read(p, 4))[0]
    def cstr(p):
        b = bytearray()
        while uc.mem_read(p + len(b), 1) != b'\0': b.extend(uc.mem_read(p + len(b), 1))
        return bytes(b)
    for cell, value in ((0x5b2050, load), (0x5b205c, proc),
                        (0x6b001c, box if seed & 1 else 0),
                        (0x6b0020, get_active if seed & 2 else 0),
                        (0x6b0024, get_popup if seed & 4 else 0)): put(cell, value)
    uc.mem_write(ARENA, b'fatal text\0caption\0')
    events = []
    def hook(m, address, _size, _data):
        esp = m.reg_read(UC_X86_REG_ESP)
        arg = lambda i: word(esp + 4 + 4 * i)
        def finish(value, cleanup):
            m.reg_write(UC_X86_REG_EIP, word(esp))
            m.reg_write(UC_X86_REG_ESP, esp + 4 + cleanup)
            m.reg_write(UC_X86_REG_EAX, value & 0xffffffff)
        if address == EXIT: m.emu_stop()
        elif address == load:
            events.append('load:' + cstr(arg(0)).hex()); finish(0 if load_fail else 0x3000, 4)
        elif address == proc:
            name = cstr(arg(1))
            events.append(f'proc:{arg(0)}:{name.hex()}')
            bit, target = {b'MessageBoxA': (1, box), b'GetActiveWindow': (2, get_active),
                           b'GetLastActivePopup': (4, get_popup)}[name]
            finish(target if mask & bit else 0, 8)
        elif address == get_active:
            events.append('active')
            if mutation == 1: put(0x6b0024, 0)
            if mutation == 3: put(0x6b001c, alternate)
            finish(active, 0)
        elif address == get_popup:
            events.append(f'popup:{arg(0)}')
            if mutation == 2: put(0x6b001c, alternate)
            finish(popup, 4)
        elif address in (box, alternate):
            prefix = 'message' if address == box else 'alternate'
            events.append(f'{prefix}:{arg(0)}:{cstr(arg(1)).hex()}:{cstr(arg(2)).hex()}:{arg(3)}')
            finish(result + int(address == alternate), 16)
    handle = uc.hook_add(UC_HOOK_CODE, hook)
    returns = []
    for _ in range(repeat):
        value = start(uc, 0x5acfb9, [ARENA, ARENA + 11, 0x12010])
        returns.append(struct.unpack('<i', struct.pack('<I', value))[0])
    uc.hook_del(handle)
    cells = [0 if word(0x6b001c) == 0 else 1 if word(0x6b001c) == box else 2,
             int(word(0x6b0020) != 0), int(word(0x6b0024) != 0)]
    return {'kind': 'dialog', 'returns': returns, 'cells': cells, 'events': events}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--production-probe', type=Path)
    parser.add_argument('--report-dir', required=True, type=Path)
    args = parser.parse_args()
    module = next(json.loads(x) for x in (ROOT / 'research/binary-index/static/binaries.jsonl').read_text().splitlines()
                  if json.loads(x)['file'] == 'Porsche.exe')
    image = (ROOT / 'local/game' / module['path']).read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA
    assert mapped(image, module, 0x6b001c, 12) == bytes(12)
    strings, dialogs = list(string_cases()), list(dialog_cases())
    inputs = [f"s {c['operation']} {c['destination']} {c['source']} {c['count']} {c['initial'].hex()}" for c in strings]
    inputs += ['d ' + ' '.join(map(str, c)) for c in dialogs]
    native = [json.loads(x) for x in subprocess.run([str(args.probe.resolve())],
               input='\n'.join(inputs) + '\n', text=True, capture_output=True, check=True).stdout.splitlines()]
    assert len(native) == len(strings) + len(dialogs)
    production_equal = None
    if args.production_probe:
        production = [json.loads(x) for x in subprocess.run([str(args.production_probe.resolve())],
                       input='\n'.join(inputs) + '\n', text=True, capture_output=True, check=True).stdout.splitlines()]
        assert len(production) == len(native)
        for case, expected in zip(production, native):
            if expected['kind'] == 'string':
                assert case == {**expected, 'events': []}
            else: assert case == expected
        production_equal = True
    uc = make_uc(image, module)
    rows = []
    reads = writes = 0
    for i, c in enumerate(strings):
        expected = original_string(uc, c)
        assert native[i] == expected, (c['name'], native[i], expected)
        reads += sum(e.startswith('r:') for e in expected['events'])
        writes += sum(e.startswith('w:') for e in expected['events'])
        rows.append({'name': c['name'], 'operation': c['operation'], 'destination': c['destination'],
                     'source': c['source'], 'count': c['count'],
                     'initial_sha256': hashlib.sha256(c['initial']).hexdigest(),
                     'output_sha256': hashlib.sha256(bytes.fromhex(expected['arena'])).hexdigest(),
                     'memory_trace_sha256': hashlib.sha256(json.dumps(expected['events']).encode()).hexdigest(),
                     'memory_accesses': len(expected['events']), 'return_offset': expected['return_offset']})
    dialog_rows = []
    for i, c in enumerate(dialogs, len(strings)):
        expected = original_dialog(uc, c)
        assert native[i] == expected, (c, native[i], expected)
        dialog_rows.append({'input': list(c), 'output': expected})
    index = ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
    functions = {int(r['entry_va'], 16): r for r in map(json.loads, (index / 'functions.jsonl').read_text().splitlines())}
    bodies = {}
    for va in VAS:
        entry = functions[va]
        assert len(entry['ranges']) == 1
        begin, end = [int(p, 16) for p in entry['ranges'][0]]
        body = mapped(image, module, begin, end - begin + 1)
        assert len(body) == entry['body_bytes']
        bodies[f'{va:08x}'] = {'body_bytes': len(body), 'body_sha256': hashlib.sha256(body).hexdigest(), 'ranges': entry['ranges']}
    suffix = mapped(image, module, 0x5aa551, 0x5aa5d0 - 0x5aa551)
    assert mapped(image, module, 0x5aa4e5, 2) == bytes.fromhex('eb6a')
    wanted = {'005a97f2': '005aa4e0', '005a9834': '005a28a0',
              '005a9855': '005aa4f0', '005a988e': '005acfb9'}
    calls = [json.loads(x) for x in (index / 'calls.jsonl').read_text().splitlines()]
    evidence = [r for r in calls if wanted.get(r['from_va']) == r['to_va']]
    assert {r['from_va'] for r in evidence} == set(wanted)
    paths = ['iterations/v2/001-original-recovery/source/include/porsche/formatter_strings.hpp',
             'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_strings.cpp',
             'iterations/v2/001-original-recovery/source/recovered/formatter_strings_probe.cpp',
             'iterations/v2/001-original-recovery/runs/144-crt-strings/CMakeLists.txt',
             'iterations/v2/001-original-recovery/runs/144-crt-strings/README.md',
             'scripts/research/verify-v2-formatter-strings.py']
    report = {'schema': 1, 'module': 'Porsche.exe', 'sha256': SHA, 'module_sha256': SHA,
              'function_vas': [f'{va:08x}' for va in VAS], 'full_function_vas': [f'{va:08x}' for va in VAS],
              'partial_function_vas': [], 'functions': bodies,
              'shared_suffix': {'begin_va': '005aa551', 'end_va_inclusive': '005aa5cf',
                                'bytes': len(suffix), 'sha256': hashlib.sha256(suffix).hexdigest(),
                                'entry_jump_va': '005aa4e5', 'entry_jump_hex': 'eb6a'},
              'cases': len(strings) + len(dialogs), 'string_cases': len(strings), 'dialog_cases': len(dialogs),
              'native_cpp_equal_original_x86': True, 'full_arena_and_memory_trace_equal': True,
              'uninstrumented_native_equal_instrumented': production_equal,
              'memory_reads_compared': reads, 'memory_writes_compared': writes,
              'case_results': rows, 'dialog_case_results': dialog_rows,
              'index_calls': evidence, 'source_sha256': source_hashes(paths),
              'unrecovered_dependencies': ['KERNEL32.LoadLibraryA', 'KERNEL32.GetProcAddress'],
              'limits': ['Private memory tracing observes exact ordered byte/word/DWORD read/write tuples; compiled out in production.',
                         'Every string case compares entire1024-byte arena and return pointer, including controlled overlapping spans.',
                         'Finite controlled machine overlap cases do not imply memmove semantics or a valid ISO C strcpy/strcat overlap contract.',
                         'Lazy dialog proof records LoadLibrary/GetProcAddress and resolved callbacks; no real OS dialogs execute.',
                         'No malformed/unmapped/nonterminated string or concurrency acceptance; no live game/visual acceptance.']}
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'ok': True, 'full_functions': len(VAS), 'cases': report['cases'],
                      'string_cases': len(strings), 'dialog_cases': len(dialogs),
                      'ordered_reads': reads, 'ordered_writes': writes}))


if __name__ == '__main__': main()
