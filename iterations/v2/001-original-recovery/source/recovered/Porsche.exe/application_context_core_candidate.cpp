#include "porsche/application_context_core_candidate.hpp"
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
L_004d3420: // 004d3420 81ec90000000 SUB ESP,0x90
    ESP = alu_sub(ESP, 0x00000090u, 32, state.flags);
L_004d3426: // 004d3426 53 PUSH EBX
    ESP -= 4u;
L_004d3427: // 004d3427 55 PUSH EBP
    ESP -= 4u;
L_004d3428: // 004d3428 56 PUSH ESI
    ESP -= 4u;
L_004d3429: // 004d3429 57 PUSH EDI
    ESP -= 4u;
L_004d342a: // 004d342a 6a02 PUSH 0x2
    ESP -= 4u; write32(ESP, 0x00000002u);
L_004d342c: // 004d342c 8bf1 MOV ESI,ECX
    ESI = ECX;
L_004d342e: // 004d342e 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d3434: // 004d3434 6a10 PUSH 0x10
    ESP -= 4u; write32(ESP, 0x00000010u);
L_004d3436: // 004d3436 68e0010000 PUSH 0x1e0
    ESP -= 4u; write32(ESP, 0x000001e0u);
L_004d343b: // 004d343b 6880020000 PUSH 0x280
    ESP -= 4u; write32(ESP, 0x00000280u);
L_004d3440: // 004d3440 e87b4bf9ff CALL 0x00467fc0
    state.argument_stack = pointer(ESP); application_core_effect_00467fc0(state); ESP += 16u;
L_004d3445: // 004d3445 a058915d00 MOV AL,[0x005d9158]
    set_byte(EAX, 0, read8((address(application_core_address_005d9158()))));
L_004d344a: // 004d344a 33db XOR EBX,EBX
    EBX = alu_xor(0u, 0u, 32, state.flags);
L_004d344c: // 004d344c 3ac3 CMP AL,BL
    (void)alu_sub(get_byte(EAX, 0), get_byte(EBX, 0), 8, state.flags);
L_004d344e: // 004d344e c644242301 MOV byte ptr [ESP + 0x23],0x1
    write8((ESP + 0x00000023u), 0x00000001u);
L_004d3453: // 004d3453 7406 JZ 0x004d345b
    if(state.flags.zero) goto L_004d345b;
L_004d3455: // 004d3455 885c2423 MOV byte ptr [ESP + 0x23],BL
    write8((ESP + 0x00000023u), get_byte(EBX, 0));
L_004d3459: // 004d3459 eb09 JMP 0x004d3464
    goto L_004d3464;
L_004d345b: // 004d345b 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d345c: // 004d345c e89fa50000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d3461: // 004d3461 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d3464: // 004d3464 8b8424ac000000 MOV EAX,dword ptr [ESP + 0xac]
    EAX = read32((ESP + 0x000000acu));
L_004d346b: // 004d346b 898678010000 MOV dword ptr [ESI + 0x178],EAX
    write32((ESI + 0x00000178u), EAX);
L_004d3471: // 004d3471 e8ead20000 CALL 0x004e0760
    state.argument_stack = pointer(ESP); application_core_effect_004e0760(state); ESP += 0u;
L_004d3476: // 004d3476 e835d30000 CALL 0x004e07b0
    state.argument_stack = pointer(ESP); application_core_effect_004e07b0(state); ESP += 0u;
L_004d347b: // 004d347b 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d347c: // 004d347c 6a0c PUSH 0xc
    ESP -= 4u; write32(ESP, 0x0000000cu);
L_004d347e: // 004d347e e83dbb0c00 CALL 0x0059efc0
    state.argument_stack = pointer(ESP); application_core_effect_0059efc0(state); ESP += 0u;
L_004d3483: // 004d3483 8bf8 MOV EDI,EAX
    EDI = EAX;
L_004d3485: // 004d3485 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d3488: // 004d3488 3bfb CMP EDI,EBX
    (void)alu_sub(EDI, EBX, 32, state.flags);
L_004d348a: // 004d348a 7413 JZ 0x004d349f
    if(state.flags.zero) goto L_004d349f;
L_004d348c: // 004d348c 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d3490: // 004d3490 e87b01f5ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d3495: // 004d3495 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3496: // 004d3496 8bcf MOV ECX,EDI
    ECX = EDI;
L_004d3498: // 004d3498 e873230300 CALL 0x00505810
    state.argument_stack = pointer(ESP); application_core_effect_00505810(state); ESP += 4u;
L_004d349d: // 004d349d eb02 JMP 0x004d34a1
    goto L_004d34a1;
L_004d349f: // 004d349f 33ff XOR EDI,EDI
    EDI = alu_xor(0u, 0u, 32, state.flags);
L_004d34a1: // 004d34a1 89bed8000000 MOV dword ptr [ESI + 0xd8],EDI
    write32((ESI + 0x000000d8u), EDI);
L_004d34a7: // 004d34a7 e864360000 CALL 0x004d6b10
    state.argument_stack = pointer(ESP); application_core_effect_004d6b10(state); ESP += 0u;
L_004d34ac: // 004d34ac 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d34b0: // 004d34b0 740a JZ 0x004d34bc
    if(state.flags.zero) goto L_004d34bc;
L_004d34b2: // 004d34b2 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d34b4: // 004d34b4 e847a50000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d34b9: // 004d34b9 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d34bc: // 004d34bc 8b8678010000 MOV EAX,dword ptr [ESI + 0x178]
    EAX = read32((ESI + 0x00000178u));
L_004d34c2: // 004d34c2 bd01000000 MOV EBP,0x1
    EBP = 0x00000001u;
L_004d34c7: // 004d34c7 3bc5 CMP EAX,EBP
    (void)alu_sub(EAX, EBP, 32, state.flags);
L_004d34c9: // 004d34c9 7431 JZ 0x004d34fc
    if(state.flags.zero) goto L_004d34fc;
L_004d34cb: // 004d34cb 381d58915d00 CMP byte ptr [0x005d9158],BL
    (void)alu_sub(read8((address(application_core_address_005d9158()))), get_byte(EBX, 0), 8, state.flags);
L_004d34d1: // 004d34d1 7529 JNZ 0x004d34fc
    if(!state.flags.zero) goto L_004d34fc;
L_004d34d3: // 004d34d3 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d34d9: // 004d34d9 e872340400 CALL 0x00516950
    state.argument_stack = pointer(ESP); application_core_effect_00516950(state); ESP += 0u;
L_004d34de: // 004d34de 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d34e4: // 004d34e4 8b4974 MOV ECX,dword ptr [ECX + 0x74]
    ECX = read32((ECX + 0x00000074u));
L_004d34e7: // 004d34e7 e8942b0600 CALL 0x00536080
    state.argument_stack = pointer(ESP); application_core_effect_00536080(state); ESP += 0u;
L_004d34ec: // 004d34ec e89f1e0800 CALL 0x00555390
    state.argument_stack = pointer(ESP); application_core_effect_00555390(state); ESP += 0u;
L_004d34f1: // 004d34f1 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d34f7: // 004d34f7 e8444af9ff CALL 0x00467f40
    state.argument_stack = pointer(ESP); application_core_effect_00467f40(state); ESP += 0u;
L_004d34fc: // 004d34fc c6050098610001 MOV byte ptr [0x00619800],0x1
    write8((address(application_core_address_00619800())), 0x00000001u);
L_004d3503: // 004d3503 e808b8f7ff CALL 0x0044ed10
    state.argument_stack = pointer(ESP); application_core_effect_0044ed10(state); ESP += 0u;
L_004d3508: // 004d3508 39ae78010000 CMP dword ptr [ESI + 0x178],EBP
    (void)alu_sub(read32((ESI + 0x00000178u)), EBP, 32, state.flags);
L_004d350e: // 004d350e 7422 JZ 0x004d3532
    if(state.flags.zero) goto L_004d3532;
L_004d3510: // 004d3510 6a08 PUSH 0x8
    ESP -= 4u; write32(ESP, 0x00000008u);
L_004d3512: // 004d3512 e879ba0c00 CALL 0x0059ef90
    state.argument_stack = pointer(ESP); application_core_effect_0059ef90(state); ESP += 0u;
L_004d3517: // 004d3517 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d351a: // 004d351a 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d351c: // 004d351c 740e JZ 0x004d352c
    if(state.flags.zero) goto L_004d352c;
L_004d351e: // 004d351e 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d3520: // 004d3520 e83b84f7ff CALL 0x0044b960
    state.argument_stack = pointer(ESP); application_core_effect_0044b960(state); ESP += 0u;
L_004d3525: // 004d3525 a36c976100 MOV [0x0061976c],EAX
    write32((address(application_core_address_0061976c())), EAX);
L_004d352a: // 004d352a eb06 JMP 0x004d3532
    goto L_004d3532;
L_004d352c: // 004d352c 891d6c976100 MOV dword ptr [0x0061976c],EBX
    write32((address(application_core_address_0061976c())), EBX);
L_004d3532: // 004d3532 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d3536: // 004d3536 740a JZ 0x004d3542
    if(state.flags.zero) goto L_004d3542;
L_004d3538: // 004d3538 6a02 PUSH 0x2
    ESP -= 4u; write32(ESP, 0x00000002u);
L_004d353a: // 004d353a e8c1a40000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d353f: // 004d353f 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d3542: // 004d3542 39ae78010000 CMP dword ptr [ESI + 0x178],EBP
    (void)alu_sub(read32((ESI + 0x00000178u)), EBP, 32, state.flags);
L_004d3548: // 004d3548 740a JZ 0x004d3554
    if(state.flags.zero) goto L_004d3554;
L_004d354a: // 004d354a e8c155f7ff CALL 0x00448b10
    state.argument_stack = pointer(ESP); application_core_effect_00448b10(state); ESP += 0u;
L_004d354f: // 004d354f e80c02f7ff CALL 0x00443760
    state.argument_stack = pointer(ESP); application_core_effect_00443760(state); ESP += 0u;
L_004d3554: // 004d3554 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d3558: // 004d3558 740a JZ 0x004d3564
    if(state.flags.zero) goto L_004d3564;
L_004d355a: // 004d355a 6a03 PUSH 0x3
    ESP -= 4u; write32(ESP, 0x00000003u);
L_004d355c: // 004d355c e89fa40000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d3561: // 004d3561 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d3564: // 004d3564 893528b96500 MOV dword ptr [0x0065b928],ESI
    write32((address(application_core_address_0065b928())), ESI);
L_004d356a: // 004d356a 8b8678010000 MOV EAX,dword ptr [ESI + 0x178]
    EAX = read32((ESI + 0x00000178u));
L_004d3570: // 004d3570 3bc5 CMP EAX,EBP
    (void)alu_sub(EAX, EBP, 32, state.flags);
L_004d3572: // 004d3572 8d86f4000000 LEA EAX,[ESI + 0xf4]
    EAX = (ESI + 0x000000f4u);
L_004d3578: // 004d3578 89442448 MOV dword ptr [ESP + 0x48],EAX
    write32((ESP + 0x00000048u), EAX);
L_004d357c: // 004d357c 7504 JNZ 0x004d3582
    if(!state.flags.zero) goto L_004d3582;
L_004d357e: // 004d357e 8918 MOV dword ptr [EAX],EBX
    write32((EAX), EBX);
L_004d3580: // 004d3580 eb02 JMP 0x004d3584
    goto L_004d3584;
L_004d3582: // 004d3582 8928 MOV dword ptr [EAX],EBP
    write32((EAX), EBP);
L_004d3584: // 004d3584 e827010100 CALL 0x004e36b0
    state.argument_stack = pointer(ESP); application_core_effect_004e36b0(state); ESP += 0u;
L_004d3589: // 004d3589 e862890000 CALL 0x004dbef0
    state.argument_stack = pointer(ESP); application_core_effect_004dbef0(state); ESP += 0u;
L_004d358e: // 004d358e 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d3592: // 004d3592 740a JZ 0x004d359e
    if(state.flags.zero) goto L_004d359e;
L_004d3594: // 004d3594 6a04 PUSH 0x4
    ESP -= 4u; write32(ESP, 0x00000004u);
L_004d3596: // 004d3596 e865a40000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d359b: // 004d359b 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d359e: // 004d359e 6a10 PUSH 0x10
    ESP -= 4u; write32(ESP, 0x00000010u);
L_004d35a0: // 004d35a0 680000f043 PUSH 0x43f00000
    ESP -= 4u; write32(ESP, 0x43f00000u);
L_004d35a5: // 004d35a5 6800002044 PUSH 0x44200000
    ESP -= 4u; write32(ESP, 0x44200000u);
L_004d35aa: // 004d35aa 680000f043 PUSH 0x43f00000
    ESP -= 4u; write32(ESP, 0x43f00000u);
L_004d35af: // 004d35af 6800002044 PUSH 0x44200000
    ESP -= 4u; write32(ESP, 0x44200000u);
L_004d35b4: // 004d35b4 e8a7ff0000 CALL 0x004e3560
    state.argument_stack = pointer(ESP); application_core_effect_004e3560(state); ESP += 0u;
L_004d35b9: // 004d35b9 8b1534b36500 MOV EDX,dword ptr [0x0065b334]
    EDX = read32((address(application_core_address_0065b334())));
L_004d35bf: // 004d35bf 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d35c2: // 004d35c2 8bfa MOV EDI,EDX
    EDI = EDX;
L_004d35c4: // 004d35c4 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d35c6: // 004d35c6 83c414 ADD ESP,0x14
    ESP = alu_add(ESP, 0x00000014u, 32, state.flags);
L_004d35c9: // 004d35c9 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d35cd: // 004d35cd 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d35d1: // 004d35d1 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d35d5: // 004d35d5 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d35d7: // 004d35d7 f7d1 NOT ECX
    ECX = (~ECX);
L_004d35d9: // 004d35d9 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d35da: // 004d35da 03ca ADD ECX,EDX
    ECX = alu_add(ECX, EDX, 32, state.flags);
L_004d35dc: // 004d35dc 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d35dd: // 004d35dd 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d35de: // 004d35de 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d35e2: // 004d35e2 e8b962f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d35e7: // 004d35e7 8b1530b36500 MOV EDX,dword ptr [0x0065b330]
    EDX = read32((address(application_core_address_0065b330())));
L_004d35ed: // 004d35ed 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d35f0: // 004d35f0 8bfa MOV EDI,EDX
    EDI = EDX;
L_004d35f2: // 004d35f2 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d35f4: // 004d35f4 895c2428 MOV dword ptr [ESP + 0x28],EBX
    write32((ESP + 0x00000028u), EBX);
L_004d35f8: // 004d35f8 895c242c MOV dword ptr [ESP + 0x2c],EBX
    write32((ESP + 0x0000002cu), EBX);
L_004d35fc: // 004d35fc 895c2430 MOV dword ptr [ESP + 0x30],EBX
    write32((ESP + 0x00000030u), EBX);
L_004d3600: // 004d3600 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3602: // 004d3602 f7d1 NOT ECX
    ECX = (~ECX);
L_004d3604: // 004d3604 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3605: // 004d3605 03ca ADD ECX,EDX
    ECX = alu_add(ECX, EDX, 32, state.flags);
L_004d3607: // 004d3607 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3608: // 004d3608 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3609: // 004d3609 8d4c2430 LEA ECX,[ESP + 0x30]
    ECX = (ESP + 0x00000030u);
L_004d360d: // 004d360d e88e62f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3612: // 004d3612 8d542414 LEA EDX,[ESP + 0x14]
    EDX = (ESP + 0x00000014u);
L_004d3616: // 004d3616 8d442428 LEA EAX,[ESP + 0x28]
    EAX = (ESP + 0x00000028u);
L_004d361a: // 004d361a 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d361b: // 004d361b 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d361c: // 004d361c e86f6a0500 CALL 0x0052a090
    state.argument_stack = pointer(ESP); application_core_effect_0052a090(state); ESP += 0u;
L_004d3621: // 004d3621 8b442438 MOV EAX,dword ptr [ESP + 0x38]
    EAX = read32((ESP + 0x00000038u));
L_004d3625: // 004d3625 8b4c2430 MOV ECX,dword ptr [ESP + 0x30]
    ECX = read32((ESP + 0x00000030u));
L_004d3629: // 004d3629 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d362c: // 004d362c 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d362e: // 004d362e 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3630: // 004d3630 740f JZ 0x004d3641
    if(state.flags.zero) goto L_004d3641;
L_004d3632: // 004d3632 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3634: // 004d3634 740b JZ 0x004d3641
    if(state.flags.zero) goto L_004d3641;
L_004d3636: // 004d3636 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3637: // 004d3637 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3638: // 004d3638 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3639: // 004d3639 e89201f5ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d363e: // 004d363e 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d3641: // 004d3641 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d3645: // 004d3645 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d3649: // 004d3649 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d364b: // 004d364b 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d364d: // 004d364d 740f JZ 0x004d365e
    if(state.flags.zero) goto L_004d365e;
L_004d364f: // 004d364f 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3651: // 004d3651 740b JZ 0x004d365e
    if(state.flags.zero) goto L_004d365e;
L_004d3653: // 004d3653 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3654: // 004d3654 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3655: // 004d3655 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3656: // 004d3656 e87501f5ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d365b: // 004d365b 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d365e: // 004d365e 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d3662: // 004d3662 740a JZ 0x004d366e
    if(state.flags.zero) goto L_004d366e;
L_004d3664: // 004d3664 6a05 PUSH 0x5
    ESP -= 4u; write32(ESP, 0x00000005u);
L_004d3666: // 004d3666 e895a30000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d366b: // 004d366b 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d366e: // 004d366e e87dce0000 CALL 0x004e04f0
    state.argument_stack = pointer(ESP); application_core_effect_004e04f0(state); ESP += 0u;
L_004d3673: // 004d3673 e878ac0000 CALL 0x004de2f0
    state.argument_stack = pointer(ESP); application_core_effect_004de2f0(state); ESP += 0u;
L_004d3678: // 004d3678 e853440400 CALL 0x00517ad0
    state.argument_stack = pointer(ESP); application_core_effect_00517ad0(state); ESP += 0u;
L_004d367d: // 004d367d e8feab0100 CALL 0x004ee280
    state.argument_stack = pointer(ESP); application_core_effect_004ee280(state); ESP += 0u;
L_004d3682: // 004d3682 e889570000 CALL 0x004d8e10
    state.argument_stack = pointer(ESP); application_core_effect_004d8e10(state); ESP += 0u;
L_004d3687: // 004d3687 e8543affff CALL 0x004c70e0
    state.argument_stack = pointer(ESP); application_core_effect_004c70e0(state); ESP += 0u;
L_004d368c: // 004d368c e8ef910300 CALL 0x0050c880
    state.argument_stack = pointer(ESP); application_core_effect_0050c880(state); ESP += 0u;
L_004d3691: // 004d3691 e83ab50400 CALL 0x0051ebd0
    state.argument_stack = pointer(ESP); application_core_effect_0051ebd0(state); ESP += 0u;
L_004d3696: // 004d3696 e87541feff CALL 0x004b7810
    state.argument_stack = pointer(ESP); application_core_effect_004b7810(state); ESP += 0u;
L_004d369b: // 004d369b e810eb0300 CALL 0x005121b0
    state.argument_stack = pointer(ESP); application_core_effect_005121b0(state); ESP += 0u;
L_004d36a0: // 004d36a0 e88b3d0100 CALL 0x004e7430
    state.argument_stack = pointer(ESP); application_core_effect_004e7430(state); ESP += 0u;
L_004d36a5: // 004d36a5 e8a6320400 CALL 0x00516950
    state.argument_stack = pointer(ESP); application_core_effect_00516950(state); ESP += 0u;
L_004d36aa: // 004d36aa e881d70000 CALL 0x004e0e30
    state.argument_stack = pointer(ESP); application_core_effect_004e0e30(state); ESP += 0u;
L_004d36af: // 004d36af e88c030200 CALL 0x004f3a40
    state.argument_stack = pointer(ESP); application_core_effect_004f3a40(state); ESP += 0u;
L_004d36b4: // 004d36b4 e837f90200 CALL 0x00502ff0
    state.argument_stack = pointer(ESP); application_core_effect_00502ff0(state); ESP += 0u;
L_004d36b9: // 004d36b9 e892800200 CALL 0x004fb750
    state.argument_stack = pointer(ESP); application_core_effect_004fb750(state); ESP += 0u;
L_004d36be: // 004d36be e85d770200 CALL 0x004fae20
    state.argument_stack = pointer(ESP); application_core_effect_004fae20(state); ESP += 0u;
L_004d36c3: // 004d36c3 e888320400 CALL 0x00516950
    state.argument_stack = pointer(ESP); application_core_effect_00516950(state); ESP += 0u;
L_004d36c8: // 004d36c8 e8d3740400 CALL 0x0051aba0
    state.argument_stack = pointer(ESP); application_core_effect_0051aba0(state); ESP += 0u;
L_004d36cd: // 004d36cd e86edc0200 CALL 0x00501340
    state.argument_stack = pointer(ESP); application_core_effect_00501340(state); ESP += 0u;
L_004d36d2: // 004d36d2 e8f9acfeff CALL 0x004be3d0
    state.argument_stack = pointer(ESP); application_core_effect_004be3d0(state); ESP += 0u;
L_004d36d7: // 004d36d7 e824260100 CALL 0x004e5d00
    state.argument_stack = pointer(ESP); application_core_effect_004e5d00(state); ESP += 0u;
L_004d36dc: // 004d36dc e8ef430200 CALL 0x004f7ad0
    state.argument_stack = pointer(ESP); application_core_effect_004f7ad0(state); ESP += 0u;
L_004d36e1: // 004d36e1 e8ea620300 CALL 0x005099d0
    state.argument_stack = pointer(ESP); application_core_effect_005099d0(state); ESP += 0u;
L_004d36e6: // 004d36e6 e845f80000 CALL 0x004e2f30
    state.argument_stack = pointer(ESP); application_core_effect_004e2f30(state); ESP += 0u;
L_004d36eb: // 004d36eb e8a0a70000 CALL 0x004dde90
    state.argument_stack = pointer(ESP); application_core_effect_004dde90(state); ESP += 0u;
L_004d36f0: // 004d36f0 e89b5d0300 CALL 0x00509490
    state.argument_stack = pointer(ESP); application_core_effect_00509490(state); ESP += 0u;
L_004d36f5: // 004d36f5 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d36f9: // 004d36f9 740a JZ 0x004d3705
    if(state.flags.zero) goto L_004d3705;
L_004d36fb: // 004d36fb 6a06 PUSH 0x6
    ESP -= 4u; write32(ESP, 0x00000006u);
L_004d36fd: // 004d36fd e8fea20000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d3702: // 004d3702 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d3705: // 004d3705 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d370b: // 004d370b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d370c: // 004d370c d94108 FLD float ptr [ECX + 0x8]
    x87_load((ECX + 0x00000008u));
L_004d370f: // 004d370f d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d3712: // 004d3712 d94104 FLD float ptr [ECX + 0x4]
    x87_load((ECX + 0x00000004u));
L_004d3715: // 004d3715 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3716: // 004d3716 d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d3719: // 004d3719 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d371a: // 004d371a 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d371f: // 004d371f 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d3724: // 004d3724 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3725: // 004d3725 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3726: // 004d3726 6a06 PUSH 0x6
    ESP -= 4u; write32(ESP, 0x00000006u);
L_004d3728: // 004d3728 e8c33bf9ff CALL 0x004672f0
    state.argument_stack = pointer(ESP); application_core_effect_004672f0(state); ESP += 32u;
L_004d372d: // 004d372d 8986fc000000 MOV dword ptr [ESI + 0xfc],EAX
    write32((ESI + 0x000000fcu), EAX);
L_004d3733: // 004d3733 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d3739: // 004d3739 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d373a: // 004d373a d94108 FLD float ptr [ECX + 0x8]
    x87_load((ECX + 0x00000008u));
L_004d373d: // 004d373d d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d3740: // 004d3740 d94104 FLD float ptr [ECX + 0x4]
    x87_load((ECX + 0x00000004u));
L_004d3743: // 004d3743 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3744: // 004d3744 d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d3747: // 004d3747 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3748: // 004d3748 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d374d: // 004d374d 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d3752: // 004d3752 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3753: // 004d3753 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3754: // 004d3754 6a05 PUSH 0x5
    ESP -= 4u; write32(ESP, 0x00000005u);
L_004d3756: // 004d3756 e8953bf9ff CALL 0x004672f0
    state.argument_stack = pointer(ESP); application_core_effect_004672f0(state); ESP += 32u;
L_004d375b: // 004d375b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d375c: // 004d375c 8986f8000000 MOV dword ptr [ESI + 0xf8],EAX
    write32((ESI + 0x000000f8u), EAX);
L_004d3762: // 004d3762 8bc4 MOV EAX,ESP
    EAX = ESP;
L_004d3764: // 004d3764 c700000000ff MOV dword ptr [EAX],0xff000000
    write32((EAX), 0xff000000u);
