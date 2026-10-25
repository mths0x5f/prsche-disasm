"""Run 430: lower every catalogued Porsche.exe function and link them into one EXE.

Prototype of the "lower everything, then humanize" path. The lowered functions run
against the original image, which the runtime maps at its original VAs from
local/game/Porsche.exe at start-up; no game bytes are written to the repository.

Extra lowering rules on top of x86-cpp-backend-fpu.py (needed to execute, not syntax):
- fs-relative operands add the thread's TEB base (the frozen backend treats fs as flat);
- an indirect JMP through a jump table inside the function becomes a switch over the
  table's in-function targets, read from the PE; other indirect JMPs fall back to every
  instruction start of the function.

Usage: py -3 scripts/research/build-v2-lowered-exe-430.py [--generate-only] [--jobs N]
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import ntpath
import os
import re
import struct
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PE_PATH = ROOT / 'local/game/Porsche.exe'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CATALOG = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
OUT = ROOT / 'local/experiments/v2-lowered-exe-430'
# Generated C++ (the game's code, never committed) lives outside the repository.
GEN = Path(os.environ.get('PORSCHE430_GEN', r'D:\projetos\porsche-src'))
PER_TU = 64

FS_BEFORE = "        terms = [f'0x{m.disp & 0xffffffff:08x}u']"
FS_AFTER = "        terms = [f'0x{m.disp & 0xffffffff:08x}u'] + (['fs257()'] if m.segment == 32 else [])"

# Approximations this branch accepts (documented in the run README); upstream rejects them.
THREEDNOW = {'femms', 'pfmul', 'pfadd', 'pfsub', 'pfacc', 'pi2fd', 'pfrcp', 'pfrcpit1', 'pfrcpit2'}
GPR32 = {'eax': 0, 'ecx': 1, 'edx': 2, 'ebx': 3, 'esp': 4, 'ebp': 5, 'esi': 6, 'edi': 7}


def native_kind(i):
    """'x87', 'mmx' or 'rcpss' when the instruction runs on the host CPU itself, else None.

    x87 and MMX state lives in the host FPU (MMX registers alias the x87 stack), exactly as in the
    original process: every x87/MMX instruction is executed as itself. 3DNow! does not exist on
    the target CPU and stays unlowered.
    """
    m = i.mnemonic
    if m in THREEDNOW:
        return None
    if m.startswith('f') or m in ('wait', 'fwait'):
        return 'x87'
    regs = [i.reg_name(op.reg) for op in i.operands if op.type == 1]
    if m == 'emms' or any(r.startswith('mm') for r in regs):
        return 'mmx'
    if m == 'rcpss':
        return 'rcpss'
    return None


def native_bytes(i):
    """The instruction's own encoding, with only its memory operand redirected to [ECX] (mod 00,
    rm 001: no SIB, no displacement) or its rm-field GPR redirected to EAX. Everything else
    (prefixes, opcode, reg field, immediate) is the original byte for byte."""
    raw = bytes(i.bytes)
    k = i.modrm_offset
    if not k:
        return raw
    modrm = raw[k]
    mem = any(op.type == 3 for op in i.operands)
    if mem:
        new = (modrm & 0x38) | 0x01
    elif modrm >> 6 == 3 and any(op.type == 1 and i.reg_name(op.reg) in GPR32 for op in i.operands):
        new = (modrm & 0xf8) | 0x00
    else:
        return raw
    tail = raw[i.imm_offset:] if i.imm_offset else b''
    return raw[:k] + bytes([new]) + tail


def emit_bytes(*data):
    """Inline-assembly lines that place raw instruction bytes (VC6: _emit)."""
    return [f'_emit 0x{b:02x}' for b in data]


def native_code(i, address):
    """C++ with MSVC inline assembly that runs instruction `i` on the host CPU with the guest's
    operands: memory through ECX (host address = guest address), the GPR operand through EAX,
    XMM registers loaded from/stored to s.xmm, EFLAGS bridged where the instruction reads or
    writes it. x87/MMX are emitted as their own bytes (native_bytes); forms with XMM are written
    as mnemonics so the compiler sees the XMM registers it must not keep values in."""
    m, ops = i.mnemonic, i.operands
    pre, asm, post = [], [], []
    mem = [op for op in ops if op.type == 3]
    if any(op.mem.segment for op in mem):
        raise ValueError('Native FPU operand with segment override')
    if mem:
        pre.append(f'U a_={address(i, mem[0])};')
        asm.append('mov ecx, a_')
    gprs = [i.reg_name(op.reg) for op in ops if op.type == 1 and i.reg_name(op.reg) in GPR32]
    xmms = [i.reg_name(op.reg) for op in ops if op.type == 1 and i.reg_name(op.reg).startswith('xmm')]
    if len(gprs) > 1:
        raise ValueError('Native MMX with several GPR operands')
    if gprs:
        g = gprs[0]
        pre.append(f'U g_=s.r[{GPR32[g]}];')
        asm.append('mov eax, g_')
        if ops[0].type == 1 and i.reg_name(ops[0].reg) == g:
            post.append(f's.r[{GPR32[g]}]=g_;')
    if m == 'fnstsw' and ops and ops[0].type == 1:
        pre.append('U g_;')
        post.append('s.r[0]=(s.r[0]&0xffff0000u)|(g_&0xffffu);')
    if m.startswith('fcmov'):
        pre.append('U f_=s.flags&0x8d5u;')
        asm += ['pushfd', 'pop eax', 'and eax, 0xfffff72a', 'or eax, f_', 'push eax', 'popfd']
    if xmms:
        # VC6's inline assembler has no SSE mnemonics: every SSE instruction is _emit-ted.
        # Guest XMMn is loaded into host XMMn, so the instruction keeps its own bytes.
        lanes = list(dict.fromkeys(xmms))
        for k, x in enumerate(lanes):
            n = int(x[3:])
            pre.append(f'U x{k}_=reinterpret_cast<U>(&s.xmm[{n}][0]);')
            asm += [f'mov edx, x{k}_'] + emit_bytes(0x0f, 0x10, (n << 3) | 2)       # movups xmmN,[edx]
        pre.append('U mx_=s.mxcsr; U hx_;')
        asm += ['lea edx, hx_'] + emit_bytes(0x0f, 0xae, 0x1a)                       # stmxcsr [edx]
        asm += ['lea edx, mx_'] + emit_bytes(0x0f, 0xae, 0x12)                       # ldmxcsr [edx]
        asm += emit_bytes(*native_bytes(i))
        asm += ['lea edx, mx_'] + emit_bytes(0x0f, 0xae, 0x1a)                       # stmxcsr [edx]
        for k, x in enumerate(lanes):
            n = int(x[3:])
            asm += [f'mov edx, x{k}_'] + emit_bytes(0x0f, 0x11, (n << 3) | 2)       # movups [edx],xmmN
        asm += ['lea edx, hx_'] + emit_bytes(0x0f, 0xae, 0x12)                       # ldmxcsr [edx]
        post.append('s.mxcsr=mx_;')
    else:
        asm += emit_bytes(*native_bytes(i))
    if m == 'fnstsw' and ops and ops[0].type == 1:
        asm += ['movzx eax, ax', 'mov g_, eax']
    if m in ('fcomi', 'fcomip', 'fucomi', 'fucomip'):
        pre.append('U fl_;')
        asm += ['pushfd', 'pop eax', 'mov fl_, eax']
        post.append('s.flags=(s.flags&~0x8d5u)|(fl_&0x45u);')
    if gprs and any(x.startswith('s.r[') for x in post) and m != 'fnstsw':
        asm.append('mov g_, eax')
    # One instruction per line inside __asm { }: in MSVC inline assembly ';' starts a comment.
    return '{' + ''.join(pre) + '\n __asm {\n' + ''.join(f'  {x}\n' for x in asm) + ' }\n ' + ''.join(post) + '}'


# Run 430 only (the rest of the exact semantics is x86-cpp-backend-exact.py, Run 431):
# x87, MMX and RCPSS run on the host CPU itself (see native_code); this takes precedence over every
# emulated lowering of those instructions.
NATIVE_HOOK = ("        if m == 'mov' and len(ops) == 2:",
               "        if native_kind(i):\n"
               "            code = native_code(i, address)\n"
               "        elif m == 'mov' and len(ops) == 2:")

APPROXIMATIONS = [
    # Unreachable for x87 (native_code runs first); kept so an instruction that is neither native nor
    # lowered (3DNow!) becomes a stop instead of a rejected body.
    ("            raise ValueError('Unsupported instruction (no exact lowering): ' + m)",
     "            code = 'unlowered430(s);return;'"),
]

HEADER_EXTRA = r'''
#include <math.h>
#include <intrin.h>
extern "C" unsigned long __readfsdword(unsigned long);
#pragma intrinsic(__readfsdword)
static inline U fs257(){return static_cast<U>(__readfsdword(0x18));}
// Guest memory is shared between guest threads (e.g. STREAM_get on the movie thread reads a
// tap's count and head outside the lock). Volatile keeps every access, in program order, like
// the original x86 code (MSVC /volatile:ms); plain pointers let /O2 reorder or merge them.
static inline U read257(U a,U n){
    return n==1?*reinterpret_cast<const volatile B*>(a):n==2?*reinterpret_cast<const volatile unsigned short*>(a):*reinterpret_cast<const volatile U*>(a);
}
static inline void write257(U a,U n,U v){
    if(n==1)*reinterpret_cast<volatile B*>(a)=static_cast<B>(v);
    else if(n==2)*reinterpret_cast<volatile unsigned short*>(a)=static_cast<unsigned short>(v);
    else *reinterpret_cast<volatile U*>(a)=v;
}
static inline double read_f80_430(U a){
    U64 man=static_cast<U64>(read257(a,4u))|(static_cast<U64>(read257(a+4u,4u))<<32);
    U se=read257(a+8u,2u);int e=static_cast<int>(se&0x7fffu);double sign=(se&0x8000u)?-1.0:1.0;
    if(e==0&&man==0)return sign*0.0;
    if(e==0x7fff)return (man<<1)?NAN:sign*INFINITY;
    return sign*ldexp(static_cast<double>(man),e-16383-63);
}
static inline void write_f80_430(U a,double v){
    U se=signbit(v)?0x8000u:0u;U64 man=0;
    if(isnan(v)){se|=0x7fffu;man=0xc000000000000000ull;}
    else if(isinf(v)){se|=0x7fffu;man=0x8000000000000000ull;}
    else if(v!=0.0){int e;double m=frexp(fabs(v),&e);man=static_cast<U64>(ldexp(m,64));se|=static_cast<U>(e-1+16383);}
    write257(a,4u,static_cast<U>(man));write257(a+4u,4u,static_cast<U>(man>>32));write257(a+8u,2u,se);
}
void unlowered430(Machine257&);  // 3DNow!/FPU environment images: fatal if reached
extern "C" U __cdecl humanized_enter430();          // host stack for calls out of humanized code
extern "C" void __cdecl humanized_leave430(U saved);
void repne_scasb_down430(Machine257&);  // repne scasb with DF set
// Target is evaluated by the generated caller before ESP changes.
static inline bool call257(Machine257&s,U target,U returnPC){
    s.r[4]-=4u;write257(s.r[4],4u,returnPC);dispatch257(s,target);
    if(s.stop!=Stop257::Returned||s.pc!=returnPC){if(s.stop==Stop257::Returned)s.stop=Stop257::BadReturn;return false;}
    s.stop=Stop257::Running;return true;
}
'''


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def backend():
    be = load('backend_exact_430', ROOT / 'scripts/research/x86-cpp-backend-exact.py')
    src = be.DERIVED_SOURCE
    for before, after in [(FS_BEFORE, FS_AFTER), NATIVE_HOOK, *APPROXIMATIONS]:
        assert src.count(before) == 1, 'patch context drift: ' + before
        src = src.replace(before, after)
    ns = dict(be._namespace)
    ns.update(native_kind=native_kind, native_code=native_code, re=re)
    exec(compile(src, 'backend-430::derived', 'exec'), ns)
    header = be.HEADER
    for decl in ('U read257(U address, U bytes);\n', 'void write257(U address, U bytes, U value);\n'):
        assert header.count(decl) == 1
        header = header.replace(decl, '')
    header = header.replace('void dispatch257(Machine257&, U target);\n',
                            'void dispatch257(Machine257&, U target);\n' + HEADER_EXTRA)
    # Speed (same results): force-inline every helper, and divide in 32 bits when EDX only
    # sign-/zero-extends EAX (the cdq/xor edx,edx + div pattern) instead of calling the
    # CRT's 64-bit division.
    header = header.replace('static inline ', 'static __forceinline ')
    fast_paths = [
        ('static __forceinline void idiv257_1(Machine257& s, U b) {\n',
         'static __forceinline void idiv257_1(Machine257& s, U b) {\n'
         '    if (b != 0u && s.r[2] == ((s.r[0] & 0x80000000u) ? 0xffffffffu : 0u) &&\n'
         '        !(s.r[0] == 0x80000000u && b == 0xffffffffu)) {\n'
         '        int a = (int)s.r[0], d = (int)b; s.r[0] = (U)(a / d); s.r[2] = (U)(a % d); return;\n'
         '    }\n'),
        ('static __forceinline void div257_1(Machine257& s, U b) {\n',
         'static __forceinline void div257_1(Machine257& s, U b) {\n'
         '    if (b != 0u && s.r[2] == 0u) { U a = s.r[0]; s.r[0] = a / b; s.r[2] = a % b; return; }\n'),
    ]
    for before, after in fast_paths:
        assert header.count(before) == 1, before
        header = header.replace(before, after)
    # The runtime never budgets execution; keep pc for diagnostics.
    step_old = ('static __forceinline bool step257(Machine257&s,U pc){\n'
                '    if(s.stop!=Stop257::Running)return false;s.pc=pc;\n'
                '    if(!s.budget){s.stop=Stop257::BudgetExhausted;return false;}--s.budget;return true;\n}')
    assert header.count(step_old) == 1
    header = header.replace(step_old, 'static __forceinline bool step257(Machine257&s,U pc){\n'
                            '    if(s.stop!=Stop257::Running)return false;s.pc=pc;return true;\n}')
    return ns["translate"], header + HEADER_NF

class Image:
    def __init__(self, data):
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        self.base = struct.unpack_from('<I', data, pe + 52)[0]
        self.size = struct.unpack_from('<I', data, pe + 80)[0]
        self.entry = self.base + struct.unpack_from('<I', data, pe + 40)[0]
        sh = pe + 24 + struct.unpack_from('<H', data, pe + 20)[0]
        self.sections = []
        for i in range(struct.unpack_from('<H', data, pe + 6)[0]):
            q = sh + 40 * i
            vs, va, rs, raw = struct.unpack_from('<IIII', data, q + 8)
            self.sections.append((data[q:q + 8].rstrip(b'\0').decode(), self.base + va, vs, rs, raw,
                                  struct.unpack_from('<I', data, q + 36)[0]))
        self.data = data

    def read(self, va, n):
        for _, sva, vs, rs, raw, _ in self.sections:
            if sva <= va and va + n <= sva + min(vs, rs):
                return self.data[raw + va - sva:raw + va - sva + n]
        return None


JMP_TABLE = re.compile(r'dword ptr \[(?:e[a-z]{2})\*4 \+ (0x[0-9a-f]+)\]')


STATS = {"dead_flag_writes": 0}
BRANCH_IMM = re.compile(r'0x[0-9a-f]+')

# Dead-flag elimination. A flag write is dead when, going forward in the same range, a full
# flag writer comes before anything that may read EFLAGS or leave the straight line. Only
# instructions known not to touch EFLAGS are crossed; everything else keeps flags live.
FLAG_FULL = {'add', 'sub', 'cmp', 'test', 'and', 'or', 'xor', 'neg'}
FLAG_PARTIAL = {'inc', 'dec'}
FLAG_NEUTRAL = {'mov', 'movzx', 'movsx', 'lea', 'push', 'pop', 'nop', 'not', 'cdq', 'xchg',
                'fld', 'fst', 'fstp', 'fild', 'fistp', 'fadd', 'faddp', 'fsub', 'fsubp', 'fsubr',
                'fsubrp', 'fmul', 'fmulp', 'fdiv', 'fdivp', 'fdivr', 'fdivrp', 'fchs', 'fabs', 'fxch',
                'fldz', 'fld1', 'fnstsw', 'fldcw', 'fnstcw', 'fcom', 'fcomp', 'fcompp', 'fucom',
                'fucomp', 'fucompp', 'fst', 'fsin', 'fcos', 'fsqrt', 'wait',
                'movss', 'movaps', 'movups', 'movd', 'movq'}
NO_FLAGS = [('add257(s,', 'add257nf('), ('subtract257(s,', 'subtract257nf('), ('logical257(s,', 'logical257nf('),
            ('inc257(s,', 'inc257nf('), ('dec257(s,', 'dec257nf(')]
VC6_PRELUDE = '// Visual C++ 6.0 code (the game\'s own compiler); it also builds with current MSVC.\n'
STOP_NAMES = ('Running', 'Returned', 'MissingEntry', 'BadReturn', 'BudgetExhausted')


def vc6_stops(text):
    """Stop257::Running -> STOP257_RUNNING: a plain VC6 enum, no scoped-enum emulation."""
    for n in STOP_NAMES:
        text = text.replace(f'Stop257::{n}', 'STOP257_' + re.sub(r'(?<!^)([A-Z])', r'_\1', n).upper())
    return text


SSE_OPCODES = [('SseAddSs', 'addss', (0xf3, 0x0f, 0x58, 0xc1)), ('SseAddPs', 'addps', (0x0f, 0x58, 0xc1)),
               ('SseSubSs', 'subss', (0xf3, 0x0f, 0x5c, 0xc1)), ('SseSubPs', 'subps', (0x0f, 0x5c, 0xc1)),
               ('SseMulSs', 'mulss', (0xf3, 0x0f, 0x59, 0xc1)), ('SseMulPs', 'mulps', (0x0f, 0x59, 0xc1))]


def vc6_sse_helpers():
    """sse257 / cvt_i2f257 with every SSE instruction as _emit bytes (no SSE mnemonics in VC6)."""
    def block(insn_bytes, insn):
        lines = ['mov eax, d', 'mov edx, src', 'lea ecx, host'] + emit_bytes(0x0f, 0xae, 0x19) + \
                ['lea ecx, guest'] + emit_bytes(0x0f, 0xae, 0x11) + emit_bytes(0x0f, 0x10, 0x00) + \
                emit_bytes(0x0f, 0x10, 0x0a) + emit_bytes(*insn_bytes) + emit_bytes(0x0f, 0x11, 0x00) + \
                ['lea ecx, guest'] + emit_bytes(0x0f, 0xae, 0x19) + ['lea ecx, host'] + emit_bytes(0x0f, 0xae, 0x11)
        return ('            // stmxcsr host; ldmxcsr guest; movups xmm0,[eax]; movups xmm1,[edx];\n'
                f'            // {insn} xmm0,xmm1; movups [eax],xmm0; stmxcsr guest; ldmxcsr host\n'
                '            __asm {\n' + ''.join(f'                {x}\n' for x in lines) + '            }\n')
    cases = ''.join(f'        case {name}:\n{block(b, insn)}            break;\n' for name, insn, b in SSE_OPCODES)
    return ('enum Sse257 { SseAddSs, SseAddPs, SseSubSs, SseSubPs, SseMulSs, SseMulPs };\n'
            'static __forceinline void sse257(Machine257& s, U op, U* d, const U* src) {\n'
            '    U host, guest = s.mxcsr;\n    switch (op) {\n' + cases + '    }\n    s.mxcsr = guest;\n}\n'
            '// cvtsi2ss / cvtpi2ps lane: int32 -> float under the guest MXCSR.\n'
            'static __forceinline U cvt_i2f257(Machine257& s, U value) {\n'
            '    U host, guest = s.mxcsr, r;\n'
            '    // stmxcsr host; ldmxcsr guest; cvtsi2ss xmm0,eax; movss [ecx],xmm0; stmxcsr guest; ldmxcsr host\n'
            '    __asm {\n' + ''.join(f'        {x}\n' for x in
                                      ['lea ecx, host'] + emit_bytes(0x0f, 0xae, 0x19) + ['lea ecx, guest'] +
                                      emit_bytes(0x0f, 0xae, 0x11) + ['mov eax, value'] +
                                      emit_bytes(0xf3, 0x0f, 0x2a, 0xc0) + ['lea ecx, r'] +
                                      emit_bytes(0xf3, 0x0f, 0x11, 0x01) + ['lea ecx, guest'] +
                                      emit_bytes(0x0f, 0xae, 0x19) + ['lea ecx, host'] + emit_bytes(0x0f, 0xae, 0x11)) +
            '    }\n    s.mxcsr = guest;\n    return r;\n}\n')


def vc6_compatible(text):
    """Write the backend header the way VC6 code is written: typedef, __int64, plain enum,
    __asm; no C++11 constructs and no compatibility macros."""
    reps = [
        ('#include <intrin.h>\n', ''),
        ('using U=unsigned int; using U64=unsigned long long; using B=unsigned char;',
         'typedef unsigned int U; typedef unsigned __int64 U64; typedef unsigned char B;'),
        ('static_assert(sizeof(U)==4,"32-bit register type required");\n', ''),
        ('enum class Stop257:U {Running,Returned,MissingEntry,BadReturn,BudgetExhausted};',
         'enum Stop257 { STOP257_RUNNING, STOP257_RETURNED, STOP257_MISSING_ENTRY, STOP257_BAD_RETURN,\n'
         '               STOP257_BUDGET_EXHAUSTED };'),
        ('extern "C" unsigned long __readfsdword(unsigned long);\n#pragma intrinsic(__readfsdword)\n'
         'static __forceinline U fs257(){return static_cast<U>(__readfsdword(0x18));}',
         'static __forceinline U fs257(){\n    U v;\n    __asm {\n        mov eax, fs:[0x18]\n        mov v, eax\n    }\n    return v;\n}'),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    # 80-bit helpers: unused since x87 runs natively (and they need C99 math).
    for fn in ('read_f80_430', 'write_f80_430'):
        a = text.find(f'static __forceinline double {fn}' if fn.startswith('read') else f'static __forceinline void {fn}')
        if a >= 0:
            text = text[:a] + text[text.index('\n}\n', a) + 3:]
    a = text.find('enum Sse257 : U {')
    if a >= 0:
        b = text.index('static __forceinline void shufps257', a)
        text = text[:a] + vc6_sse_helpers() + text[b:]
    text = re.sub(r'\b(\d+)LL\b', r'\1i64', text)
    text = re.sub(r'\bunsigned long long\b', 'unsigned __int64', text)
    text = re.sub(r'\blong long\b', '__int64', text)
    text = re.sub(r'\b((?:0x[0-9a-fA-F]+)|[0-9]+)ull\b', r'\1ui64', text)
    text = re.sub(r'\b((?:0x[0-9a-fA-F]+)|[0-9]+)ll\b', r'\1i64', text)
    text = text.replace('_InterlockedExchangeAdd(reinterpret_cast<volatile long*>(',
                        'InterlockedExchangeAdd(reinterpret_cast<long*>(')
    # LOCK INC/DEC in the generated code use the Win32 interlocked add (kernel32).
    text = text.replace('#pragma once\n', '#pragma once\nextern "C" __declspec(dllimport) long __stdcall '
                        'InterlockedExchangeAdd(long*, long);\n', 1)
    return vc6_stops(text).replace('#pragma once\n', '#pragma once\n' + VC6_PRELUDE, 1)


HEADER_NF = r'''
// Value-only forms used where the flags an instruction writes are provably dead.
static __forceinline U add257nf(U a,U b,U bits){return (a+b)&mask257(bits);}
static __forceinline U subtract257nf(U a,U b,U c,U bits){return (a-b-c)&mask257(bits);}
static __forceinline U logical257nf(U v,U bits){return v&mask257(bits);}
static __forceinline U inc257nf(U a,U bits){return (a+1u)&mask257(bits);}
static __forceinline U dec257nf(U a,U bits){return (a-1u)&mask257(bits);}
'''


def full_writer(w):
    # Only a lowering that really goes through a full-flag helper counts as a killer.
    return w['mnemonic'] in FLAG_FULL and any(h in w['cpp'] for h in ('add257(s,', 'subtract257(s,', 'logical257(s,'))


def kill_dead_flags(code, witness):
    killed = 0
    for k, w in enumerate(witness):
        m = w['mnemonic']
        if m not in FLAG_FULL and m not in FLAG_PARTIAL:
            continue
        if not any(old in w['cpp'] for old, _ in NO_FLAGS):
            continue
        dead = False
        for nxt in witness[k + 1:k + 24]:
            n = nxt['mnemonic']
            if full_writer(nxt):
                dead = True
                break
            if n not in FLAG_NEUTRAL:
                break
        if not dead:
            continue
        new = w['cpp']
        for old, nf in NO_FLAGS:
            new = new.replace(old, nf)
        marker = f" // {w['va']} {w['bytes']} "
        at = code.index(marker)
        block = '{ ' + w['cpp'] + ' }'
        at = code.index(block, at)
        code = code[:at] + '{ ' + new + ' }' + code[at + len(block):]
        killed += 1
    return code, killed


def lower(translate, img, va, size, entries=()):
    """Lower one contiguous range. `entries` are mid-range addresses other ranges enter."""
    raw = img.read(va, size)
    code, witness = translate(raw, va)
    code, killed = kill_dead_flags(code, witness)
    STATS["dead_flag_writes"] += killed
    starts = [int(w['va'], 16) for w in witness]
    lo, hi = va, va + len(raw)
    need = set(t for t in entries if t in starts and t != va)
    for w in witness:
        if (w['mnemonic'] != 'jmp' or 'dispatch257(s,target);return;' not in w['cpp']
                or w['operands'].startswith('0x')):
            continue
        targets = []
        m = JMP_TABLE.fullmatch(w['operands'])
        if m:
            table = int(m.group(1), 16)
            while True:
                cell = img.read(table + 4 * len(targets), 4)
                t = struct.unpack('<I', cell)[0] if cell else 0
                if not lo <= t < hi or t not in starts:
                    break
                targets.append(t)
        if not targets:
            targets = starts
        targets = sorted(set(targets))
        need.update(targets)
        cases = ''.join(f'case 0x{t:08x}u:goto L_{t:08x};' for t in targets)
        old = '{ ' + w['cpp'] + ' }'
        new = '{ ' + w['cpp'].replace('dispatch257(s,target);return;',
                                      f'switch(target){{{cases}default:dispatch257(s,target);return;}}') + ' }'
        marker = f" // {w['va']} {w['bytes']} "
        at = code.index(marker)
        at = code.index(old, at)
        code = code[:at] + new + code[at + len(old):]
    for t in sorted(need):
        label = f'L_{t:08x}:'
        if label not in code:
            marker = f' // {t:08x} '
            code = code.replace('\n' + marker, f'\n{label}\n{marker}', 1)
    # Falling off the end of a range continues at the next address (tail dispatch).
    tail = ' s.stop = Stop257::Returned; return;\n}'
    if code.rstrip().endswith(tail.strip()):
        at = code.rindex(' s.stop = Stop257::Returned; return;')
        code = code[:at] + f' dispatch257(s,0x{hi:08x}u); return;' + code[at + len(' s.stop = Stop257::Returned; return;'):]
    mids = sorted(t for t in set(entries) if t in starts and t != va)
    if mids:
        head = f'void translated_{va:08x}(Machine257&s){{'
        cases = ''.join(f'case 0x{t:08x}u:goto L_{t:08x};' for t in mids)
        code = code.replace(head, head + f'\n switch(s.pc){{{cases}default:break;}}', 1)
    branch_targets = set()
    for w in witness:
        if w['mnemonic'].startswith('j') or w['mnemonic'] == 'call':
            for x in BRANCH_IMM.findall(w['operands']):
                if 'ptr' not in w['operands']:
                    branch_targets.add(int(x, 16))
    return code, len(witness), mids, starts, branch_targets


def pointer_entries(img, entries):
    """Code addresses stored in data (HIGHLOW relocations) that the catalog does not start.

    Returns synthetic functions for targets outside every catalogued range (each runs to
    the next catalogued range, minus padding) and the set of all pointer targets, which
    become mid-body entries when they land inside a range.
    """
    data, base = img.data, img.base
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    rva, size = struct.unpack_from('<II', data, pe + 24 + 96 + 8 * 5)
    code = [(sva, sva + vs) for name, sva, vs, rs, raw, ch in img.sections if ch & 0x20000000]
    targets = set()
    at = 0
    while at < size:
        page, block = struct.unpack('<II', img.read(base + rva + at, 8))
        if block < 8:
            break
        for k in range((block - 8) // 2):
            item = struct.unpack('<H', img.read(base + rva + at + 8 + 2 * k, 2))[0]
            if item >> 12 == 3:
                cell = img.read(base + page + (item & 0xfff), 4)
                v = struct.unpack('<I', cell)[0] if cell else 0
                if any(lo <= v < hi for lo, hi in code):
                    targets.add(v)
        at += block
    return gap_pieces(img, entries, targets), targets


def direct_targets(img, bodies):
    """Targets of rel32 `call`/`jmp` instructions in the given bodies (entry dicts)."""
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    out = set()
    for e in bodies:
        for a, b in e['ranges']:
            lo, hi = int(a, 16), int(b, 16) + 1
            for ins in md.disasm(img.read(lo, hi - lo) or b'', lo):
                if ins.mnemonic in ('call', 'jmp') and ins.size == 5 and ins.bytes[0] in (0xe8, 0xe9):
                    out.add(int(ins.op_str, 16))
    return out


def closed_entries(img, entries, pointers):
    """Synthetic pieces for pointer targets and, transitively, for direct call/jmp targets that
    land outside the catalog (code reached only from other uncatalogued code, e.g. the
    race-start region 004184e2..00419d4f with 00419c50 called from 00418629)."""
    targets = set(pointers)
    synthetic = gap_pieces(img, entries, targets)
    scanned = set()
    while True:
        fresh = [e for e in entries + synthetic if e['entry_va'] not in scanned]
        if not fresh:
            return synthetic, targets
        scanned.update(e['entry_va'] for e in fresh)
        before = len(targets)
        targets |= direct_targets(img, fresh)
        if len(targets) == before:
            return synthetic, targets
        synthetic = gap_pieces(img, entries, targets)


def code_ranges(img):
    return [(sva, sva + vs) for name, sva, vs, rs, raw, ch in img.sections if ch & 0x20000000]


def gap_pieces(img, entries, targets):
    """Synthetic functions for code targets that no range of `entries` covers."""
    code = code_ranges(img)
    ranges = sorted((int(a, 16), int(b, 16) + 1) for e in entries for a, b in e['ranges'])
    starts = [a for a, _ in ranges]
    synthetic = []
    import bisect
    outside = []
    for t in sorted(targets):
        if not any(lo <= t < hi for lo, hi in code):
            continue
        k = bisect.bisect_right(starts, t) - 1
        if not (k >= 0 and ranges[k][0] <= t < ranges[k][1]):
            outside.append((t, k))
    # One piece per target, ending at the next target in the same gap (or the gap's end);
    # a piece that falls off its end continues into the next one by tail dispatch, and a
    # piece that is really data fails on its own.
    for j, (t, k) in enumerate(outside):
        end = starts[k + 1] if k + 1 < len(starts) else next(hi for lo, hi in code if lo <= t < hi)
        if j + 1 < len(outside) and outside[j + 1][1] == k:
            end = min(end, outside[j + 1][0])
        body = img.read(t, end - t) or b''
        n = len(body)
        while n and body[n - 1] in (0xcc, 0x90):
            n -= 1
        if n:
            synthetic.append(dict(entry_va=f'{t:08x}', name=f'PTR_{t:08x}', ranges=[[f'{t:08x}', f'{t + n - 1:08x}']],
                                  body_bytes=n, synthetic=True))
    return synthetic


def generate(translate, header, img, entries, pointers=()):
    gen = GEN
    gen.mkdir(parents=True, exist_ok=True)
    written = set()

    def put(path, text):
        # Rewrite only changed files so the build recompiles only what changed. Windows names
        # are case-insensitive: a file whose spelling changed (FECREDITS -> FECredits) is
        # removed first so the new spelling reaches the disk.
        written.add(str(path).lower())
        if path.exists() and path.name not in os.listdir(path.parent):
            path.unlink()
        if not path.exists() or path.read_text(encoding='utf-8') != text:
            path.write_text(text, encoding='utf-8')

    put(gen / 'machine257.h', vc6_compatible(header))
    # Types shared by humanized functions (included as "humanized/<name>.h").
    (gen / 'humanized').mkdir(exist_ok=True)
    for hdr in (RUN / 'humanized').glob('*.h'):
        put(gen / 'humanized' / hdr.name, hdr.read_text(encoding='utf-8'))
    table_rows, rejected = [], []
    tu, tu_index, insns, functions, ranges = [], 0, 0, 0, 0
    t0 = time.time()

    def flush():
        nonlocal tu, tu_index
        if tu:
            put(gen / f'lowered_{tu_index:03d}.cpp', '#include "machine257.h"\n' + '\n'.join(tu))
            tu, tu_index = [], tu_index + 1

    # Pass 1: lower every range alone and collect direct branch/call targets that come from
    # outside the range they land in (cross-range jumps, shared CRT tails such as strcpy ->
    # strcat). Pass 2 re-lowers only the ranges that such targets enter mid-body.
    first, external = {}, set(pointers)
    entries = list(entries)
    pending = list(entries)
    added = 0
    while pending:
        for e in pending:
            spans = [(int(a, 16), int(b, 16) + 1 - int(a, 16)) for a, b in e['ranges']]
            try:
                first[e['entry_va']] = [(a, n, lower(translate, img, a, n)) for a, n in spans]
            except Exception as x:  # noqa: BLE001 - recorded as an explicit boundary
                rejected.append(dict(va=e['entry_va'], reason=str(x)[:120]))
                continue
            for a, n, res in first[e['entry_va']]:
                external.update(t for t in res[4] if not a <= t < a + n)
                if f'dispatch257(s,0x{a + n:08x}u); return;' in res[0][-200:]:
                    external.add(a + n)  # fallthrough into the next range
        # Direct targets in gaps (code no catalogued range covers) become new pieces.
        pending = [p for p in gap_pieces(img, entries, external) if p['entry_va'] not in first]
        pending = [p for p in pending if p['entry_va'] not in {r['va'] for r in rejected}]
        entries += pending
        added += len(pending)
    layout = source_layout(entries)
    files = collections.defaultdict(list)
    for e in entries:
        if e['entry_va'] not in first:
            continue
        out = []
        for a, n, res in first[e['entry_va']]:
            mids = {t for t in external if a < t < a + n} & set(res[3])
            out.append(lower(translate, img, a, n, mids) if mids else res)
        spans = [(a, n) for a, n, _ in first[e['entry_va']]]
        rel, ident = layout[e['entry_va']]
        functions += 1
        h = HUMANIZED.get(e['entry_va'])
        only = os.environ.get('HUMANIZED_ONLY')  # diagnostics: comma-separated VAs to keep humanized
        if h and only is not None and e['entry_va'] not in only.split(','):
            h = None
        if h:
            # A humanized function replaces the whole lowered body: only when nothing else
            # enters it in the middle (the bridge serves the entry address alone).
            if len(spans) != 1 or out[0][2]:
                raise ValueError(f"humanized {e['entry_va']} has several ranges or mid-entries")
            a = spans[0][0]
            body = (RUN / h['source']).read_text(encoding='utf-8') + '\n' + bridge_code(e['entry_va'], h)
            files[rel].append((a, f"humanized_{e['entry_va']}_430", body))
            table_rows.append((a, f"humanized_{e['entry_va']}_430"))
            STATS['humanized'] = STATS.get('humanized', 0) + 1
            continue
        for k, ((a, _), (code, n, mids, _, _)) in enumerate(zip(spans, out)):
            ranges += 1
            insns += n
            name = ident if k == 0 else f'{ident}_part_{a:08x}'
            code = code.replace('#include "machine257.h"\n', '')
            code = code.replace(f'void translated_{a:08x}(Machine257&s){{', f'void {name}(Machine257&s){{', 1)
            if a in VC6_NO_FPO:
                code = f'#pragma optimize("y", off)\n{code}\n#pragma optimize("y", on)\n'
            files[rel].append((a, name, code))
            table_rows.append((a, name))
            table_rows.extend((t, name) for t in mids)
    src = gen / 'src'
    for rel, items in sorted(files.items()):
        path = src / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        origin = SOURCE_NOTES.get(rel, '')
        body = '\n'.join(code for _, _, code in sorted(items)).replace(
            '_InterlockedExchangeAdd(reinterpret_cast<volatile long*>(', 'InterlockedExchangeAdd(reinterpret_cast<long*>(')
        body = vc6_stops(body)
        put(path, f'// {origin}\n#include "machine257.h"\n' + body if origin else '#include "machine257.h"\n' + body)
        tu_index += 1
    fns = sorted({f for _, f in table_rows})
    table = ['#include "machine257.h"', *(f'void {f}(Machine257&);' for f in fns),
             'struct LoweredEntry430{U va;void(*fn)(Machine257&);};',
             f'extern const unsigned lowered_count430={len(table_rows)}u;',
             'extern const LoweredEntry430 lowered_table430[]={',
             *(f'{{0x{v:08x}u,{f}}},' for v, f in sorted(table_rows)), '};', '']
    put(gen / 'lowered_table.cpp', '\n'.join(table))
    # Every original file the binaries name exists in the tree, even before any function is
    # attributed to it; every original directory exists too.
    for original in KNOWN['files']:
        path = src / canonical_rel(original)
        if str(path).lower() not in written:
            path.parent.mkdir(parents=True, exist_ok=True)
            put(path, f'// original source: {original}\n'
                      '// Arquivo original conhecido; nenhuma funcao atribuida ainda.\n')
    keep_dirs = set()
    for original in KNOWN['dirs']:
        d = src / canonical_rel(original)
        d.mkdir(parents=True, exist_ok=True)
        keep_dirs.add(str(d).lower())
    tree = [p for p in src.rglob('*') if p.is_file() and p.suffix.lower() in SOURCE_SUFFIXES]
    for old in list(gen.glob('lowered_[0-9]*.cpp')) + [p for p in tree if str(p).lower() not in written]:
        old.unlink()
    for d in sorted((p for p in src.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(d.iterdir()) and str(d).lower() not in keep_dirs:
            d.rmdir()
    return dict(dead_flag_writes=STATS["dead_flag_writes"], humanized=STATS.get("humanized", 0), gap_pieces_added=added, lowered=functions, ranges=ranges,
                table_entries=len(table_rows), rejected=rejected, instructions=insns, source_files=tu_index,
                generate_seconds=round(time.time() - t0, 1))


SOURCE_NOTES = {}
INFERRED_STEM = {}


def case_like(stem, ref):
    """Spell an NFS4 (all-caps) file stem the way Porsche's own names spell it.

    FECREDITS + class FECreditsCallBackList -> FECredits; AIH_HUM + AIHigh_Human -> AIH_Hum;
    AUDIOMUS + function AudioMus_SysStartUp -> AudioMus. Without a matching name the stem is
    left as NFS4 wrote it.
    """
    parts, ref_parts = stem.split('_'), ref.split('_')
    if len(parts) > 1 and len(parts) == len(ref_parts):
        if all(r.lower().startswith(p.lower()) for p, r in zip(parts, ref_parts)):
            return '_'.join(r[:len(p)] for p, r in zip(parts, ref_parts))
    flat = ref.replace('_', '')
    if len(parts) == 1 and flat.lower().startswith(stem.lower()):
        return flat[:len(stem)]
    return stem
SPELLING = {}
KNOWN = {'files': [], 'dirs': []}
SOURCE_SUFFIXES = ('.c', '.cpp', '.h', '.hpp', '.inl')
# gimme.dll objects were compiled from D:\dev\NFS5\Game (objects in Game\Debug, Game\Release);
# their relative includes (..\..\library\...) resolve from there.
GIMME_CWD = 'D:\\dev\\NFS5\\Game'


def path_parts(original):
    """Original path -> its components below the drive, each build root kept as written:
    D:\\dev\\... stays dev\\..., d:\\Nfs\\Nfs5\\... stays Nfs\\Nfs5\\..., \\real\\... stays real\\...
    """
    p = original.replace('/', '\\')
    if p.startswith('..'):
        p = ntpath.normpath(ntpath.join(GIMME_CWD, p))
    return [x for x in p.split('\\') if x and not x.endswith(':')]


def learn_spelling(paths):
    """Windows paths are case-insensitive, so one directory shows up in several spellings. Each
    directory takes the most frequent spelling that has capitals (all-lowercase names come
    from the compiler's normalised include probes), else the most frequent one."""
    seen = collections.defaultdict(collections.Counter)
    for original in paths:
        parts = path_parts(original)
        for k in range(len(parts)):
            seen['/'.join(x.lower() for x in parts[:k + 1])][parts[k]] += 1
    for key, spellings in seen.items():
        mixed = [s for s in spellings if s != s.lower()] or list(spellings)
        SPELLING[key] = max(mixed, key=lambda s: (spellings[s], s))


def canonical_rel(original):
    """Original path -> relative path in the generated tree, with the original extension."""
    parts = path_parts(original)
    return '/'.join(SPELLING.get('/'.join(y.lower() for y in parts[:k + 1]), parts[k]) for k in range(len(parts)))


def source_layout(entries):
    """entry_va -> (relative .cpp path, function identifier), following the game's own source tree.

    Uses attribution.json from attribute-v2-source-files-430.py. Functions whose original file
    is known go to that path (drive and leading separators dropped, extension .cpp). Functions
    with only an RTTI class go to _sem_arquivo/classes/<outer name>.cpp; the rest go to
    _sem_arquivo/codigo/ in contiguous .text chunks. Identifiers come from RTTI names when
    present, otherwise FUN_<va> (catalog) or PTR_<va> (pointer-only pieces).
    """
    path = OUT / 'attribution.json'
    attribution = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    by_func = attribution.get('by_function', {})
    KNOWN['files'] = attribution.get('known_files', [])
    KNOWN['dirs'] = attribution.get('known_dirs', [])
    learn_spelling(KNOWN['files'] + KNOWN['dirs'] + [v['file'] for v in by_func.values() if v.get('file')])
    layout, used, rest = {}, {}, []
    for e in sorted(entries, key=lambda e: int(e['entry_va'], 16)):
        va = e['entry_va']
        info = by_func.get(va, {})
        real = info.get('real_names') or []
        # Free-function names (recovered C names, NFS4 names) carry no class: grouping by class
        # uses only Class::method names, from the real names or else from RTTI.
        names = [n for n in real if '::' in n] or info.get('names') or []
        shared = len({n.split('::')[0] for n in names}) > 1  # folded body used by several classes
        if real and len(real) == 1:
            ident = re.sub(r'[^A-Za-z0-9]+', '_', real[0].replace('::', '__'))
            if not ident.endswith('_' + va):
                ident += '_' + va
        elif shared:
            ident = f'shared_{va}'
        elif names:
            ident = re.sub(r'[^A-Za-z0-9]+', '_', names[0].replace('::', '__')) + '_' + va
        else:
            ident = f'PTR_{va}' if e.get('synthetic') else f'FUN_{va}'
        if info.get('file'):
            original = info['file']
            rel = canonical_rel(original)
            SOURCE_NOTES[rel] = f'original source: {original} (evidence: see attribution.json)'
        elif info.get('inferred_file') and not shared:
            # Lineage only (NFS4 file names): kept apart from proven paths.
            original = info['inferred_file']
            parts = [p for p in re.split(r'[\\/]', original) if p and not p.endswith(':')]
            if parts and parts[0].lower() == 'nfs4':
                parts = parts[1:]
            ref = (names[0].split('::')[0] if names else '') or (real[0] if real else '')
            stem = INFERRED_STEM.setdefault(original.lower(), case_like(parts[-1].rsplit('.', 1)[0], ref))
            rel = '_inferido_nfs4/' + '/'.join([p.lower() for p in parts[:-1]] + [stem + '.cpp'])
            SOURCE_NOTES[rel] = (f'file name inferred from NFS4 (High Stakes PS1 prototype): {original}; '
                                 'Porsche Unleashed directory unknown (evidence: attribution.json)')
        elif shared:
            rel = '_sem_arquivo/classes/_compartilhadas.cpp'
            SOURCE_NOTES[rel] = ('original file unknown; bodies folded by the linker and shared by several '
                                 'classes (all names in attribution.json)')
        elif names:
            outer = re.sub(r'[^A-Za-z0-9]+', '_', names[0].split('::')[0])
            rel = f'_sem_arquivo/classes/{outer}.cpp'
            SOURCE_NOTES[rel] = 'original file unknown; grouped by RTTI class/namespace'
        else:
            rel = None
            rest.append(va)
        layout[va] = (rel, ident)
    # Contiguous chunks of at most 64 functions and 16 KB of x86 code: a few very large bodies
    # in one file exhausted the compiler's heap (C1002).
    size_of = {e['entry_va']: e.get('body_bytes', 0) for e in entries}
    chunks, cur, cur_bytes = [], [], 0
    for va in rest:
        n = size_of.get(va, 0)
        if cur and (len(cur) == 64 or cur_bytes + n > 16384):
            chunks.append(cur)
            cur, cur_bytes = [], 0
        cur.append(va)
        cur_bytes += n
    if cur:
        chunks.append(cur)
    for chunk in chunks:
        rel = f'_sem_arquivo/codigo/{chunk[0]}_{chunk[-1]}.cpp'
        SOURCE_NOTES[rel] = 'original file unknown; contiguous .text range'
        for va in chunk:
            layout[va] = (rel, layout[va][1])
    # Object files are named after the source base name; keep base names unique.
    count, final = collections.Counter(), {}
    for rel in sorted({r for r, _ in layout.values()}):
        base = rel.rsplit('/', 1)[-1].lower()
        count[base] += 1
        stem, ext = rel.rsplit('.', 1)
        final[rel] = rel if count[base] == 1 else f'{stem}_{count[base]}.{ext}'
        SOURCE_NOTES[final[rel]] = SOURCE_NOTES.get(rel, '')
    return {va: (final[rel], ident) for va, (rel, ident) in layout.items()}


def toolchain():
    roots = [Path(r'C:\Program Files\Microsoft Visual Studio'), Path(r'C:\Program Files (x86)\Microsoft Visual Studio')]
    cl = sorted(c for r in roots if r.exists() for c in r.glob('*/*/VC/Tools/MSVC/*/bin/Hostx64/x86/cl.exe'))[-1]
    kits = Path(r'C:\Program Files (x86)\Windows Kits\10')
    sdk_inc = sorted(p for p in (kits / 'Include').iterdir() if (p / 'um').exists())[-1]
    vc = cl.parents[3]
    env = dict(os.environ)
    env['INCLUDE'] = ';'.join(str(p) for p in [vc / 'include', sdk_inc / 'ucrt', sdk_inc / 'shared', sdk_inc / 'um'])
    env['LIB'] = ';'.join(str(p) for p in [vc / 'lib/x86', kits / 'Lib' / sdk_inc.name / 'ucrt/x86',
                                            kits / 'Lib' / sdk_inc.name / 'um/x86'])
    return cl, cl.parent / 'link.exe', env


def build(jobs):
    cl, link, env = toolchain()
    gen, obj = GEN, OUT / 'obj'
    obj.mkdir(parents=True, exist_ok=True)
    # Original .c files hold lowered C++ too (compiled with /TP); placeholders of known files
    # without functions are not compiled.
    tree = [q for q in (gen / 'src').rglob('*') if q.suffix.lower() in ('.c', '.cpp')]
    sources = sorted(q for q in tree if '#include "machine257.h"' in q.read_text(encoding='utf-8'))
    sources += [gen / 'lowered_table.cpp', RUN / 'runtime_430.cpp']
    # Windows file names are case-insensitive: cl may keep an old object's spelling.
    keep = {p.stem.lower() for p in sources} | {'reserve_430'}
    header = gen / 'machine257.h'

    def stale(src):
        o = obj / (src.stem + '.obj')
        return not o.exists() or o.stat().st_mtime < max(src.stat().st_mtime, header.stat().st_mtime)

    sources = [s for s in sources if stale(s)]
    t0 = time.time()
    r = subprocess.CompletedProcess([], 0, '', '')
    if sources:
        # Hundreds of sources: pass them through a response file.
        rsp = OUT / 'compile.rsp'
        rsp.write_text('\n'.join(f'"{p}"' for p in sources), encoding='utf-8')
        cmd = [str(cl), '/nologo', '/c', '/TP', '/std:c++17', '/O2', '/GS-', '/EHs-c-', '/bigobj', '/W0', f'/MP{jobs}',
               f'/I{gen}', f'/Fo{obj}\\', f'@{rsp}']
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=OUT)
    (OUT / 'compile.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    compile_s = round(time.time() - t0, 1)
    for o in obj.glob('*.obj'):
        if o.stem.lower() not in keep:
            o.unlink()
    if r.returncode:
        errors = [ln for ln in r.stdout.splitlines() if ' error ' in ln]
        return dict(compile_seconds=compile_s, compile_errors=len(errors), first_errors=errors[:10])
    r = subprocess.run([str(cl.parent / 'ml.exe'), '/nologo', '/c', '/safeseh', f'/Fo{obj / "reserve_430.obj"}',
                        str(RUN / 'reserve_430.asm')], capture_output=True, text=True, env=env, cwd=OUT)
    if r.returncode:
        return dict(compile_seconds=compile_s, compile_errors=1, first_errors=r.stdout.splitlines()[-5:])
    exe = OUT / 'PorscheLowered.exe'
    link_rsp = OUT / 'link.rsp'
    link_rsp.write_text('\n'.join(f'"{p}"' for p in sorted(obj.glob('*.obj'))), encoding='utf-8')
    # Based at the original's 0x00400000: reserve_430.obj holds the original image's pages.
    cmd = [str(link), '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE,5.01', '/MANIFEST:NO', '/BASE:0x400000', '/DYNAMICBASE:NO',
           '/FIXED', '/NXCOMPAT', '/LARGEADDRESSAWARE', '/STACK:0x200000,0x200000', f'/OUT:{exe}', f'/MAP:{OUT / "PorscheLowered.map"}', f'@{link_rsp}',
           'kernel32.lib', 'user32.lib']
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=OUT)
    (OUT / 'link.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    return dict(compiled_sources=len(sources), compile_seconds=compile_s, compile_errors=0, link_exit=r.returncode,
                link_errors=[ln for ln in r.stdout.splitlines() if 'error' in ln][:10],
                exe_bytes=exe.stat().st_size if exe.exists() else 0)


