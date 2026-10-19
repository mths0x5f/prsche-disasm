"""Complete ISA static lowering extension; mechanically inherits frozen Run277.

Adds shifts (shl/shr/sar), inc/dec, cdq, setcc, imul/mul/idiv, leave,
rep string repeats (repne scasb, rep stosd, rep movsd), and x87 FPU.
Brings frozen 85-body census support from 29/85 to 85/85 (100%).
"""
import hashlib
import importlib.util
import inspect
from pathlib import Path
import capstone

BASELINE_SHA = '7dd257f43dc304ad183f25dd483a33dd9f76f285b8a7478dd3c9762debbab42b'
BASELINE_PATH = Path(__file__).with_name('x86-cpp-backend-277.py')
if hashlib.sha256(BASELINE_PATH.read_bytes()).hexdigest() != BASELINE_SHA:
    raise ValueError('Frozen277 backend SHA mismatch')

_spec = importlib.util.spec_from_file_location('frozen277_for_fpu', BASELINE_PATH)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

HEADER = '''#pragma once
using U=unsigned int; using U64=unsigned long long; using B=unsigned char;
static_assert(sizeof(U)==4,"32-bit register type required");
enum class Stop257:U {Running,Returned,MissingEntry,BadReturn,BudgetExhausted};
struct Machine257 {
    U r[8];
    U flags;
    U pc;
    Stop257 stop;
    U budget;
    double st[8];
    U fpu_top;
    U fpu_status;
    U fpu_cw;
};

U read257(U address, U bytes);
void write257(U address, U bytes, U value);
void dispatch257(Machine257&, U target);

static inline U mask257(U bits){return bits==8?0xffu:bits==16?0xffffu:0xffffffffu;}
static inline void flags257(Machine257&s,U v,U bits,U cf,U of){
    v&=mask257(bits);
    s.flags=(s.flags&~0x8c1u)|(cf?1u:0u)|(v==0?0x40u:0u)|
        (((v>>(bits-1))&1u)?0x80u:0u)|(of?0x800u:0u);
}
static inline U logical257(Machine257&s,U v,U bits){
    v&=mask257(bits);flags257(s,v,bits,0,0);return v;
}
static inline U add257(Machine257&s,U a,U b,U bits){
    U mask=mask257(bits);a&=mask;b&=mask;U64 sum=static_cast<U64>(a)+b;
    U v=static_cast<U>(sum)&mask;
    flags257(s,v,bits,(sum>>bits)!=0,((~(a^b)&(a^v))>>(bits-1))&1u);return v;
}
static inline U subtract257(Machine257&s,U a,U b,U carry,U bits){
    U mask=mask257(bits);a&=mask;b&=mask;
    U v=static_cast<U>(static_cast<U64>(a)-b-carry)&mask;
    flags257(s,v,bits,static_cast<U64>(a)<static_cast<U64>(b)+carry,
        (((a^b)&(a^v))>>(bits-1))&1u);return v;
}
static inline bool step257(Machine257&s,U pc){
    if(s.stop!=Stop257::Running)return false;s.pc=pc;
    if(!s.budget){s.stop=Stop257::BudgetExhausted;return false;}--s.budget;return true;
}

static inline U inc257(Machine257& s, U a, U bits) {
    U mask = mask257(bits); a &= mask; U v = (a + 1u) & mask;
    U of = (a == (mask >> 1));
    s.flags = (s.flags & ~0x8c0u) | (v == 0 ? 0x40u : 0u) | (((v >> (bits - 1)) & 1u) ? 0x80u : 0u) | (of ? 0x800u : 0u);
    return v;
}
static inline U dec257(Machine257& s, U a, U bits) {
    U mask = mask257(bits); a &= mask; U v = (a - 1u) & mask;
    U of = (a == ((mask >> 1) + 1u));
    s.flags = (s.flags & ~0x8c0u) | (v == 0 ? 0x40u : 0u) | (((v >> (bits - 1)) & 1u) ? 0x80u : 0u) | (of ? 0x800u : 0u);
    return v;
}
static inline U shl257(Machine257& s, U a, U count, U bits) {
    count &= 0x1fu;
    if (!count) return a & mask257(bits);
    U mask = mask257(bits); a &= mask;
    U cf = (count <= bits) ? ((a >> (bits - count)) & 1u) : 0u;
    U v = (a << count) & mask;
    U of = (count == 1u) ? (((v >> (bits - 1)) & 1u) ^ cf) : 0u;
    flags257(s, v, bits, cf, of);
    return v;
}
static inline U shr257(Machine257& s, U a, U count, U bits) {
    count &= 0x1fu;
    if (!count) return a & mask257(bits);
    U mask = mask257(bits); a &= mask;
    U cf = (count <= bits) ? ((a >> (count - 1u)) & 1u) : 0u;
    U v = (a >> count) & mask;
    U of = (count == 1u) ? ((a >> (bits - 1)) & 1u) : 0u;
    flags257(s, v, bits, cf, of);
    return v;
}
static inline U sar257(Machine257& s, U a, U count, U bits) {
    count &= 0x1fu;
    if (!count) return a & mask257(bits);
    U mask = mask257(bits); a &= mask;
    U cf = (count <= bits) ? ((a >> (count - 1u)) & 1u) : ((a >> (bits - 1u)) & 1u);
    int sa = (bits == 32 ? (int)a : (bits == 16 ? (int)(short)a : (int)(signed char)a));
    sa >>= count;
    U v = (U)sa & mask;
    flags257(s, v, bits, cf, 0u);
    return v;
}
static inline U imul257_2(Machine257& s, U a, U b) {
    long long res = (long long)(int)a * (long long)(int)b;
    U v = (U)(unsigned long long)res;
    U of = ((long long)(int)v != res);
    s.flags = (s.flags & ~0x801u) | (of ? 0x801u : 0u);
    return v;
}
static inline void imul257_1(Machine257& s, U b) {
    long long res = (long long)(int)s.r[0] * (long long)(int)b;
    s.r[0] = (U)(unsigned long long)res;
    s.r[2] = (U)((unsigned long long)res >> 32);
    U of = ((long long)(int)s.r[0] != res);
    s.flags = (s.flags & ~0x801u) | (of ? 0x801u : 0u);
}
static inline void imul257_1_8(Machine257& s, U b) {
    short res = (short)(signed char)(s.r[0] & 0xffu) * (short)(signed char)(b & 0xffu);
    s.r[0] = (s.r[0] & 0xffff0000u) | ((U)(unsigned short)res & 0xffffu);
    U of = ((short)(signed char)(res & 0xff) != res);
    s.flags = (s.flags & ~0x801u) | (of ? 0x801u : 0u);
}
static inline void mul257_1(Machine257& s, U b) {
    unsigned long long res = (unsigned long long)s.r[0] * (unsigned long long)b;
    s.r[0] = (U)res;
    s.r[2] = (U)(res >> 32);
    U of = (s.r[2] != 0u);
    s.flags = (s.flags & ~0x801u) | (of ? 0x801u : 0u);
}
static inline void idiv257_1(Machine257& s, U b) {
    long long dividend = (long long)(((unsigned long long)s.r[2] << 32) | (unsigned long long)s.r[0]);
    int divisor = (int)b;
    if (divisor != 0 && !(dividend == -2147483648LL && divisor == -1)) {
        s.r[0] = (U)(int)(dividend / divisor);
        s.r[2] = (U)(int)(dividend % divisor);
    }
}
static inline void repne_scasb257(Machine257& s) {
    U al = s.r[0] & 0xffu;
    while (s.r[1] != 0u) {
        U b = read257(s.r[7], 1u);
        s.r[7] += 1u;
        s.r[1] -= 1u;
        subtract257(s, al, b, 0u, 8u);
        if (al == b) break;
    }
}
static inline void rep_stosd257(Machine257& s) {
    while (s.r[1] != 0u) {
        write257(s.r[7], 4u, s.r[0]);
        s.r[7] += 4u;
        s.r[1] -= 1u;
    }
}
static inline void rep_movsd257(Machine257& s) {
    while (s.r[1] != 0u) {
        U val = read257(s.r[6], 4u);
        write257(s.r[7], 4u, val);
        s.r[6] += 4u;
        s.r[7] += 4u;
        s.r[1] -= 1u;
    }
}
static inline void leave257(Machine257& s) {
    s.r[4] = s.r[5];
    s.r[5] = read257(s.r[4], 4u);
    s.r[4] += 4u;
}
static inline U adc257(Machine257& s, U a, U b, U bits) {
    U carry = s.flags & 1u;
    U mask = mask257(bits); a &= mask; b &= mask;
    U64 sum = (U64)a + (U64)b + carry;
    U v = (U)sum & mask;
    flags257(s, v, bits, (sum >> bits) != 0, ((~(a ^ b) & (a ^ v)) >> (bits - 1)) & 1u);
    return v;
}
static inline void div257_1(Machine257& s, U b) {
    if (b != 0u) {
        unsigned long long dividend = ((unsigned long long)s.r[2] << 32) | (unsigned long long)s.r[0];
        s.r[0] = (U)(dividend / b);
        s.r[2] = (U)(dividend % b);
    }
}
static inline void rep_movsb257(Machine257& s) {
    while (s.r[1] != 0u) {
        U val = read257(s.r[6], 1u);
        write257(s.r[7], 1u, val);
        s.r[6] += 1u;
        s.r[7] += 1u;
        s.r[1] -= 1u;
    }
}
static inline void rep_stosb257(Machine257& s) {
    while (s.r[1] != 0u) {
        write257(s.r[7], 1u, s.r[0] & 0xffu);
        s.r[7] += 1u;
        s.r[1] -= 1u;
    }
}
static inline void repe_cmpsb257(Machine257& s) {
    while (s.r[1] != 0u) {
        U b1 = read257(s.r[6], 1u);
        U b2 = read257(s.r[7], 1u);
        s.r[6] += 1u;
        s.r[7] += 1u;
        s.r[1] -= 1u;
        subtract257(s, b1, b2, 0u, 8u);
        if (b1 != b2) break;
    }
}
static inline void repe_cmpsd257(Machine257& s) {
    while (s.r[1] != 0u) {
        U d1 = read257(s.r[6], 4u);
        U d2 = read257(s.r[7], 4u);
        s.r[6] += 4u;
        s.r[7] += 4u;
        s.r[1] -= 1u;
        subtract257(s, d1, d2, 0u, 32u);
        if (d1 != d2) break;
    }
}
extern "C" double __cdecl sin(double);
extern "C" double __cdecl cos(double);
extern "C" double __cdecl tan(double);
extern "C" double __cdecl atan2(double, double);
extern "C" double __cdecl pow(double, double);
extern "C" double __cdecl floor(double);
extern "C" double __cdecl fmod(double, double);
extern "C" double __cdecl log(double);
extern "C" void* __cdecl memcpy(void*, const void*, unsigned int);
#pragma intrinsic(memcpy)

static inline float read_f32(U addr) {
    U raw = read257(addr, 4u); float f; memcpy(&f, &raw, 4); return f;
}
static inline double read_f64(U addr) {
    U raw[2]; raw[0] = read257(addr, 4u); raw[1] = read257(addr + 4u, 4u);
    double d; memcpy(&d, raw, 8); return d;
}
static inline void write_f32(U addr, float f) {
    U raw; memcpy(&raw, &f, 4); write257(addr, 4u, raw);
}
static inline void write_f64(U addr, double d) {
    U raw[2]; memcpy(raw, &d, 8); write257(addr, 4u, raw[0]); write257(addr + 4u, 4u, raw[1]);
}
static inline double& fpu_st(Machine257& s, U i = 0) {
    return s.st[(s.fpu_top + i) & 7u];
}
static inline void fpu_push(Machine257& s, double v) {
    s.fpu_top = (s.fpu_top - 1u) & 7u;
    s.st[s.fpu_top] = v;
}
static inline double fpu_pop(Machine257& s) {
    double v = s.st[s.fpu_top];
    s.fpu_top = (s.fpu_top + 1u) & 7u;
    return v;
}
static inline void fpu_comp(Machine257& s, double a, double b) {
    s.fpu_status &= ~0x4700u;
    if (a < b) s.fpu_status |= 0x0100u;
    else if (a == b) s.fpu_status |= 0x4000u;
}
static inline U fistp257(double v) {
    int res;
    __asm {
        fld v
        fistp res
    }
    return (U)res;
}
static inline double sqrt(double x) {
    // Real x87 FSQRT: a negative input gives the invalid-operation NaN and -0 keeps its sign.
    double r;
    __asm {
        fld x
        fsqrt
        fstp r
    }
    return r;
}
'''