L_004d376a: // 004d376a 8b8ef8000000 MOV ECX,dword ptr [ESI + 0xf8]
    ECX = read32((ESI + 0x000000f8u));
L_004d3770: // 004d3770 e81b550600 CALL 0x00538c90
    state.argument_stack = pointer(ESP); application_core_effect_00538c90(state); ESP += 0u;
L_004d3775: // 004d3775 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d3777: // 004d3777 81c1b8000000 ADD ECX,0xb8
    ECX = alu_add(ECX, 0x000000b8u, 32, state.flags);
L_004d377d: // 004d377d e8fe36f9ff CALL 0x00466e80
    state.argument_stack = pointer(ESP); application_core_effect_00466e80(state); ESP += 4u;
L_004d3782: // 004d3782 8b8ef8000000 MOV ECX,dword ptr [ESI + 0xf8]
    ECX = read32((ESI + 0x000000f8u));
L_004d3788: // 004d3788 6800ff7f3f PUSH 0x3f7fff00
    ESP -= 4u; write32(ESP, 0x3f7fff00u);
L_004d378d: // 004d378d 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d378e: // 004d378e 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d378f: // 004d378f 8b490c MOV ECX,dword ptr [ECX + 0xc]
    ECX = read32((ECX + 0x0000000cu));
L_004d3792: // 004d3792 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3793: // 004d3793 680000f043 PUSH 0x43f00000
    ESP -= 4u; write32(ESP, 0x43f00000u);
L_004d3798: // 004d3798 6800002044 PUSH 0x44200000
    ESP -= 4u; write32(ESP, 0x44200000u);
L_004d379d: // 004d379d e8fe550600 CALL 0x00538da0
    state.argument_stack = pointer(ESP); application_core_effect_00538da0(state); ESP += 24u;
L_004d37a2: // 004d37a2 8b96f8000000 MOV EDX,dword ptr [ESI + 0xf8]
    EDX = read32((ESI + 0x000000f8u));
L_004d37a8: // 004d37a8 6800ff7f3f PUSH 0x3f7fff00
    ESP -= 4u; write32(ESP, 0x3f7fff00u);
L_004d37ad: // 004d37ad 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d37ae: // 004d37ae 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d37b3: // 004d37b3 8b4a0c MOV ECX,dword ptr [EDX + 0xc]
    ECX = read32((EDX + 0x0000000cu));
L_004d37b6: // 004d37b6 e8155b0600 CALL 0x005392d0
    state.argument_stack = pointer(ESP); application_core_effect_005392d0(state); ESP += 12u;
L_004d37bb: // 004d37bb 8b86f8000000 MOV EAX,dword ptr [ESI + 0xf8]
    EAX = read32((ESI + 0x000000f8u));
L_004d37c1: // 004d37c1 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d37c2: // 004d37c2 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d37c7: // 004d37c7 68000080bf PUSH 0xbf800000
    ESP -= 4u; write32(ESP, 0xbf800000u);
L_004d37cc: // 004d37cc 8b480c MOV ECX,dword ptr [EAX + 0xc]
    ECX = read32((EAX + 0x0000000cu));
L_004d37cf: // 004d37cf e86c670600 CALL 0x00539f40
    state.argument_stack = pointer(ESP); application_core_effect_00539f40(state); ESP += 0u;
L_004d37d4: // 004d37d4 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d37d6: // 004d37d6 e8a5630600 CALL 0x00539b80
    state.argument_stack = pointer(ESP); application_core_effect_00539b80(state); ESP += 12u;
L_004d37db: // 004d37db 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d37e0: // 004d37e0 68000080bf PUSH 0xbf800000
    ESP -= 4u; write32(ESP, 0xbf800000u);
L_004d37e5: // 004d37e5 68898888bb PUSH 0xbb888889
    ESP -= 4u; write32(ESP, 0xbb888889u);
L_004d37ea: // 004d37ea 68cdcc4c3b PUSH 0x3b4ccccd
    ESP -= 4u; write32(ESP, 0x3b4ccccdu);
L_004d37ef: // 004d37ef 8d4c2460 LEA ECX,[ESP + 0x60]
    ECX = (ESP + 0x00000060u);
L_004d37f3: // 004d37f3 e838630600 CALL 0x00539b30
    state.argument_stack = pointer(ESP); application_core_effect_00539b30(state); ESP += 16u;
L_004d37f8: // 004d37f8 8b8ef8000000 MOV ECX,dword ptr [ESI + 0xf8]
    ECX = read32((ESI + 0x000000f8u));
L_004d37fe: // 004d37fe 8d542450 LEA EDX,[ESP + 0x50]
    EDX = (ESP + 0x00000050u);
L_004d3802: // 004d3802 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3803: // 004d3803 8b490c MOV ECX,dword ptr [ECX + 0xc]
    ECX = read32((ECX + 0x0000000cu));
L_004d3806: // 004d3806 e835670600 CALL 0x00539f40
    state.argument_stack = pointer(ESP); application_core_effect_00539f40(state); ESP += 0u;
L_004d380b: // 004d380b 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d380d: // 004d380d e8ee620600 CALL 0x00539b00
    state.argument_stack = pointer(ESP); application_core_effect_00539b00(state); ESP += 4u;
L_004d3812: // 004d3812 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d3818: // 004d3818 d94108 FLD float ptr [ECX + 0x8]
    x87_load((ECX + 0x00000008u));
L_004d381b: // 004d381b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d381c: // 004d381c d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d381f: // 004d381f d94104 FLD float ptr [ECX + 0x4]
    x87_load((ECX + 0x00000004u));
L_004d3822: // 004d3822 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3823: // 004d3823 d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d3826: // 004d3826 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3827: // 004d3827 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d382c: // 004d382c 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d3831: // 004d3831 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3832: // 004d3832 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3833: // 004d3833 6a06 PUSH 0x6
    ESP -= 4u; write32(ESP, 0x00000006u);
L_004d3835: // 004d3835 e8b63af9ff CALL 0x004672f0
    state.argument_stack = pointer(ESP); application_core_effect_004672f0(state); ESP += 32u;
L_004d383a: // 004d383a 898604010000 MOV dword ptr [ESI + 0x104],EAX
    write32((ESI + 0x00000104u), EAX);
L_004d3840: // 004d3840 8b0d30816200 MOV ECX,dword ptr [0x00628130]
    ECX = read32((address(application_core_address_00628130())));
L_004d3846: // 004d3846 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3847: // 004d3847 d94108 FLD float ptr [ECX + 0x8]
    x87_load((ECX + 0x00000008u));
L_004d384a: // 004d384a d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d384d: // 004d384d d94104 FLD float ptr [ECX + 0x4]
    x87_load((ECX + 0x00000004u));
L_004d3850: // 004d3850 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3851: // 004d3851 d91c24 FSTP float ptr [ESP]
    x87_store((ESP));
L_004d3854: // 004d3854 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3855: // 004d3855 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d385a: // 004d385a 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d385f: // 004d385f 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3860: // 004d3860 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3861: // 004d3861 6a05 PUSH 0x5
    ESP -= 4u; write32(ESP, 0x00000005u);
L_004d3863: // 004d3863 e8883af9ff CALL 0x004672f0
    state.argument_stack = pointer(ESP); application_core_effect_004672f0(state); ESP += 32u;
L_004d3868: // 004d3868 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3869: // 004d3869 898600010000 MOV dword ptr [ESI + 0x100],EAX
    write32((ESI + 0x00000100u), EAX);
L_004d386f: // 004d386f 8bc4 MOV EAX,ESP
    EAX = ESP;
L_004d3871: // 004d3871 c700000000ff MOV dword ptr [EAX],0xff000000
    write32((EAX), 0xff000000u);
L_004d3877: // 004d3877 8b8e00010000 MOV ECX,dword ptr [ESI + 0x100]
    ECX = read32((ESI + 0x00000100u));
L_004d387d: // 004d387d e80e540600 CALL 0x00538c90
    state.argument_stack = pointer(ESP); application_core_effect_00538c90(state); ESP += 0u;
L_004d3882: // 004d3882 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d3884: // 004d3884 81c1b8000000 ADD ECX,0xb8
    ECX = alu_add(ECX, 0x000000b8u, 32, state.flags);
L_004d388a: // 004d388a e8f135f9ff CALL 0x00466e80
    state.argument_stack = pointer(ESP); application_core_effect_00466e80(state); ESP += 4u;
L_004d388f: // 004d388f 8b8600010000 MOV EAX,dword ptr [ESI + 0x100]
    EAX = read32((ESI + 0x00000100u));
L_004d3895: // 004d3895 6800ff7f3f PUSH 0x3f7fff00
    ESP -= 4u; write32(ESP, 0x3f7fff00u);
L_004d389a: // 004d389a 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d389b: // 004d389b 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d389c: // 004d389c 8b480c MOV ECX,dword ptr [EAX + 0xc]
    ECX = read32((EAX + 0x0000000cu));
L_004d389f: // 004d389f 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d38a0: // 004d38a0 680000f043 PUSH 0x43f00000
    ESP -= 4u; write32(ESP, 0x43f00000u);
L_004d38a5: // 004d38a5 6800002044 PUSH 0x44200000
    ESP -= 4u; write32(ESP, 0x44200000u);
L_004d38aa: // 004d38aa e8f1540600 CALL 0x00538da0
    state.argument_stack = pointer(ESP); application_core_effect_00538da0(state); ESP += 24u;
L_004d38af: // 004d38af 8b8e00010000 MOV ECX,dword ptr [ESI + 0x100]
    ECX = read32((ESI + 0x00000100u));
L_004d38b5: // 004d38b5 6800ff7f3f PUSH 0x3f7fff00
    ESP -= 4u; write32(ESP, 0x3f7fff00u);
L_004d38ba: // 004d38ba 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d38bb: // 004d38bb 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d38c0: // 004d38c0 8b490c MOV ECX,dword ptr [ECX + 0xc]
    ECX = read32((ECX + 0x0000000cu));
L_004d38c3: // 004d38c3 e8085a0600 CALL 0x005392d0
    state.argument_stack = pointer(ESP); application_core_effect_005392d0(state); ESP += 12u;
L_004d38c8: // 004d38c8 8b9600010000 MOV EDX,dword ptr [ESI + 0x100]
    EDX = read32((ESI + 0x00000100u));
L_004d38ce: // 004d38ce 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d38cf: // 004d38cf 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d38d4: // 004d38d4 68000080bf PUSH 0xbf800000
    ESP -= 4u; write32(ESP, 0xbf800000u);
L_004d38d9: // 004d38d9 8b4a0c MOV ECX,dword ptr [EDX + 0xc]
    ECX = read32((EDX + 0x0000000cu));
L_004d38dc: // 004d38dc e85f660600 CALL 0x00539f40
    state.argument_stack = pointer(ESP); application_core_effect_00539f40(state); ESP += 0u;
L_004d38e1: // 004d38e1 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d38e3: // 004d38e3 e898620600 CALL 0x00539b80
    state.argument_stack = pointer(ESP); application_core_effect_00539b80(state); ESP += 12u;
L_004d38e8: // 004d38e8 680000803f PUSH 0x3f800000
    ESP -= 4u; write32(ESP, 0x3f800000u);
L_004d38ed: // 004d38ed 68000080bf PUSH 0xbf800000
    ESP -= 4u; write32(ESP, 0xbf800000u);
L_004d38f2: // 004d38f2 68898888bb PUSH 0xbb888889
    ESP -= 4u; write32(ESP, 0xbb888889u);
L_004d38f7: // 004d38f7 68cdcc4c3b PUSH 0x3b4ccccd
    ESP -= 4u; write32(ESP, 0x3b4ccccdu);
L_004d38fc: // 004d38fc 8d4c2460 LEA ECX,[ESP + 0x60]
    ECX = (ESP + 0x00000060u);
L_004d3900: // 004d3900 e82b620600 CALL 0x00539b30
    state.argument_stack = pointer(ESP); application_core_effect_00539b30(state); ESP += 16u;
L_004d3905: // 004d3905 8b8600010000 MOV EAX,dword ptr [ESI + 0x100]
    EAX = read32((ESI + 0x00000100u));
L_004d390b: // 004d390b 8d542450 LEA EDX,[ESP + 0x50]
    EDX = (ESP + 0x00000050u);
L_004d390f: // 004d390f 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3910: // 004d3910 8b480c MOV ECX,dword ptr [EAX + 0xc]
    ECX = read32((EAX + 0x0000000cu));
L_004d3913: // 004d3913 e828660600 CALL 0x00539f40
    state.argument_stack = pointer(ESP); application_core_effect_00539f40(state); ESP += 0u;
L_004d3918: // 004d3918 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d391a: // 004d391a e8e1610600 CALL 0x00539b00
    state.argument_stack = pointer(ESP); application_core_effect_00539b00(state); ESP += 4u;
L_004d391f: // 004d391f 8b8efc000000 MOV ECX,dword ptr [ESI + 0xfc]
    ECX = read32((ESI + 0x000000fcu));
L_004d3925: // 004d3925 b800003442 MOV EAX,0x42340000
    EAX = 0x42340000u;
L_004d392a: // 004d392a 898130010000 MOV dword ptr [ECX + 0x130],EAX
    write32((ECX + 0x00000130u), EAX);
L_004d3930: // 004d3930 8b9604010000 MOV EDX,dword ptr [ESI + 0x104]
    EDX = read32((ESI + 0x00000104u));
L_004d3936: // 004d3936 898230010000 MOV dword ptr [EDX + 0x130],EAX
    write32((EDX + 0x00000130u), EAX);
L_004d393c: // 004d393c 8b86fc000000 MOV EAX,dword ptr [ESI + 0xfc]
    EAX = read32((ESI + 0x000000fcu));
L_004d3942: // 004d3942 05b8000000 ADD EAX,0xb8
    EAX = alu_add(EAX, 0x000000b8u, 32, state.flags);
L_004d3947: // 004d3947 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3948: // 004d3948 e8f3600800 CALL 0x00559a40
    state.argument_stack = pointer(ESP); application_core_effect_00559a40(state); ESP += 0u;
L_004d394d: // 004d394d 8b8efc000000 MOV ECX,dword ptr [ESI + 0xfc]
    ECX = read32((ESI + 0x000000fcu));
L_004d3953: // 004d3953 81c1dc000000 ADD ECX,0xdc
    ECX = alu_add(ECX, 0x000000dcu, 32, state.flags);
L_004d3959: // 004d3959 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d395a: // 004d395a e8b1600800 CALL 0x00559a10
    state.argument_stack = pointer(ESP); application_core_effect_00559a10(state); ESP += 0u;
L_004d395f: // 004d395f 8b9604010000 MOV EDX,dword ptr [ESI + 0x104]
    EDX = read32((ESI + 0x00000104u));
L_004d3965: // 004d3965 81c2b8000000 ADD EDX,0xb8
    EDX = alu_add(EDX, 0x000000b8u, 32, state.flags);
L_004d396b: // 004d396b 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d396c: // 004d396c e8cf600800 CALL 0x00559a40
    state.argument_stack = pointer(ESP); application_core_effect_00559a40(state); ESP += 0u;
L_004d3971: // 004d3971 8b8604010000 MOV EAX,dword ptr [ESI + 0x104]
    EAX = read32((ESI + 0x00000104u));
L_004d3977: // 004d3977 05dc000000 ADD EAX,0xdc
    EAX = alu_add(EAX, 0x000000dcu, 32, state.flags);
L_004d397c: // 004d397c 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d397d: // 004d397d e88e600800 CALL 0x00559a10
    state.argument_stack = pointer(ESP); application_core_effect_00559a10(state); ESP += 0u;
L_004d3982: // 004d3982 8a442433 MOV AL,byte ptr [ESP + 0x33]
    set_byte(EAX, 0, read8((ESP + 0x00000033u)));
L_004d3986: // 004d3986 83c410 ADD ESP,0x10
    ESP = alu_add(ESP, 0x00000010u, 32, state.flags);
L_004d3989: // 004d3989 3ac3 CMP AL,BL
    (void)alu_sub(get_byte(EAX, 0), get_byte(EBX, 0), 8, state.flags);
L_004d398b: // 004d398b 740a JZ 0x004d3997
    if(state.flags.zero) goto L_004d3997;
L_004d398d: // 004d398d 6a07 PUSH 0x7
    ESP -= 4u; write32(ESP, 0x00000007u);
L_004d398f: // 004d398f e86ca00000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d3994: // 004d3994 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d3997: // 004d3997 e834530500 CALL 0x00528cd0
    state.argument_stack = pointer(ESP); application_core_effect_00528cd0(state); ESP += 0u;
L_004d399c: // 004d399c 392d10b96500 CMP dword ptr [0x0065b910],EBP
    (void)alu_sub(read32((address(application_core_address_0065b910()))), EBP, 32, state.flags);
L_004d39a2: // 004d39a2 7507 JNZ 0x004d39ab
    if(!state.flags.zero) goto L_004d39ab;
L_004d39a4: // 004d39a4 8bce MOV ECX,ESI
    ECX = ESI;
L_004d39a6: // 004d39a6 e805f3ffff CALL 0x004d2cb0
    state.argument_stack = pointer(ESP); application_core_effect_004d2cb0(state); ESP += 0u;
L_004d39ab: // 004d39ab e800ce0000 CALL 0x004e07b0
    state.argument_stack = pointer(ESP); application_core_effect_004e07b0(state); ESP += 0u;
L_004d39b0: // 004d39b0 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d39b1: // 004d39b1 6894020000 PUSH 0x294
    ESP -= 4u; write32(ESP, 0x00000294u);
L_004d39b6: // 004d39b6 e805b60c00 CALL 0x0059efc0
    state.argument_stack = pointer(ESP); application_core_effect_0059efc0(state); ESP += 0u;
L_004d39bb: // 004d39bb 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d39be: // 004d39be 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d39c0: // 004d39c0 7409 JZ 0x004d39cb
    if(state.flags.zero) goto L_004d39cb;
L_004d39c2: // 004d39c2 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d39c4: // 004d39c4 e8a7440000 CALL 0x004d7e70
    state.argument_stack = pointer(ESP); application_core_effect_004d7e70(state); ESP += 0u;
L_004d39c9: // 004d39c9 eb02 JMP 0x004d39cd
    goto L_004d39cd;
L_004d39cb: // 004d39cb 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d39cd: // 004d39cd 8986dc000000 MOV dword ptr [ESI + 0xdc],EAX
    write32((ESI + 0x000000dcu), EAX);
L_004d39d3: // 004d39d3 bf54945d00 MOV EDI,0x5d9454
    EDI = address(application_core_address_005d9454());
L_004d39d8: // 004d39d8 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d39db: // 004d39db 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d39dd: // 004d39dd f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d39df: // 004d39df f7d1 NOT ECX
    ECX = (~ECX);
L_004d39e1: // 004d39e1 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d39e2: // 004d39e2 895c2428 MOV dword ptr [ESP + 0x28],EBX
    write32((ESP + 0x00000028u), EBX);
L_004d39e6: // 004d39e6 81c154945d00 ADD ECX,0x5d9454
    ECX = alu_add(ECX, address(application_core_address_005d9454()), 32, state.flags);
L_004d39ec: // 004d39ec 895c242c MOV dword ptr [ESP + 0x2c],EBX
    write32((ESP + 0x0000002cu), EBX);
L_004d39f0: // 004d39f0 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d39f1: // 004d39f1 6854945d00 PUSH 0x5d9454
    ESP -= 4u; write32(ESP, address(application_core_address_005d9454()));
L_004d39f6: // 004d39f6 8d4c2430 LEA ECX,[ESP + 0x30]
    ECX = (ESP + 0x00000030u);
L_004d39fa: // 004d39fa 895c2438 MOV dword ptr [ESP + 0x38],EBX
    write32((ESP + 0x00000038u), EBX);
L_004d39fe: // 004d39fe e89d5ef5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3a03: // 004d3a03 8b2d44b36500 MOV EBP,dword ptr [0x0065b344]
    EBP = read32((address(application_core_address_0065b344())));
L_004d3a09: // 004d3a09 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3a0c: // 004d3a0c 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d3a0e: // 004d3a0e 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3a10: // 004d3a10 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3a12: // 004d3a12 8b54242c MOV EDX,dword ptr [ESP + 0x2c]
    EDX = read32((ESP + 0x0000002cu));
L_004d3a16: // 004d3a16 8b442428 MOV EAX,dword ptr [ESP + 0x28]
    EAX = read32((ESP + 0x00000028u));
L_004d3a1a: // 004d3a1a f7d1 NOT ECX
    ECX = (~ECX);
L_004d3a1c: // 004d3a1c 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3a1d: // 004d3a1d 2bd0 SUB EDX,EAX
    EDX = alu_sub(EDX, EAX, 32, state.flags);
L_004d3a1f: // 004d3a1f 8b442440 MOV EAX,dword ptr [ESP + 0x40]
    EAX = read32((ESP + 0x00000040u));
L_004d3a23: // 004d3a23 8bf9 MOV EDI,ECX
    EDI = ECX;
L_004d3a25: // 004d3a25 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d3a29: // 004d3a29 03d7 ADD EDX,EDI
    EDX = alu_add(EDX, EDI, 32, state.flags);
L_004d3a2b: // 004d3a2b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3a2c: // 004d3a2c 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3a2d: // 004d3a2d 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3a2e: // 004d3a2e 8d4c2420 LEA ECX,[ESP + 0x20]
    ECX = (ESP + 0x00000020u);
L_004d3a32: // 004d3a32 e8992d0000 CALL 0x004d67d0
    state.argument_stack = pointer(ESP); application_core_effect_004d67d0(state); ESP += 12u;
L_004d3a37: // 004d3a37 03fd ADD EDI,EBP
    EDI = alu_add(EDI, EBP, 32, state.flags);
L_004d3a39: // 004d3a39 8d4c2414 LEA ECX,[ESP + 0x14]
    ECX = (ESP + 0x00000014u);
L_004d3a3d: // 004d3a3d 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d3a3e: // 004d3a3e 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d3a3f: // 004d3a3f e81ceef9ff CALL 0x00472860
    state.argument_stack = pointer(ESP); application_core_effect_00472860(state); ESP += 8u;
L_004d3a44: // 004d3a44 8d4c2428 LEA ECX,[ESP + 0x28]
    ECX = (ESP + 0x00000028u);
L_004d3a48: // 004d3a48 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3a49: // 004d3a49 8d4c2418 LEA ECX,[ESP + 0x18]
    ECX = (ESP + 0x00000018u);
L_004d3a4d: // 004d3a4d e82e2e0000 CALL 0x004d6880
    state.argument_stack = pointer(ESP); application_core_effect_004d6880(state); ESP += 4u;
L_004d3a52: // 004d3a52 8d542414 LEA EDX,[ESP + 0x14]
    EDX = (ESP + 0x00000014u);
L_004d3a56: // 004d3a56 8d4c2434 LEA ECX,[ESP + 0x34]
    ECX = (ESP + 0x00000034u);
L_004d3a5a: // 004d3a5a 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3a5b: // 004d3a5b e89061f5ff CALL 0x00429bf0
    state.argument_stack = pointer(ESP); application_core_effect_00429bf0(state); ESP += 4u;
L_004d3a60: // 004d3a60 8d4c2414 LEA ECX,[ESP + 0x14]
    ECX = (ESP + 0x00000014u);
L_004d3a64: // 004d3a64 e8d75df5ff CALL 0x00429840
    state.argument_stack = pointer(ESP); application_core_effect_00429840(state); ESP += 0u;
L_004d3a69: // 004d3a69 8b8edc000000 MOV ECX,dword ptr [ESI + 0xdc]
    ECX = read32((ESI + 0x000000dcu));
L_004d3a6f: // 004d3a6f 8b542434 MOV EDX,dword ptr [ESP + 0x34]
    EDX = read32((ESP + 0x00000034u));
L_004d3a73: // 004d3a73 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3a74: // 004d3a74 8b01 MOV EAX,dword ptr [ECX]
    EAX = read32((ECX));
L_004d3a76: // 004d3a76 ff5054 CALL dword ptr [EAX + 0x54]
    state.argument_stack = pointer(ESP); application_core_virtual_004d3a76(state, read32((EAX + 0x00000054u))); ESP += 4u;
L_004d3a79: // 004d3a79 8b8edc000000 MOV ECX,dword ptr [ESI + 0xdc]
    ECX = read32((ESI + 0x000000dcu));
L_004d3a7f: // 004d3a7f 8b01 MOV EAX,dword ptr [ECX]
    EAX = read32((ECX));
L_004d3a81: // 004d3a81 ff506c CALL dword ptr [EAX + 0x6c]
    state.argument_stack = pointer(ESP); application_core_virtual_004d3a81(state, read32((EAX + 0x0000006cu))); ESP += 0u;
L_004d3a84: // 004d3a84 8b8edc000000 MOV ECX,dword ptr [ESI + 0xdc]
    ECX = read32((ESI + 0x000000dcu));
L_004d3a8a: // 004d3a8a 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d3a8c: // 004d3a8c ff5278 CALL dword ptr [EDX + 0x78]
    state.argument_stack = pointer(ESP); application_core_virtual_004d3a8c(state, read32((EDX + 0x00000078u))); ESP += 0u;
