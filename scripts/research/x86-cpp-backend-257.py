"""Experimental static x86 lowering. No opcode interpreter or native-code fallback.

Memory/dispatch are explicit fixture boundaries; only CF/ZF/SF/OF are modeled.
This module is not a PE loader, complete CPU, or accepted game implementation.
"""
import capstone
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG

REG = {n: i for i, n in enumerate(('eax','ecx','edx','ebx','esp','ebp','esi','edi'))}
SUBREG = {n: (i, 0, 16) for i, n in enumerate(('ax','cx','dx','bx','sp','bp','si','di'))}
SUBREG.update({n: (i, 0, 8) for i, n in enumerate(('al','cl','dl','bl'))})
SUBREG.update({n: (i, 8, 8) for i, n in enumerate(('ah','ch','dh','bh'))})

HEADER = '''#pragma once
using U=unsigned int; using U64=unsigned long long; using B=unsigned char;
static_assert(sizeof(U)==4,"32-bit register type required");
enum class Stop257:U {Running,Returned,MissingEntry,BadReturn,BudgetExhausted};
struct Machine257 {U r[8];U flags;U pc;Stop257 stop;U budget;};
U read257(U address,U bytes);
void write257(U address,U bytes,U value);
void dispatch257(Machine257&,U target);
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
// Target is evaluated by generated caller before ESP changes.
static inline bool call257(Machine257&s,U target,U returnPC){
 s.r[4]-=4u;write257(s.r[4],4u,returnPC);dispatch257(s,target);
 if(s.stop==Stop257::MissingEntry||s.stop==Stop257::BadReturn||
    s.stop==Stop257::BudgetExhausted)return false;
 if(s.stop!=Stop257::Returned||s.pc!=returnPC){s.stop=Stop257::BadReturn;return false;}
 s.stop=Stop257::Running;return true;
}
'''