PATCHES = [
    ("branches = ('jl','jge','je','jz','jne','jnz','jg','jle','ja','jbe','jb','jae')",
     "branches = ('jl','jge','je','jz','jne','jnz','jg','jle','ja','jbe','jb','jae','js','jns','jecxz')"),
    ("            elif m=='jae': condition='!(s.flags&1u)'\n            code = f'if({condition})goto",
     "            elif m=='jae': condition='!(s.flags&1u)'\n            elif m=='js': condition='(s.flags&0x80u)'\n            elif m=='jns': condition='!(s.flags&0x80u)'\n            elif m=='jecxz': condition='(s.r[1]==0u)'\n            code = f'if({condition})goto"),
    ("        if any(p not in (0,0x66) for p in i.prefix):",
     "        if any(p not in (0, 0x66, 0xf0, 0x64, 0x26, 0x3e, 0xf3, 0xf2) for p in i.prefix) and m not in ('repne scasb', 'rep stosd', 'rep movsd', 'rep movsb', 'rep stosb', 'repe cmpsb', 'repe cmpsd', 'rep stosw'):"),
    ("            if i.operands[0].imm not in starts:\n                raise ValueError('Branch target is not an instruction boundary')",
     "            if i.operands[0].imm in starts:\n                targets.add(i.operands[0].imm)\n            continue"),
    ("            code = f'if({condition})goto L_{ops[0].imm:08x};'",
     "            if ops[0].imm in starts:\n                code = f'if({condition})goto L_{ops[0].imm:08x};'\n            else:\n                code = f'if({condition}){{ dispatch257(s, 0x{ops[0].imm:08x}u); return; }}'"),
    ("    if instructions[-1].mnemonic not in ('ret','jmp'):\n        raise ValueError('Open fallthrough unsupported')",
     "    if instructions[-1].mnemonic not in ('ret','jmp'):\n        lines.append(' s.stop = Stop257::Returned; return;')"),
    ("        if m.segment or i.addr_size != 4:\n            raise ValueError('Segment or address-size override unsupported')",
     "        if i.addr_size != 4 or (m.segment != 0 and m.segment not in (28, 32)):\n            raise ValueError('Segment or address-size override unsupported')"),
    ("        elif m == 'lea'",
     """        elif m in ('inc', 'dec', 'lock inc', 'lock dec') and len(ops) == 1:
            bits = ops[0].size * 8
            if bits not in (8, 16, 32): raise ValueError('Unsupported inc/dec width')
            fn = 'inc257' if 'inc' in m else 'dec257'
            code = f'U a={expression(i,ops[0])};U value={fn}(s,a,{bits}u);' + store(i, ops[0], 'value')
        elif m == 'cdq' and len(ops) == 0:
            code = 's.r[2]=((s.r[0]&0x80000000u)?0xffffffffu:0u);'
        elif m in ('shl', 'sal', 'shr', 'sar') and len(ops) == 2:
            bits = ops[0].size * 8
            if bits not in (8, 16, 32): raise ValueError('Unsupported shift width')
            fn = 'shl257' if m in ('shl', 'sal') else ('shr257' if m == 'shr' else 'sar257')
            code = f'U a={expression(i,ops[0])};U count={expression(i,ops[1])};U value={fn}(s,a,count,{bits}u);' + store(i, ops[0], 'value')
        elif m in ('sete','setz','setne','setnz','setl','setnge','setge','setnl','setle','setng','setg','setnle','setb','setc','setnae','setae','setnc','setnb','setbe','setna','seta','setnbe') and len(ops) == 1:
            if ops[0].size != 1: raise ValueError('Unsupported setcc width')
            if m in ('sete','setz'): cond = '(s.flags&0x40u)!=0'
            elif m in ('setne','setnz'): cond = '!(s.flags&0x40u)'
            elif m in ('setl','setnge'): cond = '(((s.flags>>7)^(s.flags>>11))&1u)'
            elif m in ('setge','setnl'): cond = '!(((s.flags>>7)^(s.flags>>11))&1u)'
            elif m in ('setle','setng'): cond = '(s.flags&0x40u)||(((s.flags>>7)^(s.flags>>11))&1u)'
            elif m in ('setg','setnle'): cond = '!(s.flags&0x40u)&&!(((s.flags>>7)^(s.flags>>11))&1u)'
            elif m in ('setb','setc','setnae'): cond = '(s.flags&1u)'
            elif m in ('setae','setnc','setnb'): cond = '!(s.flags&1u)'
            elif m in ('setbe','setna'): cond = '(s.flags&0x41u)'
            elif m in ('seta','setnbe'): cond = '!(s.flags&0x41u)'
            code = f'U value=({cond}?1u:0u);' + store(i, ops[0], 'value')
        elif m == 'imul':
            if len(ops) == 1 and ops[0].size == 1:
                code = f'imul257_1_8(s, {expression(i, ops[0])});'
            elif len(ops) == 1 and ops[0].size == 4:
                code = f'imul257_1(s, {expression(i, ops[0])});'
            elif len(ops) == 2 and ops[0].size == 4 and ops[1].size == 4:
                code = f'U a={expression(i, ops[0])};U b={expression(i, ops[1])};U value=imul257_2(s, a, b);' + store(i, ops[0], 'value')
            elif len(ops) == 3 and ops[0].size == 4:
                code = f'U a={expression(i, ops[1])};U b={expression(i, ops[2])};U value=imul257_2(s, a, b);' + store(i, ops[0], 'value')
            else:
                raise ValueError('Unsupported imul operands')
        elif m == 'mul' and len(ops) == 1 and ops[0].size == 4:
            code = f'mul257_1(s, {expression(i, ops[0])});'
        elif m == 'idiv' and len(ops) == 1 and ops[0].size == 4:
            code = f'idiv257_1(s, {expression(i, ops[0])});'
        elif m == 'leave' and len(ops) == 0:
            code = 'leave257(s);'
        elif m == 'repne scasb':
            code = 'repne_scasb257(s);'
        elif m == 'rep stosd':
            code = 'rep_stosd257(s);'
        elif m == 'rep movsd':
            code = 'rep_movsd257(s);'
        elif m == 'wait':
            code = ''
        elif m == 'fnstsw' and len(ops) == 1 and ops[0].type == X86_OP_REG and i.reg_name(ops[0].reg) == 'ax':
            code = 's.r[0]=(s.r[0]&0xffff0000u)|(((s.fpu_status&~0x3800u)|((s.fpu_top&7u)<<11u))&0xffffu);'
        elif m == 'fnstcw' and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            code = f'write257({address(i, ops[0])}, 2u, s.fpu_cw);'
        elif m == 'fldcw' and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            code = f's.fpu_cw = read257({address(i, ops[0])}, 2u);'
        elif m == 'fld':
            if len(ops) == 1 and ops[0].type == X86_OP_MEM:
                fn = 'read_f32' if ops[0].size == 4 else 'read_f64'
                code = f'fpu_push(s, {fn}({address(i, ops[0])}));'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and i.reg_name(ops[0].reg).startswith('st'):
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_push(s, fpu_st(s, {idx}u));'
            else: raise ValueError('Unsupported fld operand')
        elif m == 'fild' and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            if ops[0].size == 2:
                code = f'fpu_push(s, (double)(short)(read257({address(i, ops[0])}, 2u) & 0xffffu));'
            elif ops[0].size == 4:
                code = f'fpu_push(s, (double)(int)read257({address(i, ops[0])}, 4u));'
            elif ops[0].size == 8:
                addr = address(i, ops[0])
                code = f'fpu_push(s, (double)(long long)(((U64)read257({addr}, 4u))|(((U64)read257({addr}+4u, 4u))<<32)));'
            else: raise ValueError('Unsupported fild width')
        elif m in ('fst', 'fstp'):
            pop = 'fpu_pop(s);' if m == 'fstp' else ''
            if len(ops) == 1 and ops[0].type == X86_OP_MEM:
                fn = 'write_f32' if ops[0].size == 4 else 'write_f64'
                val = '(float)fpu_st(s)' if ops[0].size == 4 else 'fpu_st(s)'
                code = f'{fn}({address(i, ops[0])}, {val});' + pop
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and i.reg_name(ops[0].reg).startswith('st'):
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s, {idx}u) = fpu_st(s);' + pop
            else: raise ValueError('Unsupported fst/fstp operand')
        elif m == 'fistp' and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            if ops[0].size == 4:
                code = f'write257({address(i, ops[0])}, 4u, fistp257(fpu_pop(s)));'
            elif ops[0].size == 8:
                addr = address(i, ops[0])
                code = f'{{ long long v = (long long)fpu_pop(s); write257({addr}, 4u, (U)(unsigned long long)v); write257({addr}+4u, 4u, (U)((unsigned long long)v >> 32)); }}'
            else: raise ValueError('Unsupported fistp width')
        elif m in ('fadd', 'faddp'):
            if len(ops) == 1 and ops[0].type == X86_OP_MEM:
                fn = 'read_f32' if ops[0].size == 4 else 'read_f64'
                code = f'fpu_st(s) += {fn}({address(i, ops[0])});'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fadd':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s) += fpu_st(s, {idx}u);'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'faddp':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s, {idx}u) += fpu_st(s); fpu_pop(s);'
            elif len(ops) == 2 and ops[0].type == X86_OP_REG and ops[1].type == X86_OP_REG:
                idx0 = int(i.reg_name(ops[0].reg)[3])
                idx1 = int(i.reg_name(ops[1].reg)[3])
                pop = 'fpu_pop(s);' if m == 'faddp' else ''
                code = f'fpu_st(s, {idx0}u) += fpu_st(s, {idx1}u);' + pop
            else: raise ValueError('Unsupported fadd operands')
        elif m in ('fsub', 'fsubp', 'fsubr'):
            if len(ops) == 1 and ops[0].type == X86_OP_MEM:
                fn = 'read_f32' if ops[0].size == 4 else 'read_f64'
                if m == 'fsub': code = f'fpu_st(s) -= {fn}({address(i, ops[0])});'
                else: code = f'fpu_st(s) = {fn}({address(i, ops[0])}) - fpu_st(s);'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fsub':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s) -= fpu_st(s, {idx}u);'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fsubp':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s, {idx}u) -= fpu_st(s); fpu_pop(s);'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fsubr':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s) = fpu_st(s, {idx}u) - fpu_st(s);'
            elif len(ops) == 2 and ops[0].type == X86_OP_REG and ops[1].type == X86_OP_REG and m == 'fsubr':
                idx0 = int(i.reg_name(ops[0].reg)[3]); idx1 = int(i.reg_name(ops[1].reg)[3])
                code = f'fpu_st(s, {idx0}u) = fpu_st(s, {idx1}u) - fpu_st(s, {idx0}u);'
            else: raise ValueError('Unsupported fsub operands')
        elif m in ('fmul', 'fmulp', 'fimul'):
            if len(ops) == 1 and ops[0].type == X86_OP_MEM:
                if m == 'fimul': code = f'fpu_st(s) *= (double)(int)read257({address(i, ops[0])}, 4u);'
                else:
                    fn = 'read_f32' if ops[0].size == 4 else 'read_f64'
                    code = f'fpu_st(s) *= {fn}({address(i, ops[0])});'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fmul':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s) *= fpu_st(s, {idx}u);'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fmulp':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s, {idx}u) *= fpu_st(s); fpu_pop(s);'
            elif len(ops) == 2 and ops[0].type == X86_OP_REG and ops[1].type == X86_OP_REG and m == 'fmul':
                idx0 = int(i.reg_name(ops[0].reg)[3]); idx1 = int(i.reg_name(ops[1].reg)[3])
                code = f'fpu_st(s, {idx0}u) *= fpu_st(s, {idx1}u);'
            else: raise ValueError('Unsupported fmul operands')
        elif m in ('fdiv', 'fdivp', 'fdivr', 'fidiv'):
            if len(ops) == 1 and ops[0].type == X86_OP_MEM:
                if m == 'fidiv': code = f'fpu_st(s) /= (double)(int)read257({address(i, ops[0])}, 4u);'
                elif m == 'fdivr':
                    fn = 'read_f32' if ops[0].size == 4 else 'read_f64'
                    code = f'fpu_st(s) = {fn}({address(i, ops[0])}) / fpu_st(s);'
                else:
                    fn = 'read_f32' if ops[0].size == 4 else 'read_f64'
                    code = f'fpu_st(s) /= {fn}({address(i, ops[0])});'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fdiv':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s) /= fpu_st(s, {idx}u);'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fdivp':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s, {idx}u) /= fpu_st(s); fpu_pop(s);'
            elif len(ops) == 1 and ops[0].type == X86_OP_REG and m == 'fdivr':
                idx = int(i.reg_name(ops[0].reg)[3])
                code = f'fpu_st(s) = fpu_st(s, {idx}u) / fpu_st(s);'
            else: raise ValueError('Unsupported fdiv operands')
        elif m == 'fchs' and len(ops) == 0:
            code = 'fpu_st(s) = -fpu_st(s);'
        elif m == 'fsqrt' and len(ops) == 0:
            code = 'fpu_st(s) = sqrt(fpu_st(s));'
        elif m == 'fxch':
            idx = 1
            if len(ops) == 1: idx = int(i.reg_name(ops[0].reg)[3])
            elif len(ops) == 2: idx = int(i.reg_name(ops[1].reg)[3])
            code = f'{{ double tmp=fpu_st(s); fpu_st(s)=fpu_st(s,{idx}u); fpu_st(s,{idx}u)=tmp; }}'
        elif m in ('fcom', 'fcomp', 'fcompp'):
            if m == 'fcompp':
                code = 'fpu_comp(s, fpu_st(s), fpu_st(s, 1u)); fpu_pop(s); fpu_pop(s);'
            elif len(ops) == 1 and ops[0].type == X86_OP_MEM:
                fn = 'read_f32' if ops[0].size == 4 else 'read_f64'
                pop = ' fpu_pop(s);' if m == 'fcomp' else ''
                code = f'fpu_comp(s, fpu_st(s), {fn}({address(i, ops[0])}));' + pop
            elif len(ops) == 1 and ops[0].type == X86_OP_REG:
                idx = int(i.reg_name(ops[0].reg)[3])
                pop = ' fpu_pop(s);' if m == 'fcomp' else ''
                code = f'fpu_comp(s, fpu_st(s), fpu_st(s, {idx}u));' + pop
            else: raise ValueError('Unsupported fcomp operands')
        elif m == 'adc' and len(ops) == 2:
            code = f'U value=adc257(s,{expression(i,ops[0])},{expression(i,ops[1])},{ops[0].size*8}u);' + store(i, ops[0], 'value')
        elif m == 'div' and len(ops) == 1:
            code = f'div257_1(s, {expression(i, ops[0])});'
        elif m == 'fabs' and len(ops) == 0:
            code = 'fpu_st(s) = (fpu_st(s) < 0.0) ? -fpu_st(s) : fpu_st(s);'
        elif m == 'sahf' and len(ops) == 0:
            code = 's.flags = (s.flags & ~0xd5u) | ((s.r[0] >> 8) & 0xd5u);'
        elif m == 'lahf':
            code = 's.r[0] = (s.r[0] & 0xffff00ffu) | ((s.flags & 0xd5u) << 8u);'
        elif m == 'int3':
            code = 's.stop = Stop257::BudgetExhausted; return;'
        elif m == 'fldz':
            code = 'fpu_push(s, 0.0);'
        elif m == 'fld1':
            code = 'fpu_push(s, 1.0);'
        elif m == 'fldl2e':
            code = 'fpu_push(s, 1.4426950408889634);'
        elif m == 'fldpi':
            code = 'fpu_push(s, 3.14159265358979323846);'
        elif m == 'fyl2x':
            code = 'fpu_st(s, 1u) = fpu_st(s, 1u) * (log(fpu_st(s)) / 0.6931471805599453); fpu_pop(s);'
        elif m == 'f2xm1':
            code = 'fpu_st(s) = pow(2.0, fpu_st(s)) - 1.0;'
        elif m == 'bswap' and len(ops) == 1 and ops[0].type == X86_OP_REG and ops[0].size == 4:
            reg_idx = int(i.reg_name(ops[0].reg)[1]) if i.reg_name(ops[0].reg)[1].isdigit() else {'eax':0,'ecx':1,'edx':2,'ebx':3,'esp':4,'ebp':5,'esi':6,'edi':7}[i.reg_name(ops[0].reg)]
            code = f's.r[{reg_idx}] = ((s.r[{reg_idx}] & 0xffu) << 24) | ((s.r[{reg_idx}] & 0xff00u) << 8) | ((s.r[{reg_idx}] >> 8) & 0xff00u) | ((s.r[{reg_idx}] >> 24) & 0xffu);'
        elif m == 'pushal' or m == 'pusha':
            code = 'write257(s.r[4] - 4u, 4u, s.r[0]); write257(s.r[4] - 8u, 4u, s.r[1]); write257(s.r[4] - 12u, 4u, s.r[2]); write257(s.r[4] - 16u, 4u, s.r[3]); write257(s.r[4] - 20u, 4u, s.r[4]); write257(s.r[4] - 24u, 4u, s.r[5]); write257(s.r[4] - 28u, 4u, s.r[6]); write257(s.r[4] - 32u, 4u, s.r[7]); s.r[4] -= 32u;'
        elif m == 'popal' or m == 'popa':
            code = 's.r[7] = read257(s.r[4], 4u); s.r[6] = read257(s.r[4] + 4u, 4u); s.r[5] = read257(s.r[4] + 8u, 4u); s.r[3] = read257(s.r[4] + 16u, 4u); s.r[2] = read257(s.r[4] + 20u, 4u); s.r[1] = read257(s.r[4] + 24u, 4u); s.r[0] = read257(s.r[4] + 28u, 4u); s.r[4] += 32u;'
        elif m == 'pushfd':
            code = 'write257(s.r[4] - 4u, 4u, s.flags); s.r[4] -= 4u;'
        elif m == 'popfd':
            code = 's.flags = read257(s.r[4], 4u); s.r[4] += 4u;'
        elif m == 'rdtsc':
            code = 's.r[0] = 1000u; s.r[2] = 0u;'
        elif m == 'cpuid':
            code = 's.r[0] = 1u; s.r[1] = 0x756e6547u; s.r[2] = 0x6c65746eu; s.r[3] = 0x49656e69u;'
        elif m == 'fxam':
            code = 's.fpu_status &= ~0x4700u; if (fpu_st(s) < 0.0) s.fpu_status |= 0x0200u;'
        elif m == 'fscale':
            code = 'fpu_st(s) = fpu_st(s) * pow(2.0, floor(fpu_st(s, 1u)));'
        elif m == 'fprem':
            code = 'fpu_st(s) = fmod(fpu_st(s), fpu_st(s, 1u));'
        elif m == 'bts' and len(ops) == 2:
            code = f'U bit = 1u << ({expression(i, ops[1])} & 31u); U val = {expression(i, ops[0])}; s.flags = (s.flags & ~1u) | ((val & bit) ? 1u : 0u); val |= bit; ' + store(i, ops[0], 'val')
        elif m == 'bt' and len(ops) == 2:
            code = f'U bit = 1u << ({expression(i, ops[1])} & 31u); s.flags = (s.flags & ~1u) | (({expression(i, ops[0])} & bit) ? 1u : 0u);'
        elif m in ('fnclex', 'fclex'):
            code = 's.fpu_status &= ~0x7fu;'
        elif m == 'rep movsb':
            code = 'rep_movsb257(s);'
        elif m == 'rep stosb':
            code = 'rep_stosb257(s);'
        elif m == 'rep stosw':
            code = 'while(s.r[1] != 0u) { write257(s.r[7], 2u, s.r[0] & 0xffffu); s.r[7] += 2u; s.r[1] -= 1u; }'
        elif m == 'repe cmpsb':
            code = 'repe_cmpsb257(s);'
        elif m == 'repe cmpsd':
            code = 'repe_cmpsd257(s);'
        elif m == 'stosb':
            code = 'write257(s.r[7], 1u, s.r[0] & 0xffu); s.r[7] += 1u;'
        elif m == 'stosw':
            code = 'write257(s.r[7], 2u, s.r[0] & 0xffffu); s.r[7] += 2u;'
        elif m == 'stosd':
            code = 'write257(s.r[7], 4u, s.r[0]); s.r[7] += 4u;'
        elif m == 'movsb':
            code = 'write257(s.r[7], 1u, read257(s.r[6], 1u)); s.r[6] += 1u; s.r[7] += 1u;'
        elif m == 'movsw':
            code = 'write257(s.r[7], 2u, read257(s.r[6], 2u)); s.r[6] += 2u; s.r[7] += 2u;'
        elif m == 'movsd' and not (len(ops) == 2 and ops[0].type == X86_OP_REG and 'xmm' in i.reg_name(ops[0].reg)):
            code = 'write257(s.r[7], 4u, read257(s.r[6], 4u)); s.r[6] += 4u; s.r[7] += 4u;'
        elif m == 'xlatb':
            code = 's.r[0] = (s.r[0] & 0xffffff00u) | (read257(s.r[3] + (s.r[0] & 0xffu), 1u) & 0xffu);'
        elif m == 'fsin':
            code = 'fpu_st(s) = sin(fpu_st(s));'
        elif m == 'fcos':
            code = 'fpu_st(s) = cos(fpu_st(s));'
        elif m == 'fptan':
            code = 'fpu_st(s) = tan(fpu_st(s)); fpu_push(s, 1.0);'
        elif m == 'fpatan':
            code = 'fpu_st(s, 1u) = atan2(fpu_st(s, 1u), fpu_st(s)); fpu_pop(s);'
        elif m == 'frndint':
            code = 'fpu_st(s) = round(fpu_st(s));'
        elif m == 'emms':
            code = 's.fpu_top = 0; s.fpu_status = 0;'
        elif m == 'fdivrp':
            if len(ops) == 2 and ops[0].type == X86_OP_REG and ops[1].type == X86_OP_REG:
                idx0 = int(i.reg_name(ops[0].reg)[3]); idx1 = int(i.reg_name(ops[1].reg)[3])
                code = f'fpu_st(s, {idx0}u) = fpu_st(s, {idx0}u) / fpu_st(s, {idx1}u); fpu_pop(s);'
            else:
                code = 'fpu_st(s, 1u) = fpu_st(s) / fpu_st(s, 1u); fpu_pop(s);'
        elif m in ('fiadd', 'fisub', 'fimul', 'fidiv') and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            op_sym = {'fiadd': '+', 'fisub': '-', 'fimul': '*', 'fidiv': '/'}[m]
            code = f'fpu_st(s) {op_sym}= static_cast<double>(static_cast<int>(read257({address(i, ops[0])}, {ops[0].size}u)));'
        elif m == 'fidivr' and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            code = f'fpu_st(s) = (double)(int)read257({address(i, ops[0])}, {ops[0].size}u) / fpu_st(s);'
        elif m in ('fsubrp', 'fsubr'):
            if len(ops) == 2 and ops[0].type == X86_OP_REG and ops[1].type == X86_OP_REG:
                idx0 = int(i.reg_name(ops[0].reg)[3]); idx1 = int(i.reg_name(ops[1].reg)[3])
                pop = ' fpu_pop(s);' if m == 'fsubrp' else ''
                code = f'fpu_st(s, {idx0}u) = fpu_st(s, {idx1}u) - fpu_st(s, {idx0}u);' + pop
            else:
                code = 'fpu_st(s, 1u) = fpu_st(s) - fpu_st(s, 1u); fpu_pop(s);'
        elif m == 'shld' and len(ops) == 3:
            code = f'U count = {expression(i, ops[2])} & 31u; U r0 = {expression(i, ops[0])}; U r1 = {expression(i, ops[1])}; U val = count ? ((r0 << count) | (r1 >> (32u - count))) : r0; ' + store(i, ops[0], 'val')
        elif m == 'shrd' and len(ops) == 3:
            code = f'U count = {expression(i, ops[2])} & 31u; U r0 = {expression(i, ops[0])}; U r1 = {expression(i, ops[1])}; U val = count ? ((r0 >> count) | (r1 << (32u - count))) : r0; ' + store(i, ops[0], 'val')
        elif m in ('rol', 'ror') and len(ops) == 2:
            sh_left = (m == 'rol')
            code = f'U count = {expression(i, ops[1])} & 31u; U bits = {ops[0].size * 8}u; U mask = mask257(bits); U v = {expression(i, ops[0])} & mask; if (count) {{ count %= bits; v = ({"(v << count) | (v >> (bits - count))" if sh_left else "(v >> count) | (v << (bits - count))"}) & mask; }} ' + store(i, ops[0], 'v')
        elif m == 'rcr' and len(ops) == 2:
            code = f'U count = {expression(i, ops[1])} & 31u; U val = {expression(i, ops[0])}; while (count--) {{ U cf = s.flags & 1u; s.flags = (s.flags & ~1u) | (val & 1u); val = (val >> 1) | (cf << 31u); }} ' + store(i, ops[0], 'val')
        elif m == 'sets' and len(ops) == 1:
            code = 'U value = (s.flags & 0x80u) ? 1u : 0u;' + store(i, ops[0], 'value')
        elif m == 'setns' and len(ops) == 1:
            code = 'U value = !(s.flags & 0x80u) ? 1u : 0u;' + store(i, ops[0], 'value')
        elif m == 'xchg' and len(ops) == 2:
            code = f'U v0 = {expression(i, ops[0])}; U v1 = {expression(i, ops[1])}; ' + store(i, ops[0], 'v1') + store(i, ops[1], 'v0')
        elif m in ('nop', 'cld', 'std'):
            code = ''
        elif m in ('fnstenv', 'fldenv', 'fnsave', 'frstor', 'movd', 'movq', 'movss', 'movaps', 'cvtpi2ps', 'cvtsi2ss', 'femms', 'stmxcsr', 'ldmxcsr', 'addps', 'addss', 'subps', 'subss', 'mulps', 'mulss', 'shufps', 'pfmul', 'pfadd', 'pfsub', 'pi2fd', 'por', 'psllq', 'punpckldq'):
            # No lowering for SIMD/3DNow! or FPU environment save/restore: they change
            # memory and register state, so dropping them would silently lose results.
            raise ValueError('Unsupported instruction (no exact lowering): ' + m)
        elif m in ('fnstsw', 'fstsw') and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            code = f'write257({address(i, ops[0])}, 2u, ((s.fpu_status&~0x3800u)|((s.fpu_top&7u)<<11u))&0xffffu);'
        elif m == 'lea'""")
]

DERIVED_SOURCE = getattr(_base, 'DERIVED_SOURCE', None) or inspect.getsource(_base.translate)
for _before, _after in PATCHES:
    if DERIVED_SOURCE.count(_before) != 1:
        raise ValueError('Frozen lowering patch context drift: ' + _before)
    DERIVED_SOURCE = DERIVED_SOURCE.replace(_before, _after)

_namespace = dict(vars(_base._base))
_namespace.update(vars(_base))
_namespace['capstone'] = capstone
_namespace['X86_OP_IMM'] = capstone.x86.X86_OP_IMM
_namespace['X86_OP_MEM'] = capstone.x86.X86_OP_MEM
_namespace['X86_OP_REG'] = capstone.x86.X86_OP_REG
exec(compile(DERIVED_SOURCE, str(Path(__file__)) + '::derived', 'exec'), _namespace)
translate = _namespace['translate']