L_004d3a8f: // 004d3a8f 8b44243c MOV EAX,dword ptr [ESP + 0x3c]
    EAX = read32((ESP + 0x0000003cu));
L_004d3a93: // 004d3a93 8b4c2434 MOV ECX,dword ptr [ESP + 0x34]
    ECX = read32((ESP + 0x00000034u));
L_004d3a97: // 004d3a97 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d3a99: // 004d3a99 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3a9b: // 004d3a9b 740f JZ 0x004d3aac
    if(state.flags.zero) goto L_004d3aac;
L_004d3a9d: // 004d3a9d 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3a9f: // 004d3a9f 740b JZ 0x004d3aac
    if(state.flags.zero) goto L_004d3aac;
L_004d3aa1: // 004d3aa1 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3aa2: // 004d3aa2 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3aa3: // 004d3aa3 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3aa4: // 004d3aa4 e827fdf4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d3aa9: // 004d3aa9 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d3aac: // 004d3aac 8b442430 MOV EAX,dword ptr [ESP + 0x30]
    EAX = read32((ESP + 0x00000030u));
L_004d3ab0: // 004d3ab0 8b4c2428 MOV ECX,dword ptr [ESP + 0x28]
    ECX = read32((ESP + 0x00000028u));
L_004d3ab4: // 004d3ab4 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d3ab6: // 004d3ab6 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3ab8: // 004d3ab8 740f JZ 0x004d3ac9
    if(state.flags.zero) goto L_004d3ac9;
L_004d3aba: // 004d3aba 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3abc: // 004d3abc 740b JZ 0x004d3ac9
    if(state.flags.zero) goto L_004d3ac9;
L_004d3abe: // 004d3abe 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3abf: // 004d3abf 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3ac0: // 004d3ac0 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3ac1: // 004d3ac1 e80afdf4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d3ac6: // 004d3ac6 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d3ac9: // 004d3ac9 899ee4000000 MOV dword ptr [ESI + 0xe4],EBX
    write32((ESI + 0x000000e4u), EBX);
L_004d3acf: // 004d3acf 899ee8000000 MOV dword ptr [ESI + 0xe8],EBX
    write32((ESI + 0x000000e8u), EBX);
L_004d3ad5: // 004d3ad5 e8d6cc0000 CALL 0x004e07b0
    state.argument_stack = pointer(ESP); application_core_effect_004e07b0(state); ESP += 0u;
L_004d3ada: // 004d3ada 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3adb: // 004d3adb 6a14 PUSH 0x14
    ESP -= 4u; write32(ESP, 0x00000014u);
L_004d3add: // 004d3add e8deb40c00 CALL 0x0059efc0
    state.argument_stack = pointer(ESP); application_core_effect_0059efc0(state); ESP += 0u;
L_004d3ae2: // 004d3ae2 8bf8 MOV EDI,EAX
    EDI = EAX;
L_004d3ae4: // 004d3ae4 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d3ae7: // 004d3ae7 3bfb CMP EDI,EBX
    (void)alu_sub(EDI, EBX, 32, state.flags);
L_004d3ae9: // 004d3ae9 7414 JZ 0x004d3aff
    if(state.flags.zero) goto L_004d3aff;
L_004d3aeb: // 004d3aeb 8d442413 LEA EAX,[ESP + 0x13]
    EAX = (ESP + 0x00000013u);
L_004d3aef: // 004d3aef 8d4f08 LEA ECX,[EDI + 0x8]
    ECX = (EDI + 0x00000008u);
L_004d3af2: // 004d3af2 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3af3: // 004d3af3 891f MOV dword ptr [EDI],EBX
    write32((EDI), EBX);
L_004d3af5: // 004d3af5 895f04 MOV dword ptr [EDI + 0x4],EBX
    write32((EDI + 0x00000004u), EBX);
L_004d3af8: // 004d3af8 e8131d0300 CALL 0x00505810
    state.argument_stack = pointer(ESP); application_core_effect_00505810(state); ESP += 4u;
L_004d3afd: // 004d3afd eb02 JMP 0x004d3b01
    goto L_004d3b01;
L_004d3aff: // 004d3aff 33ff XOR EDI,EDI
    EDI = alu_xor(0u, 0u, 32, state.flags);
L_004d3b01: // 004d3b01 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3b07: // 004d3b07 897c2440 MOV dword ptr [ESP + 0x40],EDI
    write32((ESP + 0x00000040u), EDI);
L_004d3b0b: // 004d3b0b 8b4104 MOV EAX,dword ptr [ECX + 0x4]
    EAX = read32((ECX + 0x00000004u));
L_004d3b0e: // 004d3b0e 8b5108 MOV EDX,dword ptr [ECX + 0x8]
    EDX = read32((ECX + 0x00000008u));
L_004d3b11: // 004d3b11 3bc2 CMP EAX,EDX
    (void)alu_sub(EAX, EDX, 32, state.flags);
L_004d3b13: // 004d3b13 740c JZ 0x004d3b21
    if(state.flags.zero) goto L_004d3b21;
L_004d3b15: // 004d3b15 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3b17: // 004d3b17 7402 JZ 0x004d3b1b
    if(state.flags.zero) goto L_004d3b1b;
L_004d3b19: // 004d3b19 8938 MOV dword ptr [EAX],EDI
    write32((EAX), EDI);
L_004d3b1b: // 004d3b1b 83410404 ADD dword ptr [ECX + 0x4],0x4
    write32((ECX + 0x00000004u), alu_add(read32((ECX + 0x00000004u)), 0x00000004u, 32, state.flags));
L_004d3b1f: // 004d3b1f eb0b JMP 0x004d3b2c
    goto L_004d3b2c;
L_004d3b21: // 004d3b21 8d542440 LEA EDX,[ESP + 0x40]
    EDX = (ESP + 0x00000040u);
L_004d3b25: // 004d3b25 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3b26: // 004d3b26 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3b27: // 004d3b27 e854c0faff CALL 0x0047fb80
    state.argument_stack = pointer(ESP); application_core_effect_0047fb80(state); ESP += 8u;
L_004d3b2c: // 004d3b2c 885c2413 MOV byte ptr [ESP + 0x13],BL
    write8((ESP + 0x00000013u), get_byte(EBX, 0));
L_004d3b30: // 004d3b30 e8ebe00000 CALL 0x004e1c20
    state.argument_stack = pointer(ESP); application_core_effect_004e1c20(state); ESP += 0u;
L_004d3b35: // 004d3b35 e826b40000 CALL 0x004def60
    state.argument_stack = pointer(ESP); application_core_effect_004def60(state); ESP += 0u;
L_004d3b3a: // 004d3b3a 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d3b3e: // 004d3b3e 740a JZ 0x004d3b4a
    if(state.flags.zero) goto L_004d3b4a;
L_004d3b40: // 004d3b40 6a08 PUSH 0x8
    ESP -= 4u; write32(ESP, 0x00000008u);
L_004d3b42: // 004d3b42 e8b99e0000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d3b47: // 004d3b47 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d3b4a: // 004d3b4a 381d58915d00 CMP byte ptr [0x005d9158],BL
    (void)alu_sub(read8((address(application_core_address_005d9158()))), get_byte(EBX, 0), 8, state.flags);
L_004d3b50: // 004d3b50 7517 JNZ 0x004d3b69
    if(!state.flags.zero) goto L_004d3b69;
L_004d3b52: // 004d3b52 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3b53: // 004d3b53 e868b80000 CALL 0x004df3c0
    state.argument_stack = pointer(ESP); application_core_effect_004df3c0(state); ESP += 0u;
L_004d3b58: // 004d3b58 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3b59: // 004d3b59 e852ae0000 CALL 0x004de9b0
    state.argument_stack = pointer(ESP); application_core_effect_004de9b0(state); ESP += 0u;
L_004d3b5e: // 004d3b5e 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d3b61: // 004d3b61 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d3b63: // 004d3b63 0f8549030000 JNZ 0x004d3eb2
    if(!state.flags.zero) goto L_004d3eb2;
L_004d3b69: // 004d3b69 83be7801000001 CMP dword ptr [ESI + 0x178],0x1
    (void)alu_sub(read32((ESI + 0x00000178u)), 0x00000001u, 32, state.flags);
L_004d3b70: // 004d3b70 0f843c030000 JZ 0x004d3eb2
    if(state.flags.zero) goto L_004d3eb2;
L_004d3b76: // 004d3b76 e805ad0000 CALL 0x004de880
    state.argument_stack = pointer(ESP); application_core_effect_004de880(state); ESP += 0u;
L_004d3b7b: // 004d3b7b bd508e5e00 MOV EBP,0x5e8e50
    EBP = address(application_core_address_005e8e50());
L_004d3b80: // 004d3b80 bf647a6500 MOV EDI,0x657a64
    EDI = address(application_core_address_00657a64());
L_004d3b85: // 004d3b85 8a0f MOV CL,byte ptr [EDI]
    set_byte(ECX, 0, read8((EDI)));
L_004d3b87: // 004d3b87 8a5500 MOV DL,byte ptr [EBP]
    set_byte(EDX, 0, read8((EBP)));
L_004d3b8a: // 004d3b8a 8ac1 MOV AL,CL
    set_byte(EAX, 0, get_byte(ECX, 0));
L_004d3b8c: // 004d3b8c 3aca CMP CL,DL
    (void)alu_sub(get_byte(ECX, 0), get_byte(EDX, 0), 8, state.flags);
L_004d3b8e: // 004d3b8e 751e JNZ 0x004d3bae
    if(!state.flags.zero) goto L_004d3bae;
L_004d3b90: // 004d3b90 3ac3 CMP AL,BL
    (void)alu_sub(get_byte(EAX, 0), get_byte(EBX, 0), 8, state.flags);
L_004d3b92: // 004d3b92 7416 JZ 0x004d3baa
    if(state.flags.zero) goto L_004d3baa;
L_004d3b94: // 004d3b94 8a5701 MOV DL,byte ptr [EDI + 0x1]
    set_byte(EDX, 0, read8((EDI + 0x00000001u)));
L_004d3b97: // 004d3b97 8a4d01 MOV CL,byte ptr [EBP + 0x1]
    set_byte(ECX, 0, read8((EBP + 0x00000001u)));
L_004d3b9a: // 004d3b9a 8ac2 MOV AL,DL
    set_byte(EAX, 0, get_byte(EDX, 0));
L_004d3b9c: // 004d3b9c 3ad1 CMP DL,CL
    (void)alu_sub(get_byte(EDX, 0), get_byte(ECX, 0), 8, state.flags);
L_004d3b9e: // 004d3b9e 750e JNZ 0x004d3bae
    if(!state.flags.zero) goto L_004d3bae;
L_004d3ba0: // 004d3ba0 83c702 ADD EDI,0x2
    EDI = alu_add(EDI, 0x00000002u, 32, state.flags);
L_004d3ba3: // 004d3ba3 83c502 ADD EBP,0x2
    EBP = alu_add(EBP, 0x00000002u, 32, state.flags);
L_004d3ba6: // 004d3ba6 3ac3 CMP AL,BL
    (void)alu_sub(get_byte(EAX, 0), get_byte(EBX, 0), 8, state.flags);
L_004d3ba8: // 004d3ba8 75db JNZ 0x004d3b85
    if(!state.flags.zero) goto L_004d3b85;
L_004d3baa: // 004d3baa 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3bac: // 004d3bac eb05 JMP 0x004d3bb3
    goto L_004d3bb3;
L_004d3bae: // 004d3bae 1bc0 SBB EAX,EAX
    EAX = alu_sbb(0u, 0u, 32, state.flags);
L_004d3bb0: // 004d3bb0 83d8ff SBB EAX,-0x1
    EAX = alu_sbb(EAX, 0xffffffffu, 32, state.flags);
L_004d3bb3: // 004d3bb3 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3bb5: // 004d3bb5 750c JNZ 0x004d3bc3
    if(!state.flags.zero) goto L_004d3bc3;
L_004d3bb7: // 004d3bb7 391d607a6500 CMP dword ptr [0x00657a60],EBX
    (void)alu_sub(read32((address(application_core_address_00657a60()))), EBX, 32, state.flags);
L_004d3bbd: // 004d3bbd 0f845a020000 JZ 0x004d3e1d
    if(state.flags.zero) goto L_004d3e1d;
L_004d3bc3: // 004d3bc3 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3bc4: // 004d3bc4 6884746500 PUSH 0x657484
    ESP -= 4u; write32(ESP, address(application_core_address_00657484()));
L_004d3bc9: // 004d3bc9 e8e2ad0000 CALL 0x004de9b0
    state.argument_stack = pointer(ESP); application_core_effect_004de9b0(state); ESP += 0u;
L_004d3bce: // 004d3bce 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d3bd1: // 004d3bd1 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d3bd3: // 004d3bd3 0f8444020000 JZ 0x004d3e1d
    if(state.flags.zero) goto L_004d3e1d;
L_004d3bd9: // 004d3bd9 391d607a6500 CMP dword ptr [0x00657a60],EBX
    (void)alu_sub(read32((address(application_core_address_00657a60()))), EBX, 32, state.flags);
L_004d3bdf: // 004d3bdf 0f8415010000 JZ 0x004d3cfa
    if(state.flags.zero) goto L_004d3cfa;
L_004d3be5: // 004d3be5 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3be6: // 004d3be6 e8155e0300 CALL 0x00509a00
    state.argument_stack = pointer(ESP); application_core_effect_00509a00(state); ESP += 0u;
L_004d3beb: // 004d3beb 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d3bee: // 004d3bee 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d3bf2: // 004d3bf2 e819faf4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d3bf7: // 004d3bf7 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d3bfa: // 004d3bfa bf786e5d00 MOV EDI,0x5d6e78
    EDI = address(application_core_address_005d6e78());
L_004d3bff: // 004d3bff 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d3c01: // 004d3c01 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3c04: // 004d3c04 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3c06: // 004d3c06 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d3c08: // 004d3c08 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d3c0b: // 004d3c0b 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d3c0e: // 004d3c0e f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3c10: // 004d3c10 f7d1 NOT ECX
    ECX = (~ECX);
L_004d3c12: // 004d3c12 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3c13: // 004d3c13 81c1786e5d00 ADD ECX,0x5d6e78
    ECX = alu_add(ECX, address(application_core_address_005d6e78()), 32, state.flags);
L_004d3c19: // 004d3c19 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3c1a: // 004d3c1a 68786e5d00 PUSH 0x5d6e78
    ESP -= 4u; write32(ESP, address(application_core_address_005d6e78()));
L_004d3c1f: // 004d3c1f 8bca MOV ECX,EDX
    ECX = EDX;
L_004d3c21: // 004d3c21 e87a5cf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3c26: // 004d3c26 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3c2c: // 004d3c2c 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3c2d: // 004d3c2d e8ee280000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d3c32: // 004d3c32 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d3c34: // 004d3c34 e8a71f0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d3c39: // 004d3c39 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d3c3d: // 004d3c3d e8cef9f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d3c42: // 004d3c42 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d3c45: // 004d3c45 bf44945d00 MOV EDI,0x5d9444
    EDI = address(application_core_address_005d9444());
L_004d3c4a: // 004d3c4a 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d3c4c: // 004d3c4c 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3c4f: // 004d3c4f 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3c51: // 004d3c51 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d3c53: // 004d3c53 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d3c56: // 004d3c56 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d3c59: // 004d3c59 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3c5b: // 004d3c5b f7d1 NOT ECX
    ECX = (~ECX);
L_004d3c5d: // 004d3c5d 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3c5e: // 004d3c5e 81c144945d00 ADD ECX,0x5d9444
    ECX = alu_add(ECX, address(application_core_address_005d9444()), 32, state.flags);
L_004d3c64: // 004d3c64 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3c65: // 004d3c65 6844945d00 PUSH 0x5d9444
    ESP -= 4u; write32(ESP, address(application_core_address_005d9444()));
L_004d3c6a: // 004d3c6a 8bca MOV ECX,EDX
    ECX = EDX;
L_004d3c6c: // 004d3c6c e82f5cf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3c71: // 004d3c71 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3c77: // 004d3c77 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3c78: // 004d3c78 e8a3280000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d3c7d: // 004d3c7d 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d3c7f: // 004d3c7f e85c1f0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d3c84: // 004d3c84 bf38945d00 MOV EDI,0x5d9438
    EDI = address(application_core_address_005d9438());
L_004d3c89: // 004d3c89 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3c8c: // 004d3c8c 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3c8e: // 004d3c8e 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d3c92: // 004d3c92 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3c94: // 004d3c94 f7d1 NOT ECX
    ECX = (~ECX);
L_004d3c96: // 004d3c96 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3c97: // 004d3c97 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d3c9b: // 004d3c9b 81c138945d00 ADD ECX,0x5d9438
    ECX = alu_add(ECX, address(application_core_address_005d9438()), 32, state.flags);
L_004d3ca1: // 004d3ca1 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d3ca5: // 004d3ca5 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3ca6: // 004d3ca6 6838945d00 PUSH 0x5d9438
    ESP -= 4u; write32(ESP, address(application_core_address_005d9438()));
L_004d3cab: // 004d3cab 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d3caf: // 004d3caf e8ec5bf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3cb4: // 004d3cb4 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3cba: // 004d3cba 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d3cbe: // 004d3cbe 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3cc0: // 004d3cc0 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3cc1: // 004d3cc1 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d3cc3: // 004d3cc3 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d3cc5: // 004d3cc5 e826210000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d3cca: // 004d3cca 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d3cce: // 004d3cce 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d3cd2: // 004d3cd2 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d3cd4: // 004d3cd4 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3cd6: // 004d3cd6 0f84cb010000 JZ 0x004d3ea7
    if(state.flags.zero) goto L_004d3ea7;
L_004d3cdc: // 004d3cdc 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3cde: // 004d3cde 0f84c3010000 JZ 0x004d3ea7
    if(state.flags.zero) goto L_004d3ea7;
L_004d3ce4: // 004d3ce4 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3ce5: // 004d3ce5 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3ce6: // 004d3ce6 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3ce7: // 004d3ce7 e8e4faf4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d3cec: // 004d3cec 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d3cef: // 004d3cef 881d58915d00 MOV byte ptr [0x005d9158],BL
    write8((address(application_core_address_005d9158())), get_byte(EBX, 0));
L_004d3cf5: // 004d3cf5 e90d150000 JMP 0x004d5207
    goto L_004d5207;
L_004d3cfa: // 004d3cfa 8b0d708c6200 MOV ECX,dword ptr [0x00628c70]
    ECX = read32((address(application_core_address_00628c70())));
L_004d3d00: // 004d3d00 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3d02: // 004d3d02 740d JZ 0x004d3d11
    if(state.flags.zero) goto L_004d3d11;
L_004d3d04: // 004d3d04 68647a6500 PUSH 0x657a64
    ESP -= 4u; write32(ESP, address(application_core_address_00657a64()));
L_004d3d09: // 004d3d09 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3d0a: // 004d3d0a 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3d0c: // 004d3d0c e88fa4fbff CALL 0x0048e1a0
    state.argument_stack = pointer(ESP); application_core_effect_0048e1a0(state); ESP += 12u;
L_004d3d11: // 004d3d11 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d3d15: // 004d3d15 e8f6f8f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d3d1a: // 004d3d1a 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d3d1d: // 004d3d1d bf786e5d00 MOV EDI,0x5d6e78
    EDI = address(application_core_address_005d6e78());
L_004d3d22: // 004d3d22 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d3d24: // 004d3d24 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3d27: // 004d3d27 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3d29: // 004d3d29 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d3d2b: // 004d3d2b 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d3d2e: // 004d3d2e 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d3d31: // 004d3d31 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3d33: // 004d3d33 f7d1 NOT ECX
    ECX = (~ECX);
L_004d3d35: // 004d3d35 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3d36: // 004d3d36 81c1786e5d00 ADD ECX,0x5d6e78
    ECX = alu_add(ECX, address(application_core_address_005d6e78()), 32, state.flags);
L_004d3d3c: // 004d3d3c 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3d3d: // 004d3d3d 68786e5d00 PUSH 0x5d6e78
    ESP -= 4u; write32(ESP, address(application_core_address_005d6e78()));
L_004d3d42: // 004d3d42 8bca MOV ECX,EDX
    ECX = EDX;
L_004d3d44: // 004d3d44 e8575bf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3d49: // 004d3d49 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3d4f: // 004d3d4f 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3d50: // 004d3d50 e8cb270000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d3d55: // 004d3d55 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d3d57: // 004d3d57 e8841e0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d3d5c: // 004d3d5c 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d3d60: // 004d3d60 e8abf8f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d3d65: // 004d3d65 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d3d68: // 004d3d68 bf44945d00 MOV EDI,0x5d9444
    EDI = address(application_core_address_005d9444());
L_004d3d6d: // 004d3d6d 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d3d6f: // 004d3d6f 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3d72: // 004d3d72 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3d74: // 004d3d74 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d3d76: // 004d3d76 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d3d79: // 004d3d79 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d3d7c: // 004d3d7c f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3d7e: // 004d3d7e f7d1 NOT ECX
    ECX = (~ECX);
L_004d3d80: // 004d3d80 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3d81: // 004d3d81 81c144945d00 ADD ECX,0x5d9444
    ECX = alu_add(ECX, address(application_core_address_005d9444()), 32, state.flags);
L_004d3d87: // 004d3d87 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3d88: // 004d3d88 6844945d00 PUSH 0x5d9444
    ESP -= 4u; write32(ESP, address(application_core_address_005d9444()));
L_004d3d8d: // 004d3d8d 8bca MOV ECX,EDX
    ECX = EDX;
L_004d3d8f: // 004d3d8f e80c5bf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3d94: // 004d3d94 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3d9a: // 004d3d9a 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3d9b: // 004d3d9b e880270000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d3da0: // 004d3da0 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d3da2: // 004d3da2 e8391e0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d3da7: // 004d3da7 bf2c945d00 MOV EDI,0x5d942c
    EDI = address(application_core_address_005d942c());
L_004d3dac: // 004d3dac 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3daf: // 004d3daf 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3db1: // 004d3db1 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d3db5: // 004d3db5 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3db7: // 004d3db7 f7d1 NOT ECX
    ECX = (~ECX);
L_004d3db9: // 004d3db9 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3dba: // 004d3dba 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d3dbe: // 004d3dbe 81c12c945d00 ADD ECX,0x5d942c
    ECX = alu_add(ECX, address(application_core_address_005d942c()), 32, state.flags);
L_004d3dc4: // 004d3dc4 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d3dc8: // 004d3dc8 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3dc9: // 004d3dc9 682c945d00 PUSH 0x5d942c
    ESP -= 4u; write32(ESP, address(application_core_address_005d942c()));
L_004d3dce: // 004d3dce 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d3dd2: // 004d3dd2 e8c95af5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3dd7: // 004d3dd7 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3ddd: // 004d3ddd 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d3de1: // 004d3de1 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3de3: // 004d3de3 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3de4: // 004d3de4 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d3de6: // 004d3de6 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d3de8: // 004d3de8 e803200000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d3ded: // 004d3ded 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d3df1: // 004d3df1 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d3df5: // 004d3df5 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d3df7: // 004d3df7 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3df9: // 004d3df9 0f84a8000000 JZ 0x004d3ea7
    if(state.flags.zero) goto L_004d3ea7;
L_004d3dff: // 004d3dff 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3e01: // 004d3e01 0f84a0000000 JZ 0x004d3ea7
    if(state.flags.zero) goto L_004d3ea7;
L_004d3e07: // 004d3e07 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3e08: // 004d3e08 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3e09: // 004d3e09 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3e0a: // 004d3e0a e8c1f9f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d3e0f: // 004d3e0f 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d3e12: // 004d3e12 881d58915d00 MOV byte ptr [0x005d9158],BL
    write8((address(application_core_address_005d9158())), get_byte(EBX, 0));
L_004d3e18: // 004d3e18 e9ea130000 JMP 0x004d5207
    goto L_004d5207;
L_004d3e1d: // 004d3e1d 8b9424a4000000 MOV EDX,dword ptr [ESP + 0xa4]
    EDX = read32((ESP + 0x000000a4u));
L_004d3e24: // 004d3e24 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3e27: // 004d3e27 8bfa MOV EDI,EDX
    EDI = EDX;
L_004d3e29: // 004d3e29 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3e2b: // 004d3e2b f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3e2d: // 004d3e2d f7d1 NOT ECX
    ECX = (~ECX);
L_004d3e2f: // 004d3e2f 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3e30: // 004d3e30 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d3e34: // 004d3e34 03ca ADD ECX,EDX
    ECX = alu_add(ECX, EDX, 32, state.flags);
L_004d3e36: // 004d3e36 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d3e3a: // 004d3e3a 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3e3b: // 004d3e3b 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d3e3c: // 004d3e3c 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d3e40: // 004d3e40 895c2424 MOV dword ptr [ESP + 0x24],EBX
    write32((ESP + 0x00000024u), EBX);