# Humanized functions: readable VC6 C++ that replaces the lowered body of an entry (file in
# runs/430-lowered-whole-game/humanized/, with its own bridge `<name>_430`). Each one is proven
# against the original bytes by verify-v2-humanized-430.py before it is listed here.
#   abi:  'cdecl' (caller pops) or 'thiscall' (this in ECX, callee pops the stack arguments)
#   args: kinds of the stack arguments, used by the oracle: 'ptr' (into a buffer), 'str' (a
#         NUL-terminated string in it), 'dword', 'char'
#   this: kind of ECX for thiscall
#   call: C++ expression the bridge evaluates, with a0..a3 (stack arguments) and self (ECX)
#   ret:  True when the function returns a value (EAX)
HUMANIZED = {
    '00556640': dict(source='humanized/00556640.cpp', abi='cdecl', args=['ptr'], ret=True,
                     call='install_paths_size_00556640((const void *)a0)'),
    '0055f730': dict(source='humanized/0055f730.cpp', abi='cdecl', args=['ptr'], ret=True,
                     call='thread_handle_0055f730((const ThreadRecord *)a0)'),
    '0055f7e0': dict(source='humanized/0055f7e0.cpp', abi='cdecl', args=['ptr'], ret=True,
                     call='thread_id_0055f7e0((const ThreadRecord *)a0)'),
    '004d6510': dict(source='humanized/004d6510.cpp', abi='thiscall', this='ptr', args=[], ret=True,
                     call='((const PointerVector *)self)->count()'),
    '004d6520': dict(source='humanized/004d6520.cpp', abi='thiscall', this='ptr', args=['dword'], ret=True,
                     call='((const PointerVector *)self)->at(a0)'),
    '004d6530': dict(source='humanized/004d6530.cpp', abi='thiscall', this='ptr', args=[], ret=False,
                     call='((PointerVector *)self)->pop_back()'),
    '00423610': dict(source='humanized/00423610.cpp', abi='thiscall', this='ptr', args=[], ret=True,
                     call='((ContextObject *)self)->self()'),
    '0055d730': dict(source='humanized/0055d730.cpp', abi='cdecl', args=['ptr'], ret=True,
                     call='network_address_provider_mode_0055d730((const NetworkWorker *)a0)'),
    '0055d750': dict(source='humanized/0055d750.cpp', abi='cdecl', args=['ptr'], ret=True,
                     call='network_address_text_mode_0055d750((const NetworkWorker *)a0)'),
    '005a2870': dict(source='humanized/005a2870.cpp', abi='cdecl', args=['str', 'char'], ret=True,
                     call='formatter_text_find_last_005a2870((const char *)a0, (int)a1)'),
    # stream.c (verify-v2-humanized-stream-430.py: the functions call the stream lock and the
    # error handler, so they are proven with the original image mapped).
    '0056b380': dict(source='humanized/0056b380.cpp', abi='cdecl', args=['ptr', 'ptr', 'ptr'], ret=True,
                     oracle='stream', call='stream_handle_0056b380((StreamTap *)a0, (Stream **)a1, (StreamTap **)a2)'),
    '0056c000': dict(source='humanized/0056c000.cpp', abi='cdecl', args=['ptr', 'ptr'], ret=True,
                     oracle='stream', call='stream_filter_0056c000((Stream *)a0, (const StreamChunk *)a1)'),
    '0056be40': dict(source='humanized/0056be40.cpp', abi='cdecl', args=['ptr'], ret=True, calls_out=True,
                     oracle='stream', call='stream_classify_0056be40((Stream *)a0)'),
    '0056c540': dict(source='humanized/0056c540.cpp', abi='cdecl', args=['ptr'], ret=True, calls_out=True,
                     oracle='stream', call='STREAM_get((StreamTap *)a0)'),
    # Batch 2: leaf functions, some reading or writing globals at their original addresses.
    '00516950': dict(source='humanized/00516950.cpp', abi='cdecl', args=[], ret=False, call='startup_service_00516950()'),
    '005367b0': dict(source='humanized/005367b0.cpp', abi='cdecl', args=[], ret=True, call='window_runtime_zero_005367b0()'),
    '0059e9c0': dict(source='humanized/0059e9c0.cpp', abi='cdecl', args=['dword'], ret=True, call='heap_state_report_0059e9c0((const char *)a0)'),
    '00557460': dict(source='humanized/00557460.cpp', abi='cdecl', args=[], ret=True, call='startup_input_device_00557460()', globals=[('bytes', 7044088, 4)]),
    '00573980': dict(source='humanized/00573980.cpp', abi='cdecl', args=[], ret=True, call='window_main_handle_00573980()', globals=[('bytes', 6972576, 4)]),
    '005654d0': dict(source='humanized/005654d0.cpp', abi='cdecl', args=[], ret=False, call='window_input_binding_changed_005654d0()', globals=[('bytes', 6970412, 4)]),
    '005809f0': dict(source='humanized/005809f0.cpp', abi='cdecl', args=['ptr'], ret=True, call='network_worker_first_005809f0((const unsigned long *)a0)'),
    '0055c260': dict(source='humanized/0055c260.cpp', abi='cdecl', args=['dword'], ret=True, call='network_object_header_0055c260((void *)a0)'),
    '00535b40': dict(source='humanized/00535b40.cpp', abi='cdecl', args=['dword'], ret=False, call='render_mode_set_flag_00535b40((unsigned char)a0)', globals=[('bytes', 6937885, 1)]),
    '00592e00': dict(source='humanized/00592e00.cpp', abi='cdecl', args=['dword'], ret=False, call='mono_set_attribute_00592e00((unsigned char)a0)', globals=[('bytes', 6170088, 1)]),
    '00529050': dict(source='humanized/00529050.cpp', abi='thiscall', this='ptr', args=['ptr'], ret=True, call='((const NetworkMember *)self)->copy_to((unsigned long *)a0)'),
    '005aba53': dict(source='humanized/005aba53.cpp', abi='cdecl', args=['ptr'], ret=False, call='float_parse_clear_005aba53((unsigned long *)a0)'),
    '004c3150': dict(source='humanized/004c3150.cpp', abi='thiscall', this='ptrptr', args=['ptr'], ret=True, call='((const NetworkHolder *)self)->copy_to((unsigned long *)a0)'),
    '0050e140': dict(source='humanized/0050e140.cpp', abi='thiscall', this='ptr', args=['ptr'], ret=True, call='((NetworkValue *)self)->assign((const NetworkValue *)a0)'),
    '005a4b50': dict(source='humanized/005a4b50.cpp', abi='cdecl', args=['cursor'], ret=True, call='format_next_int_005a4b50((char **)a0)'),
    '005a4b6d': dict(source='humanized/005a4b6d.cpp', abi='cdecl', args=['cursor'], ret='ax', call='format_next_short_005a4b6d((char **)a0)'),
    '00505810': dict(source='humanized/00505810.cpp', abi='thiscall', this='ptr', args=['dword'], ret=True, call='((ContextRange *)self)->make_empty(a0)'),
    '005a4b5d': dict(source='humanized/005a4b5d.cpp', abi='cdecl', args=['cursor'], ret='edx:eax', call='format_next_int64_005a4b5d((char **)a0)'),
    '00537f90': dict(source='humanized/00537f90.cpp', abi='cdecl', args=['ptr'], ret=True, call='render_descriptor_bits_00537f90((const unsigned long *)a0)', globals=[('bytes', 6154384, 128)]),
    '00556620': dict(source='humanized/00556620.cpp', abi='cdecl', args=['dword'], ret=True, call='heap_suffix_00556620(a0)', globals=[('ptrs', 7032608, 16)]),
    '004d55c0': dict(source='humanized/004d55c0.cpp', abi='cdecl', args=['str'], ret=True, call='context_strlen_004d55c0((const char *)a0)'),
    '005a5449': dict(source='humanized/005a5449.cpp', abi='cdecl', args=['ptr'], ret=True, call='crt_stream_default_005a5449((CrtStreamRecord *)a0)'),
    '004d67b0': dict(source='humanized/004d67b0.cpp', abi='cdecl', args=['ptr', 'ptr'], ret=True, call='context_word_not_equal_004d67b0((const unsigned long *)a0, (const unsigned long *)a1)'),
    '00529a20': dict(source='humanized/00529a20.cpp', abi='thiscall', this='ptr', args=['ptr'], ret=False, call='((DequeIterator *)self)->set_node((char **)a0)'),
    '00565560': dict(source='humanized/00565560.cpp', abi='cdecl', args=[], ret=True, call='window_input_ready_00565560()', globals=[('maybezero', 7044116, 4), ('maybezero', 7044088, 4)]),
    '005aba38': dict(source='humanized/005aba38.cpp', abi='cdecl', args=['ptr', 'ptr'], ret=False, call='float_parse_copy_005aba38((unsigned long *)a0, (const unsigned long *)a1)'),
    '005aba5f': dict(source='humanized/005aba5f.cpp', abi='cdecl', args=['maybezero12'], ret=True, call='float_parse_is_zero_005aba5f((const unsigned long *)a0)'),
    '00569a70': dict(source='humanized/00569a70.cpp', abi='cdecl', args=[], ret=True, call='heap_first_free_00569a70()', globals=[('maybezero', 7032608, 64)]),
    '00580b70': dict(source='humanized/00580b70.cpp', abi='cdecl', args=['list', 'small'], ret=True, call='network_list_at_00580b70((ListNode **)a0, a1)'),
    '005299d0': dict(source='humanized/005299d0.cpp', abi='thiscall', this='ptr', args=['ptr'], ret=True, call='((DequeIterator16 *)self)->assign((const DequeIterator16 *)a0)'),
    '00467700': dict(source='humanized/00467700.cpp', abi='thiscall', this='ptr', args=['dword', 'dword'], ret=True, call='((RenderCore *)self)->construct(a0, a1)'),
    '005adaae': dict(source='humanized/005adaae.cpp', abi='cdecl', args=['dword', 'dword', 'ptr'], ret=True, call='float_add_carry_005adaae(a0, a1, (unsigned long *)a2)'),
    '00570ed0': dict(source='humanized/00570ed0.cpp', abi='cdecl', args=['ptr'], ret=False, call='cursor_state_save_00570ed0((unsigned long *)a0)', globals=[('bytes', 6153760, 96)]),
    '00560180': dict(source='humanized/00560180.cpp', abi='cdecl', args=['table:0x6b7c20:8'], ret=False, call='network_callback_remove_00560180(a0)', globals=[('bytes', 7044128, 32)]),
    '00574050': dict(source='humanized/00574050.cpp', abi='cdecl', args=['dword', 'dword'], ret=True, call='pixel_address_00574050((long)a0, (long)a1)', globals=[('bytes', 6153774, 1), ('bytes', 6153796, 4), ('bytes', 6153804, 4)]),
    '005a6abf': dict(source='humanized/005a6abf.cpp', abi='cdecl', args=[], ret=False, call='locale_reset_005a6abf()', globals=[('bytes', 7078636, 20), ('bytes', 7078912, 264)]),
    '005abf35': dict(source='humanized/005abf35.cpp', abi='cdecl', args=['handle'], ret=True, call='crt_handle_is_device_005abf35(a0)', globals=[('count', 7078624, 4), ('ptrs', 7078368, 4)]),
    '0055ed20': dict(source='humanized/0055ed20.cpp', abi='cdecl', args=['small8', 'dword'], ret=False, call='diagnostic_device_enable_0055ed20(a0, (long)a1)', globals=[('bytes', 6167696, 96)]),
    '005aa9aa': dict(source='humanized/005aa9aa.cpp', abi='cdecl', args=['dword'], ret=True, call='small_heap_find_005aa9aa((char *)a0)', globals=[('count', 7078352, 4), ('ptrs', 7078356, 1)]),
    '005ad2bf': dict(source='humanized/005ad2bf.cpp', abi='cdecl', args=['str', 'small'], ret=True, call='locale_strnlen_005ad2bf((const char *)a0, a1)'),
    '005a12cd': dict(source='humanized/005a12cd.cpp', abi='cdecl', args=['ptr', 'ptr', 'small'], ret=False, call='sort_swap_005a12cd((char *)a0, (char *)a1, a2)'),
    '005adb5b': dict(source='humanized/005adb5b.cpp', abi='cdecl', args=['ptr'], ret=False, call='float_shift_right_005adb5b((unsigned long *)a0)'),
}
# Later batches: humanized/specs/<batch>.json, {va: spec} with the same keys, plus
#   stubs: {callee_va: [nargs, 'cdecl'|'thiscall'|'stdcall']} for functions that call other
#          game code (the oracle replaces each callee by a recorder; calls_out is implied).
# Only functions whose oracle passed are listed (the oracle writes <batch>.oracle.json).
for _spec_file in sorted((RUN / 'humanized' / 'specs').glob('*.json')):
    if _spec_file.name.endswith('.oracle.json'):
        continue
    for _va, _h in json.loads(_spec_file.read_text(encoding='utf-8-sig')).items():
        if _h.get('stubs'):
            _h['calls_out'] = True
        HUMANIZED.setdefault(_va, _h)