def translate(raw, entry):
    if not isinstance(entry, int) or not 0 <= entry <= 0xffffffff:
        raise ValueError('Invalid entry')
    if not raw or entry + len(raw) > 0x100000000:
        raise ValueError('Empty or wrapping body')
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(raw, entry))
    if sum(i.size for i in instructions) != len(raw):
        raise ValueError('Undecoded bytes')
    starts = {i.address for i in instructions}
    branches = ('jl','jge','je','jz','jne','jnz')
    targets = set()
    for i in instructions:
        if i.mnemonic in branches:
            if len(i.operands) != 1 or i.operands[0].type != X86_OP_IMM:
                raise ValueError('Unsupported conditional target')
            if i.operands[0].imm not in starts:
                raise ValueError('Branch target is not an instruction boundary')
            targets.add(i.operands[0].imm)
        elif i.mnemonic == 'jmp' and len(i.operands) == 1 and i.operands[0].type == X86_OP_IMM:
            target = i.operands[0].imm
            if entry <= target < entry+len(raw) and target not in starts:
                raise ValueError('JMP target is not an instruction boundary')
            if target in starts:
                targets.add(target)

    def address(i, op):
        m = op.mem
        if m.segment or i.addr_size != 4:
            raise ValueError('Segment or address-size override unsupported')
        terms = [f'0x{m.disp & 0xffffffff:08x}u']
        for register, scale in ((m.base, 1), (m.index, m.scale)):
            if register:
                name = i.reg_name(register)
                if name not in REG or scale not in (1,2,4,8):
                    raise ValueError('Unsupported address register/scale')
                terms.append(f's.r[{REG[name]}]*{scale}u')
        return '(' + '+'.join(terms) + ')'

    def expression(i, op):
        if op.type == X86_OP_IMM:
            return f'0x{op.imm & 0xffffffff:08x}u'
        if op.type == X86_OP_REG:
            name = i.reg_name(op.reg)
            if name in REG and op.size == 4:
                return f's.r[{REG[name]}]'
            if name in SUBREG:
                index, shift, bits = SUBREG[name]
                if op.size*8 == bits:
                    return f'((s.r[{index}]>>{shift})&0x{(1<<bits)-1:x}u)'
        if op.type == X86_OP_MEM and op.size in (1,2,4):
            return f'read257({address(i,op)},{op.size}u)'
        raise ValueError('Unsupported operand')

    def store(i, op, value):
        if op.type == X86_OP_REG:
            name = i.reg_name(op.reg)
            if name in REG and op.size == 4:
                return f's.r[{REG[name]}]={value};'
            if name in SUBREG:
                index, shift, bits = SUBREG[name]
                if op.size*8 == bits:
                    mask = ((1<<bits)-1)<<shift
                    return (f's.r[{index}]=(s.r[{index}]&0x{~mask & 0xffffffff:08x}u)|'
                            f'((({value})&0x{(1<<bits)-1:x}u)<<{shift});')
        if op.type == X86_OP_MEM and op.size in (1,2,4):
            return f'write257({address(i,op)},{op.size}u,{value});'
        raise ValueError('Unsupported destination')

    lines = ['#include "machine257.h"',f'void translated_{entry:08x}(Machine257&s){{']
    witnesses = []
    for i in instructions:
        ops, m = i.operands, i.mnemonic
        if any(p not in (0,0x66) for p in i.prefix):
            raise ValueError('Unsupported instruction prefix')
        if m in ('push','pop','call','ret','jmp',*branches) and 0x66 in i.prefix:
            raise ValueError('16-bit stack/control operation unsupported')
        if m == 'mov' and len(ops) == 2:
            code = 'U value='+expression(i,ops[1])+';'+store(i,ops[0],'value')
        elif m == 'lea' and len(ops) == 2 and ops[1].type == X86_OP_MEM and ops[0].type == X86_OP_REG:
            code = 'U value='+address(i,ops[1])+';'+store(i,ops[0],'value')
        elif m in ('xor','and','test','cmp','sbb','sub','add') and len(ops) == 2:
            bits = ops[0].size*8
            if bits not in (8,16,32):
                raise ValueError('Unsupported arithmetic width')
            a,b = expression(i,ops[0]),expression(i,ops[1])
            code = f'U a={a};U b={b};'
            if m in ('xor','and','test'):
                value = f'logical257(s,a'+('^' if m == 'xor' else '&')+f'b,{bits}u)'
            elif m == 'add':
                value = f'add257(s,a,b,{bits}u)'
            else:
                value = f'subtract257(s,a,b,'+('(s.flags&1u)' if m == 'sbb' else '0u')+f',{bits}u)'
            code += f'U value={value};'
            code += '(void)value;' if m in ('test','cmp') else store(i,ops[0],'value')
        elif m == 'neg' and len(ops) == 1:
            if ops[0].size not in (1,2,4):
                raise ValueError('Unsupported NEG width')
            code = (f'U a={expression(i,ops[0])};U value=subtract257(s,0u,a,0u,{ops[0].size*8}u);'
                    +store(i,ops[0],'value'))
        elif m in branches:
            condition = '(((s.flags>>7)^(s.flags>>11))&1u)'
            if m == 'jge': condition = '!'+condition
            elif m in ('je','jz'): condition = '(s.flags&0x40u)'
            elif m in ('jne','jnz'): condition = '!(s.flags&0x40u)'
            code = f'if({condition})goto L_{ops[0].imm:08x};'
        elif m == 'push' and len(ops) == 1 and ops[0].size == 4:
            code = f'U value={expression(i,ops[0])};s.r[4]-=4u;write257(s.r[4],4u,value);'
        elif m == 'pop' and len(ops) == 1 and ops[0].size == 4 and ops[0].type in (X86_OP_REG,X86_OP_MEM):
            code = 'U value=read257(s.r[4],4u);s.r[4]+=4u;'+store(i,ops[0],'value')
        elif m == 'call' and len(ops) == 1 and ops[0].size == 4:
            if ops[0].type == X86_OP_IMM and entry <= ops[0].imm < entry+len(raw) and ops[0].imm not in starts:
                raise ValueError('CALL target is not an instruction boundary')
            code = (f'U target={expression(i,ops[0])};'
                    f'if(!call257(s,target,0x{i.address+i.size:08x}u))return;')
        elif m == 'jmp' and len(ops) == 1 and ops[0].size == 4:
            if ops[0].type == X86_OP_IMM and ops[0].imm in starts:
                code = f'goto L_{ops[0].imm:08x};'
            else:
                code = f'U target={expression(i,ops[0])};dispatch257(s,target);return;'
        elif m == 'ret' and (not ops or (len(ops)==1 and ops[0].type==X86_OP_IMM)):
            pop = ops[0].imm if ops else 0
            if not 0 <= pop <= 65535:
                raise ValueError('Invalid RET immediate')
            code = f's.pc=read257(s.r[4],4u);s.r[4]+={4+pop}u;s.stop=Stop257::Returned;return;'
        else:
            raise ValueError(f'Unsupported opcode {i.address:08x}: {m} {i.op_str}')
        if i.address in targets:
            lines.append(f'L_{i.address:08x}:')
        lines.append(f' // {i.address:08x} {i.bytes.hex()} {m} {i.op_str}\n'
                     f' if(!step257(s,0x{i.address:08x}u))return;\n {{ {code} }}')
        witnesses.append(dict(va=f'{i.address:08x}',bytes=i.bytes.hex(),mnemonic=m,operands=i.op_str,cpp=code))
    if instructions[-1].mnemonic not in ('ret','jmp'):
        raise ValueError('Open fallthrough unsupported')
    lines.append('}\n')
    return '\n'.join(lines),witnesses