L_004d3e44: // 004d3e44 e8575af5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3e49: // 004d3e49 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3e4f: // 004d3e4f 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d3e53: // 004d3e53 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3e55: // 004d3e55 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3e56: // 004d3e56 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d3e58: // 004d3e58 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d3e5a: // 004d3e5a e8911f0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d3e5f: // 004d3e5f 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d3e63: // 004d3e63 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d3e67: // 004d3e67 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d3e69: // 004d3e69 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3e6b: // 004d3e6b 740f JZ 0x004d3e7c
    if(state.flags.zero) goto L_004d3e7c;
L_004d3e6d: // 004d3e6d 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3e6f: // 004d3e6f 740b JZ 0x004d3e7c
    if(state.flags.zero) goto L_004d3e7c;
L_004d3e71: // 004d3e71 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3e72: // 004d3e72 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3e73: // 004d3e73 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3e74: // 004d3e74 e857f9f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d3e79: // 004d3e79 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d3e7c: // 004d3e7c 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3e7e: // 004d3e7e 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3e80: // 004d3e80 6820945d00 PUSH 0x5d9420
    ESP -= 4u; write32(ESP, address(application_core_address_005d9420()));
L_004d3e85: // 004d3e85 8bce MOV ECX,ESI
    ECX = ESI;
L_004d3e87: // 004d3e87 e874e2ffff CALL 0x004d2100
    state.argument_stack = pointer(ESP); application_core_effect_004d2100(state); ESP += 12u;
L_004d3e8c: // 004d3e8c 6840010000 PUSH 0x140
    ESP -= 4u; write32(ESP, 0x00000140u);
L_004d3e91: // 004d3e91 6a03 PUSH 0x3
    ESP -= 4u; write32(ESP, 0x00000003u);
L_004d3e93: // 004d3e93 e828320600 CALL 0x005370c0
    state.argument_stack = pointer(ESP); application_core_effect_005370c0(state); ESP += 0u;
L_004d3e98: // 004d3e98 688a010000 PUSH 0x18a
    ESP -= 4u; write32(ESP, 0x0000018au);
L_004d3e9d: // 004d3e9d 6a04 PUSH 0x4
    ESP -= 4u; write32(ESP, 0x00000004u);
L_004d3e9f: // 004d3e9f e81c320600 CALL 0x005370c0
    state.argument_stack = pointer(ESP); application_core_effect_005370c0(state); ESP += 0u;
L_004d3ea4: // 004d3ea4 83c410 ADD ESP,0x10
    ESP = alu_add(ESP, 0x00000010u, 32, state.flags);
L_004d3ea7: // 004d3ea7 881d58915d00 MOV byte ptr [0x005d9158],BL
    write8((address(application_core_address_005d9158())), get_byte(EBX, 0));
L_004d3ead: // 004d3ead e955130000 JMP 0x004d5207
    goto L_004d5207;
L_004d3eb2: // 004d3eb2 e869820300 CALL 0x0050c120
    state.argument_stack = pointer(ESP); application_core_effect_0050c120(state); ESP += 0u;
L_004d3eb7: // 004d3eb7 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d3eb9: // 004d3eb9 7424 JZ 0x004d3edf
    if(state.flags.zero) goto L_004d3edf;
L_004d3ebb: // 004d3ebb 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3ebd: // 004d3ebd 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3ebe: // 004d3ebe 68786e5d00 PUSH 0x5d6e78
    ESP -= 4u; write32(ESP, address(application_core_address_005d6e78()));
L_004d3ec3: // 004d3ec3 8bce MOV ECX,ESI
    ECX = ESI;
L_004d3ec5: // 004d3ec5 e836e2ffff CALL 0x004d2100
    state.argument_stack = pointer(ESP); application_core_effect_004d2100(state); ESP += 12u;
L_004d3eca: // 004d3eca 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3ecc: // 004d3ecc 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3ece: // 004d3ece 6814945d00 PUSH 0x5d9414
    ESP -= 4u; write32(ESP, address(application_core_address_005d9414()));
L_004d3ed3: // 004d3ed3 8bce MOV ECX,ESI
    ECX = ESI;
L_004d3ed5: // 004d3ed5 e826e2ffff CALL 0x004d2100
    state.argument_stack = pointer(ESP); application_core_effect_004d2100(state); ESP += 12u;
L_004d3eda: // 004d3eda e928130000 JMP 0x004d5207
    goto L_004d5207;
L_004d3edf: // 004d3edf 83be7801000001 CMP dword ptr [ESI + 0x178],0x1
    (void)alu_sub(read32((ESI + 0x00000178u)), 0x00000001u, 32, state.flags);
L_004d3ee6: // 004d3ee6 0f84d4120000 JZ 0x004d51c0
    if(state.flags.zero) goto L_004d51c0;
L_004d3eec: // 004d3eec e80f9e0100 CALL 0x004edd00
    state.argument_stack = pointer(ESP); application_core_effect_004edd00(state); ESP += 0u;
L_004d3ef1: // 004d3ef1 381d347e6500 CMP byte ptr [0x00657e34],BL
    (void)alu_sub(read8((address(application_core_address_00657e34()))), get_byte(EBX, 0), 8, state.flags);
L_004d3ef7: // 004d3ef7 0f8467010000 JZ 0x004d4064
    if(state.flags.zero) goto L_004d4064;
L_004d3efd: // 004d3efd a1e8736500 MOV EAX,[0x006573e8]
    EAX = read32((address(application_core_address_006573e8())));
L_004d3f02: // 004d3f02 83f805 CMP EAX,0x5
    (void)alu_sub(EAX, 0x00000005u, 32, state.flags);
L_004d3f05: // 004d3f05 0f8459010000 JZ 0x004d4064
    if(state.flags.zero) goto L_004d4064;
L_004d3f0b: // 004d3f0b 83f806 CMP EAX,0x6
    (void)alu_sub(EAX, 0x00000006u, 32, state.flags);
L_004d3f0e: // 004d3f0e 0f8450010000 JZ 0x004d4064
    if(state.flags.zero) goto L_004d4064;
L_004d3f14: // 004d3f14 83f807 CMP EAX,0x7
    (void)alu_sub(EAX, 0x00000007u, 32, state.flags);
L_004d3f17: // 004d3f17 0f8447010000 JZ 0x004d4064
    if(state.flags.zero) goto L_004d4064;
L_004d3f1d: // 004d3f1d 83f808 CMP EAX,0x8
    (void)alu_sub(EAX, 0x00000008u, 32, state.flags);
L_004d3f20: // 004d3f20 0f843e010000 JZ 0x004d4064
    if(state.flags.zero) goto L_004d4064;
L_004d3f26: // 004d3f26 83f809 CMP EAX,0x9
    (void)alu_sub(EAX, 0x00000009u, 32, state.flags);
L_004d3f29: // 004d3f29 0f8435010000 JZ 0x004d4064
    if(state.flags.zero) goto L_004d4064;
L_004d3f2f: // 004d3f2f e80ca10000 CALL 0x004de040
    state.argument_stack = pointer(ESP); application_core_effect_004de040(state); ESP += 0u;
L_004d3f34: // 004d3f34 833de87365000b CMP dword ptr [0x006573e8],0xb
    (void)alu_sub(read32((address(application_core_address_006573e8()))), 0x0000000bu, 32, state.flags);
L_004d3f3b: // 004d3f3b 0f85b7000000 JNZ 0x004d3ff8
    if(!state.flags.zero) goto L_004d3ff8;
L_004d3f41: // 004d3f41 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d3f45: // 004d3f45 e8c6f6f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d3f4a: // 004d3f4a 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d3f51: // 004d3f51 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d3f54: // 004d3f54 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d3f56: // 004d3f56 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d3f58: // 004d3f58 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3f5b: // 004d3f5b 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3f5d: // 004d3f5d 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d3f5f: // 004d3f5f 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d3f62: // 004d3f62 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d3f65: // 004d3f65 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3f67: // 004d3f67 f7d1 NOT ECX
    ECX = (~ECX);
L_004d3f69: // 004d3f69 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3f6a: // 004d3f6a 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d3f6c: // 004d3f6c 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3f6d: // 004d3f6d 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d3f6e: // 004d3f6e 8bca MOV ECX,EDX
    ECX = EDX;
L_004d3f70: // 004d3f70 e82b59f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3f75: // 004d3f75 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3f7b: // 004d3f7b 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3f7c: // 004d3f7c e89f250000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d3f81: // 004d3f81 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d3f83: // 004d3f83 e8581c0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d3f88: // 004d3f88 bf08945d00 MOV EDI,0x5d9408
    EDI = address(application_core_address_005d9408());
L_004d3f8d: // 004d3f8d 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d3f90: // 004d3f90 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d3f92: // 004d3f92 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d3f96: // 004d3f96 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d3f98: // 004d3f98 f7d1 NOT ECX
    ECX = (~ECX);
L_004d3f9a: // 004d3f9a 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d3f9b: // 004d3f9b 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d3f9f: // 004d3f9f 81c108945d00 ADD ECX,0x5d9408
    ECX = alu_add(ECX, address(application_core_address_005d9408()), 32, state.flags);
L_004d3fa5: // 004d3fa5 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d3fa9: // 004d3fa9 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3faa: // 004d3faa 6808945d00 PUSH 0x5d9408
    ESP -= 4u; write32(ESP, address(application_core_address_005d9408()));
L_004d3faf: // 004d3faf 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d3fb3: // 004d3fb3 e8e858f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d3fb8: // 004d3fb8 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d3fbe: // 004d3fbe 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d3fc2: // 004d3fc2 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d3fc4: // 004d3fc4 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3fc5: // 004d3fc5 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d3fc7: // 004d3fc7 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d3fc9: // 004d3fc9 e8221e0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d3fce: // 004d3fce 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d3fd2: // 004d3fd2 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d3fd6: // 004d3fd6 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d3fd8: // 004d3fd8 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d3fda: // 004d3fda 0f8427120000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d3fe0: // 004d3fe0 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d3fe2: // 004d3fe2 0f841f120000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d3fe8: // 004d3fe8 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d3fe9: // 004d3fe9 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d3fea: // 004d3fea 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d3feb: // 004d3feb e8e0f7f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d3ff0: // 004d3ff0 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d3ff3: // 004d3ff3 e90f120000 JMP 0x004d5207
    goto L_004d5207;
L_004d3ff8: // 004d3ff8 8b9424a4000000 MOV EDX,dword ptr [ESP + 0xa4]
    EDX = read32((ESP + 0x000000a4u));
L_004d3fff: // 004d3fff 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4002: // 004d4002 8bfa MOV EDI,EDX
    EDI = EDX;
L_004d4004: // 004d4004 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4006: // 004d4006 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4008: // 004d4008 f7d1 NOT ECX
    ECX = (~ECX);
L_004d400a: // 004d400a 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d400b: // 004d400b 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d400f: // 004d400f 03ca ADD ECX,EDX
    ECX = alu_add(ECX, EDX, 32, state.flags);
L_004d4011: // 004d4011 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4015: // 004d4015 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4016: // 004d4016 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d4017: // 004d4017 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d401b: // 004d401b 895c2424 MOV dword ptr [ESP + 0x24],EBX
    write32((ESP + 0x00000024u), EBX);
L_004d401f: // 004d401f e87c58f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4024: // 004d4024 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d402a: // 004d402a 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d402e: // 004d402e 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4030: // 004d4030 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4031: // 004d4031 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4033: // 004d4033 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4035: // 004d4035 e8b61d0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d403a: // 004d403a 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d403e: // 004d403e 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4042: // 004d4042 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4044: // 004d4044 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4046: // 004d4046 0f84bb110000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d404c: // 004d404c 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d404e: // 004d404e 0f84b3110000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4054: // 004d4054 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4055: // 004d4055 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4056: // 004d4056 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4057: // 004d4057 e874f7f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d405c: // 004d405c 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d405f: // 004d405f e9a3110000 JMP 0x004d5207
    goto L_004d5207;
L_004d4064: // 004d4064 e8979e0000 CALL 0x004ddf00
    state.argument_stack = pointer(ESP); application_core_effect_004ddf00(state); ESP += 0u;
L_004d4069: // 004d4069 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d406b: // 004d406b 7405 JZ 0x004d4072
    if(state.flags.zero) goto L_004d4072;
L_004d406d: // 004d406d c644241301 MOV byte ptr [ESP + 0x13],0x1
    write8((ESP + 0x00000013u), 0x00000001u);
L_004d4072: // 004d4072 a1708c6200 MOV EAX,[0x00628c70]
    EAX = read32((address(application_core_address_00628c70())));
L_004d4077: // 004d4077 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4079: // 004d4079 0f84c8020000 JZ 0x004d4347
    if(state.flags.zero) goto L_004d4347;
L_004d407f: // 004d407f 395808 CMP dword ptr [EAX + 0x8],EBX
    (void)alu_sub(read32((EAX + 0x00000008u)), EBX, 32, state.flags);
L_004d4082: // 004d4082 0f84bf020000 JZ 0x004d4347
    if(state.flags.zero) goto L_004d4347;
L_004d4088: // 004d4088 3898bf000000 CMP byte ptr [EAX + 0xbf],BL
    (void)alu_sub(read8((EAX + 0x000000bfu)), get_byte(EBX, 0), 8, state.flags);
L_004d408e: // 004d408e 0f85b3020000 JNZ 0x004d4347
    if(!state.flags.zero) goto L_004d4347;
L_004d4094: // 004d4094 3898be000000 CMP byte ptr [EAX + 0xbe],BL
    (void)alu_sub(read8((EAX + 0x000000beu)), get_byte(EBX, 0), 8, state.flags);
L_004d409a: // 004d409a 0f84a7020000 JZ 0x004d4347
    if(state.flags.zero) goto L_004d4347;
L_004d40a0: // 004d40a0 3998dc000000 CMP dword ptr [EAX + 0xdc],EBX
    (void)alu_sub(read32((EAX + 0x000000dcu)), EBX, 32, state.flags);
L_004d40a6: // 004d40a6 0f8c9b020000 JL 0x004d4347
    if(state.flags.sign != state.flags.overflow) goto L_004d4347;
L_004d40ac: // 004d40ac 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d40b0: // 004d40b0 e85bf5f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d40b5: // 004d40b5 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d40bc: // 004d40bc 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d40bf: // 004d40bf 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d40c1: // 004d40c1 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d40c3: // 004d40c3 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d40c6: // 004d40c6 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d40c8: // 004d40c8 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d40ca: // 004d40ca 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d40cd: // 004d40cd 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d40d0: // 004d40d0 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d40d2: // 004d40d2 f7d1 NOT ECX
    ECX = (~ECX);
L_004d40d4: // 004d40d4 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d40d5: // 004d40d5 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d40d7: // 004d40d7 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d40d8: // 004d40d8 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d40d9: // 004d40d9 8bca MOV ECX,EDX
    ECX = EDX;
L_004d40db: // 004d40db e8c057f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d40e0: // 004d40e0 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d40e6: // 004d40e6 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d40e7: // 004d40e7 e834240000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d40ec: // 004d40ec 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d40ee: // 004d40ee e8ed1a0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d40f3: // 004d40f3 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d40f4: // 004d40f4 68e0705d00 PUSH 0x5d70e0
    ESP -= 4u; write32(ESP, address(application_core_address_005d70e0()));
L_004d40f9: // 004d40f9 68a8d65c00 PUSH 0x5cd6a8
    ESP -= 4u; write32(ESP, address(application_core_address_005cd6a8()));
L_004d40fe: // 004d40fe 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d40ff: // 004d40ff 6878735d00 PUSH 0x5d7378
    ESP -= 4u; write32(ESP, address(application_core_address_005d7378()));
L_004d4104: // 004d4104 e8a739feff CALL 0x004b7ab0
    state.argument_stack = pointer(ESP); application_core_effect_004b7ab0(state); ESP += 0u;
L_004d4109: // 004d4109 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d410c: // 004d410c 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d410d: // 004d410d e839d20c00 CALL 0x005a134b
    state.argument_stack = pointer(ESP); application_core_effect_005a134b(state); ESP += 0u;
L_004d4112: // 004d4112 8b10 MOV EDX,dword ptr [EAX]
    EDX = read32((EAX));
L_004d4114: // 004d4114 83c414 ADD ESP,0x14
    ESP = alu_add(ESP, 0x00000014u, 32, state.flags);
L_004d4117: // 004d4117 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d4119: // 004d4119 ff5228 CALL dword ptr [EDX + 0x28]
    state.argument_stack = pointer(ESP); application_core_virtual_004d4119(state, read32((EDX + 0x00000028u))); ESP += 0u;
L_004d411c: // 004d411c 83f803 CMP EAX,0x3
    (void)alu_sub(EAX, 0x00000003u, 32, state.flags);
L_004d411f: // 004d411f 0f8739010000 JA 0x004d425e
    if(!state.flags.carry && !state.flags.zero) goto L_004d425e;
L_004d4125: // 004d4125 ff2485b0554d00 JMP dword ptr [EAX*0x4 + 0x4d55b0]
    switch(EAX) { case 0: goto L_004d412c; case 1: goto L_004d41ad; case 2: goto L_004d41e0; case 3: goto L_004d4213; default: __assume(0); }
L_004d412c: // 004d412c 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d4130: // 004d4130 e8dbf4f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4135: // 004d4135 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4138: // 004d4138 bffc935d00 MOV EDI,0x5d93fc
    EDI = address(application_core_address_005d93fc());
L_004d413d: // 004d413d 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d413f: // 004d413f 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4142: // 004d4142 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4144: // 004d4144 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4146: // 004d4146 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4149: // 004d4149 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d414c: // 004d414c f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d414e: // 004d414e f7d1 NOT ECX
    ECX = (~ECX);
L_004d4150: // 004d4150 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4151: // 004d4151 81c1fc935d00 ADD ECX,0x5d93fc
    ECX = alu_add(ECX, address(application_core_address_005d93fc()), 32, state.flags);
L_004d4157: // 004d4157 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4158: // 004d4158 68fc935d00 PUSH 0x5d93fc
    ESP -= 4u; write32(ESP, address(application_core_address_005d93fc()));
L_004d415d: // 004d415d 8bca MOV ECX,EDX
    ECX = EDX;
L_004d415f: // 004d415f e83c57f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4164: // 004d4164 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d416a: // 004d416a 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d416b: // 004d416b e8b0230000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4170: // 004d4170 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4172: // 004d4172 e8691a0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4177: // 004d4177 8d4c2447 LEA ECX,[ESP + 0x47]
    ECX = (ESP + 0x00000047u);
L_004d417b: // 004d417b e890f4f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4180: // 004d4180 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4183: // 004d4183 bff4935d00 MOV EDI,0x5d93f4
    EDI = address(application_core_address_005d93f4());
L_004d4188: // 004d4188 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d418a: // 004d418a 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d418d: // 004d418d 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d418f: // 004d418f 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4191: // 004d4191 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4194: // 004d4194 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4197: // 004d4197 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4199: // 004d4199 f7d1 NOT ECX
    ECX = (~ECX);
L_004d419b: // 004d419b 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d419c: // 004d419c 81c1f4935d00 ADD ECX,0x5d93f4
    ECX = alu_add(ECX, address(application_core_address_005d93f4()), 32, state.flags);
L_004d41a2: // 004d41a2 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d41a3: // 004d41a3 68f4935d00 PUSH 0x5d93f4
    ESP -= 4u; write32(ESP, address(application_core_address_005d93f4()));
L_004d41a8: // 004d41a8 e997000000 JMP 0x004d4244
    goto L_004d4244;
L_004d41ad: // 004d41ad 8d4c244f LEA ECX,[ESP + 0x4f]
    ECX = (ESP + 0x0000004fu);
L_004d41b1: // 004d41b1 e85af4f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d41b6: // 004d41b6 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d41b9: // 004d41b9 bfec935d00 MOV EDI,0x5d93ec
    EDI = address(application_core_address_005d93ec());
L_004d41be: // 004d41be 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d41c0: // 004d41c0 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d41c3: // 004d41c3 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d41c5: // 004d41c5 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d41c7: // 004d41c7 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d41ca: // 004d41ca 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d41cd: // 004d41cd f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d41cf: // 004d41cf f7d1 NOT ECX
    ECX = (~ECX);
L_004d41d1: // 004d41d1 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d41d2: // 004d41d2 81c1ec935d00 ADD ECX,0x5d93ec
    ECX = alu_add(ECX, address(application_core_address_005d93ec()), 32, state.flags);
L_004d41d8: // 004d41d8 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d41d9: // 004d41d9 68ec935d00 PUSH 0x5d93ec
    ESP -= 4u; write32(ESP, address(application_core_address_005d93ec()));
L_004d41de: // 004d41de eb64 JMP 0x004d4244
    goto L_004d4244;
L_004d41e0: // 004d41e0 8d4c2446 LEA ECX,[ESP + 0x46]
    ECX = (ESP + 0x00000046u);
L_004d41e4: // 004d41e4 e827f4f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d41e9: // 004d41e9 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d41ec: // 004d41ec bfe4935d00 MOV EDI,0x5d93e4
    EDI = address(application_core_address_005d93e4());
L_004d41f1: // 004d41f1 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d41f3: // 004d41f3 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d41f6: // 004d41f6 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d41f8: // 004d41f8 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d41fa: // 004d41fa 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d41fd: // 004d41fd 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4200: // 004d4200 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4202: // 004d4202 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4204: // 004d4204 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4205: // 004d4205 81c1e4935d00 ADD ECX,0x5d93e4
    ECX = alu_add(ECX, address(application_core_address_005d93e4()), 32, state.flags);
L_004d420b: // 004d420b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d420c: // 004d420c 68e4935d00 PUSH 0x5d93e4
    ESP -= 4u; write32(ESP, address(application_core_address_005d93e4()));
L_004d4211: // 004d4211 eb31 JMP 0x004d4244
    goto L_004d4244;
L_004d4213: // 004d4213 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4217: // 004d4217 e8f4f3f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d421c: // 004d421c 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d421f: // 004d421f bf44945d00 MOV EDI,0x5d9444
    EDI = address(application_core_address_005d9444());
L_004d4224: // 004d4224 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4226: // 004d4226 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4229: // 004d4229 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d422b: // 004d422b 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d422d: // 004d422d 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4230: // 004d4230 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4233: // 004d4233 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4235: // 004d4235 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4237: // 004d4237 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4238: // 004d4238 81c144945d00 ADD ECX,0x5d9444
    ECX = alu_add(ECX, address(application_core_address_005d9444()), 32, state.flags);
L_004d423e: // 004d423e 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d423f: // 004d423f 6844945d00 PUSH 0x5d9444
    ESP -= 4u; write32(ESP, address(application_core_address_005d9444()));
L_004d4244: // 004d4244 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4246: // 004d4246 e85556f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d424b: // 004d424b 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4251: // 004d4251 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4252: // 004d4252 e8c9220000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4257: // 004d4257 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4259: // 004d4259 e882190000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d425e: // 004d425e e83d88fbff CALL 0x0048caa0
    state.argument_stack = pointer(ESP); application_core_effect_0048caa0(state); ESP += 0u;
L_004d4263: // 004d4263 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d4265: // 004d4265 7470 JZ 0x004d42d7
    if(state.flags.zero) goto L_004d42d7;
L_004d4267: // 004d4267 bf38945d00 MOV EDI,0x5d9438
    EDI = address(application_core_address_005d9438());
L_004d426c: // 004d426c 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d426f: // 004d426f 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4271: // 004d4271 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4275: // 004d4275 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4277: // 004d4277 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4279: // 004d4279 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d427a: // 004d427a 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d427e: // 004d427e 81c138945d00 ADD ECX,0x5d9438
    ECX = alu_add(ECX, address(application_core_address_005d9438()), 32, state.flags);
L_004d4284: // 004d4284 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4288: // 004d4288 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4289: // 004d4289 6838945d00 PUSH 0x5d9438
    ESP -= 4u; write32(ESP, address(application_core_address_005d9438()));
L_004d428e: // 004d428e 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4292: // 004d4292 e80956f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4297: // 004d4297 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d429d: // 004d429d 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d42a1: // 004d42a1 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d42a3: // 004d42a3 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d42a4: // 004d42a4 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d42a6: // 004d42a6 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d42a8: // 004d42a8 e8431b0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d42ad: // 004d42ad 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d42b1: // 004d42b1 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d42b5: // 004d42b5 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d42b7: // 004d42b7 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d42b9: // 004d42b9 0f84480f0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d42bf: // 004d42bf 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d42c1: // 004d42c1 0f84400f0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d42c7: // 004d42c7 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d42c8: // 004d42c8 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d42c9: // 004d42c9 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d42ca: // 004d42ca e801f5f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d42cf: // 004d42cf 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d42d2: // 004d42d2 e9300f0000 JMP 0x004d5207
    goto L_004d5207;
L_004d42d7: // 004d42d7 bf2c945d00 MOV EDI,0x5d942c
    EDI = address(application_core_address_005d942c());
L_004d42dc: // 004d42dc 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d42df: // 004d42df 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d42e1: // 004d42e1 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d42e5: // 004d42e5 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d42e7: // 004d42e7 f7d1 NOT ECX
    ECX = (~ECX);
