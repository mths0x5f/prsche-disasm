"""Differential original-x86/native proof of CRT float bootstrap and fatal closure."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE, MEM, EXIT = 0x400000, 0x2200000, 0x220f000
TERMINAL, HOOK = MEM + 0x1000, MEM + 0x1100
VAS = (0x5abee8, 0x5a2e22, 0x5a9736, 0x5a976f, 0x5a0f5d, 0x5a247f)
MESSAGE_IDS = (2, 8, 9, 10, 16, 17, 18, 19, 24, 25, 26, 27, 28, 120, 121, 122, 252, 255)


def cases():
    # kind, mode, app, message, hook (-2 absent/-1 unchanged/0..2 new mode),
    # module-name length, module failure, name. Code0 is original null-pointer UB.
    rows = []
    for code in MESSAGE_IDS:
        for mode, app in ((1, 2), (0, 2)):
            rows.append((4, mode, app, code, -2, 25, 0, f'message_{code}_{mode}_{app}'))
    for mode in (-1, 0, 1, 2):
        for app in (0, 1, 2):
            rows.append((3, mode, app, 2, -2, 25, 0, f'header_{mode}_{app}'))
            rows.append((2, mode, app, 2, -2, 25, 0, f'fatal_{mode}_{app}'))
    for kind in (0, 1, 7, 8):
        for mode in (0, 1):
            rows.append((kind, mode, 2, 2, -2, 25, 0, f'default_{kind}_{mode}'))
    for length in (0, 1, 58, 59, 60, 61, 100, 259):
        rows.append((4, 2, 2, 2, -2, length, 0, f'path_length_{length}'))
    rows.append((4, 2, 2, 2, -2, 25, 1, 'module_failure'))
    for kind in (2, 3):
        for mode in (-1, 0, 2):
            rows.append((kind, 1, 2, 2, mode, 60, 0, f'hook_mode_{kind}_{mode}'))
    for code in (-2147483648, -1, 1, 3, 253, 256, 2147483647):
        rows.append((4, 1, 1, code, -2, 25, 0, f'unknown_{code}'))
    for code in (0, 255, -1):
        rows.append((6, 0, 2, code, -2, 25, 0, f'quick_exit_{code}'))
    rows.append((5, 0, 2, 2, -2, 25, 0, 'bootstrap'))
    return rows


def mapped(image, module, va, size):
    rva = va - BASE
    section = next(s for s in module['sections']
                   if s['rva'] <= rva and rva + size <= s['rva'] + max(s['raw_size'], s['vsize']))
    rel = rva - section['rva']
    count = max(0, min(size, section['raw_size'] - rel))
    off = section['raw_offset'] + rel
    return image[off:off + count] + bytes(size - count)


def original(image, module, case, connected_strings=False):
    sys.path.insert(0, str(ROOT / 'local/tools/python-unicorn'))
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
    from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX,
                                  UC_X86_REG_ESI, UC_X86_REG_EDI,
                                  UC_X86_REG_ESP, UC_X86_REG_EIP)
    kind, mode, app, message, hook_mode, name_length, module_fail, name = case
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(BASE, 0x300000)
    for s in module['sections']:
        if s['raw_size']:
            uc.mem_write(BASE + s['rva'], image[s['raw_offset']:s['raw_offset'] + s['raw_size']])
    uc.mem_map(MEM, 0x10000)
    put = lambda p, value: uc.mem_write(p, struct.pack('<I', value & 0xffffffff))
    word = lambda p: struct.unpack('<I', uc.mem_read(p, 4))[0]
    def cstr(p):
        if p == 0:
            raise AssertionError('original consumed null string')
        out = bytearray()
        while True:
            b = bytes(uc.mem_read(p + len(out), 1))
            if b == b'\0': return bytes(out)
            out.extend(b)
    events, writes = [], []
    put(0x6afcf4, mode); put(0x5e52cc, app)
    put(0x6afec0, 0 if hook_mode == -2 else HOOK)
    put(0x5e52c8, TERMINAL)
    api = {0x5b2064: MEM + 0x1200, 0x5b20e4: MEM + 0x1300, 0x5b21f0: MEM + 0x1400}
    for cell, target in api.items(): put(cell, target)
    if connected_strings:
        put(0x6b001c,MEM+0x1500);put(0x6b0020,0);put(0x6b0024,0)
    # Defaults execute the exact same original address with each consumer ABI.
    va = {0: 0x5abee8, 1: 0x5abee8, 2: 0x5a2e22, 3: 0x5a9736,
          4: 0x5a976f, 5: 0x5a0f5d, 6: 0x5a247f, 7: 0x5abee8, 8: 0x5abee8}[kind]
    args = {0: [0, 0, 0, 0, 0], 1: [0], 2: [message], 3: [],
            4: [message], 5: [], 6: [message], 7: [0, 0, 0], 8: [0]}[kind]
    sp = MEM + 0xe000
    uc.mem_write(sp, struct.pack('<' + 'I' * (len(args) + 1), EXIT, *[a & 0xffffffff for a in args]))
    uc.reg_write(UC_X86_REG_ESP, sp)
    for reg in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI): uc.reg_write(reg, 0x12345678)
    terminated = False
    def finish(ret=0, cleanup=0):
        esp = uc.reg_read(UC_X86_REG_ESP)
        destination = word(esp)
        uc.reg_write(UC_X86_REG_EAX, ret & 0xffffffff)
        uc.reg_write(UC_X86_REG_ESP, esp + 4 + cleanup)
        uc.reg_write(UC_X86_REG_EIP, destination)
    def code(_m, address, _size, _data):
        nonlocal terminated
        esp = uc.reg_read(UC_X86_REG_ESP)
        arg = lambda i: word(esp + 4 + i * 4)
        if address == EXIT: uc.emu_stop()
        elif address == TERMINAL:
            events.append(f'exit:{arg(0)}'); terminated = True; uc.emu_stop()
        elif address == HOOK:
            events.append(f'hook:{hook_mode}')
            if hook_mode >= 0: put(0x6afcf4, hook_mode)
            finish()
        elif address == api[0x5b2064]:
            events.append(f'module:{int(arg(0) == 0)}:{arg(2)}')
            if not module_fail:
                uc.mem_write(arg(1), bytes(ord('A') + i % 26 for i in range(name_length)) + b'\0')
            finish(0 if module_fail else name_length, 12)
        elif address == api[0x5b20e4]:
            signed = struct.unpack('<i', struct.pack('<I', arg(0)))[0]
            events.append(f'handle:{signed}'); finish(0x1234, 4)
        elif address == api[0x5b21f0]:
            events.append(f'write:{arg(0)}:{arg(2)}:{word(arg(3))}:{int(arg(4) == 0)}:{cstr(arg(1)).hex()}')
            put(arg(3), arg(2)); finish(1, 20)
        elif address in (0x5aa4e0, 0x5aa4f0, 0x5a28a0):
            if connected_strings:return
            dst, src = arg(0), cstr(arg(1))
            if address == 0x5a28a0:
                events.append(f'copy_n:{arg(2)}:{src.hex()}')
                data = (src + bytes(arg(2)))[:arg(2)]
            else:
                events.append(('copy:' if address == 0x5aa4e0 else 'concat:') + src.hex())
                data = src + b'\0'
                if address == 0x5aa4f0: dst += len(cstr(dst))
            uc.mem_write(dst, data); finish(arg(0))
        elif address == 0x5acfb9:
            if connected_strings:return
            events.append(f'dialog:{arg(2)}:{cstr(arg(1)).hex()}:{cstr(arg(0)).hex()}'); finish(17)
        elif connected_strings and address == MEM+0x1500:
            assert arg(0)==0
            events.append(f'dialog:{arg(3)}:{cstr(arg(2)).hex()}:{cstr(arg(1)).hex()}');finish(17,16)
        elif address == 0x5a2490:
            events.append(f'shutdown:{arg(0)}:{arg(1)}:{arg(2)}'); finish()
    def memory_write(_m, _access, address, size, value, _data):
        if kind == 5 and 0x5e5788 <= address <= 0x5e579c:
            writes.append([f'{address:08x}', f'{value:08x}', size])
    uc.hook_add(UC_HOOK_CODE, code)
    uc.hook_add(UC_HOOK_MEM_WRITE, memory_write)
    uc.emu_start(va, 0, count=100000)
    writer = False
    if kind == 5:
        targets = [0x5a41e3, 0x5a3e8d, 0x5a3ef3, 0x5a3e33, 0x5a3edb, 0x5a41e3]
        writer = [word(0x5e5788 + i * 4) for i in range(6)] == targets and uc.reg_read(UC_X86_REG_EAX) == targets[0]
        expected_order = [1, 0, 2, 3, 4, 5]
        assert writes == [[f'{0x5e5788 + i * 4:08x}', f'{targets[i]:08x}', 4] for i in expected_order]
    if not terminated:
        assert uc.reg_read(UC_X86_REG_EIP) == EXIT
        assert uc.reg_read(UC_X86_REG_ESP) == sp + 4
        for reg in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI): assert uc.reg_read(reg) == 0x12345678
    return {'name': name, 'terminated': terminated, 'mode': struct.unpack('<i', uc.mem_read(0x6afcf4, 4))[0],
            'app': app, 'writer': writer, 'events': events}, writes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--report-dir', required=True, type=Path)
    parser.add_argument('--connected-strings', action='store_true')
    args = parser.parse_args()
    module = next(json.loads(line) for line in (ROOT / 'research/binary-index/static/binaries.jsonl').read_text().splitlines()
                  if json.loads(line)['file'] == 'Porsche.exe')
    image = (ROOT / 'local/game' / module['path']).read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA
    assert mapped(image, module, 0x5e52c8, 8) == struct.pack('<II', 0x5a247f, 2)
    assert mapped(image, module, 0x6afcf4, 4) == bytes(4)
    assert mapped(image, module, 0x6afec0, 4) == bytes(4)
    assert mapped(image, module, 0x5e5788, 24) == struct.pack('<6I', *([0x5abee8] * 6))
    initial = json.loads(subprocess.run([str(args.probe.resolve()), '--initial'],
                                        capture_output=True, text=True, check=True).stdout)
    assert initial == {'initial_native_identities': True}
    index = ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
    functions = {int(r['entry_va'], 16): r for r in map(json.loads, (index / 'functions.jsonl').read_text().splitlines())}
    calls = [json.loads(line) for line in (index / 'calls.jsonl').read_text().splitlines()]
    wanted = {'005a2e2b': '005a9736', '005a2e34': '005a976f',
              '005a9752': '005a976f', '005a9768': '005a976f',
              '005a2487': '005a2490', '005abeea': '005a2e22'}
    evidence = [r for r in calls if wanted.get(r['from_va']) == r['to_va']]
    assert {r['from_va'] for r in evidence} == set(wanted)
    bodies = {}
    verified_vas=VAS+((0x5aa4e0,0x5aa4f0,0x5a28a0,0x5acfb9,0x5a6730) if args.connected_strings else ())
    for va in verified_vas:
        entry = functions[va]
        assert len(entry['ranges']) == 1
        begin, end = [int(p, 16) for p in entry['ranges'][0]]
        body = mapped(image, module, begin, end - begin + 1)
        assert len(body) == entry['body_bytes']
        bodies[f'{va:08x}'] = {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(), 'ranges': entry['ranges']}
    comparisons, writer_writes = [], []
    for case in cases():
        expected, writes = original(image, module, case,args.connected_strings)
        native = json.loads(subprocess.run([str(args.probe.resolve()), *map(str, case)],
                                           capture_output=True, text=True, check=True).stdout)
        assert native == expected, (case, native, expected)
        comparisons.append({'input': list(case), 'output': expected})
        writer_writes.extend(writes)
    paths = ['iterations/v2/001-original-recovery/source/include/porsche/formatter_bootstrap.hpp',
             'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_bootstrap.cpp',
             'iterations/v2/001-original-recovery/source/recovered/formatter_bootstrap_probe.cpp',
             'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_runtime.cpp',
             'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_runtime_storage.cpp',
             'iterations/v2/001-original-recovery/runs/140-formatter-bootstrap/CMakeLists.txt',
             'iterations/v2/001-original-recovery/runs/140-formatter-bootstrap/README.md',
             'scripts/research/verify-v2-formatter-bootstrap.py']
    if args.connected_strings:
        paths += ['iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_strings.cpp',
                  'iterations/v2/001-original-recovery/runs/143-runtime-network-integration/CMakeLists.txt',
                  'iterations/v2/001-original-recovery/runs/144-crt-strings/CMakeLists.txt']
    report = {'schema': 1, 'module': 'Porsche.exe', 'sha256': SHA, 'module_sha256': SHA,
              'function_vas': [f'{va:08x}' for va in verified_vas],
              'full_function_vas': [f'{va:08x}' for va in verified_vas], 'partial_function_vas': [],
              'function_bodies': bodies, 'cases': len(comparisons),
              'native_cpp_equal_original_x86': True, 'comparisons': comparisons,
              'bootstrap_write_order': writer_writes,
              'native_initial_identities': initial,
              'index_calls': evidence,
              'disassembly_sha256': hashlib.sha256((ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_bytes()).hexdigest(),
              'source_sha256': source_hashes(paths),
              'recovered_dependencies': ['005a6730', '005a2490'],
              'unrecovered_dependencies': ['005a41e3', '005a3e8d', '005a3ef3', '005a3e33', '005a3edb',
                                           '005aa4e0', '005aa4f0', '005a28a0', '005acfb9'],
              'limits': ['Scoped original-x86 proof: OS/string/dialog/shutdown calls are recorded fixture boundaries.',
                         'Real 005a6730 executes in both versions; real shutdown005a2490 is not executed here.',
                         'Runtime float targets remain typed unresolved bodies and are never executed.',
                         'Native typed adapters share original005abee8 identity, not native pointer equality.',
                         'Message0 reaches original null text; malformed pointers/unterminated module names excluded.',
                         'Void function incidental EAX values are not promoted to return contracts.',
                         'No live CRT/game/visual acceptance.']}
    report['connected_original_strings']=args.connected_strings
    if args.connected_strings:
        report['recovered_dependencies'] += ['005aa4e0','005aa4f0','005a28a0','005acfb9']
        report['unrecovered_dependencies']=[v for v in report['unrecovered_dependencies'] if v not in
            ('005aa4e0','005aa4f0','005a28a0','005acfb9')]
        report['limits'][0]='OS/MessageBox/shutdown effects are controlled; actual recovered string/dialog bodies execute on both sides.'
        suffix=mapped(image,module,0x5aa551,0x7f)
        report['shared_copy_suffix']={'begin_va':'005aa551','bytes':len(suffix),'sha256':hashlib.sha256(suffix).hexdigest()}
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'ok': True, 'full_functions': len(verified_vas), 'cases': len(comparisons), 'native_cpp_equal_original_x86': True}))


if __name__ == '__main__': main()
