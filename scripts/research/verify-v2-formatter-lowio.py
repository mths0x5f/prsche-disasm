"""Original-x86 differential proof of CRT lowio init and descriptor lifecycle."""
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
BASE, MEM, EXIT = 0x400000, 0x2200000, 0x220f000
POOL, RESERVED = MEM + 0x10000, MEM + 0x40000
ERRNO, DOSERRNO = MEM + 0x600, MEM + 0x604
VAS = (0x5a953e, 0x5ab4c6, 0x5ab5e9, 0x5ab665, 0x5ab6e4, 0x5ab726, 0x5ab785)
sys.path.insert(0, str(ROOT / 'local/tools/python-unicorn'))
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EBP, UC_X86_REG_ESI,
                              UC_X86_REG_EDI, UC_X86_REG_ESP, UC_X86_REG_EIP)


def mapped(image, module, va, size):
    rva = va - BASE
    s = next(s for s in module['sections']
             if s['rva'] <= rva and rva + size <= s['rva'] + max(s['raw_size'], s['vsize']))
    rel = rva - s['rva']; n = max(0, min(size, s['raw_size'] - rel))
    off = s['raw_offset'] + rel
    return image[off:off + n] + bytes(size - n)


def make_uc(image, module):
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(BASE, 0x300000)
    for s in module['sections']:
        if s['raw_size']: uc.mem_write(BASE + s['rva'], image[s['raw_offset']:s['raw_offset'] + s['raw_size']])
    uc.mem_map(MEM, 0x50000)
    return uc


def cases():
    rows = []
    for count, std_mode, pattern, types in itertools.product((-1, 0, 1, 3, 31, 32, 33, 63, 64, 65, 100),
                                                            (0, 1, 2), (0, 1), (0, 1, 2, 3)):
        rows.append(('i', 1, 1, count, 0, std_mode, pattern, types, 0))
    for count, failure in ((0, 1), (33, 2), (65, 2), (65, 3), (100, 4), (2048, 0), (2050, 0), (2050, 3)):
        rows.append(('i', 1, 1, count, failure, 0, 1, 1, 0))
    for present, pointer in ((0, 0), (0, 1), (1, 0)):
        rows.append(('i', present, pointer, 65, 0, 2, 1, 1, 0))
    rows.append(('i', 1, 1, 33, 0, 0, 0, 0, 5))
    for scenario in (0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11): rows.append(('a', scenario))
    for op, id, app, old, flags in itertools.product((0, 1, 2), (0, 1, 2, 3, 31, 32, 63, 64, 0xffffffff),
                                                     (0, 1, 2), (0, 0xffffffff, 0x7000), (0, 1, 0x81)):
        rows.append(('l', op, id, app, old, flags, 1, 0))
    for op, id, state in itertools.product((3, 4), (0, 5, 31, 32, 63), (0, 1, 3)):
        rows.append(('l', op, id, 2, 0x7000, 1, state, 0))
    for op, id in ((0, 0), (1, 0), (3, 5)):
        rows.append(('l', op, id, 1, 0xffffffff if op == 0 else 0x7000, 1, 0, 4))
    return rows