L_004d42e9: // 004d42e9 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d42ea: // 004d42ea 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d42ee: // 004d42ee 81c12c945d00 ADD ECX,0x5d942c
    ECX = alu_add(ECX, address(application_core_address_005d942c()), 32, state.flags);
L_004d42f4: // 004d42f4 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d42f8: // 004d42f8 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d42f9: // 004d42f9 682c945d00 PUSH 0x5d942c
    ESP -= 4u; write32(ESP, address(application_core_address_005d942c()));
L_004d42fe: // 004d42fe 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4302: // 004d4302 e89955f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4307: // 004d4307 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d430d: // 004d430d 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4311: // 004d4311 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4313: // 004d4313 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4314: // 004d4314 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4316: // 004d4316 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4318: // 004d4318 e8d31a0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d431d: // 004d431d 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4321: // 004d4321 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4325: // 004d4325 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4327: // 004d4327 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4329: // 004d4329 0f84d80e0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d432f: // 004d432f 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4331: // 004d4331 0f84d00e0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4337: // 004d4337 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4338: // 004d4338 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4339: // 004d4339 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d433a: // 004d433a e891f4f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d433f: // 004d433f 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4342: // 004d4342 e9c00e0000 JMP 0x004d5207
    goto L_004d5207;
L_004d4347: // 004d4347 a1e8736500 MOV EAX,[0x006573e8]
    EAX = read32((address(application_core_address_006573e8())));
L_004d434c: // 004d434c 83f806 CMP EAX,0x6
    (void)alu_sub(EAX, 0x00000006u, 32, state.flags);
L_004d434f: // 004d434f 0f854d010000 JNZ 0x004d44a2
    if(!state.flags.zero) goto L_004d44a2;
L_004d4355: // 004d4355 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4359: // 004d4359 e8b2f2f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d435e: // 004d435e 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4365: // 004d4365 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4368: // 004d4368 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d436a: // 004d436a 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d436c: // 004d436c 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d436f: // 004d436f 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4371: // 004d4371 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4373: // 004d4373 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4376: // 004d4376 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4379: // 004d4379 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d437b: // 004d437b f7d1 NOT ECX
    ECX = (~ECX);
L_004d437d: // 004d437d 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d437e: // 004d437e 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4380: // 004d4380 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4381: // 004d4381 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4382: // 004d4382 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4384: // 004d4384 e81755f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4389: // 004d4389 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d438f: // 004d438f 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4390: // 004d4390 e88b210000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4395: // 004d4395 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4397: // 004d4397 e844180000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d439c: // 004d439c 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d43a0: // 004d43a0 e86bf2f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d43a5: // 004d43a5 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d43a8: // 004d43a8 bfdc8b5d00 MOV EDI,0x5d8bdc
    EDI = address(application_core_address_005d8bdc());
L_004d43ad: // 004d43ad 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d43af: // 004d43af 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d43b2: // 004d43b2 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d43b4: // 004d43b4 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d43b6: // 004d43b6 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d43b9: // 004d43b9 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d43bc: // 004d43bc f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d43be: // 004d43be f7d1 NOT ECX
    ECX = (~ECX);
L_004d43c0: // 004d43c0 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d43c1: // 004d43c1 81c1dc8b5d00 ADD ECX,0x5d8bdc
    ECX = alu_add(ECX, address(application_core_address_005d8bdc()), 32, state.flags);
L_004d43c7: // 004d43c7 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d43c8: // 004d43c8 68dc8b5d00 PUSH 0x5d8bdc
    ESP -= 4u; write32(ESP, address(application_core_address_005d8bdc()));
L_004d43cd: // 004d43cd 8bca MOV ECX,EDX
    ECX = EDX;
L_004d43cf: // 004d43cf e8cc54f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d43d4: // 004d43d4 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d43da: // 004d43da 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d43db: // 004d43db e840210000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d43e0: // 004d43e0 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d43e2: // 004d43e2 e8f9170000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d43e7: // 004d43e7 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d43eb: // 004d43eb e820f2f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d43f0: // 004d43f0 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d43f3: // 004d43f3 bfdc935d00 MOV EDI,0x5d93dc
    EDI = address(application_core_address_005d93dc());
L_004d43f8: // 004d43f8 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d43fa: // 004d43fa 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d43fd: // 004d43fd 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d43ff: // 004d43ff 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4401: // 004d4401 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4404: // 004d4404 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4407: // 004d4407 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4409: // 004d4409 f7d1 NOT ECX
    ECX = (~ECX);
L_004d440b: // 004d440b 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d440c: // 004d440c 81c1dc935d00 ADD ECX,0x5d93dc
    ECX = alu_add(ECX, address(application_core_address_005d93dc()), 32, state.flags);
L_004d4412: // 004d4412 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4413: // 004d4413 68dc935d00 PUSH 0x5d93dc
    ESP -= 4u; write32(ESP, address(application_core_address_005d93dc()));
L_004d4418: // 004d4418 8bca MOV ECX,EDX
    ECX = EDX;
L_004d441a: // 004d441a e88154f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d441f: // 004d441f 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4425: // 004d4425 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4426: // 004d4426 e8f5200000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d442b: // 004d442b 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d442d: // 004d442d e8ae170000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4432: // 004d4432 bfd0935d00 MOV EDI,0x5d93d0
    EDI = address(application_core_address_005d93d0());
L_004d4437: // 004d4437 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d443a: // 004d443a 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d443c: // 004d443c 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4440: // 004d4440 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4442: // 004d4442 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4444: // 004d4444 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4445: // 004d4445 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4449: // 004d4449 81c1d0935d00 ADD ECX,0x5d93d0
    ECX = alu_add(ECX, address(application_core_address_005d93d0()), 32, state.flags);
L_004d444f: // 004d444f 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4453: // 004d4453 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4454: // 004d4454 68d0935d00 PUSH 0x5d93d0
    ESP -= 4u; write32(ESP, address(application_core_address_005d93d0()));
L_004d4459: // 004d4459 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d445d: // 004d445d e83e54f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4462: // 004d4462 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4468: // 004d4468 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d446c: // 004d446c 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d446e: // 004d446e 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d446f: // 004d446f 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4471: // 004d4471 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4473: // 004d4473 e878190000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4478: // 004d4478 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d447c: // 004d447c 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4480: // 004d4480 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4482: // 004d4482 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4484: // 004d4484 0f847d0d0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d448a: // 004d448a 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d448c: // 004d448c 0f84750d0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4492: // 004d4492 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4493: // 004d4493 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4494: // 004d4494 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4495: // 004d4495 e836f3f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d449a: // 004d449a 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d449d: // 004d449d e9650d0000 JMP 0x004d5207
    goto L_004d5207;
L_004d44a2: // 004d44a2 83f807 CMP EAX,0x7
    (void)alu_sub(EAX, 0x00000007u, 32, state.flags);
L_004d44a5: // 004d44a5 0f854d010000 JNZ 0x004d45f8
    if(!state.flags.zero) goto L_004d45f8;
L_004d44ab: // 004d44ab 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d44af: // 004d44af e85cf1f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d44b4: // 004d44b4 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d44bb: // 004d44bb 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d44be: // 004d44be 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d44c0: // 004d44c0 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d44c2: // 004d44c2 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d44c5: // 004d44c5 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d44c7: // 004d44c7 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d44c9: // 004d44c9 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d44cc: // 004d44cc 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d44cf: // 004d44cf f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d44d1: // 004d44d1 f7d1 NOT ECX
    ECX = (~ECX);
L_004d44d3: // 004d44d3 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d44d4: // 004d44d4 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d44d6: // 004d44d6 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d44d7: // 004d44d7 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d44d8: // 004d44d8 8bca MOV ECX,EDX
    ECX = EDX;
L_004d44da: // 004d44da e8c153f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d44df: // 004d44df 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d44e5: // 004d44e5 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d44e6: // 004d44e6 e835200000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d44eb: // 004d44eb 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d44ed: // 004d44ed e8ee160000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d44f2: // 004d44f2 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d44f6: // 004d44f6 e815f1f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d44fb: // 004d44fb 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d44fe: // 004d44fe bfdc8b5d00 MOV EDI,0x5d8bdc
    EDI = address(application_core_address_005d8bdc());
L_004d4503: // 004d4503 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4505: // 004d4505 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4508: // 004d4508 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d450a: // 004d450a 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d450c: // 004d450c 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d450f: // 004d450f 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4512: // 004d4512 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4514: // 004d4514 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4516: // 004d4516 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4517: // 004d4517 81c1dc8b5d00 ADD ECX,0x5d8bdc
    ECX = alu_add(ECX, address(application_core_address_005d8bdc()), 32, state.flags);
L_004d451d: // 004d451d 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d451e: // 004d451e 68dc8b5d00 PUSH 0x5d8bdc
    ESP -= 4u; write32(ESP, address(application_core_address_005d8bdc()));
L_004d4523: // 004d4523 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4525: // 004d4525 e87653f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d452a: // 004d452a 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4530: // 004d4530 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4531: // 004d4531 e8ea1f0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4536: // 004d4536 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4538: // 004d4538 e8a3160000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d453d: // 004d453d 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4541: // 004d4541 e8caf0f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4546: // 004d4546 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4549: // 004d4549 bfdc935d00 MOV EDI,0x5d93dc
    EDI = address(application_core_address_005d93dc());
L_004d454e: // 004d454e 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4550: // 004d4550 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4553: // 004d4553 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4555: // 004d4555 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4557: // 004d4557 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d455a: // 004d455a 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d455d: // 004d455d f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d455f: // 004d455f f7d1 NOT ECX
    ECX = (~ECX);
L_004d4561: // 004d4561 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4562: // 004d4562 81c1dc935d00 ADD ECX,0x5d93dc
    ECX = alu_add(ECX, address(application_core_address_005d93dc()), 32, state.flags);
L_004d4568: // 004d4568 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4569: // 004d4569 68dc935d00 PUSH 0x5d93dc
    ESP -= 4u; write32(ESP, address(application_core_address_005d93dc()));
L_004d456e: // 004d456e 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4570: // 004d4570 e82b53f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4575: // 004d4575 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d457b: // 004d457b 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d457c: // 004d457c e89f1f0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4581: // 004d4581 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4583: // 004d4583 e858160000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4588: // 004d4588 bfc4935d00 MOV EDI,0x5d93c4
    EDI = address(application_core_address_005d93c4());
L_004d458d: // 004d458d 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4590: // 004d4590 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4592: // 004d4592 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4596: // 004d4596 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4598: // 004d4598 f7d1 NOT ECX
    ECX = (~ECX);
L_004d459a: // 004d459a 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d459b: // 004d459b 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d459f: // 004d459f 81c1c4935d00 ADD ECX,0x5d93c4
    ECX = alu_add(ECX, address(application_core_address_005d93c4()), 32, state.flags);
L_004d45a5: // 004d45a5 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d45a9: // 004d45a9 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d45aa: // 004d45aa 68c4935d00 PUSH 0x5d93c4
    ESP -= 4u; write32(ESP, address(application_core_address_005d93c4()));
L_004d45af: // 004d45af 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d45b3: // 004d45b3 e8e852f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d45b8: // 004d45b8 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d45be: // 004d45be 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d45c2: // 004d45c2 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d45c4: // 004d45c4 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d45c5: // 004d45c5 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d45c7: // 004d45c7 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d45c9: // 004d45c9 e822180000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d45ce: // 004d45ce 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d45d2: // 004d45d2 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d45d6: // 004d45d6 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d45d8: // 004d45d8 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d45da: // 004d45da 0f84270c0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d45e0: // 004d45e0 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d45e2: // 004d45e2 0f841f0c0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d45e8: // 004d45e8 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d45e9: // 004d45e9 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d45ea: // 004d45ea 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d45eb: // 004d45eb e8e0f1f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d45f0: // 004d45f0 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d45f3: // 004d45f3 e90f0c0000 JMP 0x004d5207
    goto L_004d5207;
L_004d45f8: // 004d45f8 83f808 CMP EAX,0x8
    (void)alu_sub(EAX, 0x00000008u, 32, state.flags);
L_004d45fb: // 004d45fb 0f854d010000 JNZ 0x004d474e
    if(!state.flags.zero) goto L_004d474e;
L_004d4601: // 004d4601 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4605: // 004d4605 e806f0f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d460a: // 004d460a 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4611: // 004d4611 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4614: // 004d4614 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4616: // 004d4616 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4618: // 004d4618 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d461b: // 004d461b 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d461d: // 004d461d 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d461f: // 004d461f 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4622: // 004d4622 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4625: // 004d4625 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4627: // 004d4627 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4629: // 004d4629 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d462a: // 004d462a 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d462c: // 004d462c 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d462d: // 004d462d 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d462e: // 004d462e 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4630: // 004d4630 e86b52f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4635: // 004d4635 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d463b: // 004d463b 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d463c: // 004d463c e8df1e0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4641: // 004d4641 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4643: // 004d4643 e898150000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4648: // 004d4648 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d464c: // 004d464c e8bfeff4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4651: // 004d4651 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4654: // 004d4654 bfdc8b5d00 MOV EDI,0x5d8bdc
    EDI = address(application_core_address_005d8bdc());
L_004d4659: // 004d4659 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d465b: // 004d465b 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d465e: // 004d465e 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4660: // 004d4660 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4662: // 004d4662 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4665: // 004d4665 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4668: // 004d4668 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d466a: // 004d466a f7d1 NOT ECX
    ECX = (~ECX);
L_004d466c: // 004d466c 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d466d: // 004d466d 81c1dc8b5d00 ADD ECX,0x5d8bdc
    ECX = alu_add(ECX, address(application_core_address_005d8bdc()), 32, state.flags);
L_004d4673: // 004d4673 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4674: // 004d4674 68dc8b5d00 PUSH 0x5d8bdc
    ESP -= 4u; write32(ESP, address(application_core_address_005d8bdc()));
L_004d4679: // 004d4679 8bca MOV ECX,EDX
    ECX = EDX;
L_004d467b: // 004d467b e82052f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4680: // 004d4680 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4686: // 004d4686 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4687: // 004d4687 e8941e0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d468c: // 004d468c 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d468e: // 004d468e e84d150000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4693: // 004d4693 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4697: // 004d4697 e874eff4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d469c: // 004d469c 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d469f: // 004d469f bfdc935d00 MOV EDI,0x5d93dc
    EDI = address(application_core_address_005d93dc());
L_004d46a4: // 004d46a4 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d46a6: // 004d46a6 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d46a9: // 004d46a9 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d46ab: // 004d46ab 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d46ad: // 004d46ad 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d46b0: // 004d46b0 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d46b3: // 004d46b3 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d46b5: // 004d46b5 f7d1 NOT ECX
    ECX = (~ECX);
L_004d46b7: // 004d46b7 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d46b8: // 004d46b8 81c1dc935d00 ADD ECX,0x5d93dc
    ECX = alu_add(ECX, address(application_core_address_005d93dc()), 32, state.flags);
L_004d46be: // 004d46be 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d46bf: // 004d46bf 68dc935d00 PUSH 0x5d93dc
    ESP -= 4u; write32(ESP, address(application_core_address_005d93dc()));
L_004d46c4: // 004d46c4 8bca MOV ECX,EDX
    ECX = EDX;
L_004d46c6: // 004d46c6 e8d551f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d46cb: // 004d46cb 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d46d1: // 004d46d1 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d46d2: // 004d46d2 e8491e0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d46d7: // 004d46d7 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d46d9: // 004d46d9 e802150000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d46de: // 004d46de bfb8935d00 MOV EDI,0x5d93b8
    EDI = address(application_core_address_005d93b8());
L_004d46e3: // 004d46e3 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d46e6: // 004d46e6 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d46e8: // 004d46e8 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d46ec: // 004d46ec f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d46ee: // 004d46ee f7d1 NOT ECX
    ECX = (~ECX);
L_004d46f0: // 004d46f0 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d46f1: // 004d46f1 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d46f5: // 004d46f5 81c1b8935d00 ADD ECX,0x5d93b8
    ECX = alu_add(ECX, address(application_core_address_005d93b8()), 32, state.flags);
L_004d46fb: // 004d46fb 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d46ff: // 004d46ff 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4700: // 004d4700 68b8935d00 PUSH 0x5d93b8
    ESP -= 4u; write32(ESP, address(application_core_address_005d93b8()));
L_004d4705: // 004d4705 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4709: // 004d4709 e89251f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d470e: // 004d470e 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4714: // 004d4714 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4718: // 004d4718 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d471a: // 004d471a 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d471b: // 004d471b 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d471d: // 004d471d 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d471f: // 004d471f e8cc160000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4724: // 004d4724 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4728: // 004d4728 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d472c: // 004d472c 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d472e: // 004d472e 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4730: // 004d4730 0f84d10a0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4736: // 004d4736 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4738: // 004d4738 0f84c90a0000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d473e: // 004d473e 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d473f: // 004d473f 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4740: // 004d4740 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4741: // 004d4741 e88af0f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4746: // 004d4746 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4749: // 004d4749 e9b90a0000 JMP 0x004d5207
    goto L_004d5207;
L_004d474e: // 004d474e 83f804 CMP EAX,0x4
    (void)alu_sub(EAX, 0x00000004u, 32, state.flags);
L_004d4751: // 004d4751 0f8527010000 JNZ 0x004d487e
    if(!state.flags.zero) goto L_004d487e;
L_004d4757: // 004d4757 391dd8776500 CMP dword ptr [0x006577d8],EBX
    (void)alu_sub(read32((address(application_core_address_006577d8()))), EBX, 32, state.flags);
L_004d475d: // 004d475d 0f8424010000 JZ 0x004d4887
    if(state.flags.zero) goto L_004d4887;
L_004d4763: // 004d4763 391ddc776500 CMP dword ptr [0x006577dc],EBX
    (void)alu_sub(read32((address(application_core_address_006577dc()))), EBX, 32, state.flags);
L_004d4769: // 004d4769 0f8428020000 JZ 0x004d4997
    if(state.flags.zero) goto L_004d4997;
L_004d476f: // 004d476f e88c100300 CALL 0x00505800
    state.argument_stack = pointer(ESP); application_core_effect_00505800(state); ESP += 0u;
L_004d4774: // 004d4774 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d4776: // 004d4776 0f840d020000 JZ 0x004d4989
    if(state.flags.zero) goto L_004d4989;
L_004d477c: // 004d477c 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4780: // 004d4780 e88beef4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4785: // 004d4785 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d478c: // 004d478c 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d478f: // 004d478f 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4791: // 004d4791 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4793: // 004d4793 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4796: // 004d4796 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4798: // 004d4798 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d479a: // 004d479a 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d479d: // 004d479d 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d47a0: // 004d47a0 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d47a2: // 004d47a2 f7d1 NOT ECX
    ECX = (~ECX);
L_004d47a4: // 004d47a4 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d47a5: // 004d47a5 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d47a7: // 004d47a7 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d47a8: // 004d47a8 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d47a9: // 004d47a9 8bca MOV ECX,EDX
    ECX = EDX;
L_004d47ab: // 004d47ab e8f050f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d47b0: // 004d47b0 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d47b6: // 004d47b6 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d47b7: // 004d47b7 e8641d0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d47bc: // 004d47bc 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d47be: // 004d47be e81d140000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d47c3: // 004d47c3 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d47c7: // 004d47c7 e844eef4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d47cc: // 004d47cc 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d47cf: // 004d47cf bfac935d00 MOV EDI,0x5d93ac
    EDI = address(application_core_address_005d93ac());
L_004d47d4: // 004d47d4 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d47d6: // 004d47d6 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d47d9: // 004d47d9 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d47db: // 004d47db 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d47dd: // 004d47dd 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d47e0: // 004d47e0 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d47e3: // 004d47e3 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d47e5: // 004d47e5 f7d1 NOT ECX
    ECX = (~ECX);
L_004d47e7: // 004d47e7 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d47e8: // 004d47e8 81c1ac935d00 ADD ECX,0x5d93ac
    ECX = alu_add(ECX, address(application_core_address_005d93ac()), 32, state.flags);
L_004d47ee: // 004d47ee 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d47ef: // 004d47ef 68ac935d00 PUSH 0x5d93ac
    ESP -= 4u; write32(ESP, address(application_core_address_005d93ac()));
L_004d47f4: // 004d47f4 8bca MOV ECX,EDX
    ECX = EDX;
L_004d47f6: // 004d47f6 e8a550f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d47fb: // 004d47fb 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4801: // 004d4801 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4802: // 004d4802 e8191d0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4807: // 004d4807 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4809: // 004d4809 e8d2130000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d480e: // 004d480e bfa0935d00 MOV EDI,0x5d93a0
    EDI = address(application_core_address_005d93a0());
L_004d4813: // 004d4813 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4816: // 004d4816 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4818: // 004d4818 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d481c: // 004d481c f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d481e: // 004d481e f7d1 NOT ECX
    ECX = (~ECX);
L_004d4820: // 004d4820 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4821: // 004d4821 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4825: // 004d4825 81c1a0935d00 ADD ECX,0x5d93a0
    ECX = alu_add(ECX, address(application_core_address_005d93a0()), 32, state.flags);
L_004d482b: // 004d482b 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d482f: // 004d482f 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4830: // 004d4830 68a0935d00 PUSH 0x5d93a0
    ESP -= 4u; write32(ESP, address(application_core_address_005d93a0()));
L_004d4835: // 004d4835 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4839: // 004d4839 e86250f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d483e: // 004d483e 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4844: // 004d4844 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4848: // 004d4848 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d484a: // 004d484a 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d484b: // 004d484b 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d484d: // 004d484d 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d484f: // 004d484f e89c150000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4854: // 004d4854 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4858: // 004d4858 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d485c: // 004d485c 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d485e: // 004d485e 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4860: // 004d4860 0f84a1090000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4866: // 004d4866 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4868: // 004d4868 0f8499090000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d486e: // 004d486e 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d486f: // 004d486f 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4870: // 004d4870 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4871: // 004d4871 e85aeff4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4876: // 004d4876 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4879: // 004d4879 e989090000 JMP 0x004d5207
    goto L_004d5207;
L_004d487e: // 004d487e 83f805 CMP EAX,0x5
    (void)alu_sub(EAX, 0x00000005u, 32, state.flags);
L_004d4881: // 004d4881 0f85d3010000 JNZ 0x004d4a5a
    if(!state.flags.zero) goto L_004d4a5a;
L_004d4887: // 004d4887 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d488b: // 004d488b e880edf4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4890: // 004d4890 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4897: // 004d4897 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d489a: // 004d489a 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d489c: // 004d489c 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d489e: // 004d489e 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d48a1: // 004d48a1 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d48a3: // 004d48a3 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d48a5: // 004d48a5 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d48a8: // 004d48a8 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d48ab: // 004d48ab f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d48ad: // 004d48ad f7d1 NOT ECX
    ECX = (~ECX);
L_004d48af: // 004d48af 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d48b0: // 004d48b0 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d48b2: // 004d48b2 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d48b3: // 004d48b3 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d48b4: // 004d48b4 8bca MOV ECX,EDX
    ECX = EDX;
L_004d48b6: // 004d48b6 e8e54ff5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d48bb: // 004d48bb 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d48c1: // 004d48c1 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d48c2: // 004d48c2 e8591c0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d48c7: // 004d48c7 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d48c9: // 004d48c9 e812130000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d48ce: // 004d48ce 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d48d2: // 004d48d2 e839edf4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d48d7: // 004d48d7 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d48da: // 004d48da bfdc8b5d00 MOV EDI,0x5d8bdc
    EDI = address(application_core_address_005d8bdc());
L_004d48df: // 004d48df 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d48e1: // 004d48e1 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d48e4: // 004d48e4 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d48e6: // 004d48e6 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d48e8: // 004d48e8 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d48eb: // 004d48eb 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d48ee: // 004d48ee f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d48f0: // 004d48f0 f7d1 NOT ECX
    ECX = (~ECX);
L_004d48f2: // 004d48f2 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d48f3: // 004d48f3 81c1dc8b5d00 ADD ECX,0x5d8bdc
    ECX = alu_add(ECX, address(application_core_address_005d8bdc()), 32, state.flags);
L_004d48f9: // 004d48f9 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d48fa: // 004d48fa 68dc8b5d00 PUSH 0x5d8bdc
    ESP -= 4u; write32(ESP, address(application_core_address_005d8bdc()));
L_004d48ff: // 004d48ff 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4901: // 004d4901 e89a4ff5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4906: // 004d4906 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d490c: // 004d490c 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d490d: // 004d490d e80e1c0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4912: // 004d4912 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4914: // 004d4914 e8c7120000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4919: // 004d4919 bf98935d00 MOV EDI,0x5d9398
    EDI = address(application_core_address_005d9398());
L_004d491e: // 004d491e 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4921: // 004d4921 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4923: // 004d4923 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4927: // 004d4927 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4929: // 004d4929 f7d1 NOT ECX
    ECX = (~ECX);
L_004d492b: // 004d492b 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d492c: // 004d492c 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4930: // 004d4930 81c198935d00 ADD ECX,0x5d9398
    ECX = alu_add(ECX, address(application_core_address_005d9398()), 32, state.flags);
