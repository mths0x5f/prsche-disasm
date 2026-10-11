"""Differential proof of typed CRT float wrappers, text callbacks and x87 sign."""
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
BASE, MEM, EXIT, ARENA, TABLE = 0x400000, 0x2200000, 0x220f000, 0x2202000, 0x2204000
VAS = (0x5a3e33, 0x5a3e8d, 0x5a3edb, 0x5a3ef3, 0x5a41e3,
       0x5abc9f, 0x5abccc, 0x5abc73, 0x5abc89)
MANUAL = {0x5a3e8d: (0x5a3eda, 'ed1dde4ffdcb55e59e09a639bf532881b5a1bf4d92acf72bfc1cc239a06c4094'),
          0x5a3edb: (0x5a3ef2, '1a2009ab9c19b46f571fbc2149ff42fd7b018b05d1a4b9923230499935bf204d')}
sys.path.insert(0, str(ROOT / 'local/tools/python-unicorn'))
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ESI,
                              UC_X86_REG_EDI, UC_X86_REG_ESP, UC_X86_REG_EIP)


def mapped(image, module, va, size):
    rva = va - BASE
    s = next(s for s in module['sections']
             if s['rva'] <= rva and rva + size <= s['rva'] + max(s['raw_size'], s['vsize']))
    rel = rva - s['rva']
    n = max(0, min(size, s['raw_size'] - rel))
    off = s['raw_offset'] + rel
    return image[off:off + n] + bytes(size - n)


def make_uc(image, module):
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(BASE, 0x300000)
    for s in module['sections']:
        if s['raw_size']: uc.mem_write(BASE + s['rva'], image[s['raw_offset']:s['raw_offset'] + s['raw_size']])
    uc.mem_map(MEM, 0x10000)
    return uc


def cases():
    rows = []
    for text, width, decimal, mutation in itertools.product(
            (b'1', b'123', b'-123', b'+0123', b'e+003', b'E-009', b'123e+002', b'0', b'.5', b'123x', b'\xff123'),
            (-1, 0, 1, 2, 3), (ord('.'), ord(','), ord(':')), (0, 1, 2, 3)):
        rows.append({'kind': 't', 'op': 0, 'text': text, 'width': width, 'decimal': decimal, 'mutation': mutation})
    for text, decimal in itertools.product(
            (b'', b'1', b'0', b'123e+000', b'0.000', b'1.23000', b'1.200e+003', b'1.000E-019',
             b'.000', b'1.', b'-.000', b'1.0000', b'1,2000e+001', b'0:000', b'\xff.000'),
            (ord('.'), ord(','), ord(':'))):
        rows.append({'kind': 't', 'op': 1, 'text': text, 'width': 1, 'decimal': decimal, 'mutation': 0})
    bits = (0, 0x8000000000000000, 0x3ff0000000000000, 0xbff0000000000000,
            0x7ff0000000000000, 0xfff0000000000000, 1, 0x8000000000000001,
            0x000fffffffffffff, 0x800fffffffffffff, 0x0010000000000000,
            0x7fefffffffffffff, 0x7ff8000000000000, 0xfff8000000000001,
            0x7ff0000000000001, 0xfff0000000000001)
    for value, rounding, prefix in itertools.product(bits, (0, 0x400, 0x800, 0xc00), (0, 1, 3, 7)):
        rows.append({'kind': 's', 'bits': struct.pack('<Q', value), 'control': 0x37f | rounding, 'prefix': prefix})
    for op, wide, text in itertools.product(range(5), (0, 1, -1, 2), (b'', b'0', b'-1.25e+3', b'nan', b'\xff')):
        rows.append({'kind': 'p', 'op': op, 'wide': wide, 'text': text})
    for conversion, precision, caps in itertools.product((0, ord('e'), ord('E'), ord('f'), ord('F'), ord('g'), ord('G'), -1, 255),
                                                         (-1, 0, 1, 6, 17), (0, 1, -1)):
        rows.append({'kind': 'c', 'conversion': conversion, 'precision': precision, 'caps': caps})
    return rows