def bridge_code(va, h):
    """The lowered-code entry of a humanized function: arguments from the guest stack (and ECX),
    result in EAX, the original RET (cdecl: caller pops; thiscall: RET 4*n)."""
    n = len(h['args'])
    lines = [f'/* {va}: entry from lowered code ({h["abi"]}, {n} stack argument{"s" if n != 1 else ""}). */',
             f'void humanized_{va}_430(Machine257 &s)', '{', '    U esp = s.r[4];']
    lines += [f'    U a{k} = read257(esp + {4 * (k + 1)}, 4);' for k in range(n)]
    if h['abi'] == 'thiscall':
        lines.append('    U self = s.r[1];')
    if h.get('calls_out'):
        lines.append('    U host = humanized_enter430();')
    if h['ret'] == 'ax':        # a 16-bit result: the upper half of EAX is not part of it
        lines.append(f'    s.r[0] = (s.r[0] & 0xffff0000u) | (unsigned short){h["call"]};')
    elif h['ret'] == 'al':        # an 8-bit result (bool)
        lines.append(f'    s.r[0] = (s.r[0] & 0xffffff00u) | (unsigned char){h["call"]};')
    elif h['ret'] == 'edx:eax':
        lines.append(f'    {{ __int64 v = {h["call"]}; s.r[0] = (U)v; s.r[2] = (U)(v >> 32); }}')
    elif h['ret']:
        lines.append(f'    s.r[0] = (U){h["call"]};')
    else:
        lines.append(f'    {h["call"]};')
    if h.get('calls_out'):
        lines.append('    humanized_leave430(host);')
    pop = 4 + (4 * n if h['abi'] == 'thiscall' else 0)
    lines += ['    s.pc = read257(esp, 4);', f'    s.r[4] = esp + {pop};', '    s.stop = STOP257_RETURNED;', '}']
    return '\n'.join(lines) + '\n'

