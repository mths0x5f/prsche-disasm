"""Run 430: generates VC6 C++ for straight-line Porsche.exe functions (no branches).

A small symbolic execution of the original instructions: registers and pushed stack slots hold
C expressions; every memory read becomes a temporary at its place in the instruction order,
every store a statement, every call a statement with the arguments the original pushes and its
convention (the callee's RET size; thiscall when the callee reads ECX). The result is EAX when
the function writes it. Functions using anything else (branches, x87, string ops, division,
register inputs other than ECX, locals below ESP) are skipped.

Each generated function gets a spec (humanized/specs/<batch>_NN.json, 80 per file, the
oracle's compile limit) and must pass verify-v2-humanized-430.py before it is kept.

Usage: py -3 scripts/research/humanize-generate-430.py --batch g1 [--limit N]
"""
import argparse
import importlib.util
import json
import re
from pathlib import Path

import capstone
from capstone import x86

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
REGS = ('eax', 'ecx', 'edx', 'ebx', 'esp', 'ebp', 'esi', 'edi')
SUB8 = {'al': 'eax', 'cl': 'ecx', 'dl': 'edx', 'bl': 'ebx'}
SUB8H = {'ah': 'eax', 'ch': 'ecx', 'dh': 'edx', 'bh': 'ebx'}
SUB16 = {'ax': 'eax', 'cx': 'ecx', 'dx': 'edx', 'bx': 'ebx', 'si': 'esi', 'di': 'edi', 'bp': 'ebp'}
TYPE = {1: 'unsigned char', 2: 'unsigned short', 4: 'unsigned long'}
STYPE = {1: 'signed char', 2: 'short', 4: 'long'}
CC = {'e': '==', 'ne': '!=', 'a': '>', 'ae': '>=', 'b': '<', 'be': '<=', 'g': '>', 'ge': '>=', 'l': '<', 'le': '<='}
SIGNED = {'g', 'ge', 'l', 'le'}


class Skip(Exception):
    pass


