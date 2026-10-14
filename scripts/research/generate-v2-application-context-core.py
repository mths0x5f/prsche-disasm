"""Emit a complete direct C++ compile candidate; this does not certify behavior."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'iterations/v2/001-original-recovery'
RUN=BASE/'runs/177-application-context-core'
SOURCE=BASE/'source/recovered/Porsche.exe/application_context_core_candidate.cpp'
HEADER=BASE/'source/include/porsche/application_context_core_candidate.hpp'
REGS={'EAX','ECX','EDX','EBX','EBP','ESI','EDI','ESP'}
BYTES={'AL':('EAX',0),'AH':('EAX',8),'BL':('EBX',0),'BH':('EBX',8),
       'CL':('ECX',0),'CH':('ECX',8),'DL':('EDX',0),'DH':('EDX',8)}
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

def main():
    evidence=json.loads((RUN/'stack-evidence.json').read_text())
    pop={int(x['va'],16):x['stack_cleanup_bytes'] for x in evidence['callees']}
    virtual={int(x['call_va'],16):x['assumed_cleanup'] for x in evidence['indirect_calls']}
    instructions=[]
    for line in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines():
        p=line.split(None,3)
        if len(p)<3:continue
        try:a=int(p[0],16);code=bytes.fromhex(p[1])
        except ValueError:continue
        if 0x4d3420<=a<=0x4d55ac:instructions.append((a,code,p[2],p[3] if len(p)>3 else ''))
    assert sum(len(code) for _,code,_,_ in instructions)==8589
    assert instructions[0][0]==0x4d3420 and instructions[-1][0]+len(instructions[-1][1])==0x4d55ad
    assert all(a+len(c)==b for (a,c,_,_),(b,_,_,_) in zip(instructions,instructions[1:]))
    assert hashlib.sha256(b''.join(c for _,c,_,_ in instructions)).hexdigest()==evidence['pins'][0]['sha256']
    globals=set()
    def number(n):
        v=int(n,16)
        if 0x400000<=v<0x700000:
            globals.add(v);return f'address(application_core_address_{v:08x}())'
        return f'0x{v&0xffffffff:08x}u'
    def expression(s):
        s=s.strip().removeprefix('[').removesuffix(']')
        s=re.sub(r'0x[0-9a-fA-F]+',lambda m:number(m[0]),s)
        return '('+s+')'
    def width(s):return 8 if 'byte ptr' in s or s in BYTES else 32
    def value(s,bits=None):
        s=s.strip()
        if s in REGS:return s
        if s in BYTES:
            r,n=BYTES[s];return f'get_byte({r}, {n})'
        if '[' in s:return f'read{bits or width(s)}({expression(s[s.index("["):])})'
        if s.startswith('0x') or s.startswith('-0x'):return number(s)
        raise ValueError(('operand',s))
    def assign(s,v,bits=None):
        if s in REGS:return f'{s} = {v};'
        if s in BYTES:
            r,n=BYTES[s];return f'set_byte({r}, {n}, {v});'
        if '[' in s:return f'write{bits or width(s)}({expression(s[s.index("["):])}, {v});'
        raise ValueError(('destination',s))
    emitted=[];coverage=[]
    saved_push={0x4d3426,0x4d3427,0x4d3428,0x4d3429}
    saved_pop={0x4d5598,0x4d5599,0x4d55a2,0x4d55a3}
    decoder=Cs(CS_ARCH_X86,CS_MODE_32);decoder.detail=True
    for a,code,m,o in instructions:
        decoded=next(decoder.disasm(code,a));bits=decoded.operands[0].size*8 if decoded.operands else 32
        fields=o.split(',',1);d=fields[0].strip() if fields else '';s=fields[1].strip() if len(fields)>1 else ''
        line=f'L_{a:08x}: // {a:08x} {code.hex()} {m} {o}\n'
        if m=='MOV':body=assign(d,value(s,bits),bits)
        elif m=='LEA':body=assign(d,expression(s))
        elif m=='PUSH':body='ESP -= 4u;' + ('' if a in saved_push else f' write32(ESP, {value(d)});')
        elif m=='POP':
            assert a in saved_pop;body='ESP += 4u; // Native C++ ABI preserves the caller nonvolatile registers.'
        elif m in ['ADD','SUB','SBB','XOR','OR']:
            if m in ['XOR','SUB','SBB'] and d==s:left,right='0u','0u'
            elif m=='OR' and s.startswith('0x') and int(s,16)==(1<<bits)-1:left,right='0u',value(s,bits)
            else:left,right=value(d,bits),value(s,bits)
            body=assign(d,f'alu_{m.lower()}({left}, {right}, {bits}, state.flags)',bits)
        elif m=='DEC':body=assign(d,f'alu_dec({value(d)}, {width(d)}, state.flags)')
        elif m=='NOT':body=assign(d,f'(~{value(d)})')
        elif m=='CMP':body=f'(void)alu_sub({value(d,bits)}, {value(s,bits)}, {bits}, state.flags);'
        elif m=='TEST':body=f'(void)alu_test({value(d,bits)}, {value(s,bits)}, {bits}, state.flags);'
        elif m=='SCASB.REPNE':body='scan_zero(EDI, ECX, EAX & 255u, state.flags);'
        elif m=='FLD':body=f'x87_load({expression(o[o.index("["):])});'
        elif m=='FSTP':body=f'x87_store({expression(o[o.index("["):])});'
        elif m=='CALL':
            if o.startswith('0x'):
                target=int(o,16);body=f'state.argument_stack = pointer(ESP); application_core_effect_{target:08x}(state); ESP += {pop[target]}u;'
            else:
                body=f'state.argument_stack = pointer(ESP); application_core_virtual_{a:08x}(state, {value(o)}); ESP += {virtual[a]}u;'
        elif m=='JMP':
            if o.startswith('0x'):body=f'goto L_{int(o,16):08x};'
            else:
                assert a==0x4d4125
                body='switch(EAX) { '+''.join(f'case {i}: goto L_{int(v,16):08x}; ' for i,v in enumerate(evidence['jump_table']['targets']))+'default: __assume(0); }'
        elif m.startswith('J'):
            condition={'JZ':'state.flags.zero','JNZ':'!state.flags.zero','JA':'!state.flags.carry && !state.flags.zero',
                'JBE':'state.flags.carry || state.flags.zero','JL':'state.flags.sign != state.flags.overflow'}[m]
            body=f'if({condition}) goto L_{int(o,16):08x};'
        elif m=='RET':assert o=='0xc';body='return EAX;'
        else:raise ValueError((hex(a),m,o))
        emitted.append(line+'    '+body+'\n')
        coverage.append({'va':f'{a:08x}','bytes':len(code),'original_hex':code.hex(),'mnemonic':m})
    declarations='\n'.join(f'void __cdecl application_core_effect_{a:08x}(ApplicationCoreCallState&); // Original RET cleanup {pop[a]} bytes.' for a in sorted(pop))
    declarations+='\n'+'\n'.join(f'void __cdecl application_core_virtual_{a:08x}(ApplicationCoreCallState&, std::uint32_t target); // Cleanup {virtual[a]}: see unresolved contract evidence.' for a in sorted(virtual))
    declarations+='\n'+'\n'.join(f'void* __cdecl application_core_address_{a:08x}(); // Original address view, unknown extent; no storage defined.' for a in sorted(globals))
    HEADER.write_text('''#pragma once
#include "porsche/application_context.hpp"
namespace porsche {
// Compile candidate only. No behavioral recovery/production binding is claimed.
struct ApplicationCoreFlags { bool carry, zero, sign, overflow, direction; };
struct ApplicationCoreCallState {
    std::uint32_t eax, ecx, edx;
    ApplicationCoreFlags flags;
    // Points to source argument zero (source callee ESP+4), with exact original
    // shadow-frame lifetimes. Effects may mutate registers, flags and memory.
    // Native x87 state is live hardware state across every effect call.
    std::uint8_t* argument_stack;
};
std::uint32_t __fastcall application_context_core_candidate_004d3420(
    ApplicationSetupContext*, void* incoming_edx, const char* name, void* stream, std::uint32_t mode);
// Explicit per-callee machine contracts. Actual callee input/output liveness,
// semantic adapter types and address-view ownership are not yet proven/bound.
'''+declarations+'\n}\n',encoding='utf-8',newline='\n')
    helpers='''#include "porsche/application_context_core_candidate.hpp"
#include <intrin.h>
#pragma warning(disable:4102) // Original-VA labels retained for source coverage.
namespace porsche {
namespace {
using U=std::uint32_t;
U address(const void* p) {return reinterpret_cast<U>(p);}
std::uint8_t* pointer(U p) {return reinterpret_cast<std::uint8_t*>(p);}
U read8(U p) {return *reinterpret_cast<const volatile std::uint8_t*>(p);}
U read32(U p) {return *reinterpret_cast<const volatile U*>(p);}
void write8(U p,U x) {*reinterpret_cast<volatile std::uint8_t*>(p)=static_cast<std::uint8_t>(x);}
void write32(U p,U x) {*reinterpret_cast<volatile U*>(p)=x;}
U get_byte(const U& r,unsigned shift) {return reinterpret_cast<const std::uint8_t*>(&r)[shift/8];}
void set_byte(U& r,unsigned shift,U x) {reinterpret_cast<std::uint8_t*>(&r)[shift/8]=static_cast<std::uint8_t>(x);}
U mask(unsigned bits) {return bits==8?255u:0xffffffffu;}
void result_flags(U r,unsigned bits,ApplicationCoreFlags& f) {f.zero=r==0;f.sign=(r&(1u<<(bits-1)))!=0;}
U alu_add(U a,U b,unsigned bits,ApplicationCoreFlags& f) {
    a&=mask(bits);b&=mask(bits);const auto wide=static_cast<std::uint64_t>(a)+b;
    const U r=static_cast<U>(wide)&mask(bits);f.carry=(wide>>bits)!=0;
    f.overflow=((~(a^b)&(a^r))&(1u<<(bits-1)))!=0;result_flags(r,bits,f);return r;
}
U alu_sub(U a,U b,unsigned bits,ApplicationCoreFlags& f) {
    a&=mask(bits);b&=mask(bits);const U r=(a-b)&mask(bits);f.carry=a<b;
    f.overflow=(((a^b)&(a^r))&(1u<<(bits-1)))!=0;result_flags(r,bits,f);return r;
}
U alu_sbb(U a,U b,unsigned bits,ApplicationCoreFlags& f) {
    a&=mask(bits);b&=mask(bits);const auto wide=static_cast<std::uint64_t>(b)+(f.carry?1u:0u);
    const U r=static_cast<U>(a-wide)&mask(bits);f.carry=static_cast<std::uint64_t>(a)<wide;
    f.overflow=(((a^b)&(a^r))&(1u<<(bits-1)))!=0;result_flags(r,bits,f);return r;
}
U alu_logic(U r,unsigned bits,ApplicationCoreFlags& f) {r&=mask(bits);f.carry=false;f.overflow=false;result_flags(r,bits,f);return r;}
U alu_xor(U a,U b,unsigned bits,ApplicationCoreFlags& f) {return alu_logic(a^b,bits,f);}
U alu_or(U a,U b,unsigned bits,ApplicationCoreFlags& f) {return alu_logic(a|b,bits,f);}
U alu_test(U a,U b,unsigned bits,ApplicationCoreFlags& f) {return alu_logic(a&b,bits,f);}
U alu_dec(U a,unsigned bits,ApplicationCoreFlags& f) {const bool carry=f.carry;const U r=alu_sub(a,1,bits,f);f.carry=carry;return r;}
void scan_zero(U& cursor,U& remaining,U value,ApplicationCoreFlags& flags) {
    while(remaining) {const U byte=read8(cursor);cursor+=flags.direction?0xffffffffu:1u;--remaining;
        (void)alu_sub(value,byte,8,flags);if(flags.zero)break;}
}
void x87_load(U p) {__asm {mov eax,p} __asm {fld dword ptr [eax]}}
void x87_store(U p) {__asm {mov eax,p} __asm {fstp dword ptr [eax]}}
}
std::uint32_t __fastcall application_context_core_candidate_004d3420(
    ApplicationSetupContext* context,void* incoming_edx,const char* name,void* stream,U mode) {
    // The compiler owns native callee-save handling. Source PUSH/POP save slots
    // reserve shadow addresses but their incidental incoming values are not read.
    // Uninitialized source locals stay uninitialized; no invented zero fill.
    alignas(4) std::uint8_t frame[0x200];
    ApplicationCoreCallState state;
    const U entry_flags=__readeflags();
    state.flags={bool(entry_flags&1u),bool(entry_flags&64u),bool(entry_flags&128u),bool(entry_flags&2048u),bool(entry_flags&1024u)};
    state.ecx=address(context);state.edx=address(incoming_edx);
    U& EAX=state.eax;U& ECX=state.ecx;U& EDX=state.edx;
    U EBX,EBP,ESI,EDI,ESP=address(frame+0x180);
    write32(ESP+4,address(name));write32(ESP+8,address(stream));write32(ESP+12,mode);
'''
    SOURCE.write_text(helpers+''.join(emitted)+'}\n}\n',encoding='utf-8',newline='\n')
    report={'schema':1,'kind':'complete-direct-C++-compile-candidate-not-behavioral-proof','function_va':'004d3420',
        'original_sha256':evidence['module_sha256'],'indexed_body_bytes':8589,'emitted_instruction_sites':len(coverage),
        'emitted_original_bytes':sum(x['bytes'] for x in coverage),'instructions':coverage,
        'direct_callee_contracts':len(pop),'virtual_callee_contracts':len(virtual),'unresolved_address_views':[f'{a:08x}' for a in sorted(globals)],
        'unproven':['Per-callee volatile-register/condition-code liveness and semantic adapter signatures',
            'Virtual target ABI except constraints documented in stack-evidence.json','Original global/code-address view ownership and extents',
            'Typed-boundary branch-batched native/original comparisons; no behavioral acceptance claimed',
            'Native x87 states/exceptions, invalid-access domains, callbacks and intermediate-state ordering'],
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE,HEADER,Path(__file__),RUN/'stack-evidence.json']}}
    (RUN/'compile-candidate.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ['emitted_instruction_sites','emitted_original_bytes','direct_callee_contracts','virtual_callee_contracts']}))

if __name__=='__main__':main()