L_004d4936: // 004d4936 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d493a: // 004d493a 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d493b: // 004d493b 6898935d00 PUSH 0x5d9398
    ESP -= 4u; write32(ESP, address(application_core_address_005d9398()));
L_004d4940: // 004d4940 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4944: // 004d4944 e8574ff5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4949: // 004d4949 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d494f: // 004d494f 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4953: // 004d4953 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4955: // 004d4955 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4956: // 004d4956 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4958: // 004d4958 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d495a: // 004d495a e891140000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d495f: // 004d495f 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4963: // 004d4963 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4967: // 004d4967 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4969: // 004d4969 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d496b: // 004d496b 0f8496080000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4971: // 004d4971 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4973: // 004d4973 0f848e080000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4979: // 004d4979 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d497a: // 004d497a 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d497b: // 004d497b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d497c: // 004d497c e84feef4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4981: // 004d4981 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4984: // 004d4984 e97e080000 JMP 0x004d5207
    goto L_004d5207;
L_004d4989: // 004d4989 a1e8736500 MOV EAX,[0x006573e8]
    EAX = read32((address(application_core_address_006573e8())));
L_004d498e: // 004d498e 83f804 CMP EAX,0x4
    (void)alu_sub(EAX, 0x00000004u, 32, state.flags);
L_004d4991: // 004d4991 0f85c3000000 JNZ 0x004d4a5a
    if(!state.flags.zero) goto L_004d4a5a;
L_004d4997: // 004d4997 391dd8776500 CMP dword ptr [0x006577d8],EBX
    (void)alu_sub(read32((address(application_core_address_006577d8()))), EBX, 32, state.flags);
L_004d499d: // 004d499d 0f84ff040000 JZ 0x004d4ea2
    if(state.flags.zero) goto L_004d4ea2;
L_004d49a3: // 004d49a3 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d49a7: // 004d49a7 e864ecf4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d49ac: // 004d49ac 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d49b3: // 004d49b3 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d49b6: // 004d49b6 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d49b8: // 004d49b8 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d49ba: // 004d49ba 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d49bd: // 004d49bd 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d49bf: // 004d49bf 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d49c1: // 004d49c1 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d49c4: // 004d49c4 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d49c7: // 004d49c7 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d49c9: // 004d49c9 f7d1 NOT ECX
    ECX = (~ECX);
L_004d49cb: // 004d49cb 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d49cc: // 004d49cc 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d49ce: // 004d49ce 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d49cf: // 004d49cf 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d49d0: // 004d49d0 8bca MOV ECX,EDX
    ECX = EDX;
L_004d49d2: // 004d49d2 e8c94ef5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d49d7: // 004d49d7 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d49dd: // 004d49dd 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d49de: // 004d49de e83d1b0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d49e3: // 004d49e3 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d49e5: // 004d49e5 e8f6110000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d49ea: // 004d49ea bfdc8b5d00 MOV EDI,0x5d8bdc
    EDI = address(application_core_address_005d8bdc());
L_004d49ef: // 004d49ef 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d49f2: // 004d49f2 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d49f4: // 004d49f4 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d49f8: // 004d49f8 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d49fa: // 004d49fa f7d1 NOT ECX
    ECX = (~ECX);
L_004d49fc: // 004d49fc 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d49fd: // 004d49fd 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4a01: // 004d4a01 81c1dc8b5d00 ADD ECX,0x5d8bdc
    ECX = alu_add(ECX, address(application_core_address_005d8bdc()), 32, state.flags);
L_004d4a07: // 004d4a07 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4a0b: // 004d4a0b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4a0c: // 004d4a0c 68dc8b5d00 PUSH 0x5d8bdc
    ESP -= 4u; write32(ESP, address(application_core_address_005d8bdc()));
L_004d4a11: // 004d4a11 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4a15: // 004d4a15 e8864ef5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4a1a: // 004d4a1a 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4a20: // 004d4a20 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4a24: // 004d4a24 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4a26: // 004d4a26 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4a27: // 004d4a27 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4a29: // 004d4a29 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4a2b: // 004d4a2b e8c0130000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4a30: // 004d4a30 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4a34: // 004d4a34 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4a38: // 004d4a38 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4a3a: // 004d4a3a 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4a3c: // 004d4a3c 0f84c5070000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4a42: // 004d4a42 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4a44: // 004d4a44 0f84bd070000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4a4a: // 004d4a4a 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4a4b: // 004d4a4b 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4a4c: // 004d4a4c 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4a4d: // 004d4a4d e87eedf4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4a52: // 004d4a52 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4a55: // 004d4a55 e9ad070000 JMP 0x004d5207
    goto L_004d5207;
L_004d4a5a: // 004d4a5a 83f80b CMP EAX,0xb
    (void)alu_sub(EAX, 0x0000000bu, 32, state.flags);
L_004d4a5d: // 004d4a5d 0f85b7000000 JNZ 0x004d4b1a
    if(!state.flags.zero) goto L_004d4b1a;
L_004d4a63: // 004d4a63 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4a67: // 004d4a67 e8a4ebf4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4a6c: // 004d4a6c 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4a73: // 004d4a73 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4a76: // 004d4a76 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4a78: // 004d4a78 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4a7a: // 004d4a7a 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4a7d: // 004d4a7d 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4a7f: // 004d4a7f 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4a81: // 004d4a81 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4a84: // 004d4a84 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4a87: // 004d4a87 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4a89: // 004d4a89 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4a8b: // 004d4a8b 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4a8c: // 004d4a8c 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4a8e: // 004d4a8e 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4a8f: // 004d4a8f 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4a90: // 004d4a90 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4a92: // 004d4a92 e8094ef5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4a97: // 004d4a97 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4a9d: // 004d4a9d 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4a9e: // 004d4a9e e87d1a0000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4aa3: // 004d4aa3 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4aa5: // 004d4aa5 e836110000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4aaa: // 004d4aaa bf08945d00 MOV EDI,0x5d9408
    EDI = address(application_core_address_005d9408());
L_004d4aaf: // 004d4aaf 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4ab2: // 004d4ab2 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4ab4: // 004d4ab4 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4ab8: // 004d4ab8 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4aba: // 004d4aba f7d1 NOT ECX
    ECX = (~ECX);
L_004d4abc: // 004d4abc 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4abd: // 004d4abd 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4ac1: // 004d4ac1 81c108945d00 ADD ECX,0x5d9408
    ECX = alu_add(ECX, address(application_core_address_005d9408()), 32, state.flags);
L_004d4ac7: // 004d4ac7 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4acb: // 004d4acb 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4acc: // 004d4acc 6808945d00 PUSH 0x5d9408
    ESP -= 4u; write32(ESP, address(application_core_address_005d9408()));
L_004d4ad1: // 004d4ad1 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4ad5: // 004d4ad5 e8c64df5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4ada: // 004d4ada 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4ae0: // 004d4ae0 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4ae4: // 004d4ae4 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4ae6: // 004d4ae6 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4ae7: // 004d4ae7 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4ae9: // 004d4ae9 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4aeb: // 004d4aeb e800130000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4af0: // 004d4af0 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4af4: // 004d4af4 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4af8: // 004d4af8 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4afa: // 004d4afa 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4afc: // 004d4afc 0f8405070000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4b02: // 004d4b02 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4b04: // 004d4b04 0f84fd060000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4b0a: // 004d4b0a 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4b0b: // 004d4b0b 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4b0c: // 004d4b0c 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4b0d: // 004d4b0d e8beecf4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4b12: // 004d4b12 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4b15: // 004d4b15 e9ed060000 JMP 0x004d5207
    goto L_004d5207;
L_004d4b1a: // 004d4b1a 83f80a CMP EAX,0xa
    (void)alu_sub(EAX, 0x0000000au, 32, state.flags);
L_004d4b1d: // 004d4b1d 0f85b7000000 JNZ 0x004d4bda
    if(!state.flags.zero) goto L_004d4bda;
L_004d4b23: // 004d4b23 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4b27: // 004d4b27 e8e4eaf4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4b2c: // 004d4b2c 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4b33: // 004d4b33 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4b36: // 004d4b36 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4b38: // 004d4b38 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4b3a: // 004d4b3a 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4b3d: // 004d4b3d 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4b3f: // 004d4b3f 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4b41: // 004d4b41 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4b44: // 004d4b44 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4b47: // 004d4b47 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4b49: // 004d4b49 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4b4b: // 004d4b4b 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4b4c: // 004d4b4c 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4b4e: // 004d4b4e 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4b4f: // 004d4b4f 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4b50: // 004d4b50 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4b52: // 004d4b52 e8494df5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4b57: // 004d4b57 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4b5d: // 004d4b5d 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4b5e: // 004d4b5e e8bd190000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4b63: // 004d4b63 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4b65: // 004d4b65 e876100000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4b6a: // 004d4b6a bfdc8b5d00 MOV EDI,0x5d8bdc
    EDI = address(application_core_address_005d8bdc());
L_004d4b6f: // 004d4b6f 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4b72: // 004d4b72 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4b74: // 004d4b74 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4b78: // 004d4b78 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4b7a: // 004d4b7a f7d1 NOT ECX
    ECX = (~ECX);
L_004d4b7c: // 004d4b7c 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4b7d: // 004d4b7d 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4b81: // 004d4b81 81c1dc8b5d00 ADD ECX,0x5d8bdc
    ECX = alu_add(ECX, address(application_core_address_005d8bdc()), 32, state.flags);
L_004d4b87: // 004d4b87 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4b8b: // 004d4b8b 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4b8c: // 004d4b8c 68dc8b5d00 PUSH 0x5d8bdc
    ESP -= 4u; write32(ESP, address(application_core_address_005d8bdc()));
L_004d4b91: // 004d4b91 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4b95: // 004d4b95 e8064df5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4b9a: // 004d4b9a 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4ba0: // 004d4ba0 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4ba4: // 004d4ba4 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4ba6: // 004d4ba6 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4ba7: // 004d4ba7 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4ba9: // 004d4ba9 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4bab: // 004d4bab e840120000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4bb0: // 004d4bb0 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4bb4: // 004d4bb4 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4bb8: // 004d4bb8 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4bba: // 004d4bba 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4bbc: // 004d4bbc 0f8445060000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4bc2: // 004d4bc2 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4bc4: // 004d4bc4 0f843d060000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4bca: // 004d4bca 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4bcb: // 004d4bcb 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4bcc: // 004d4bcc 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4bcd: // 004d4bcd e8feebf4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4bd2: // 004d4bd2 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4bd5: // 004d4bd5 e92d060000 JMP 0x004d5207
    goto L_004d5207;
L_004d4bda: // 004d4bda 83f809 CMP EAX,0x9
    (void)alu_sub(EAX, 0x00000009u, 32, state.flags);
L_004d4bdd: // 004d4bdd 0f85bf020000 JNZ 0x004d4ea2
    if(!state.flags.zero) goto L_004d4ea2;
L_004d4be3: // 004d4be3 381d347e6500 CMP byte ptr [0x00657e34],BL
    (void)alu_sub(read8((address(application_core_address_00657e34()))), get_byte(EBX, 0), 8, state.flags);
L_004d4be9: // 004d4be9 0f84b7000000 JZ 0x004d4ca6
    if(state.flags.zero) goto L_004d4ca6;
L_004d4bef: // 004d4bef 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4bf3: // 004d4bf3 e818eaf4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4bf8: // 004d4bf8 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4bff: // 004d4bff 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4c02: // 004d4c02 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4c04: // 004d4c04 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4c06: // 004d4c06 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4c09: // 004d4c09 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4c0b: // 004d4c0b 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4c0d: // 004d4c0d 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4c10: // 004d4c10 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4c13: // 004d4c13 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4c15: // 004d4c15 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4c17: // 004d4c17 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4c18: // 004d4c18 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4c1a: // 004d4c1a 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4c1b: // 004d4c1b 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4c1c: // 004d4c1c 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4c1e: // 004d4c1e e87d4cf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4c23: // 004d4c23 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4c29: // 004d4c29 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4c2a: // 004d4c2a e8f1180000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4c2f: // 004d4c2f 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4c31: // 004d4c31 e8aa0f0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4c36: // 004d4c36 bf88935d00 MOV EDI,0x5d9388
    EDI = address(application_core_address_005d9388());
L_004d4c3b: // 004d4c3b 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4c3e: // 004d4c3e 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4c40: // 004d4c40 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4c44: // 004d4c44 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4c46: // 004d4c46 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4c48: // 004d4c48 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4c49: // 004d4c49 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4c4d: // 004d4c4d 81c188935d00 ADD ECX,0x5d9388
    ECX = alu_add(ECX, address(application_core_address_005d9388()), 32, state.flags);
L_004d4c53: // 004d4c53 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4c57: // 004d4c57 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4c58: // 004d4c58 6888935d00 PUSH 0x5d9388
    ESP -= 4u; write32(ESP, address(application_core_address_005d9388()));
L_004d4c5d: // 004d4c5d 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4c61: // 004d4c61 e83a4cf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4c66: // 004d4c66 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4c6c: // 004d4c6c 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4c70: // 004d4c70 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4c72: // 004d4c72 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4c73: // 004d4c73 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4c75: // 004d4c75 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4c77: // 004d4c77 e874110000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4c7c: // 004d4c7c 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4c80: // 004d4c80 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4c84: // 004d4c84 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4c86: // 004d4c86 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4c88: // 004d4c88 0f8479050000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4c8e: // 004d4c8e 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4c90: // 004d4c90 0f8471050000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4c96: // 004d4c96 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4c97: // 004d4c97 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4c98: // 004d4c98 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4c99: // 004d4c99 e832ebf4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4c9e: // 004d4c9e 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4ca1: // 004d4ca1 e961050000 JMP 0x004d5207
    goto L_004d5207;
L_004d4ca6: // 004d4ca6 e8e5620400 CALL 0x0051af90
    state.argument_stack = pointer(ESP); application_core_effect_0051af90(state); ESP += 0u;
L_004d4cab: // 004d4cab 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d4cad: // 004d4cad 0f84bf000000 JZ 0x004d4d72
    if(state.flags.zero) goto L_004d4d72;
L_004d4cb3: // 004d4cb3 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4cb7: // 004d4cb7 e854e9f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4cbc: // 004d4cbc 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4cc3: // 004d4cc3 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4cc6: // 004d4cc6 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4cc8: // 004d4cc8 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4cca: // 004d4cca 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4ccd: // 004d4ccd 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4ccf: // 004d4ccf 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4cd1: // 004d4cd1 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4cd4: // 004d4cd4 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4cd7: // 004d4cd7 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4cd9: // 004d4cd9 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4cdb: // 004d4cdb 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4cdc: // 004d4cdc 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4cde: // 004d4cde 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4cdf: // 004d4cdf 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4ce0: // 004d4ce0 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4ce2: // 004d4ce2 e8b94bf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4ce7: // 004d4ce7 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4ced: // 004d4ced 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4cee: // 004d4cee e82d180000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4cf3: // 004d4cf3 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4cf5: // 004d4cf5 e8e60e0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4cfa: // 004d4cfa e821630400 CALL 0x0051b020
    state.argument_stack = pointer(ESP); application_core_effect_0051b020(state); ESP += 0u;
L_004d4cff: // 004d4cff 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d4d01: // 004d4d01 754b JNZ 0x004d4d4e
    if(!state.flags.zero) goto L_004d4d4e;
L_004d4d03: // 004d4d03 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4d07: // 004d4d07 e804e9f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4d0c: // 004d4d0c 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4d0f: // 004d4d0f bf88935d00 MOV EDI,0x5d9388
    EDI = address(application_core_address_005d9388());
L_004d4d14: // 004d4d14 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4d16: // 004d4d16 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4d19: // 004d4d19 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4d1b: // 004d4d1b 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4d1d: // 004d4d1d 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4d20: // 004d4d20 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4d23: // 004d4d23 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4d25: // 004d4d25 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4d27: // 004d4d27 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4d28: // 004d4d28 81c188935d00 ADD ECX,0x5d9388
    ECX = alu_add(ECX, address(application_core_address_005d9388()), 32, state.flags);
L_004d4d2e: // 004d4d2e 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4d2f: // 004d4d2f 6888935d00 PUSH 0x5d9388
    ESP -= 4u; write32(ESP, address(application_core_address_005d9388()));
L_004d4d34: // 004d4d34 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4d36: // 004d4d36 e8654bf5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4d3b: // 004d4d3b 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4d41: // 004d4d41 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4d42: // 004d4d42 e8d9170000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4d47: // 004d4d47 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4d49: // 004d4d49 e8920e0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4d4e: // 004d4d4e 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4d50: // 004d4d50 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4d51: // 004d4d51 6878935d00 PUSH 0x5d9378
    ESP -= 4u; write32(ESP, address(application_core_address_005d9378()));
L_004d4d56: // 004d4d56 8bce MOV ECX,ESI
    ECX = ESI;
L_004d4d58: // 004d4d58 e8a3d3ffff CALL 0x004d2100
    state.argument_stack = pointer(ESP); application_core_effect_004d2100(state); ESP += 12u;
L_004d4d5d: // 004d4d5d 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4d5f: // 004d4d5f 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4d61: // 004d4d61 6868935d00 PUSH 0x5d9368
    ESP -= 4u; write32(ESP, address(application_core_address_005d9368()));
L_004d4d66: // 004d4d66 8bce MOV ECX,ESI
    ECX = ESI;
L_004d4d68: // 004d4d68 e893d3ffff CALL 0x004d2100
    state.argument_stack = pointer(ESP); application_core_effect_004d2100(state); ESP += 12u;
L_004d4d6d: // 004d4d6d e995040000 JMP 0x004d5207
    goto L_004d5207;
L_004d4d72: // 004d4d72 e8a9620400 CALL 0x0051b020
    state.argument_stack = pointer(ESP); application_core_effect_0051b020(state); ESP += 0u;
L_004d4d77: // 004d4d77 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d4d79: // 004d4d79 0f85b7000000 JNZ 0x004d4e36
    if(!state.flags.zero) goto L_004d4e36;
L_004d4d7f: // 004d4d7f 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4d83: // 004d4d83 e888e8f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4d88: // 004d4d88 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4d8f: // 004d4d8f 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4d92: // 004d4d92 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4d94: // 004d4d94 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4d96: // 004d4d96 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4d99: // 004d4d99 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4d9b: // 004d4d9b 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4d9d: // 004d4d9d 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4da0: // 004d4da0 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4da3: // 004d4da3 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4da5: // 004d4da5 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4da7: // 004d4da7 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4da8: // 004d4da8 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4daa: // 004d4daa 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4dab: // 004d4dab 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4dac: // 004d4dac 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4dae: // 004d4dae e8ed4af5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4db3: // 004d4db3 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4db9: // 004d4db9 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4dba: // 004d4dba e861170000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4dbf: // 004d4dbf 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4dc1: // 004d4dc1 e81a0e0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4dc6: // 004d4dc6 bf88935d00 MOV EDI,0x5d9388
    EDI = address(application_core_address_005d9388());
L_004d4dcb: // 004d4dcb 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4dce: // 004d4dce 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4dd0: // 004d4dd0 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4dd4: // 004d4dd4 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4dd6: // 004d4dd6 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4dd8: // 004d4dd8 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4dd9: // 004d4dd9 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4ddd: // 004d4ddd 81c188935d00 ADD ECX,0x5d9388
    ECX = alu_add(ECX, address(application_core_address_005d9388()), 32, state.flags);
L_004d4de3: // 004d4de3 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4de7: // 004d4de7 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4de8: // 004d4de8 6888935d00 PUSH 0x5d9388
    ESP -= 4u; write32(ESP, address(application_core_address_005d9388()));
L_004d4ded: // 004d4ded 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4df1: // 004d4df1 e8aa4af5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4df6: // 004d4df6 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4dfc: // 004d4dfc 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4e00: // 004d4e00 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4e02: // 004d4e02 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4e03: // 004d4e03 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4e05: // 004d4e05 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4e07: // 004d4e07 e8e40f0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4e0c: // 004d4e0c 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4e10: // 004d4e10 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4e14: // 004d4e14 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4e16: // 004d4e16 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4e18: // 004d4e18 0f84e9030000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4e1e: // 004d4e1e 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4e20: // 004d4e20 0f84e1030000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4e26: // 004d4e26 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4e27: // 004d4e27 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4e28: // 004d4e28 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4e29: // 004d4e29 e8a2e9f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4e2e: // 004d4e2e 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4e31: // 004d4e31 e9d1030000 JMP 0x004d5207
    goto L_004d5207;
L_004d4e36: // 004d4e36 8b9424a4000000 MOV EDX,dword ptr [ESP + 0xa4]
    EDX = read32((ESP + 0x000000a4u));
L_004d4e3d: // 004d4e3d 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4e40: // 004d4e40 8bfa MOV EDI,EDX
    EDI = EDX;
L_004d4e42: // 004d4e42 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4e44: // 004d4e44 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4e46: // 004d4e46 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4e48: // 004d4e48 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4e49: // 004d4e49 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4e4d: // 004d4e4d 03ca ADD ECX,EDX
    ECX = alu_add(ECX, EDX, 32, state.flags);
L_004d4e4f: // 004d4e4f 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4e53: // 004d4e53 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4e54: // 004d4e54 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d4e55: // 004d4e55 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4e59: // 004d4e59 895c2424 MOV dword ptr [ESP + 0x24],EBX
    write32((ESP + 0x00000024u), EBX);
L_004d4e5d: // 004d4e5d e83e4af5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4e62: // 004d4e62 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4e68: // 004d4e68 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4e6c: // 004d4e6c 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4e6e: // 004d4e6e 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4e6f: // 004d4e6f 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4e71: // 004d4e71 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4e73: // 004d4e73 e8780f0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4e78: // 004d4e78 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4e7c: // 004d4e7c 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4e80: // 004d4e80 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4e82: // 004d4e82 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4e84: // 004d4e84 0f847d030000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4e8a: // 004d4e8a 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4e8c: // 004d4e8c 0f8475030000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4e92: // 004d4e92 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4e93: // 004d4e93 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4e94: // 004d4e94 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4e95: // 004d4e95 e836e9f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4e9a: // 004d4e9a 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4e9d: // 004d4e9d e965030000 JMP 0x004d5207
    goto L_004d5207;
L_004d4ea2: // 004d4ea2 385c2413 CMP byte ptr [ESP + 0x13],BL
    (void)alu_sub(read8((ESP + 0x00000013u)), get_byte(EBX, 0), 8, state.flags);
L_004d4ea6: // 004d4ea6 0f84b7000000 JZ 0x004d4f63
    if(state.flags.zero) goto L_004d4f63;
L_004d4eac: // 004d4eac 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4eb0: // 004d4eb0 e85be7f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4eb5: // 004d4eb5 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4ebc: // 004d4ebc 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4ebf: // 004d4ebf 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4ec1: // 004d4ec1 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4ec3: // 004d4ec3 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4ec6: // 004d4ec6 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4ec8: // 004d4ec8 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4eca: // 004d4eca 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4ecd: // 004d4ecd 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4ed0: // 004d4ed0 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4ed2: // 004d4ed2 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4ed4: // 004d4ed4 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4ed5: // 004d4ed5 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4ed7: // 004d4ed7 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4ed8: // 004d4ed8 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4ed9: // 004d4ed9 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4edb: // 004d4edb e8c049f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4ee0: // 004d4ee0 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4ee6: // 004d4ee6 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4ee7: // 004d4ee7 e834160000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4eec: // 004d4eec 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4eee: // 004d4eee e8ed0c0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4ef3: // 004d4ef3 bf54935d00 MOV EDI,0x5d9354
    EDI = address(application_core_address_005d9354());
L_004d4ef8: // 004d4ef8 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4efb: // 004d4efb 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4efd: // 004d4efd 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4f01: // 004d4f01 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4f03: // 004d4f03 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4f05: // 004d4f05 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4f06: // 004d4f06 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4f0a: // 004d4f0a 81c154935d00 ADD ECX,0x5d9354
    ECX = alu_add(ECX, address(application_core_address_005d9354()), 32, state.flags);
L_004d4f10: // 004d4f10 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4f14: // 004d4f14 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4f15: // 004d4f15 6854935d00 PUSH 0x5d9354
    ESP -= 4u; write32(ESP, address(application_core_address_005d9354()));
L_004d4f1a: // 004d4f1a 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4f1e: // 004d4f1e e87d49f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4f23: // 004d4f23 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4f29: // 004d4f29 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4f2d: // 004d4f2d 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4f2f: // 004d4f2f 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4f30: // 004d4f30 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4f32: // 004d4f32 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4f34: // 004d4f34 e8b70e0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4f39: // 004d4f39 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4f3d: // 004d4f3d 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d4f41: // 004d4f41 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d4f43: // 004d4f43 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d4f45: // 004d4f45 0f84bc020000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4f4b: // 004d4f4b 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4f4d: // 004d4f4d 0f84b4020000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d4f53: // 004d4f53 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4f54: // 004d4f54 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4f55: // 004d4f55 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4f56: // 004d4f56 e875e8f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d4f5b: // 004d4f5b 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d4f5e: // 004d4f5e e9a4020000 JMP 0x004d5207
    goto L_004d5207;
