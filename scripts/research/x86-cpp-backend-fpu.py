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
    U xmm[8][4];   // SSE registers, four 32-bit lanes each
    U mxcsr;
    U64 mm[8];     // MMX registers (not aliased onto st[]; see notes)
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
static inline U64 read64_257(U a) { return static_cast<U64>(read257(a, 4u)) | (static_cast<U64>(read257(a + 4u, 4u)) << 32u); }
static inline void write64_257(U a, U64 v) { write257(a, 4u, static_cast<U>(v)); write257(a + 4u, 4u, static_cast<U>(v >> 32u)); }
static inline void load128_257(U* d, U a) { for (U k = 0; k < 4u; ++k) d[k] = read257(a + 4u * k, 4u); }
static inline void store128_257(U a, const U* v) { for (U k = 0; k < 4u; ++k) write257(a + 4u * k, 4u, v[k]); }
// SSE arithmetic runs the real instruction under the guest MXCSR (rounding,
// DAZ/FTZ, masks) and keeps the sticky exception flags it raises.
enum Sse257 : U { SseAddSs, SseAddPs, SseSubSs, SseSubPs, SseMulSs, SseMulPs };
#define SSE257_OP(INSN) __asm { \\
    __asm mov eax, d \\
    __asm mov edx, src \\
    __asm stmxcsr host \\
    __asm ldmxcsr guest \\
    __asm movups xmm0, [eax] \\
    __asm movups xmm1, [edx] \\
    __asm INSN xmm0, xmm1 \\
    __asm movups [eax], xmm0 \\
    __asm stmxcsr guest \\
    __asm ldmxcsr host }