class Gen:
    def __init__(self, va, ins, callee_info, catalog_name):
        self.va, self.ins, self.callee_info = va, ins, callee_info
        self.name = catalog_name
        self.regs = {r: None for r in REGS}
        self.regs['ecx'] = 'self'
        self.regs['ebx'], self.regs['esi'], self.regs['edi'], self.regs['ebp'] = 'init_ebx', 'init_esi', 'init_edi', 'init_ebp'
        self.self_used = False
        self.sp = 0
        self.stack = {}
        self.lines = []
        self.temps = 0
        self.deps = {}
        self.flags = None
        self.args_used = set()
        self.addr_args = set()
        self.index_args = set()
        self.self_addr = False
        self.globals = {}
        self.stubs = {}
        self.forwarders = []
        self.eax_written = False
        self.ret_pop = 0

    # ---- values ------------------------------------------------------------------------
    def tmp(self, expr, ctype='U'):
        self.temps += 1
        t = f't{self.temps}'
        self.deps[t] = self.expand(expr) | ({'LOAD'} if expr.startswith('*(') else set())
        self.lines.append(f'    {ctype} {t} = {expr};')
        return t

    def reg(self, name):
        if name in SUB8:
            return f'({self.reg(SUB8[name])} & 0xffu)'
        if name in SUB8H:
            return f'(({self.reg(SUB8H[name])} >> 8) & 0xffu)'
        if name in SUB16:
            return f'({self.reg(SUB16[name])} & 0xffffu)'
        v = self.regs[name]
        if v is None or v.startswith('init_'):
            raise Skip(f'register input {name}')
        if v == 'self':
            self.self_used = True
        return v

    def set_reg(self, name, value):
        if name in SUB8:
            r = SUB8[name]
            self.regs[r] = self.tmp(f'({self.reg(r)} & 0xffffff00u) | ({value} & 0xffu)')
        elif name in SUB8H:
            r = SUB8H[name]
            self.regs[r] = self.tmp(f'({self.reg(r)} & 0xffff00ffu) | (({value} & 0xffu) << 8)')
        elif name in SUB16:
            r = SUB16[name]
            self.regs[r] = self.tmp(f'({self.reg(r)} & 0xffff0000u) | ({value} & 0xffffu)')
        else:
            self.regs[name] = value if re.fullmatch(r'\w+', value) else self.tmp(value)
            name = name
        if name in ('eax', 'al', 'ax', 'ah'):
            self.eax_written = True

    def address(self, i, op):
        m = op.mem
        if m.segment:
            raise Skip('segment')
        base = i.reg_name(m.base) if m.base else None
        index = i.reg_name(m.index) if m.index else None
        if base == 'esp' or index == 'esp' or base == 'ebp':
            raise Skip('stack/ebp address')
        parts = []
        if base:
            v = self.reg(base)
            parts.append(v)
            self.note_addr(v)
        if index:
            v = self.reg(index)
            parts.append(f'{v} * {m.scale}u' if m.scale != 1 else v)
            self.note_index(v)
        disp = m.disp & 0xffffffff
        if not parts:
            return None, disp
        if disp >= 0x80000000:
            parts.append(f'- 0x{(-m.disp) & 0xffffffff:x}u')
            return '(' + ' + '.join(parts[:-1]) + ' ' + parts[-1] + ')', disp
        if disp > 0xf00 and disp < 0x400000:
            raise Skip('large displacement')
        if disp:
            parts.append(f'0x{disp:x}u')
        return '(' + ' + '.join(parts) + ')' if len(parts) > 1 else parts[0], disp

    def expand(self, v):
        found = set(re.findall(r'\b(a\d|self)\b', v))
        if v.startswith('*('):
            found.add('LOAD')
        for t in re.findall(r'\bt\d+\b', v):
            found |= self.deps.get(t, set())
        return found

    def note_addr(self, v):
        v = ' '.join(self.expand(v))
        for a in re.findall(r'\ba(\d)\b', v):
            self.addr_args.add(int(a))
        if re.search(r'\bself\b', v):
            self.self_addr = True

    def note_index(self, v):
        deps = self.expand(v)
        if 'LOAD' in deps or 'self' in deps:
            raise Skip('index from memory')
        for a in deps:
            if a.startswith('a'):
                self.index_args.add(int(a[1:]))

    def stack_slot(self, i, op):
        m = op.mem
        if m.base and i.reg_name(m.base) == 'esp' and not m.index:
            return self.sp + m.disp
        return None

    def read(self, i, op, size=None):
        size = size or op.size
        if op.type == x86.X86_OP_REG:
            return self.reg(i.reg_name(op.reg))
        if op.type == x86.X86_OP_IMM:
            return f'0x{op.imm & 0xffffffff:x}u'
        slot = self.stack_slot(i, op)
        if slot is not None:
            if size != 4 or slot % 4:
                raise Skip('odd stack read')
            if slot in self.stack:
                return self.stack[slot]
            if slot >= 4:
                k = (slot - 4) // 4
                if k > 3:
                    raise Skip('more than 4 arguments')
                self.args_used.add(k)
                return f'a{k}'
            raise Skip('stack read below')
        addr, disp = self.address(i, op)
        if addr is None:
            if disp < 0x400000 or disp >= 0x6e3000:
                raise Skip('absolute outside image')
            self.globals.setdefault(disp, set()).add(size)
            target = f'0x{disp:08x}u'
        else:
            target = addr
        return self.tmp(f'*({TYPE[size]} *){target}')

    def write(self, i, op, value):
        if op.type == x86.X86_OP_REG:
            self.set_reg(i.reg_name(op.reg), value)
            return
        size = op.size
        slot = self.stack_slot(i, op)
        if slot is not None:
            raise Skip('stack write')
        addr, disp = self.address(i, op)
        if addr is None:
            if disp < 0x400000 or disp >= 0x6e3000:
                raise Skip('absolute outside image')
            self.globals.setdefault(disp, set()).add(size)
            addr = f'0x{disp:08x}u'
        self.lines.append(f'    *({TYPE[size]} *){addr} = ({TYPE[size]}){value};')

    # ---- instructions -----------------------------------------------------------------
    def run(self):
        for k, i in enumerate(self.ins):
            ops = i.operands
            m = i.mnemonic
            if m == 'ret':
                self.ret_pop = ops[0].imm if ops else 0
                if self.sp != 0:
                    raise Skip('unbalanced stack')
                for r in ('ebx', 'esi', 'edi', 'ebp'):
                    if self.regs[r] != f'init_{r}':
                        raise Skip(f'{r} not restored')
                return
            if m in ('nop', 'int3'):
                continue
            if m == 'mov':
                if ops[0].size != ops[1].size and ops[1].type != x86.X86_OP_IMM:
                    raise Skip('mov size')
                self.write(i, ops[0], self.read(i, ops[1]))
            elif m in ('movzx', 'movsx'):
                v = self.read(i, ops[1])
                if m == 'movsx':
                    v = f'(U)(long)({STYPE[ops[1].size]}){v}'
                self.write(i, ops[0], v)
            elif m == 'lea':
                if ops[1].mem.base and i.reg_name(ops[1].mem.base) == 'esp':
                    raise Skip('lea of stack')
                addr, disp = self.address(i, ops[1])
                self.write(i, ops[0], addr if addr is not None else f'0x{disp:x}u')
            elif m == 'push':
                v = self.read(i, ops[0]) if not (ops[0].type == x86.X86_OP_REG and i.reg_name(ops[0].reg) in ('ebx', 'esi', 'edi', 'ebp')
                                                and self.regs[i.reg_name(ops[0].reg)].startswith('init_')) \
                    else self.regs[i.reg_name(ops[0].reg)]
                self.sp -= 4
                self.stack[self.sp] = v
            elif m == 'pop':
                v = self.stack.pop(self.sp, None)
                if v is None:
                    raise Skip('pop of unknown')
                self.sp += 4
                r = i.reg_name(ops[0].reg)
                if v.startswith('init_'):
                    if v != f'init_{r}':
                        raise Skip('pop of a saved register elsewhere')
                    self.regs[r] = v
                else:
                    self.set_reg(r, v)
            elif m in ('add', 'sub') and ops[0].type == x86.X86_OP_REG and i.reg_name(ops[0].reg) == 'esp':
                if ops[1].type != x86.X86_OP_IMM:
                    raise Skip('esp arithmetic')
                n = ops[1].imm if m == 'add' else -ops[1].imm
                if n < 0:
                    raise Skip('locals')
                for o in range(self.sp, self.sp + n, 4):
                    v = self.stack.pop(o, None)
                    if v and v.startswith('init_'):
                        raise Skip('saved register dropped')
                self.sp += n
            elif m in ('add', 'sub', 'and', 'or', 'xor'):
                if m == 'xor' and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and ops[0].reg == ops[1].reg:
                    self.write(i, ops[0], '0u')
                    self.flags = ('logic', '0u')
                    continue
                a, b = self.read(i, ops[0]), self.read(i, ops[1])
                op = {'add': '+', 'sub': '-', 'and': '&', 'or': '|', 'xor': '^'}[m]
                r = self.tmp(f'{a} {op} {b}') if ops[0].type == x86.X86_OP_REG else f'({a} {op} {b})'
                if ops[0].size < 4:
                    r = f'({r} & 0x{(1 << (8 * ops[0].size)) - 1:x}u)'
                self.write(i, ops[0], r)
                self.flags = ('cmp', a, b) if m == 'sub' else (('logic', r) if m in ('and', 'or', 'xor') else ('arith', r))
                if m == 'sub':
                    self.flags = ('sub', a, b, r)
            elif m in ('inc', 'dec', 'neg', 'not'):
                a = self.read(i, ops[0])
                r = {'inc': f'{a} + 1u', 'dec': f'{a} - 1u', 'neg': f'0u - {a}', 'not': f'~{a}'}[m]
                if ops[0].size < 4:
                    r = f'({r}) & 0x{(1 << (8 * ops[0].size)) - 1:x}u'
                if ops[0].size != 4 and m in ('neg',):
                    raise Skip('narrow neg')
                self.write(i, ops[0], r)
                self.flags = ('neg', a) if m == 'neg' else ('arith', r)
            elif m in ('shl', 'shr', 'sar'):
                if ops[0].size != 4:
                    raise Skip('narrow shift')
                a = self.read(i, ops[0])
                n = self.read(i, ops[1]) if len(ops) > 1 else '1u'
                if ops[1:] and ops[1].type == x86.X86_OP_REG:
                    n = f'({n} & 31u)'
                r = f'(U)((long){a} >> {n})' if m == 'sar' else f'{a} {"<<" if m == "shl" else ">>"} {n}'
                self.write(i, ops[0], r)
                self.flags = ('arith', self.regs.get(i.reg_name(ops[0].reg), 'x') if ops[0].type == x86.X86_OP_REG else 'x')
            elif m == 'imul':
                if len(ops) == 1:
                    raise Skip('one-operand imul')
                a = self.read(i, ops[1] if len(ops) == 3 else ops[0])
                b = self.read(i, ops[2] if len(ops) == 3 else ops[1])
                if ops[0].size != 4:
                    raise Skip('narrow imul')
                self.write(i, ops[0], f'(U)((long){a} * (long){b})')
                self.flags = None
            elif m == 'cdq':
                self.set_reg('edx', f'(U)((long){self.reg("eax")} >> 31)')
            elif m in ('cmp', 'test'):
                a, b = self.read(i, ops[0]), self.read(i, ops[1])
                self.flags = ('sub', a, b, None) if m == 'cmp' else ('logic', f'({a} & {b})')
            elif m.startswith('set'):
                self.write(i, ops[0], self.condition(m[3:]))
            elif m == 'sbb' and ops[0].type == x86.X86_OP_REG and ops[1].type == x86.X86_OP_REG and ops[0].reg == ops[1].reg:
                self.write(i, ops[0], f'(U)(0u - (U)({self.carry()}))')
                self.flags = None
            elif m == 'call':
                self.call(i, k)
            else:
                raise Skip(f'instruction {m}')
        raise Skip('no ret')

    def condition(self, cc):
        f = self.flags
        if f is None:
            raise Skip('unknown flags')
        if f[0] == 'sub':
            a, b = f[1], f[2]
            if cc in CC:
                if cc in SIGNED:
                    return f'(U)((long){a} {CC[cc]} (long){b})'
                return f'(U)({a} {CC[cc]} {b})'
            if cc in ('s', 'ns'):
                return f'(U)((long)({a} - {b}) {"<" if cc == "s" else ">="} 0)'
        if f[0] in ('logic', 'arith'):
            r = f[1]
            if cc in ('e', 'ne'):
                return f'(U)({r} {CC[cc]} 0u)'
            if cc in ('s', 'ns'):
                return f'(U)((long){r} {"<" if cc == "s" else ">="} 0)'
            if f[0] == 'logic' and cc in SIGNED:
                return f'(U)((long){r} {CC[cc]} 0)'
        raise Skip(f'condition {cc} on {f[0]}')

    def carry(self):
        f = self.flags
        if f and f[0] == 'neg':
            return f'{f[1]} != 0u'
        if f and f[0] == 'sub':
            return f'{f[1]} < {f[2]}'
        raise Skip('carry')

    def call(self, i, k):
        target = int(i.op_str, 16)
        info = self.callee_info(target)
        if info is None:
            raise Skip('unknown callee')
        pops, reads_ecx = info
        if pops:
            n = pops // 4
        else:
            # the caller's cleanup need not follow the call directly: find the first instruction
            # that moves esp after it (add esp / pop ecx|edx); anything else touching esp first is
            # not provable here
            n = 0
            j = k + 1
            while j < len(self.ins):
                x = self.ins[j]
                if x.mnemonic == 'add' and x.op_str.startswith('esp, '):
                    n = x.operands[1].imm // 4
                    break
                if x.mnemonic == 'pop' and x.op_str in ('ecx', 'edx'):
                    while j < len(self.ins) and self.ins[j].mnemonic == 'pop' and self.ins[j].op_str in ('ecx', 'edx'):
                        n += 1
                        j += 1
                    break
                if x.mnemonic in ('call', 'ret', 'push', 'pop', 'leave') or 'esp' in x.op_str:
                    break
                j += 1
        args = []
        for o in range(n):
            v = self.stack.get(self.sp + 4 * o)
            if v is None or v.startswith('init_'):
                raise Skip('call arguments')
            args.append(v)
        conv = 'cdecl'
        this = None
        if reads_ecx:
            this = self.reg('ecx')
            conv = 'thiscall'
        elif pops:
            conv = 'stdcall'
        self.stubs[f'{target:08x}'] = [n, conv]
        arglist = ', '.join(args)
        if conv == 'thiscall':
            fw = f'Call_{target:08x}_{self.va}'
            if not any(f'struct {fw} ' in x for x in self.forwarders):
                self.forwarders.append(
                    f'struct {fw} {{\n    U call({", ".join("U" for _ in args) or "void"});\n}};\n\n'
                    f'/* the original {target:08x} (thiscall) */\n__declspec(naked) U {fw}::call({", ".join("U" for _ in args) or "void"})\n'
                    f'{{\n    __asm mov eax, 0x{target:08x}\n    __asm jmp eax\n}}\n')
            r = self.tmp(f'(({fw} *){this})->call({arglist})')
        else:
            types = ', '.join('U' for _ in args) or 'void'
            r = self.tmp(f'((U (__{conv} *)({types}))0x{target:08x}u)({arglist})')
        if pops:
            for o in range(n):
                self.stack.pop(self.sp + 4 * o, None)
            self.sp += pops
        self.regs['eax'] = r
        self.eax_written = True
        self.regs['ecx'] = None
        self.regs['edx'] = None
        self.flags = None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch', required=True)
    ap.add_argument('--limit', type=int, default=100000)
    ap.add_argument('--max-bytes', type=int, default=200)
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('b', ROOT / 'scripts/research/build-v2-lowered-exe-430.py')
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    data = b.PE_PATH.read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    funcs = {json.loads(l)['entry_va']: json.loads(l) for l in b.CATALOG.read_text(encoding='utf-8').splitlines()}
    held = set()
    for p in (ROOT / 'local/experiments/humanize-batch3/held.json', ROOT / 'local/experiments/humanize-gen/rejected.json'):
        if p.exists():
            held |= set(json.loads(p.read_text()))

    def code(f):
        lo, hi = (int(x, 16) for x in f['ranges'][0])
        return list(md.disasm(data[lo - 0x400000:hi - 0x400000 + 1], lo))

    cache = {}

    def callee_info(t):
        if t in cache:
            return cache[t]
        f = funcs.get(f'{t:08x}')
        res = None
        if f and len(f['ranges']) == 1:
            ins = code(f)
            rets = {i.operands[0].imm if i.operands else 0 for i in ins if i.mnemonic == 'ret'}
            if len(rets) == 1:
                reads = False
                for i in ins:
                    r, w = i.regs_access()
                    names = {i.reg_name(x) for x in r}
                    if names & {'ecx', 'cx', 'cl', 'ch'} and not (i.mnemonic == 'xor' and i.op_str == 'ecx, ecx'):
                        reads = True
                        break
                    if {i.reg_name(x) for x in w} & {'ecx'} or i.mnemonic.startswith('j') or i.mnemonic in ('call', 'ret'):
                        reads = i.mnemonic.startswith('j') and False
                        break
                res = (rets.pop(), reads)
        cache[t] = res
        return res

    made, skipped = {}, {}
    sources = {}
    for va, f in sorted(funcs.items()):
        if len(made) >= args.limit:
            break
        if va in b.HUMANIZED or va in held or f.get('thunk') or len(f['ranges']) != 1:
            continue
        lo, hi = (int(x, 16) for x in f['ranges'][0])
        if hi - lo > args.max_bytes:
            continue
        ins = code(f)
        if not ins or any(i.mnemonic.startswith('j') or i.mnemonic.startswith('f') or i.mnemonic.startswith('rep')
                          or (i.mnemonic == 'call' and not i.op_str.startswith('0x')) for i in ins):
            continue
        g = Gen(va, ins, callee_info, f.get('name'))
        try:
            g.run()
        except Skip as e:
            skipped[va] = str(e)
            continue
        except Exception as e:
            skipped[va] = f'error {e}'
            continue
        thiscall = g.self_used
        stdcall = g.ret_pop and not thiscall
        if g.ret_pop and thiscall and g.ret_pop // 4 < (max(g.args_used) + 1 if g.args_used else 0):
            skipped[va] = 'args beyond ret'
            continue
        nargs = g.ret_pop // 4 if g.ret_pop else (max(g.args_used) + 1 if g.args_used else 0)
        if nargs > 4:
            skipped[va] = 'more than 4 arguments'
            continue
        name = g.name if g.name and not g.name.startswith(('FUN_', 'PTR_', 'thunk_')) and re.fullmatch(r'\w+', g.name) else f'function_{va}'
        if not name.endswith(va):
            name = f'{name}_{va}'
        params = ', '.join(f'U a{k}' for k in range(nargs)) or 'void'
        ret = g.eax_written
        rtype = 'U' if ret else 'void'
        body = list(g.lines)
        if ret:
            body.append(f'    return {g.regs["eax"]};')
        head = f'/* {va}: generated from the original by humanize-generate-430.py (straight-line code). */\n'
        fw = '\n'.join(g.forwarders)
        if thiscall:
            cls = f'Object_{va}'
            src = (head + (fw + '\n' if fw else '') +
                   f'struct {cls} {{\n    {rtype} {name}({params});\n}};\n\n'
                   f'{rtype} {cls}::{name}({params})\n{{\n    U self = (U)this;\n' + '\n'.join(body) + '\n}\n')
            call = f'(({cls} *)self)->{name}({", ".join(f"a{k}" for k in range(nargs))})'
        else:
            conv = '__stdcall' if stdcall else '__cdecl'
            src = (head + (fw + '\n' if fw else '') +
                   f'{rtype} {conv} {name}({params})\n{{\n' + '\n'.join(body) + '\n}\n')
            call = f'{name}({", ".join(f"a{k}" for k in range(nargs))})'
        if g.addr_args & g.index_args:
            skipped[va] = 'argument both pointer and index'
            continue
        kinds = ['ptr' if k in g.addr_args else ('small' if k in g.index_args else 'dword') for k in range(nargs)]
        gl = []
        for at, sizes in sorted(g.globals.items()):
            n = max(sizes)
            gl.append(['ptrs', at, 1] if n == 4 and at % 4 == 0 else ['bytes', at, n])
        spec_h = dict(source=f'humanized/{va}.cpp', abi='thiscall' if (thiscall or stdcall) else 'cdecl',
                      this='sptr' if thiscall else 'dword', args=['sptr' if k == 'ptr' else k for k in kinds],
                      ret=ret, call=call, soup=True)
        if gl:
            spec_h['globals'] = gl
        if g.stubs:
            spec_h['stubs'] = g.stubs
        made[va] = spec_h
        sources[va] = src
    out = RUN / 'humanized'
    keys = sorted(made)
    for va in keys:
        (out / f'{va}.cpp').write_text(sources[va], encoding='utf-8', newline='\n')
    for n, g0 in enumerate(range(0, len(keys), 80)):
        part = {k: made[k] for k in keys[g0:g0 + 80]}
        (out / 'specs' / f'{args.batch}_{n:02d}.json').write_text(json.dumps(part, indent=1, sort_keys=True), encoding='utf-8')
    reasons = {}
    for r in skipped.values():
        reasons[r.split(' ')[0] + ' ' + (r.split(' ')[1] if ' ' in r else '')] = reasons.get(r.split(' ')[0] + ' ' + (r.split(' ')[1] if ' ' in r else ''), 0) + 1
    print('generated', len(made), 'skipped', len(skipped))
    print(sorted(reasons.items(), key=lambda t: -t[1])[:15])


if __name__ == '__main__':
    main()