def protocol(c):
    kind = c['kind']
    if kind == 't': return f"t {c['op']} {c['width']} {c['decimal']} {c['mutation']} {c['text'].hex() or '-'}"
    if kind == 's': return f"s {c['bits'].hex()} {c['control']} {c['prefix']}"
    if kind == 'p': return f"p {c['op']} {c['wide']} {c['text'].hex() or '-'}"
    return f"c {c['conversion']} {c['precision']} {c['caps']}"


def original(uc, c):
    put = lambda p, value: uc.mem_write(p, struct.pack('<I', value & 0xffffffff))
    word = lambda p: struct.unpack('<I', uc.mem_read(p, 4))[0]
    def cstr(p):
        out = bytearray()
        while uc.mem_read(p + len(out), 1) != b'\0': out.extend(uc.mem_read(p + len(out), 1))
        return bytes(out)
    def signed(value): return struct.unpack('<i', struct.pack('<I', value))[0]
    events = []
    def hook(m, address, _size, _data):
        esp = m.reg_read(UC_X86_REG_ESP)
        arg = lambda i: word(esp + 4 + i * 4)
        def finish(result=0):
            m.reg_write(UC_X86_REG_EAX, result & 0xffffffff)
            m.reg_write(UC_X86_REG_EIP, word(esp))
            m.reg_write(UC_X86_REG_ESP, esp + 4)
        if address == EXIT: m.emu_stop()
        elif address == 0x5a2248:
            value = signed(arg(0)); events.append(f'lower:{value}')
            if c['mutation'] == 1: put(0x5e54e0, ord(','))
            if c['mutation'] == 2: put(0x5e54dc, 2)
            finish(value + 32 if ord('A') <= value <= ord('Z') else value)
        elif address == 0x5a2eae:
            value, mask = signed(arg(0)), arg(1)
            events.append(f'class:{value}:{mask}')
            if c['mutation'] == 3: put(0x5e54dc, 1)
            finish(mask if ord('0') <= value <= ord('9') else 0)
        elif address == 0x5ac716:
            flags = ':'.join(str(signed(arg(i))) for i in range(3, 7))
            events.append(f'parse:{cstr(arg(2)).hex()}:{int(word(arg(1)) == arg(2))}:{flags}')
            uc.mem_write(arg(0), struct.pack('<III', 0x76543210, 0xfedcba98, 0x89abcdef))
            put(arg(1), arg(2) + len(cstr(arg(2))))
            finish(-17)
        elif address == 0x5abb07:
            data = bytes(uc.mem_read(arg(0), 12))
            config = bytes(uc.mem_read(arg(2), 24))
            events.append(f'pack:{data.hex()}:{config.hex()}')
            a, b, _ = struct.unpack('<III', data)
            result = struct.pack('<II', a ^ 0x13579bdf, b ^ 0x2468ace0)
            uc.mem_write(arg(1), result[:8 if word(arg(2) + 16) == 64 else 4])
            finish(-39)
        elif address in (0x5a3f31, 0x5a4054, 0x5a4150):
            label = {0x5a3f31: 'scientific', 0x5a4054: 'fixed', 0x5a4150: 'general'}[address]
            events.append(f'{label}:{bytes(uc.mem_read(arg(0), 8)).hex()}:{signed(arg(2))}:{signed(arg(3)) if address != 0x5a4054 else 0}')
            uc.mem_write(arg(1), label[0].encode() + b'\0')
            finish(arg(1))
    handle = uc.hook_add(UC_HOOK_CODE, hook)
    kind = c['kind']
    if kind == 't':
        data = bytearray([0xcc] * 256)
        data[32:32 + len(c['text'])] = c['text']
        data[32 + len(c['text']):40 + len(c['text'])] = bytes(8)
        uc.mem_write(ARENA, bytes(data))
        table = bytearray(1024)
        for value in range(ord('0'), ord('9') + 1): table[256 + value * 2] = 4
        uc.mem_write(TABLE, bytes(table)); put(0x5e52d0, TABLE + 256)
        put(0x5e54dc, c['width']); put(0x5e54e0, c['decimal'])
        va, args = (0x5a3e33 if c['op'] == 0 else 0x5a3e8d), [ARENA + 32]
    elif kind == 's':
        uc.mem_write(ARENA, c['bits'])
        uc.mem_write(MEM + 0x800, struct.pack('<H', c['control']))
        uc.mem_write(MEM + 0x808, struct.pack('<d', 7.25))
        setup = bytes.fromhex('dbe3d92d') + struct.pack('<I', MEM + 0x800)
        for _ in range(c['prefix']): setup += bytes.fromhex('dd05') + struct.pack('<I', MEM + 0x808)
        setup += b'\xe9' + struct.pack('<i', EXIT - (MEM + 0x900 + len(setup) + 5))
        uc.mem_write(MEM + 0x900, setup)
        uc.emu_start(MEM + 0x900, 0, count=1000)
        va, args = 0x5a3edb, [ARENA]
    elif kind == 'p':
        data = bytearray([0xa5] * 256)
        data[32:33 + len(c['text'])] = c['text'] + b'\0'
        uc.mem_write(ARENA, bytes(data))
        uc.mem_write(MEM + 0x800, struct.pack('<III', 0x76543210, 0xfedcba98, 0x89abcdef))
        va = (0x5a3ef3, 0x5abc9f, 0x5abccc, 0x5abc73, 0x5abc89)[c['op']]
        if c['op'] == 0: args = [c['wide'] & 0xffffffff, ARENA + 128, ARENA + 32]
        elif c['op'] < 3: args = [ARENA + 128, ARENA + 32]
        else: args = [MEM + 0x800, ARENA + 128]
    else:
        uc.mem_write(ARENA, bytes([0xa5] * 256))
        uc.mem_write(MEM + 0x800, struct.pack('<Q', 0xc03123456789abcd))
        va, args = 0x5a41e3, [MEM + 0x800, ARENA + 128, c['conversion'] & 0xffffffff,
                             c['precision'] & 0xffffffff, c['caps'] & 0xffffffff]
    sp = MEM + 0xe000
    uc.mem_write(sp, struct.pack('<' + 'I' * (len(args) + 1), EXIT, *args))
    uc.reg_write(UC_X86_REG_ESP, sp)
    for reg in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI): uc.reg_write(reg, 0x12345678)
    uc.emu_start(va, 0, count=100000)
    assert uc.reg_read(UC_X86_REG_EIP) == EXIT
    assert uc.reg_read(UC_X86_REG_ESP) == sp + 4
    for reg in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI): assert uc.reg_read(reg) == 0x12345678
    value = uc.reg_read(UC_X86_REG_EAX)
    if kind == 's':
        save = b'\xdd\x35' + struct.pack('<I', MEM + 0xa00) + b'\xe9' + struct.pack('<i', EXIT - (MEM + 0x980 + 11))
        uc.mem_write(MEM + 0x980, save); uc.emu_start(MEM + 0x980, 0, count=1000)
        env = bytes(uc.mem_read(MEM + 0xa00, 108))
        result = {'kind': 'sign', 'return': value, 'control': struct.unpack_from('<H', env, 0)[0],
                  'status': struct.unpack_from('<H', env, 4)[0], 'tag': struct.unpack_from('<H', env, 8)[0],
                  'top_value': env[28:28 + c['prefix'] * 10].hex() if c['prefix'] else ''}
    elif kind == 't':
        result = {'kind': 'text', 'arena': bytes(uc.mem_read(ARENA, 256)).hex(), 'width': signed(word(0x5e54dc)),
                  'decimal': word(0x5e54e0), 'events': events}
    elif kind == 'p':
        result = {'kind': 'parse', 'arena': bytes(uc.mem_read(ARENA, 256)).hex(),
                  'return': 0 if c['op'] == 0 else signed(value), 'events': events}
    else: result = {'kind': 'convert', 'arena': bytes(uc.mem_read(ARENA, 256)).hex(), 'events': events}
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
    assert mapped(image, module, 0x5e54dc, 8) == struct.pack('<II', 1, 0x2e)
    assert mapped(image, module, 0x5b24c0, 8) == bytes(8)
    assert mapped(image, module, 0x5a3edb, 24).hex() == '8b442404dd00dc1dc0245b00dfe09e72046a0158c333c0c3'
    # Relocating that exact zero operand is a PE-supported data relocation,
    # not a patched comparison algorithm or replaced original instruction.
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    relocation_rva, relocation_size = struct.unpack_from('<II', image, pe + 24 + 96 + 5 * 8)
    relocations = mapped(image, module, BASE + relocation_rva, relocation_size)
    highlow, offset = set(), 0
    while offset < len(relocations):
        page, size = struct.unpack_from('<II', relocations, offset)
        assert size >= 8 and offset + size <= len(relocations)
        for (entry,) in struct.iter_unpack('<H', relocations[offset + 8:offset + size]):
            if entry >> 12 == 3: highlow.add(BASE + page + (entry & 0xfff))
        offset += size
    assert 0x5a3ee3 in highlow
    inputs = cases()
    native = [json.loads(x) for x in subprocess.run([str(args.probe.resolve())],
                 input='\n'.join(protocol(c) for c in inputs) + '\n', text=True,
                 capture_output=True, check=True).stdout.splitlines()]
    assert len(native) == len(inputs)
    uc = make_uc(image, module)
    comparisons = []
    unicorn_differences = []
    for c, row in zip(inputs, native):
        expected = original(uc, c)
        if c['kind'] == 's':
            hardware_original = row.pop('native_original')
            assert row == {'kind': 'sign', **hardware_original}, (protocol(c), row, hardware_original)
            if row != expected:
                unicorn_differences.append({'input': protocol(c), 'native_original': hardware_original,
                                            'unicorn_original': expected})
        else: assert row == expected, (protocol(c), row, expected)
        comparisons.append({'input': protocol(c), 'output': row})
    index = ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
    functions = {int(r['entry_va'], 16): r for r in map(json.loads, (index / 'functions.jsonl').read_text().splitlines())}
    bodies = {}
    manual = []
    for va in VAS:
        if va in MANUAL:
            from capstone import Cs, CS_ARCH_X86, CS_MODE_32
            end, sha = MANUAL[va]
            body = mapped(image, module, va, end - va + 1)
            assert hashlib.sha256(body).hexdigest() == sha and body[-1] == 0xc3
            instructions = list(Cs(CS_ARCH_X86, CS_MODE_32).disasm(body, va))
            assert sum(i.size for i in instructions) == len(body)
            assert all(b.address == a.address + a.size for a, b in zip(instructions, instructions[1:]))
            edges, returns = [], []
            for instruction in instructions:
                assert not instruction.mnemonic.startswith('call')
                if instruction.mnemonic.startswith('j'):
                    target = int(instruction.op_str, 16)
                    assert va <= target <= end
                    assert target in {i.address for i in instructions}
                    edges.append({'from_va': f'{instruction.address:08x}', 'to_va': f'{target:08x}',
                                  'mnemonic': instruction.mnemonic})
                elif instruction.mnemonic == 'ret': returns.append(f'{instruction.address:08x}')
            entry = {'ranges': [[f'{va:08x}', f'{end:08x}']], 'body_bytes': len(body)}
            file_offset = next(s['raw_offset'] + va - BASE - s['rva'] for s in module['sections']
                               if s['rva'] <= va - BASE < s['rva'] + s['raw_size'])
            manual.append({'module': 'Porsche.exe', 'sha256': SHA, 'entry_va': f'{va:08x}',
                           'ranges': entry['ranges'], 'body_bytes': len(body), 'body_sha256': sha,
                           'file_offset': file_offset,
                           'terminal_ret_vas': returns, 'control_flow_edges': edges,
                           'control_flow': 'contiguous; all branches internal; no calls; literal callback writer005a0f5d'})
        else:
            entry = functions[va]
            assert len(entry['ranges']) == 1
            begin, end = [int(p, 16) for p in entry['ranges'][0]]
            body = mapped(image, module, begin, end - begin + 1)
            assert len(body) == entry['body_bytes']
        bodies[f'{va:08x}'] = {'body_bytes': len(body), 'body_sha256': hashlib.sha256(body).hexdigest(), 'ranges': entry['ranges']}
    wanted = {'005a3e3c': '005a2248', '005a3e57': '005a2eae',
              '005a3f05': '005abc9f', '005a3f20': '005abccc',
              '005a4201': '005a4054', '005a4217': '005a4150', '005a422a': '005a3f31',
              '005abcb6': '005ac716', '005abcc2': '005abc73',
              '005abce3': '005ac716', '005abcef': '005abc89',
              '005abc80': '005abb07', '005abc96': '005abb07'}
    calls = [json.loads(x) for x in (index / 'calls.jsonl').read_text().splitlines()]
    evidence = [r for r in calls if wanted.get(r['from_va']) == r['to_va']]
    assert {r['from_va'] for r in evidence} == set(wanted)
    paths = ['iterations/v2/001-original-recovery/source/include/porsche/formatter_float_helpers.hpp',
             'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_float_helpers.cpp',
             'iterations/v2/001-original-recovery/source/recovered/formatter_float_helpers_probe.cpp',
             'iterations/v2/001-original-recovery/runs/147-float-helpers/CMakeLists.txt',
             'iterations/v2/001-original-recovery/runs/147-float-helpers/README.md',
             'scripts/research/verify-v2-formatter-float-helpers.py']
    report = {'schema': 1, 'module': 'Porsche.exe', 'sha256': SHA, 'module_sha256': SHA,
              'function_vas': [f'{va:08x}' for va in VAS], 'full_function_vas': [f'{va:08x}' for va in VAS],
              'partial_function_vas': [], 'functions': bodies, 'manual_entry_evidence': manual,
              'cases': len(comparisons), 'native_cpp_equal_original_x86': True, 'case_results': comparisons,
              'sign_native_original_x86_cases': sum(c['kind'] == 's' for c in inputs),
              'sign_original_highlow_relocation_va': '005a3ee3',
              'unicorn_original_differences': unicorn_differences,
              'index_calls': evidence,
              'source_sha256': source_hashes(paths),
              'unrecovered_dependencies': ['005a2248', '005a2eae', '005ac716', '005abb07', '005a3f31', '005a4054', '005a4150'],
              'limits': ['Converter005a41e3 is its full dispatch body, not the downstream decimal-formatting algorithms.',
                         'Decimal parsing/packing, classification/lowercase and formatting cores are typed recording boundaries.',
                         'Sign: actual24-byte original executes natively with only absolutezero operand relocation; hardware status/tag/TOP/80-bit stack compared.',
                         'Unicorn FPU status discrepancies are recorded separately; they are not masked or treated as original hardware behavior.',
                         'No unmasked FP exceptions, malformed string buffers, full decimal rounding engine or game/visual acceptance.']}
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    (args.report_dir / 'manual-entry-evidence.json').write_text(json.dumps(manual, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'ok': True, 'full_functions': len(VAS), 'cases': len(comparisons), 'native_cpp_equal_original_x86': True}))


if __name__ == '__main__': main()