def original(uc, case):
    put = lambda p, v: uc.mem_write(p, struct.pack('<I', v & 0xffffffff))
    word = lambda p: struct.unpack('<I', uc.mem_read(p, 4))[0]
    def signed(v): return struct.unpack('<i', struct.pack('<I', v))[0]
    def seed_banks(n):
        nonlocal allocated
        allocated = n; put(0x6c02e0, n * 32)
        for index in range(n):
            put(0x6c01e0 + index * 4, POOL + index * 0x480)
            for slot in range(32):
                p = POOL + index * 0x480 + slot * 36
                put(p, 0x7000 + index * 32 + slot); uc.mem_write(p + 4, b'\1'); put(p + 8, 1)
    uc.mem_write(POOL, bytes([0xa5]) * (64 * 0x480))
    uc.mem_write(RESERVED, bytes([0xcc]) * (4 + 2050 * 5))
    uc.mem_write(0x6c01e0, bytes(256)); put(0x6c02e0, 0)
    put(ERRNO, 41); put(DOSERRNO, 0x1234)
    allocated = allocations = 0
    fail_allocation = std_mode = inherited_pattern = type_pattern = mutation = count = 0
    present = pointer = False
    kind = case[0]
    if kind == 'i':
        _, present, pointer, count, fail_allocation, std_mode, inherited_pattern, type_pattern, mutation = case
        put(RESERVED, count)
        for id in range(max(0, count)):
            pattern = id % 5
            flag = 1 if inherited_pattern == 0 else 0 if pattern == 1 else 9 if pattern == 2 else 0xc1 if pattern == 3 else 0x21
            uc.mem_write(RESERVED + 4 + id, bytes([flag]))
            put(RESERVED + 4 + count + id * 4, 0xffffffff if inherited_pattern and pattern == 0 else 0x1000 + id)
        va, args = 0x5a953e, []
    elif kind == 'a':
        scenario = case[1]
        if scenario == 6: seed_banks(64)
        elif scenario == 11: seed_banks(2)
        elif scenario: seed_banks(1)
        if scenario in (1, 2, 3, 4, 9, 10):
            slot = 0 if scenario == 9 else 5
            uc.mem_write(POOL + slot * 36 + 4, b'\0'); put(POOL + slot * 36 + 8, 1 if scenario == 2 else 0)
        if scenario == 3: mutation = 1
        if scenario == 4:
            mutation = 2; uc.mem_write(POOL + 6 * 36 + 4, b'\0'); put(POOL + 6 * 36 + 8, 0)
        if scenario == 7: fail_allocation = 1
        if scenario == 10: mutation = 3
        if scenario == 11:
            mutation = 4; uc.mem_write(POOL + 31 * 36 + 4, b'\0'); put(POOL + 31 * 36 + 8, 0)
        va, args = 0x5ab4c6, []
    else:
        _, op, id, app, old, flags, lock_state, mutation = case
        put(0x5e52cc, app); seed_banks(2)
        if id < 64:
            p = POOL + (id >> 5) * 0x480 + (id & 31) * 36
            put(p, old); uc.mem_write(p + 4, bytes([flags])); put(p + 8, lock_state)
        va = (0x5ab5e9, 0x5ab665, 0x5ab6e4, 0x5ab726, 0x5ab785)[op]
        args = [id, 0x87654321] if op == 0 else [id]
    api = {cell: MEM + 0x1000 + i * 0x100 for i, cell in enumerate(
        (0x5b2120, 0x5b20e0, 0x5b20e4, 0x5b20e8, 0x5b20c4, 0x5b207c, 0x5b2078, 0x5b206c))}
    for cell, target in api.items(): put(cell, target)
    events = []; fatal = False
    def hook(m, address, _size, _data):
        nonlocal allocated, allocations, fatal
        esp = m.reg_read(UC_X86_REG_ESP)
        arg = lambda i: word(esp + 4 + i * 4)
        def finish(v=0, cleanup=0):
            m.reg_write(UC_X86_REG_EAX, v & 0xffffffff)
            m.reg_write(UC_X86_REG_EIP, word(esp)); m.reg_write(UC_X86_REG_ESP, esp + 4 + cleanup)
        if address == EXIT: m.emu_stop()
        elif address == 0x5a3be5:
            events.append(f'malloc:{arg(0)}'); allocations += 1
            if allocations == fail_allocation: finish(0)
            else:
                assert arg(0) == 0x480 and allocated < 64
                allocation = POOL + allocated * 0x480; allocated += 1; finish(allocation)
        elif address == 0x5a2e22:
            events.append(f'fatal:{arg(0)}'); fatal = True; m.emu_stop()
        elif address in (0x5a4ba4, 0x5a4c05):
            id = arg(0); enter = address == 0x5a4ba4
            events.append(f'{"lock" if enter else "unlock"}:{id}')
            if enter and id == 17 and mutation == 1: put(POOL + 5 * 36 + 8, 2)
            if not enter and id == 17 and mutation == 4: put(0x6c01e0, POOL + 0x480)
            finish()
        elif address == api[0x5b2120]:
            events.append('startup')
            data = bytearray(68); struct.pack_into('<H', data, 50, int(bool(present)))
            struct.pack_into('<I', data, 52, RESERVED if pointer else 0)
            uc.mem_write(arg(0), bytes(data)); finish(cleanup=4)
        elif address == api[0x5b20e0]:
            handle = arg(0); events.append(f'type:{handle}')
            if mutation == 5 and 0x1000 <= handle < 0x1000 + 2050:
                id = handle - 0x1000; put(RESERVED + 4 + count + id * 4, 0x9000 + id)
                uc.mem_write(RESERVED + 4 + id, b'\x41')
            value = 1 if type_pattern == 0 else handle % 4 if type_pattern == 1 else 0x100 + handle % 4 if type_pattern == 2 else 0
            finish(value, 4)
        elif address == api[0x5b20e4]:
            id = signed(arg(0)); events.append(f'getstd:{id}'); slot = -10 - id
            value = 0x3000 + slot if std_mode == 0 else 0xffffffff if std_mode == 1 else 0 if slot == 0 else 0xffffffff if slot == 1 else 0x3002
            finish(value, 4)
        elif address == api[0x5b20e8]:
            events.append(f'count:{arg(0)}'); finish(arg(0) + 7, 4)
        elif address == api[0x5b20c4]:
            events.append(f'setstd:{signed(arg(0))}:{arg(1)}')
            if mutation == 4: put(0x6c01e0, POOL + 0x480)
            finish(0, 8)
        elif address == api[0x5b207c]:
            p = arg(0); events.append(f'init:{p - POOL}'); uc.mem_write(p, bytes([0x5a]) * 24)
            if mutation == 3: put(p - 4, 3)
            finish(cleanup=4)
        elif address == api[0x5b2078]:
            p = arg(0); events.append(f'enter:{p - POOL}')
            if mutation == 2 and p - POOL == 5 * 36 + 12:
                uc.mem_write(POOL + 5 * 36 + 4, bytes([bytes(uc.mem_read(POOL + 5 * 36 + 4, 1))[0] | 1]))
            finish(cleanup=4)
        elif address == api[0x5b206c]: events.append(f'leave:{arg(0) - POOL}'); finish(cleanup=4)
        elif address == 0x5a669e: events.append('errno'); finish(ERRNO)
        elif address == 0x5a66a7: events.append('doserrno'); finish(DOSERRNO)
    handle = uc.hook_add(UC_HOOK_CODE, hook)
    sp = MEM + 0x8000
    uc.mem_write(sp, struct.pack('<' + 'I' * (len(args) + 1), EXIT, *args))
    uc.reg_write(UC_X86_REG_ESP, sp)
    for reg in (UC_X86_REG_EBX, UC_X86_REG_EBP, UC_X86_REG_ESI, UC_X86_REG_EDI): uc.reg_write(reg, 0x12345678)
    uc.emu_start(va, 0, count=500000)
    if not fatal:
        assert uc.reg_read(UC_X86_REG_EIP) == EXIT
        assert uc.reg_read(UC_X86_REG_ESP) == sp + 4
        for reg in (UC_X86_REG_EBX, UC_X86_REG_EBP, UC_X86_REG_ESI, UC_X86_REG_EDI): assert uc.reg_read(reg) == 0x12345678
    value = 0 if fatal or (kind == 'l' and case[1] >= 3) else uc.reg_read(UC_X86_REG_EAX)
    result = {'return': value, 'fatal': fatal, 'limit': word(0x6c02e0), 'errno': signed(word(ERRNO)),
              'doserrno': word(DOSERRNO), 'table': [word(0x6c01e0 + i * 4) - POOL if word(0x6c01e0 + i * 4) else -1 for i in range(64)],
              'pool': bytes(uc.mem_read(POOL, allocated * 0x480)).hex(), 'events': events}
    uc.hook_del(handle)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--report-dir', required=True, type=Path)
    args = parser.parse_args()
    module = next(json.loads(x) for x in (ROOT / 'research/binary-index/static/binaries.jsonl').read_text().splitlines()
                  if json.loads(x)['file'] == 'Porsche.exe')
    image = (ROOT / 'local/game' / module['path']).read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA
    inputs = cases()
    native = [json.loads(x) for x in subprocess.run([str(args.probe.resolve())],
                 input='\n'.join(' '.join(map(str, c)) for c in inputs) + '\n', text=True,
                 capture_output=True, check=True).stdout.splitlines()]
    assert len(native) == len(inputs)
    uc = make_uc(image, module); comparisons = []
    for c, row in zip(inputs, native):
        expected = original(uc, c)
        assert row == expected, (c, {k: v for k, v in row.items() if k != 'pool'},
                                {k: v for k, v in expected.items() if k != 'pool'},
                                'pool_equal', row['pool'] == expected['pool'])
        summary = {k: v for k, v in row.items() if k != 'pool'}
        summary['pool_bytes'] = len(row['pool']) // 2
        summary['pool_sha256'] = hashlib.sha256(bytes.fromhex(row['pool'])).hexdigest()
        comparisons.append({'input': list(c), 'output': summary})
    index = ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
    functions = {int(r['entry_va'], 16): r for r in map(json.loads, (index / 'functions.jsonl').read_text().splitlines())}
    bodies = {}
    for va in VAS:
        entry = functions[va]; assert len(entry['ranges']) == 1
        begin, end = [int(p, 16) for p in entry['ranges'][0]]
        body = mapped(image, module, begin, end - begin + 1); assert len(body) == entry['body_bytes']
        bodies[f'{va:08x}'] = {'body_bytes': len(body), 'body_sha256': hashlib.sha256(body).hexdigest(), 'ranges': entry['ranges']}
    paths = ['iterations/v2/001-original-recovery/source/include/porsche/formatter_lowio.hpp',
             'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_lowio.cpp',
             'iterations/v2/001-original-recovery/source/recovered/formatter_lowio_probe.cpp',
             'iterations/v2/001-original-recovery/runs/152-crt-lowio/CMakeLists.txt',
             'iterations/v2/001-original-recovery/runs/152-crt-lowio/README.md',
             'scripts/research/verify-v2-formatter-lowio.py']
    calls = [json.loads(x) for x in (index / 'calls.jsonl').read_text().splitlines()]
    expected_imports = {0x5b2120: 'GetStartupInfoA', 0x5b20e0: 'GetFileType',
                        0x5b20e4: 'GetStdHandle', 0x5b20e8: 'SetHandleCount',
                        0x5b20c4: 'SetStdHandle', 0x5b207c: 'InitializeCriticalSection',
                        0x5b2078: 'EnterCriticalSection', 0x5b206c: 'LeaveCriticalSection'}
    imports = [json.loads(x) for x in (ROOT / 'research/binary-index/static/imports.jsonl').read_text().splitlines()]
    actual_imports = {BASE + int(r['iat_rva'], 16): r['symbol'] for r in imports if r['path'] == module['path']}
    for cell, symbol in expected_imports.items(): assert actual_imports[cell] == symbol
    report = {'schema': 1, 'module': 'Porsche.exe', 'sha256': SHA, 'module_sha256': SHA,
              'function_vas': [f'{va:08x}' for va in VAS], 'full_function_vas': [f'{va:08x}' for va in VAS],
              'partial_function_vas': [], 'functions': bodies, 'cases': len(comparisons),
              'native_cpp_equal_original_x86': True, 'case_results': comparisons,
              'index_calls': [c for c in calls if c.get('from_function') in {f'{va:08x}' for va in VAS}],
              'iat_imports': {f'{cell:08x}': symbol for cell, symbol in expected_imports.items()},
              'source_sha256': source_hashes(paths),
              'unrecovered_dependencies': ['005a3be5', '005a4ba4', '005a4c05', '005a669e', '005a66a7'],
              'limits': ['malloc/fatal/CRTlock/error-cell and Win32 APIs are recording boundaries; no live inheritance/concurrency proof.',
                         'All allocated36-byte records and unchanged poison bytes,64pointer cells,limit,errors,returns and ordered API events compared.',
                         'lock/unlock domain is allocated nonnegative fd; original contains no validation on those entries.',
                         'Attach/detach do not close OS handles; no guessed CloseHandle or cleanup behavior.',
                         'No game launch or visual acceptance.']}
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'ok': True, 'full_functions': len(VAS), 'cases': len(comparisons), 'native_cpp_equal_original_x86': True}))


if __name__ == '__main__': main()