L_004d4f63: // 004d4f63 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d4f65: // 004d4f65 0f85b7000000 JNZ 0x004d5022
    if(!state.flags.zero) goto L_004d5022;
L_004d4f6b: // 004d4f6b 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d4f6f: // 004d4f6f e89ce6f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d4f74: // 004d4f74 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d4f7b: // 004d4f7b 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d4f7e: // 004d4f7e 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d4f80: // 004d4f80 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d4f82: // 004d4f82 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4f85: // 004d4f85 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4f87: // 004d4f87 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d4f89: // 004d4f89 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d4f8c: // 004d4f8c 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d4f8f: // 004d4f8f f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4f91: // 004d4f91 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4f93: // 004d4f93 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4f94: // 004d4f94 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d4f96: // 004d4f96 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4f97: // 004d4f97 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d4f98: // 004d4f98 8bca MOV ECX,EDX
    ECX = EDX;
L_004d4f9a: // 004d4f9a e80149f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4f9f: // 004d4f9f 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4fa5: // 004d4fa5 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d4fa6: // 004d4fa6 e875150000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d4fab: // 004d4fab 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d4fad: // 004d4fad e82e0c0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d4fb2: // 004d4fb2 bf48935d00 MOV EDI,0x5d9348
    EDI = address(application_core_address_005d9348());
L_004d4fb7: // 004d4fb7 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d4fba: // 004d4fba 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d4fbc: // 004d4fbc 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d4fc0: // 004d4fc0 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d4fc2: // 004d4fc2 f7d1 NOT ECX
    ECX = (~ECX);
L_004d4fc4: // 004d4fc4 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d4fc5: // 004d4fc5 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d4fc9: // 004d4fc9 81c148935d00 ADD ECX,0x5d9348
    ECX = alu_add(ECX, address(application_core_address_005d9348()), 32, state.flags);
L_004d4fcf: // 004d4fcf 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d4fd3: // 004d4fd3 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d4fd4: // 004d4fd4 6848935d00 PUSH 0x5d9348
    ESP -= 4u; write32(ESP, address(application_core_address_005d9348()));
L_004d4fd9: // 004d4fd9 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d4fdd: // 004d4fdd e8be48f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d4fe2: // 004d4fe2 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d4fe8: // 004d4fe8 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d4fec: // 004d4fec 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d4fee: // 004d4fee 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d4fef: // 004d4fef 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d4ff1: // 004d4ff1 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d4ff3: // 004d4ff3 e8f80d0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d4ff8: // 004d4ff8 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d4ffc: // 004d4ffc 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d5000: // 004d5000 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d5002: // 004d5002 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d5004: // 004d5004 0f84fd010000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d500a: // 004d500a 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d500c: // 004d500c 0f84f5010000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d5012: // 004d5012 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d5013: // 004d5013 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d5014: // 004d5014 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d5015: // 004d5015 e8b6e7f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d501a: // 004d501a 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d501d: // 004d501d e9e5010000 JMP 0x004d5207
    goto L_004d5207;
L_004d5022: // 004d5022 83f801 CMP EAX,0x1
    (void)alu_sub(EAX, 0x00000001u, 32, state.flags);
L_004d5025: // 004d5025 0f85b7000000 JNZ 0x004d50e2
    if(!state.flags.zero) goto L_004d50e2;
L_004d502b: // 004d502b 8d4c2412 LEA ECX,[ESP + 0x12]
    ECX = (ESP + 0x00000012u);
L_004d502f: // 004d502f e8dce5f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d5034: // 004d5034 8bac24a4000000 MOV EBP,dword ptr [ESP + 0xa4]
    EBP = read32((ESP + 0x000000a4u));
L_004d503b: // 004d503b 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d503e: // 004d503e 8bd4 MOV EDX,ESP
    EDX = ESP;
L_004d5040: // 004d5040 8bfd MOV EDI,EBP
    EDI = EBP;
L_004d5042: // 004d5042 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d5045: // 004d5045 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d5047: // 004d5047 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d5049: // 004d5049 895a04 MOV dword ptr [EDX + 0x4],EBX
    write32((EDX + 0x00000004u), EBX);
L_004d504c: // 004d504c 895a08 MOV dword ptr [EDX + 0x8],EBX
    write32((EDX + 0x00000008u), EBX);
L_004d504f: // 004d504f f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d5051: // 004d5051 f7d1 NOT ECX
    ECX = (~ECX);
L_004d5053: // 004d5053 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d5054: // 004d5054 03cd ADD ECX,EBP
    ECX = alu_add(ECX, EBP, 32, state.flags);
L_004d5056: // 004d5056 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d5057: // 004d5057 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5058: // 004d5058 8bca MOV ECX,EDX
    ECX = EDX;
L_004d505a: // 004d505a e84148f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d505f: // 004d505f 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d5065: // 004d5065 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d5066: // 004d5066 e8b5140000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d506b: // 004d506b 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d506d: // 004d506d e86e0b0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d5072: // 004d5072 bf38935d00 MOV EDI,0x5d9338
    EDI = address(application_core_address_005d9338());
L_004d5077: // 004d5077 83c9ff OR ECX,0xffffffff
    ECX = alu_or(0u, 0xffffffffu, 32, state.flags);
L_004d507a: // 004d507a 33c0 XOR EAX,EAX
    EAX = alu_xor(0u, 0u, 32, state.flags);
L_004d507c: // 004d507c 895c2414 MOV dword ptr [ESP + 0x14],EBX
    write32((ESP + 0x00000014u), EBX);
L_004d5080: // 004d5080 f2ae SCASB.REPNE ES:EDI
    scan_zero(EDI, ECX, EAX & 255u, state.flags);
L_004d5082: // 004d5082 f7d1 NOT ECX
    ECX = (~ECX);
L_004d5084: // 004d5084 49 DEC ECX
    ECX = alu_dec(ECX, 32, state.flags);
L_004d5085: // 004d5085 895c2418 MOV dword ptr [ESP + 0x18],EBX
    write32((ESP + 0x00000018u), EBX);
L_004d5089: // 004d5089 81c138935d00 ADD ECX,0x5d9338
    ECX = alu_add(ECX, address(application_core_address_005d9338()), 32, state.flags);
L_004d508f: // 004d508f 895c241c MOV dword ptr [ESP + 0x1c],EBX
    write32((ESP + 0x0000001cu), EBX);
L_004d5093: // 004d5093 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d5094: // 004d5094 6838935d00 PUSH 0x5d9338
    ESP -= 4u; write32(ESP, address(application_core_address_005d9338()));
L_004d5099: // 004d5099 8d4c241c LEA ECX,[ESP + 0x1c]
    ECX = (ESP + 0x0000001cu);
L_004d509d: // 004d509d e8fe47f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d50a2: // 004d50a2 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d50a8: // 004d50a8 8d442414 LEA EAX,[ESP + 0x14]
    EAX = (ESP + 0x00000014u);
L_004d50ac: // 004d50ac 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d50ae: // 004d50ae 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d50af: // 004d50af 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d50b1: // 004d50b1 8b0a MOV ECX,dword ptr [EDX]
    ECX = read32((EDX));
L_004d50b3: // 004d50b3 e8380d0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d50b8: // 004d50b8 8b44241c MOV EAX,dword ptr [ESP + 0x1c]
    EAX = read32((ESP + 0x0000001cu));
L_004d50bc: // 004d50bc 8b4c2414 MOV ECX,dword ptr [ESP + 0x14]
    ECX = read32((ESP + 0x00000014u));
L_004d50c0: // 004d50c0 2bc1 SUB EAX,ECX
    EAX = alu_sub(EAX, ECX, 32, state.flags);
L_004d50c2: // 004d50c2 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d50c4: // 004d50c4 0f843d010000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d50ca: // 004d50ca 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d50cc: // 004d50cc 0f8435010000 JZ 0x004d5207
    if(state.flags.zero) goto L_004d5207;
L_004d50d2: // 004d50d2 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d50d3: // 004d50d3 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d50d4: // 004d50d4 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d50d5: // 004d50d5 e8f6e6f4ff CALL 0x004237d0
    state.argument_stack = pointer(ESP); application_core_effect_004237d0(state); ESP += 0u;
L_004d50da: // 004d50da 83c40c ADD ESP,0xc
    ESP = alu_add(ESP, 0x0000000cu, 32, state.flags);
L_004d50dd: // 004d50dd e925010000 JMP 0x004d5207
    goto L_004d5207;
L_004d50e2: // 004d50e2 83f802 CMP EAX,0x2
    (void)alu_sub(EAX, 0x00000002u, 32, state.flags);
L_004d50e5: // 004d50e5 0f8591000000 JNZ 0x004d517c
    if(!state.flags.zero) goto L_004d517c;
L_004d50eb: // 004d50eb 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d50ef: // 004d50ef e81ce5f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d50f4: // 004d50f4 83ec0c SUB ESP,0xc
    ESP = alu_sub(ESP, 0x0000000cu, 32, state.flags);
L_004d50f7: // 004d50f7 8bfc MOV EDI,ESP
    EDI = ESP;
L_004d50f9: // 004d50f9 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d50fa: // 004d50fa 8bcf MOV ECX,EDI
    ECX = EDI;
L_004d50fc: // 004d50fc e80f070300 CALL 0x00505810
    state.argument_stack = pointer(ESP); application_core_effect_00505810(state); ESP += 4u;
L_004d5101: // 004d5101 8bac24b0000000 MOV EBP,dword ptr [ESP + 0xb0]
    EBP = read32((ESP + 0x000000b0u));
L_004d5108: // 004d5108 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5109: // 004d5109 e8b2040000 CALL 0x004d55c0
    state.argument_stack = pointer(ESP); application_core_effect_004d55c0(state); ESP += 0u;
L_004d510e: // 004d510e 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d5111: // 004d5111 03c5 ADD EAX,EBP
    EAX = alu_add(EAX, EBP, 32, state.flags);
L_004d5113: // 004d5113 8bcf MOV ECX,EDI
    ECX = EDI;
L_004d5115: // 004d5115 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d5116: // 004d5116 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5117: // 004d5117 e88447f5ff CALL 0x004298a0
    state.argument_stack = pointer(ESP); application_core_effect_004298a0(state); ESP += 8u;
L_004d511c: // 004d511c 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d5122: // 004d5122 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d5123: // 004d5123 e8f8130000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d5128: // 004d5128 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d512a: // 004d512a e8b10a0000 CALL 0x004d5be0
    state.argument_stack = pointer(ESP); application_core_effect_004d5be0(state); ESP += 12u;
L_004d512f: // 004d512f 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d5133: // 004d5133 e858f80300 CALL 0x00514990
    state.argument_stack = pointer(ESP); application_core_effect_00514990(state); ESP += 0u;
L_004d5138: // 004d5138 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d513c: // 004d513c e8cfe4f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d5141: // 004d5141 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d5142: // 004d5142 682c935d00 PUSH 0x5d932c
    ESP -= 4u; write32(ESP, address(application_core_address_005d932c()));
L_004d5147: // 004d5147 8d4c243c LEA ECX,[ESP + 0x3c]
    ECX = (ESP + 0x0000003cu);
L_004d514b: // 004d514b e850130000 CALL 0x004d64a0
    state.argument_stack = pointer(ESP); application_core_effect_004d64a0(state); ESP += 8u;
L_004d5150: // 004d5150 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d5156: // 004d5156 8d442434 LEA EAX,[ESP + 0x34]
    EAX = (ESP + 0x00000034u);
L_004d515a: // 004d515a 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d515c: // 004d515c 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d515d: // 004d515d 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d515e: // 004d515e e8bd130000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d5163: // 004d5163 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d5165: // 004d5165 e8860c0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d516a: // 004d516a 8d4c2434 LEA ECX,[ESP + 0x34]
    ECX = (ESP + 0x00000034u);
L_004d516e: // 004d516e e8cd46f5ff CALL 0x00429840
    state.argument_stack = pointer(ESP); application_core_effect_00429840(state); ESP += 0u;
L_004d5173: // 004d5173 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d5177: // 004d5177 e986000000 JMP 0x004d5202
    goto L_004d5202;
L_004d517c: // 004d517c 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d5180: // 004d5180 e88be4f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d5185: // 004d5185 8b8c24a4000000 MOV ECX,dword ptr [ESP + 0xa4]
    ECX = read32((ESP + 0x000000a4u));
L_004d518c: // 004d518c 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d518d: // 004d518d 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d518e: // 004d518e 8d4c243c LEA ECX,[ESP + 0x3c]
    ECX = (ESP + 0x0000003cu);
L_004d5192: // 004d5192 e809130000 CALL 0x004d64a0
    state.argument_stack = pointer(ESP); application_core_effect_004d64a0(state); ESP += 8u;
L_004d5197: // 004d5197 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d519d: // 004d519d 8d542434 LEA EDX,[ESP + 0x34]
    EDX = (ESP + 0x00000034u);
L_004d51a1: // 004d51a1 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d51a3: // 004d51a3 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d51a4: // 004d51a4 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d51a5: // 004d51a5 e876130000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d51aa: // 004d51aa 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d51ac: // 004d51ac e83f0c0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d51b1: // 004d51b1 8d4c2434 LEA ECX,[ESP + 0x34]
    ECX = (ESP + 0x00000034u);
L_004d51b5: // 004d51b5 e88646f5ff CALL 0x00429840
    state.argument_stack = pointer(ESP); application_core_effect_00429840(state); ESP += 0u;
L_004d51ba: // 004d51ba 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d51be: // 004d51be eb42 JMP 0x004d5202
    goto L_004d5202;
L_004d51c0: // 004d51c0 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d51c4: // 004d51c4 e847e4f4ff CALL 0x00423610
    state.argument_stack = pointer(ESP); application_core_effect_00423610(state); ESP += 0u;
L_004d51c9: // 004d51c9 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d51ca: // 004d51ca 8b8424a8000000 MOV EAX,dword ptr [ESP + 0xa8]
    EAX = read32((ESP + 0x000000a8u));
L_004d51d1: // 004d51d1 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d51d2: // 004d51d2 8d4c243c LEA ECX,[ESP + 0x3c]
    ECX = (ESP + 0x0000003cu);
L_004d51d6: // 004d51d6 e8c5120000 CALL 0x004d64a0
    state.argument_stack = pointer(ESP); application_core_effect_004d64a0(state); ESP += 8u;
L_004d51db: // 004d51db 8d4c2434 LEA ECX,[ESP + 0x34]
    ECX = (ESP + 0x00000034u);
L_004d51df: // 004d51df 6a01 PUSH 0x1
    ESP -= 4u; write32(ESP, 0x00000001u);
L_004d51e1: // 004d51e1 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d51e2: // 004d51e2 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d51e8: // 004d51e8 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d51e9: // 004d51e9 e832130000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d51ee: // 004d51ee 8b08 MOV ECX,dword ptr [EAX]
    ECX = read32((EAX));
L_004d51f0: // 004d51f0 e8fb0b0000 CALL 0x004d5df0
    state.argument_stack = pointer(ESP); application_core_effect_004d5df0(state); ESP += 8u;
L_004d51f5: // 004d51f5 8d4c2434 LEA ECX,[ESP + 0x34]
    ECX = (ESP + 0x00000034u);
L_004d51f9: // 004d51f9 e84246f5ff CALL 0x00429840
    state.argument_stack = pointer(ESP); application_core_effect_00429840(state); ESP += 0u;
L_004d51fe: // 004d51fe 8d4c2413 LEA ECX,[ESP + 0x13]
    ECX = (ESP + 0x00000013u);
L_004d5202: // 004d5202 e889f70300 CALL 0x00514990
    state.argument_stack = pointer(ESP); application_core_effect_00514990(state); ESP += 0u;
L_004d5207: // 004d5207 8bce MOV ECX,ESI
    ECX = ESI;
L_004d5209: // 004d5209 e8c2c9ffff CALL 0x004d1bd0
    state.argument_stack = pointer(ESP); application_core_effect_004d1bd0(state); ESP += 0u;
L_004d520e: // 004d520e 8bce MOV ECX,ESI
    ECX = ESI;
L_004d5210: // 004d5210 e81b0f0000 CALL 0x004d6130
    state.argument_stack = pointer(ESP); application_core_effect_004d6130(state); ESP += 0u;
L_004d5215: // 004d5215 385c2423 CMP byte ptr [ESP + 0x23],BL
    (void)alu_sub(read8((ESP + 0x00000023u)), get_byte(EBX, 0), 8, state.flags);
L_004d5219: // 004d5219 740a JZ 0x004d5225
    if(state.flags.zero) goto L_004d5225;
L_004d521b: // 004d521b 6a09 PUSH 0x9
    ESP -= 4u; write32(ESP, 0x00000009u);
L_004d521d: // 004d521d e8de870000 CALL 0x004dda00
    state.argument_stack = pointer(ESP); application_core_effect_004dda00(state); ESP += 0u;
L_004d5222: // 004d5222 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d5225: // 004d5225 bd01000000 MOV EBP,0x1
    EBP = 0x00000001u;
L_004d522a: // 004d522a 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d522b: // 004d522b e860acf7ff CALL 0x0044fe90
    state.argument_stack = pointer(ESP); application_core_effect_0044fe90(state); ESP += 0u;
L_004d5230: // 004d5230 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d5232: // 004d5232 e86981f8ff CALL 0x0045d3a0
    state.argument_stack = pointer(ESP); application_core_effect_0045d3a0(state); ESP += 0u;
L_004d5237: // 004d5237 8b4804 MOV ECX,dword ptr [EAX + 0x4]
    ECX = read32((EAX + 0x00000004u));
L_004d523a: // 004d523a e811260600 CALL 0x00537850
    state.argument_stack = pointer(ESP); application_core_effect_00537850(state); ESP += 4u;
L_004d523f: // 004d523f 6a03 PUSH 0x3
    ESP -= 4u; write32(ESP, 0x00000003u);
L_004d5241: // 004d5241 e84aacf7ff CALL 0x0044fe90
    state.argument_stack = pointer(ESP); application_core_effect_0044fe90(state); ESP += 0u;
L_004d5246: // 004d5246 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d5248: // 004d5248 e85381f8ff CALL 0x0045d3a0
    state.argument_stack = pointer(ESP); application_core_effect_0045d3a0(state); ESP += 0u;
L_004d524d: // 004d524d 8b4804 MOV ECX,dword ptr [EAX + 0x4]
    ECX = read32((EAX + 0x00000004u));
L_004d5250: // 004d5250 e8db250600 CALL 0x00537830
    state.argument_stack = pointer(ESP); application_core_effect_00537830(state); ESP += 4u;
L_004d5255: // 004d5255 39ae78010000 CMP dword ptr [ESI + 0x178],EBP
    (void)alu_sub(read32((ESI + 0x00000178u)), EBP, 32, state.flags);
L_004d525b: // 004d525b 7505 JNZ 0x004d5262
    if(!state.flags.zero) goto L_004d5262;
L_004d525d: // 004d525d e8ee8bf7ff CALL 0x0044de50
    state.argument_stack = pointer(ESP); application_core_effect_0044de50(state); ESP += 0u;
L_004d5262: // 004d5262 e8c9ad0800 CALL 0x00560030
    state.argument_stack = pointer(ESP); application_core_effect_00560030(state); ESP += 0u;
L_004d5267: // 004d5267 e804030300 CALL 0x00505570
    state.argument_stack = pointer(ESP); application_core_effect_00505570(state); ESP += 0u;
L_004d526c: // 004d526c 8bce MOV ECX,ESI
    ECX = ESI;
L_004d526e: // 004d526e e8bd0e0000 CALL 0x004d6130
    state.argument_stack = pointer(ESP); application_core_effect_004d6130(state); ESP += 0u;
L_004d5273: // 004d5273 8d960c010000 LEA EDX,[ESI + 0x10c]
    EDX = (ESI + 0x0000010cu);
L_004d5279: // 004d5279 68508e5e00 PUSH 0x5e8e50
    ESP -= 4u; write32(ESP, address(application_core_address_005e8e50()));
L_004d527e: // 004d527e 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d527f: // 004d527f e83bbd0c00 CALL 0x005a0fbf
    state.argument_stack = pointer(ESP); application_core_effect_005a0fbf(state); ESP += 0u;
L_004d5284: // 004d5284 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d5287: // 004d5287 8bce MOV ECX,ESI
    ECX = ESI;
L_004d5289: // 004d5289 e842c9ffff CALL 0x004d1bd0
    state.argument_stack = pointer(ESP); application_core_effect_004d1bd0(state); ESP += 0u;
L_004d528e: // 004d528e 8bce MOV ECX,ESI
    ECX = ESI;
L_004d5290: // 004d5290 e84bdbffff CALL 0x004d2de0
    state.argument_stack = pointer(ESP); application_core_effect_004d2de0(state); ESP += 0u;
L_004d5295: // 004d5295 68dc050000 PUSH 0x5dc
    ESP -= 4u; write32(ESP, 0x000005dcu);
L_004d529a: // 004d529a e82191fdff CALL 0x004ae3c0
    state.argument_stack = pointer(ESP); application_core_effect_004ae3c0(state); ESP += 0u;
L_004d529f: // 004d529f 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d52a2: // 004d52a2 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d52a3: // 004d52a3 68e0705d00 PUSH 0x5d70e0
    ESP -= 4u; write32(ESP, address(application_core_address_005d70e0()));
L_004d52a8: // 004d52a8 68a8d65c00 PUSH 0x5cd6a8
    ESP -= 4u; write32(ESP, address(application_core_address_005cd6a8()));
L_004d52ad: // 004d52ad 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d52ae: // 004d52ae 6898d65c00 PUSH 0x5cd698
    ESP -= 4u; write32(ESP, address(application_core_address_005cd698()));
L_004d52b3: // 004d52b3 e8f827feff CALL 0x004b7ab0
    state.argument_stack = pointer(ESP); application_core_effect_004b7ab0(state); ESP += 0u;
L_004d52b8: // 004d52b8 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d52bb: // 004d52bb 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d52bc: // 004d52bc e88ac00c00 CALL 0x005a134b
    state.argument_stack = pointer(ESP); application_core_effect_005a134b(state); ESP += 0u;
L_004d52c1: // 004d52c1 8b10 MOV EDX,dword ptr [EAX]
    EDX = read32((EAX));
L_004d52c3: // 004d52c3 83c414 ADD ESP,0x14
    ESP = alu_add(ESP, 0x00000014u, 32, state.flags);
L_004d52c6: // 004d52c6 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d52c8: // 004d52c8 ff5228 CALL dword ptr [EDX + 0x28]
    state.argument_stack = pointer(ESP); application_core_virtual_004d52c8(state, read32((EDX + 0x00000028u))); ESP += 0u;
L_004d52cb: // 004d52cb 83f802 CMP EAX,0x2
    (void)alu_sub(EAX, 0x00000002u, 32, state.flags);
L_004d52ce: // 004d52ce 750e JNZ 0x004d52de
    if(!state.flags.zero) goto L_004d52de;
L_004d52d0: // 004d52d0 e82b8c0000 CALL 0x004ddf00
    state.argument_stack = pointer(ESP); application_core_effect_004ddf00(state); ESP += 0u;
L_004d52d5: // 004d52d5 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d52d7: // 004d52d7 7505 JNZ 0x004d52de
    if(!state.flags.zero) goto L_004d52de;
L_004d52d9: // 004d52d9 e8528c0000 CALL 0x004ddf30
    state.argument_stack = pointer(ESP); application_core_effect_004ddf30(state); ESP += 0u;
L_004d52de: // 004d52de e8fdd10200 CALL 0x005024e0
    state.argument_stack = pointer(ESP); application_core_effect_005024e0(state); ESP += 0u;
L_004d52e3: // 004d52e3 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d52e4: // 004d52e4 e887bf0200 CALL 0x00501270
    state.argument_stack = pointer(ESP); application_core_effect_00501270(state); ESP += 0u;
L_004d52e9: // 004d52e9 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d52ea: // 004d52ea e8b19a0000 CALL 0x004deda0
    state.argument_stack = pointer(ESP); application_core_effect_004deda0(state); ESP += 0u;
L_004d52ef: // 004d52ef 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d52f2: // 004d52f2 e879c90000 CALL 0x004e1c70
    state.argument_stack = pointer(ESP); application_core_effect_004e1c70(state); ESP += 0u;
L_004d52f7: // 004d52f7 8b8ee4000000 MOV ECX,dword ptr [ESI + 0xe4]
    ECX = read32((ESI + 0x000000e4u));
L_004d52fd: // 004d52fd 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d52ff: // 004d52ff 740b JZ 0x004d530c
    if(state.flags.zero) goto L_004d530c;
L_004d5301: // 004d5301 8b01 MOV EAX,dword ptr [ECX]
    EAX = read32((ECX));
L_004d5303: // 004d5303 ff5070 CALL dword ptr [EAX + 0x70]
    state.argument_stack = pointer(ESP); application_core_virtual_004d5303(state, read32((EAX + 0x00000070u))); ESP += 0u;