VC6_ROOT = Path(os.environ.get('VC6_ROOT', r'D:\Microsoft Visual Studio\VC98'))
# Files VC6's optimizer cannot finish (HReplay.cpp: over 2.5 h at /O2); built with /Od.
VC6_NO_OPT = {'hreplay.cpp'}
# Functions VC6 /O2 miscompiles with frame-pointer omission (/Oy): the race crashes at start.
# Found by linking /O2 and /Od objects mixed, then per-function #pragma optimize; /Oy- (or /Og-)
# on this function alone fixes it. Kept with a frame pointer in every build.
VC6_NO_FPO = {0x004eb470}


def vc6_env():
    out = subprocess.run(f'cmd /c ""{VC6_ROOT / "Bin" / "VCVARS32.BAT"}" >nul && set"',
                         capture_output=True, text=True, shell=True).stdout
    return dict(line.split('=', 1) for line in out.splitlines() if '=' in line)


def build_vc6(jobs):
    """The same tree built with Visual C++ 6.0: cl per file (VC6 has no /MP), VC6 link."""
    env = vc6_env()
    gen, obj = GEN, OUT / ('obj-vc6' + os.environ.get('VC6_OBJ_SUFFIX', ''))
    obj.mkdir(parents=True, exist_ok=True)
    tree = [q for q in (gen / 'src').rglob('*') if q.suffix.lower() in ('.c', '.cpp')]
    sources = sorted(q for q in tree if '#include "machine257.h"' in q.read_text(encoding='utf-8'))
    sources += [gen / 'lowered_table.cpp', RUN / 'runtime_430.cpp', RUN / 'reserve_430.cpp']
    header = gen / 'machine257.h'
    target = {s: obj / f'{s.stem}.obj' for s in sources}

    def stale(src):
        o = target[src]
        return not o.exists() or o.stat().st_mtime < max(src.stat().st_mtime, header.stat().st_mtime)

    def compile_one(src):
        opt = '/Od' if src.name.lower() in VC6_NO_OPT else os.environ.get('VC6_OPT', '/O2')
        # /MT: the game is multithreaded, so the multithreaded static CRT (LIBCMT), as the original.
        r = subprocess.run([str(VC6_ROOT / 'Bin' / 'CL.EXE'), '/nologo', '/c', '/TP', '/MT', opt, '/W0', '/GX-', '/Zm500',
                            f'/I{gen}', f'/Fo{target[src]}', str(src)], capture_output=True, text=True, env=env)
        return src, [ln for ln in r.stdout.splitlines() if ' error ' in ln or 'fatal error' in ln]

    todo = [s for s in sources if stale(s)]
    t0 = time.time()
    with ThreadPoolExecutor(max(1, jobs)) as ex:
        results = list(ex.map(compile_one, todo))
    errors = [e for _, errs in results for e in errs]
    compile_s = round(time.time() - t0, 1)
    (OUT / 'compile-vc6.log').write_text('\n'.join(errors), encoding='utf-8')
    if errors:
        return dict(vc6=True, compile_seconds=compile_s, compile_errors=len(errors), first_errors=errors[:10])
    exe = OUT / f"PorscheLowered-vc6{os.environ.get('VC6_OBJ_SUFFIX', '')}.exe"
    rsp = OUT / 'link-vc6.rsp'
    # reserve_430.obj first: its .text contribution must be the first one, at 0x00401000.
    order = [target[RUN / 'reserve_430.cpp']] + [target[s] for s in sources if s.name != 'reserve_430.cpp']
    rsp.write_text('\n'.join(f'"{p}"' for p in order), encoding='utf-8')
    r = subprocess.run([str(VC6_ROOT / 'Bin' / 'LINK.EXE'), '/nologo', '/MACHINE:IX86', '/SUBSYSTEM:CONSOLE',
                        '/BASE:0x400000', '/FIXED', '/LARGEADDRESSAWARE', '/STACK:0x200000,0x200000',
                        f'/OUT:{exe}', f'/MAP:{OUT / "PorscheLowered-vc6.map"}', '/NODEFAULTLIB:libc.lib', f'@{rsp}',
                        'libcmt.lib', 'kernel32.lib', 'user32.lib', 'winmm.lib'], capture_output=True, text=True, env=env, cwd=OUT)
    (OUT / 'link-vc6.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    return dict(vc6=True, compiled_sources=len(todo), compile_seconds=compile_s, compile_errors=0,
                link_exit=r.returncode, link_errors=[ln for ln in r.stdout.splitlines() if 'error' in ln][:10],
                exe_bytes=exe.stat().st_size if exe.exists() else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--vc6', action='store_true', help='build with Visual C++ 6.0 (VC6_ROOT)')
    ap.add_argument('--generate-only', action='store_true')
    ap.add_argument('--build-only', action='store_true')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()
    data = PE_PATH.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PE_SHA
    img = Image(data)
    entries = [json.loads(ln) for ln in CATALOG.read_text(encoding='utf-8').splitlines() if ln.strip()]
    result = dict(schema=1, run='430-lowered-whole-game', original_sha256=PE_SHA, catalogued=len(entries))
    _, pointers = pointer_entries(img, entries)
    synthetic, closure = closed_entries(img, entries, pointers)
    result.update(pointer_targets=len(pointers), direct_targets=len(closure - set(pointers)),
                  synthetic_functions=len(synthetic))
    if not args.build_only:
        translate, header = backend()
        result.update(generate(translate, header, img, entries + synthetic, pointers))
    if not args.generate_only:
        result.update(build_vc6(args.jobs) if args.vc6 else build(args.jobs))
    print(json.dumps({k: v for k, v in result.items() if k != 'rejected'}, indent=1))
    (OUT / 'result.json').write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