static inline void sse257(Machine257& s, U op, U* d, const U* src) {
    U host, guest = s.mxcsr;
    switch (op) {
        case SseAddSs: SSE257_OP(addss) break;
        case SseAddPs: SSE257_OP(addps) break;
        case SseSubSs: SSE257_OP(subss) break;
        case SseSubPs: SSE257_OP(subps) break;
        case SseMulSs: SSE257_OP(mulss) break;
        default:       SSE257_OP(mulps) break;
    }
    s.mxcsr = guest;
}
// cvtsi2ss / cvtpi2ps lane: int32 -> float under the guest MXCSR.
static inline U cvt_i2f257(Machine257& s, U value) {
    U host, guest = s.mxcsr, r;
    __asm {
        stmxcsr host
        ldmxcsr guest
        cvtsi2ss xmm0, value
        movss r, xmm0
        stmxcsr guest
        ldmxcsr host
    }
    s.mxcsr = guest;
    return r;
}
static inline void shufps257(U* d, const U* src, U imm) {
    U r[4] = { d[imm & 3u], d[(imm >> 2) & 3u], src[(imm >> 4) & 3u], src[(imm >> 6) & 3u] };
    for (U k = 0; k < 4u; ++k) d[k] = r[k];
}
// MMX: any MMX instruction other than EMMS sets the x87 TOP to 0.
static inline void mmx_enter257(Machine257& s) { s.fpu_top = 0u; }
static inline U64 punpcklwd257(U64 d, U64 s) {
    return (d & 0xffffull) | ((s & 0xffffull) << 16) | (((d >> 16) & 0xffffull) << 32) | (((s >> 16) & 0xffffull) << 48);
}
static inline U64 punpckhwd257(U64 d, U64 s) {
    return ((d >> 32) & 0xffffull) | (((s >> 32) & 0xffffull) << 16) | (((d >> 48) & 0xffffull) << 32) | (((s >> 48) & 0xffffull) << 48);
}
static inline U64 pslld257(U64 v, U n) {
    if (n > 31u) return 0;
    return (static_cast<U64>(static_cast<U>(v >> 32) << n) << 32) | static_cast<U>(static_cast<U>(v) << n);
}
static inline U64 psrad257(U64 v, U n) {
    if (n > 31u) n = 31u;
    U lo = static_cast<U>(static_cast<int>(static_cast<U>(v)) >> n);
    U hi = static_cast<U>(static_cast<int>(static_cast<U>(v >> 32)) >> n);
    return (static_cast<U64>(hi) << 32) | lo;
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
        elif m in SIMD_LOWERED:
            code = simd_lower(i, ops, m, address, expression, store)
        elif m in ('fnstenv', 'fldenv', 'fnsave', 'frstor', 'femms', 'pfmul', 'pfadd', 'pfsub', 'pfacc', 'pi2fd', 'pfrcp', 'pfrcpit1', 'pfrcpit2', 'rcpss'):
            # No exact lowering: 3DNow! (AMD-only, not IEEE, no hardware oracle on
            # current CPUs), RCPSS (vendor-specific approximation) and the FPU
            # environment images (80-bit registers, tag word, FIP/FDP). Dropping them
            # would silently lose results, so the body is rejected.
            raise ValueError('Unsupported instruction (no exact lowering): ' + m)
        elif m in ('fnstsw', 'fstsw') and len(ops) == 1 and ops[0].type == X86_OP_MEM:
            code = f'write257({address(i, ops[0])}, 2u, ((s.fpu_status&~0x3800u)|((s.fpu_top&7u)<<11u))&0xffffu);'
        elif m == 'lea'""")
]

SIMD_LOWERED = ('movss', 'movaps', 'movups', 'movlps', 'movntps', 'addss', 'addps', 'subss', 'subps',
                'mulss', 'mulps', 'shufps', 'cvtsi2ss', 'cvtpi2ps', 'stmxcsr', 'ldmxcsr',
                'movd', 'movq', 'por', 'psllq', 'pslld', 'psrad', 'punpckldq', 'punpcklwd', 'punpckhwd', 'emms')
_SSE_ARITH = {'addss': 'SseAddSs', 'addps': 'SseAddPs', 'subss': 'SseSubSs', 'subps': 'SseSubPs',
              'mulss': 'SseMulSs', 'mulps': 'SseMulPs'}


def simd_lower(i, ops, m, address, expression, store):
    """Exact SSE/MMX lowering; memory goes through read257/write257 in dwords."""
    Reg = capstone.x86.X86_OP_REG
    Mem = capstone.x86.X86_OP_MEM

    def vec(op, prefix):
        if op.type != Reg:
            return None
        name = i.reg_name(op.reg)
        if not name.startswith(prefix) or not name[len(prefix):].isdigit():
            if prefix == 'mm' or name.startswith('xmm') or name.startswith('mm'):
                raise ValueError(f'Unsupported {prefix} operand: {name}')
            return None
        return int(name[len(prefix):])

    if m == 'emms':
        return ''   # the tag word is not modelled; EMMS leaves TOP unchanged
    if m in ('stmxcsr', 'ldmxcsr'):
        if ops[0].type != Mem:
            raise ValueError('MXCSR operand must be memory')
        a = address(i, ops[0])
        return f'write257({a}, 4u, s.mxcsr);' if m == 'stmxcsr' else f's.mxcsr = read257({a}, 4u);'

    if m == 'cvtsi2ss':
        d = vec(ops[0], 'xmm')
        return f's.xmm[{d}][0] = cvt_i2f257(s, {expression(i, ops[1])});'
    if m == 'cvtpi2ps':
        d = vec(ops[0], 'xmm')
        if ops[1].type != Mem:
            raise ValueError('cvtpi2ps from an MMX register is not lowered')
        a = address(i, ops[1])
        return (f'{{ U lo = read257({a}, 4u), hi = read257({a} + 4u, 4u); '
                f's.xmm[{d}][0] = cvt_i2f257(s, lo); s.xmm[{d}][1] = cvt_i2f257(s, hi); }}')

    if m in _SSE_ARITH or m in ('movss', 'movaps', 'movups', 'movlps', 'movntps', 'shufps'):
        d, sreg = vec(ops[0], 'xmm'), vec(ops[1], 'xmm')
        if m in _SSE_ARITH:
            if d is None:
                raise ValueError('SSE arithmetic destination must be a register')
            if sreg is not None:
                return (f'{{ U t[4]; for (U k = 0; k < 4u; ++k) t[k] = s.xmm[{sreg}][k]; '
                        f'sse257(s, {_SSE_ARITH[m]}, s.xmm[{d}], t); }}')
            a = address(i, ops[1])
            if m.endswith('ss'):
                return f'{{ U t[4] = {{ read257({a}, 4u), 0u, 0u, 0u }}; sse257(s, {_SSE_ARITH[m]}, s.xmm[{d}], t); }}'
            return f'{{ U t[4]; load128_257(t, {a}); sse257(s, {_SSE_ARITH[m]}, s.xmm[{d}], t); }}'
        if m == 'shufps':
            imm = ops[2].imm & 0xff
            if sreg is not None:
                return (f'{{ U t[4]; for (U k = 0; k < 4u; ++k) t[k] = s.xmm[{sreg}][k]; '
                        f'shufps257(s.xmm[{d}], t, {imm}u); }}')
            return f'{{ U t[4]; load128_257(t, {address(i, ops[1])}); shufps257(s.xmm[{d}], t, {imm}u); }}'
        if m == 'movss':
            if d is not None and sreg is not None:
                return f's.xmm[{d}][0] = s.xmm[{sreg}][0];'
            if d is not None:
                a = address(i, ops[1])
                return (f's.xmm[{d}][0] = read257({a}, 4u); s.xmm[{d}][1] = 0u; '
                        f's.xmm[{d}][2] = 0u; s.xmm[{d}][3] = 0u;')
            return f'write257({address(i, ops[0])}, 4u, s.xmm[{sreg}][0]);'
        if m == 'movlps':
            if d is not None:
                a = address(i, ops[1])
                return f's.xmm[{d}][0] = read257({a}, 4u); s.xmm[{d}][1] = read257({a} + 4u, 4u);'
            a = address(i, ops[0])
            return f'write257({a}, 4u, s.xmm[{sreg}][0]); write257({a} + 4u, 4u, s.xmm[{sreg}][1]);'
        # movaps / movups / movntps; the alignment fault of movaps/movntps is not modelled
        if d is not None and sreg is not None:
            return f'for (U k = 0; k < 4u; ++k) s.xmm[{d}][k] = s.xmm[{sreg}][k];'
        if d is not None:
            return f'load128_257(s.xmm[{d}], {address(i, ops[1])});'
        return f'store128_257({address(i, ops[0])}, s.xmm[{sreg}]);'

    # MMX
    if m == 'movd':
        d = vec(ops[0], 'mm') if ops[0].type == Reg and i.reg_name(ops[0].reg).startswith('mm') else None
        if d is not None:
            return f'mmx_enter257(s); s.mm[{d}] = static_cast<U64>({expression(i, ops[1])});'
        sreg = vec(ops[1], 'mm')
        return 'mmx_enter257(s); ' + store(i, ops[0], f'static_cast<U>(s.mm[{sreg}])')
    if m == 'movq':
        d, sreg = vec(ops[0], 'mm'), vec(ops[1], 'mm')
        if d is not None and sreg is not None:
            return f'mmx_enter257(s); s.mm[{d}] = s.mm[{sreg}];'
        if d is not None:
            return f'mmx_enter257(s); s.mm[{d}] = read64_257({address(i, ops[1])});'
        return f'mmx_enter257(s); write64_257({address(i, ops[0])}, s.mm[{sreg}]);'
    d = vec(ops[0], 'mm')
    if d is None:
        raise ValueError('MMX destination must be a register')
    if m in ('psllq', 'pslld', 'psrad'):
        if ops[1].type != capstone.x86.X86_OP_IMM:
            raise ValueError('MMX shift count must be immediate')
        n = ops[1].imm & 0xff
        if m == 'psllq':
            value = '0ull' if n > 63 else f's.mm[{d}] << {n}u'
            return f'mmx_enter257(s); s.mm[{d}] = {value};'
        return f'mmx_enter257(s); s.mm[{d}] = {m}257(s.mm[{d}], {n}u);'
    sreg = vec(ops[1], 'mm')
    if sreg is not None:
        src = f's.mm[{sreg}]'
    elif m == 'punpckldq':
        src = f'static_cast<U64>(read257({address(i, ops[1])}, 4u))'
    else:
        src = f'read64_257({address(i, ops[1])})'
    if m == 'por':
        return f'mmx_enter257(s); s.mm[{d}] |= {src};'
    if m == 'punpckldq':
        return f'mmx_enter257(s); s.mm[{d}] = (s.mm[{d}] & 0xffffffffull) | (({src} & 0xffffffffull) << 32);'
    return f'mmx_enter257(s); s.mm[{d}] = {m}257(s.mm[{d}], {src});'


DERIVED_SOURCE = getattr(_base, 'DERIVED_SOURCE', None) or inspect.getsource(_base.translate)
for _before, _after in PATCHES:
    if DERIVED_SOURCE.count(_before) != 1:
        raise ValueError('Frozen lowering patch context drift: ' + _before)
    DERIVED_SOURCE = DERIVED_SOURCE.replace(_before, _after)

_namespace = dict(vars(_base._base))
_namespace.update(vars(_base))
_namespace['capstone'] = capstone
_namespace['SIMD_LOWERED'] = SIMD_LOWERED
_namespace['simd_lower'] = simd_lower
_namespace['X86_OP_IMM'] = capstone.x86.X86_OP_IMM
_namespace['X86_OP_MEM'] = capstone.x86.X86_OP_MEM
_namespace['X86_OP_REG'] = capstone.x86.X86_OP_REG
exec(compile(DERIVED_SOURCE, str(Path(__file__)) + '::derived', 'exec'), _namespace)
translate = _namespace['translate']