L_004d5306: // 004d5306 899ee4000000 MOV dword ptr [ESI + 0xe4],EBX
    write32((ESI + 0x000000e4u), EBX);
L_004d530c: // 004d530c 8b8ee8000000 MOV ECX,dword ptr [ESI + 0xe8]
    ECX = read32((ESI + 0x000000e8u));
L_004d5312: // 004d5312 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d5314: // 004d5314 740b JZ 0x004d5321
    if(state.flags.zero) goto L_004d5321;
L_004d5316: // 004d5316 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d5318: // 004d5318 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5319: // 004d5319 ff12 CALL dword ptr [EDX]
    state.argument_stack = pointer(ESP); application_core_virtual_004d5319(state, read32((EDX))); ESP += 4u;
L_004d531b: // 004d531b 899ee8000000 MOV dword ptr [ESI + 0xe8],EBX
    write32((ESI + 0x000000e8u), EBX);
L_004d5321: // 004d5321 8b8ee0000000 MOV ECX,dword ptr [ESI + 0xe0]
    ECX = read32((ESI + 0x000000e0u));
L_004d5327: // 004d5327 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d5329: // 004d5329 740b JZ 0x004d5336
    if(state.flags.zero) goto L_004d5336;
L_004d532b: // 004d532b 8b01 MOV EAX,dword ptr [ECX]
    EAX = read32((ECX));
L_004d532d: // 004d532d 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d532e: // 004d532e ff10 CALL dword ptr [EAX]
    state.argument_stack = pointer(ESP); application_core_virtual_004d532e(state, read32((EAX))); ESP += 4u;
L_004d5330: // 004d5330 899ee0000000 MOV dword ptr [ESI + 0xe0],EBX
    write32((ESI + 0x000000e0u), EBX);
L_004d5336: // 004d5336 8b8edc000000 MOV ECX,dword ptr [ESI + 0xdc]
    ECX = read32((ESI + 0x000000dcu));
L_004d533c: // 004d533c 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d533e: // 004d533e 7405 JZ 0x004d5345
    if(state.flags.zero) goto L_004d5345;
L_004d5340: // 004d5340 8b11 MOV EDX,dword ptr [ECX]
    EDX = read32((ECX));
L_004d5342: // 004d5342 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5343: // 004d5343 ff12 CALL dword ptr [EDX]
    state.argument_stack = pointer(ESP); application_core_virtual_004d5343(state, read32((EDX))); ESP += 4u;
L_004d5345: // 004d5345 8bbc24a8000000 MOV EDI,dword ptr [ESP + 0xa8]
    EDI = read32((ESP + 0x000000a8u));
L_004d534c: // 004d534c 3bfb CMP EDI,EBX
    (void)alu_sub(EDI, EBX, 32, state.flags);
L_004d534e: // 004d534e 0f841f010000 JZ 0x004d5473
    if(state.flags.zero) goto L_004d5473;
L_004d5354: // 004d5354 8b4c2448 MOV ECX,dword ptr [ESP + 0x48]
    ECX = read32((ESP + 0x00000048u));
L_004d5358: // 004d5358 8d442424 LEA EAX,[ESP + 0x24]
    EAX = (ESP + 0x00000024u);
L_004d535c: // 004d535c 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d535d: // 004d535d 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d535e: // 004d535e 896c242c MOV dword ptr [ESP + 0x2c],EBP
    write32((ESP + 0x0000002cu), EBP);
L_004d5362: // 004d5362 e849140000 CALL 0x004d67b0
    state.argument_stack = pointer(ESP); application_core_effect_004d67b0(state); ESP += 0u;
L_004d5367: // 004d5367 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d536a: // 004d536a 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d536c: // 004d536c 0f8401010000 JZ 0x004d5473
    if(state.flags.zero) goto L_004d5473;
L_004d5372: // 004d5372 e8a96d0300 CALL 0x0050c120
    state.argument_stack = pointer(ESP); application_core_effect_0050c120(state); ESP += 0u;
L_004d5377: // 004d5377 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d5379: // 004d5379 0f84ab000000 JZ 0x004d542a
    if(state.flags.zero) goto L_004d542a;
L_004d537f: // 004d537f 6800200000 PUSH 0x2000
    ESP -= 4u; write32(ESP, 0x00002000u);
L_004d5384: // 004d5384 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d5385: // 004d5385 e8b6420900 CALL 0x00569640
    state.argument_stack = pointer(ESP); application_core_effect_00569640(state); ESP += 0u;
L_004d538a: // 004d538a 8d54242c LEA EDX,[ESP + 0x2c]
    EDX = (ESP + 0x0000002cu);
L_004d538e: // 004d538e 897c242c MOV dword ptr [ESP + 0x2c],EDI
    write32((ESP + 0x0000002cu), EDI);
L_004d5392: // 004d5392 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d5393: // 004d5393 e8b826feff CALL 0x004b7a50
    state.argument_stack = pointer(ESP); application_core_effect_004b7a50(state); ESP += 0u;
L_004d5398: // 004d5398 8d442430 LEA EAX,[ESP + 0x30]
    EAX = (ESP + 0x00000030u);
L_004d539c: // 004d539c 6a02 PUSH 0x2
    ESP -= 4u; write32(ESP, 0x00000002u);
L_004d539e: // 004d539e 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d539f: // 004d539f 6897000000 PUSH 0x97
    ESP -= 4u; write32(ESP, 0x00000097u);
L_004d53a4: // 004d53a4 e877870100 CALL 0x004edb20
    state.argument_stack = pointer(ESP); application_core_effect_004edb20(state); ESP += 0u;
L_004d53a9: // 004d53a9 e8a2b30000 CALL 0x004e0750
    state.argument_stack = pointer(ESP); application_core_effect_004e0750(state); ESP += 0u;
L_004d53ae: // 004d53ae 8d4c243c LEA ECX,[ESP + 0x3c]
    ECX = (ESP + 0x0000003cu);
L_004d53b2: // 004d53b2 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d53b3: // 004d53b3 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d53b4: // 004d53b4 6a32 PUSH 0x32
    ESP -= 4u; write32(ESP, 0x00000032u);
L_004d53b6: // 004d53b6 e865870100 CALL 0x004edb20
    state.argument_stack = pointer(ESP); application_core_effect_004edb20(state); ESP += 0u;
L_004d53bb: // 004d53bb 83c424 ADD ESP,0x24
    ESP = alu_add(ESP, 0x00000024u, 32, state.flags);
L_004d53be: // 004d53be 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d53bf: // 004d53bf 68e0715d00 PUSH 0x5d71e0
    ESP -= 4u; write32(ESP, address(application_core_address_005d71e0()));
L_004d53c4: // 004d53c4 68a8d65c00 PUSH 0x5cd6a8
    ESP -= 4u; write32(ESP, address(application_core_address_005cd6a8()));
L_004d53c9: // 004d53c9 53 PUSH EBX
    ESP -= 4u; write32(ESP, EBX);
L_004d53ca: // 004d53ca 6820935d00 PUSH 0x5d9320
    ESP -= 4u; write32(ESP, address(application_core_address_005d9320()));
L_004d53cf: // 004d53cf e8dc26feff CALL 0x004b7ab0
    state.argument_stack = pointer(ESP); application_core_effect_004b7ab0(state); ESP += 0u;
L_004d53d4: // 004d53d4 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d53d7: // 004d53d7 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d53d8: // 004d53d8 e86ebf0c00 CALL 0x005a134b
    state.argument_stack = pointer(ESP); application_core_effect_005a134b(state); ESP += 0u;
L_004d53dd: // 004d53dd 8b10 MOV EDX,dword ptr [EAX]
    EDX = read32((EAX));
L_004d53df: // 004d53df 83c414 ADD ESP,0x14
    ESP = alu_add(ESP, 0x00000014u, 32, state.flags);
L_004d53e2: // 004d53e2 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d53e4: // 004d53e4 ff5210 CALL dword ptr [EDX + 0x10]
    state.argument_stack = pointer(ESP); application_core_virtual_004d53e4(state, read32((EDX + 0x00000010u))); ESP += 0u;
L_004d53e7: // 004d53e7 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d53e8: // 004d53e8 8d442454 LEA EAX,[ESP + 0x54]
    EAX = (ESP + 0x00000054u);
L_004d53ec: // 004d53ec 68bcce5c00 PUSH 0x5ccebc
    ESP -= 4u; write32(ESP, address(application_core_address_005ccebc()));
L_004d53f1: // 004d53f1 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d53f2: // 004d53f2 e8c8bb0c00 CALL 0x005a0fbf
    state.argument_stack = pointer(ESP); application_core_effect_005a0fbf(state); ESP += 0u;
L_004d53f7: // 004d53f7 8d4c245c LEA ECX,[ESP + 0x5c]
    ECX = (ESP + 0x0000005cu);
L_004d53fb: // 004d53fb 8d542430 LEA EDX,[ESP + 0x30]
    EDX = (ESP + 0x00000030u);
L_004d53ff: // 004d53ff 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d5400: // 004d5400 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d5401: // 004d5401 6810010000 PUSH 0x110
    ESP -= 4u; write32(ESP, 0x00000110u);
L_004d5406: // 004d5406 e8a5860100 CALL 0x004edab0
    state.argument_stack = pointer(ESP); application_core_effect_004edab0(state); ESP += 0u;
L_004d540b: // 004d540b 8b44243c MOV EAX,dword ptr [ESP + 0x3c]
    EAX = read32((ESP + 0x0000003cu));
L_004d540f: // 004d540f 8918 MOV dword ptr [EAX],EBX
    write32((EAX), EBX);
L_004d5411: // 004d5411 8b44243c MOV EAX,dword ptr [ESP + 0x3c]
    EAX = read32((ESP + 0x0000003cu));
L_004d5415: // 004d5415 83c004 ADD EAX,0x4
    EAX = alu_add(EAX, 0x00000004u, 32, state.flags);
L_004d5418: // 004d5418 8944243c MOV dword ptr [ESP + 0x3c],EAX
    write32((ESP + 0x0000003cu), EAX);
L_004d541c: // 004d541c 2bc7 SUB EAX,EDI
    EAX = alu_sub(EAX, EDI, 32, state.flags);
L_004d541e: // 004d541e 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d541f: // 004d541f 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d5420: // 004d5420 e81b420900 CALL 0x00569640
    state.argument_stack = pointer(ESP); application_core_effect_00569640(state); ESP += 0u;
L_004d5425: // 004d5425 83c420 ADD ESP,0x20
    ESP = alu_add(ESP, 0x00000020u, 32, state.flags);
L_004d5428: // 004d5428 eb49 JMP 0x004d5473
    goto L_004d5473;
L_004d542a: // 004d542a 39ae78010000 CMP dword ptr [ESI + 0x178],EBP
    (void)alu_sub(read32((ESI + 0x00000178u)), EBP, 32, state.flags);
L_004d5430: // 004d5430 7538 JNZ 0x004d546a
    if(!state.flags.zero) goto L_004d546a;
L_004d5432: // 004d5432 6800200000 PUSH 0x2000
    ESP -= 4u; write32(ESP, 0x00002000u);
L_004d5437: // 004d5437 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d5438: // 004d5438 e803420900 CALL 0x00569640
    state.argument_stack = pointer(ESP); application_core_effect_00569640(state); ESP += 0u;
L_004d543d: // 004d543d 8d4c242c LEA ECX,[ESP + 0x2c]
    ECX = (ESP + 0x0000002cu);
L_004d5441: // 004d5441 897c242c MOV dword ptr [ESP + 0x2c],EDI
    write32((ESP + 0x0000002cu), EDI);
L_004d5445: // 004d5445 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d5446: // 004d5446 e80526feff CALL 0x004b7a50
    state.argument_stack = pointer(ESP); application_core_effect_004b7a50(state); ESP += 0u;
L_004d544b: // 004d544b 8b542430 MOV EDX,dword ptr [ESP + 0x30]
    EDX = read32((ESP + 0x00000030u));
L_004d544f: // 004d544f 891a MOV dword ptr [EDX],EBX
    write32((EDX), EBX);
L_004d5451: // 004d5451 8b442430 MOV EAX,dword ptr [ESP + 0x30]
    EAX = read32((ESP + 0x00000030u));
L_004d5455: // 004d5455 83c004 ADD EAX,0x4
    EAX = alu_add(EAX, 0x00000004u, 32, state.flags);
L_004d5458: // 004d5458 89442430 MOV dword ptr [ESP + 0x30],EAX
    write32((ESP + 0x00000030u), EAX);
L_004d545c: // 004d545c 2bc7 SUB EAX,EDI
    EAX = alu_sub(EAX, EDI, 32, state.flags);
L_004d545e: // 004d545e 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d545f: // 004d545f 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d5460: // 004d5460 e8db410900 CALL 0x00569640
    state.argument_stack = pointer(ESP); application_core_effect_00569640(state); ESP += 0u;
L_004d5465: // 004d5465 83c414 ADD ESP,0x14
    ESP = alu_add(ESP, 0x00000014u, 32, state.flags);
L_004d5468: // 004d5468 eb09 JMP 0x004d5473
    goto L_004d5473;
L_004d546a: // 004d546a 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d546b: // 004d546b e860810100 CALL 0x004ed5d0
    state.argument_stack = pointer(ESP); application_core_effect_004ed5d0(state); ESP += 0u;
L_004d5470: // 004d5470 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d5473: // 004d5473 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d5479: // 004d5479 e892100000 CALL 0x004d6510
    state.argument_stack = pointer(ESP); application_core_effect_004d6510(state); ESP += 0u;
L_004d547e: // 004d547e 85c0 TEST EAX,EAX
    (void)alu_test(EAX, EAX, 32, state.flags);
L_004d5480: // 004d5480 7640 JBE 0x004d54c2
    if(state.flags.carry || state.flags.zero) goto L_004d54c2;
L_004d5482: // 004d5482 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d5488: // 004d5488 e883100000 CALL 0x004d6510
    state.argument_stack = pointer(ESP); application_core_effect_004d6510(state); ESP += 0u;
L_004d548d: // 004d548d 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d5493: // 004d5493 48 DEC EAX
    EAX = alu_dec(EAX, 32, state.flags);
L_004d5494: // 004d5494 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d5495: // 004d5495 e886100000 CALL 0x004d6520
    state.argument_stack = pointer(ESP); application_core_effect_004d6520(state); ESP += 4u;
L_004d549a: // 004d549a 8b00 MOV EAX,dword ptr [EAX]
    EAX = read32((EAX));
L_004d549c: // 004d549c 3bc3 CMP EAX,EBX
    (void)alu_sub(EAX, EBX, 32, state.flags);
L_004d549e: // 004d549e 7408 JZ 0x004d54a8
    if(state.flags.zero) goto L_004d54a8;
L_004d54a0: // 004d54a0 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d54a1: // 004d54a1 8bc8 MOV ECX,EAX
    ECX = EAX;
L_004d54a3: // 004d54a3 e868010000 CALL 0x004d5610
    state.argument_stack = pointer(ESP); application_core_effect_004d5610(state); ESP += 4u;
L_004d54a8: // 004d54a8 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d54ae: // 004d54ae e87d100000 CALL 0x004d6530
    state.argument_stack = pointer(ESP); application_core_effect_004d6530(state); ESP += 0u;
L_004d54b3: // 004d54b3 8b8ed8000000 MOV ECX,dword ptr [ESI + 0xd8]
    ECX = read32((ESI + 0x000000d8u));
L_004d54b9: // 004d54b9 e852100000 CALL 0x004d6510
    state.argument_stack = pointer(ESP); application_core_effect_004d6510(state); ESP += 0u;
L_004d54be: // 004d54be 85c0 TEST EAX,EAX
    (void)alu_test(EAX, EAX, 32, state.flags);
L_004d54c0: // 004d54c0 77c0 JA 0x004d5482
    if(!state.flags.carry && !state.flags.zero) goto L_004d5482;
L_004d54c2: // 004d54c2 8bce MOV ECX,ESI
    ECX = ESI;
L_004d54c4: // 004d54c4 e8a70d0000 CALL 0x004d6270
    state.argument_stack = pointer(ESP); application_core_effect_004d6270(state); ESP += 0u;
L_004d54c9: // 004d54c9 8b8608010000 MOV EAX,dword ptr [ESI + 0x108]
    EAX = read32((ESI + 0x00000108u));
L_004d54cf: // 004d54cf 50 PUSH EAX
    ESP -= 4u; write32(ESP, EAX);
L_004d54d0: // 004d54d0 e8bbca0500 CALL 0x00531f90
    state.argument_stack = pointer(ESP); application_core_effect_00531f90(state); ESP += 0u;
L_004d54d5: // 004d54d5 8b8ef8000000 MOV ECX,dword ptr [ESI + 0xf8]
    ECX = read32((ESI + 0x000000f8u));
L_004d54db: // 004d54db 83c404 ADD ESP,0x4
    ESP = alu_add(ESP, 0x00000004u, 32, state.flags);
L_004d54de: // 004d54de 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d54e0: // 004d54e0 899e08010000 MOV dword ptr [ESI + 0x108],EBX
    write32((ESI + 0x00000108u), EBX);
L_004d54e6: // 004d54e6 7406 JZ 0x004d54ee
    if(state.flags.zero) goto L_004d54ee;
L_004d54e8: // 004d54e8 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d54e9: // 004d54e9 e8d2010000 CALL 0x004d56c0
    state.argument_stack = pointer(ESP); application_core_effect_004d56c0(state); ESP += 4u;
L_004d54ee: // 004d54ee 8b8e00010000 MOV ECX,dword ptr [ESI + 0x100]
    ECX = read32((ESI + 0x00000100u));
L_004d54f4: // 004d54f4 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d54f6: // 004d54f6 7406 JZ 0x004d54fe
    if(state.flags.zero) goto L_004d54fe;
L_004d54f8: // 004d54f8 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d54f9: // 004d54f9 e8c2010000 CALL 0x004d56c0
    state.argument_stack = pointer(ESP); application_core_effect_004d56c0(state); ESP += 4u;
L_004d54fe: // 004d54fe 8b8e04010000 MOV ECX,dword ptr [ESI + 0x104]
    ECX = read32((ESI + 0x00000104u));
L_004d5504: // 004d5504 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d5506: // 004d5506 7406 JZ 0x004d550e
    if(state.flags.zero) goto L_004d550e;
L_004d5508: // 004d5508 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5509: // 004d5509 e8b2010000 CALL 0x004d56c0
    state.argument_stack = pointer(ESP); application_core_effect_004d56c0(state); ESP += 4u;
L_004d550e: // 004d550e 8b8efc000000 MOV ECX,dword ptr [ESI + 0xfc]
    ECX = read32((ESI + 0x000000fcu));
L_004d5514: // 004d5514 3bcb CMP ECX,EBX
    (void)alu_sub(ECX, EBX, 32, state.flags);
L_004d5516: // 004d5516 7406 JZ 0x004d551e
    if(state.flags.zero) goto L_004d551e;
L_004d5518: // 004d5518 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5519: // 004d5519 e8a2010000 CALL 0x004d56c0
    state.argument_stack = pointer(ESP); application_core_effect_004d56c0(state); ESP += 4u;
L_004d551e: // 004d551e e8bd390500 CALL 0x00528ee0
    state.argument_stack = pointer(ESP); application_core_effect_00528ee0(state); ESP += 0u;
L_004d5523: // 004d5523 e8984b0500 CALL 0x0052a0c0
    state.argument_stack = pointer(ESP); application_core_effect_0052a0c0(state); ESP += 0u;
L_004d5528: // 004d5528 e8336a0000 CALL 0x004dbf60
    state.argument_stack = pointer(ESP); application_core_effect_004dbf60(state); ESP += 0u;
L_004d552d: // 004d552d e81ee20000 CALL 0x004e3750
    state.argument_stack = pointer(ESP); application_core_effect_004e3750(state); ESP += 0u;
L_004d5532: // 004d5532 8d4c2424 LEA ECX,[ESP + 0x24]
    ECX = (ESP + 0x00000024u);
L_004d5536: // 004d5536 8dbe78010000 LEA EDI,[ESI + 0x178]
    EDI = (ESI + 0x00000178u);
L_004d553c: // 004d553c 51 PUSH ECX
    ESP -= 4u; write32(ESP, ECX);
L_004d553d: // 004d553d 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d553e: // 004d553e 896c242c MOV dword ptr [ESP + 0x2c],EBP
    write32((ESP + 0x0000002cu), EBP);
L_004d5542: // 004d5542 e869120000 CALL 0x004d67b0
    state.argument_stack = pointer(ESP); application_core_effect_004d67b0(state); ESP += 0u;
L_004d5547: // 004d5547 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d554a: // 004d554a 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d554c: // 004d554c 740a JZ 0x004d5558
    if(state.flags.zero) goto L_004d5558;
L_004d554e: // 004d554e e8fde5f6ff CALL 0x00443b50
    state.argument_stack = pointer(ESP); application_core_effect_00443b50(state); ESP += 0u;
L_004d5553: // 004d5553 e86836f7ff CALL 0x00448bc0
    state.argument_stack = pointer(ESP); application_core_effect_00448bc0(state); ESP += 0u;
L_004d5558: // 004d5558 8d542424 LEA EDX,[ESP + 0x24]
    EDX = (ESP + 0x00000024u);
L_004d555c: // 004d555c 896c2424 MOV dword ptr [ESP + 0x24],EBP
    write32((ESP + 0x00000024u), EBP);
L_004d5560: // 004d5560 52 PUSH EDX
    ESP -= 4u; write32(ESP, EDX);
L_004d5561: // 004d5561 57 PUSH EDI
    ESP -= 4u; write32(ESP, EDI);
L_004d5562: // 004d5562 e849120000 CALL 0x004d67b0
    state.argument_stack = pointer(ESP); application_core_effect_004d67b0(state); ESP += 0u;
L_004d5567: // 004d5567 83c408 ADD ESP,0x8
    ESP = alu_add(ESP, 0x00000008u, 32, state.flags);
L_004d556a: // 004d556a 84c0 TEST AL,AL
    (void)alu_test(get_byte(EAX, 0), get_byte(EAX, 0), 8, state.flags);
L_004d556c: // 004d556c 7405 JZ 0x004d5573
    if(state.flags.zero) goto L_004d5573;
L_004d556e: // 004d556e e86d000000 CALL 0x004d55e0
    state.argument_stack = pointer(ESP); application_core_effect_004d55e0(state); ESP += 0u;
L_004d5573: // 004d5573 e808270000 CALL 0x004d7c80
    state.argument_stack = pointer(ESP); application_core_effect_004d7c80(state); ESP += 0u;
L_004d5578: // 004d5578 e863160000 CALL 0x004d6be0
    state.argument_stack = pointer(ESP); application_core_effect_004d6be0(state); ESP += 0u;
L_004d557d: // 004d557d 8bb6d8000000 MOV ESI,dword ptr [ESI + 0xd8]
    ESI = read32((ESI + 0x000000d8u));
L_004d5583: // 004d5583 3bf3 CMP ESI,EBX
    (void)alu_sub(ESI, EBX, 32, state.flags);
L_004d5585: // 004d5585 7408 JZ 0x004d558f
    if(state.flags.zero) goto L_004d558f;
L_004d5587: // 004d5587 55 PUSH EBP
    ESP -= 4u; write32(ESP, EBP);
L_004d5588: // 004d5588 8bce MOV ECX,ESI
    ECX = ESI;
L_004d558a: // 004d558a e881270200 CALL 0x004f7d10
    state.argument_stack = pointer(ESP); application_core_effect_004f7d10(state); ESP += 4u;
L_004d558f: // 004d558f e80cb20000 CALL 0x004e07a0
    state.argument_stack = pointer(ESP); application_core_effect_004e07a0(state); ESP += 0u;
L_004d5594: // 004d5594 8b442448 MOV EAX,dword ptr [ESP + 0x48]
    EAX = read32((ESP + 0x00000048u));
L_004d5598: // 004d5598 5f POP EDI
    ESP += 4u; // Native C++ ABI preserves the caller nonvolatile registers.
L_004d5599: // 004d5599 5e POP ESI
    ESP += 4u; // Native C++ ABI preserves the caller nonvolatile registers.
L_004d559a: // 004d559a 891d28b96500 MOV dword ptr [0x0065b928],EBX
    write32((address(application_core_address_0065b928())), EBX);
L_004d55a0: // 004d55a0 8b00 MOV EAX,dword ptr [EAX]
    EAX = read32((EAX));
L_004d55a2: // 004d55a2 5d POP EBP
    ESP += 4u; // Native C++ ABI preserves the caller nonvolatile registers.
L_004d55a3: // 004d55a3 5b POP EBX
    ESP += 4u; // Native C++ ABI preserves the caller nonvolatile registers.
L_004d55a4: // 004d55a4 81c490000000 ADD ESP,0x90
    ESP = alu_add(ESP, 0x00000090u, 32, state.flags);
L_004d55aa: // 004d55aa c20c00 RET 0xc
    return EAX;
}
}
