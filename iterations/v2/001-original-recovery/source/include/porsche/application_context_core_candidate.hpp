#pragma once
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
void __cdecl application_core_effect_00423610(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004237d0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00429840(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004298a0(ApplicationCoreCallState&); // Original RET cleanup 8 bytes.
void __cdecl application_core_effect_00429bf0(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_00443760(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00443b50(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00448b10(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00448bc0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0044b960(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0044de50(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0044ed10(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0044fe90(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0045d3a0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00466e80(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_004672f0(ApplicationCoreCallState&); // Original RET cleanup 32 bytes.
void __cdecl application_core_effect_00467f40(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00467fc0(ApplicationCoreCallState&); // Original RET cleanup 16 bytes.
void __cdecl application_core_effect_00472860(ApplicationCoreCallState&); // Original RET cleanup 8 bytes.
void __cdecl application_core_effect_0047fb80(ApplicationCoreCallState&); // Original RET cleanup 8 bytes.
void __cdecl application_core_effect_0048caa0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0048e1a0(ApplicationCoreCallState&); // Original RET cleanup 12 bytes.
void __cdecl application_core_effect_004ae3c0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004b7810(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004b7a50(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004b7ab0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004be3d0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004c70e0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d1bd0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d2100(ApplicationCoreCallState&); // Original RET cleanup 12 bytes.
void __cdecl application_core_effect_004d2cb0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d2de0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d55c0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d55e0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d5610(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_004d56c0(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_004d5be0(ApplicationCoreCallState&); // Original RET cleanup 12 bytes.
void __cdecl application_core_effect_004d5df0(ApplicationCoreCallState&); // Original RET cleanup 8 bytes.
void __cdecl application_core_effect_004d6130(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d6270(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d64a0(ApplicationCoreCallState&); // Original RET cleanup 8 bytes.
void __cdecl application_core_effect_004d6510(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d6520(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_004d6530(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d67b0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d67d0(ApplicationCoreCallState&); // Original RET cleanup 12 bytes.
void __cdecl application_core_effect_004d6880(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_004d6b10(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d6be0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d7c80(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d7e70(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004d8e10(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004dbef0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004dbf60(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004dda00(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004dde90(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004ddf00(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004ddf30(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004de040(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004de2f0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004de880(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004de9b0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004deda0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004def60(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004df3c0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e04f0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e0750(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e0760(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e07a0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e07b0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e0e30(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e1c20(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e1c70(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e2f30(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e3560(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e36b0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e3750(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e5d00(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004e7430(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004ed5d0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004edab0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004edb20(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004edd00(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004ee280(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004f3a40(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004f7ad0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004f7d10(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_004fae20(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_004fb750(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00501270(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00501340(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_005024e0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00502ff0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00505570(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00505800(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00505810(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_00509490(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_005099d0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00509a00(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0050c120(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0050c880(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_005121b0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00514990(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00516950(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00517ad0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0051aba0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0051af90(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0051b020(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0051ebd0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00528cd0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00528ee0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0052a090(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0052a0c0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00531f90(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00536080(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_005370c0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00537830(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_00537850(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_00538c90(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00538da0(ApplicationCoreCallState&); // Original RET cleanup 24 bytes.
void __cdecl application_core_effect_005392d0(ApplicationCoreCallState&); // Original RET cleanup 12 bytes.
void __cdecl application_core_effect_00539b00(ApplicationCoreCallState&); // Original RET cleanup 4 bytes.
void __cdecl application_core_effect_00539b30(ApplicationCoreCallState&); // Original RET cleanup 16 bytes.
void __cdecl application_core_effect_00539b80(ApplicationCoreCallState&); // Original RET cleanup 12 bytes.
void __cdecl application_core_effect_00539f40(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00555390(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00559a10(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00559a40(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00560030(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_00569640(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0059ef90(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_0059efc0(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_005a0fbf(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_effect_005a134b(ApplicationCoreCallState&); // Original RET cleanup 0 bytes.
void __cdecl application_core_virtual_004d3a76(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 4: see unresolved contract evidence.
void __cdecl application_core_virtual_004d3a81(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 0: see unresolved contract evidence.
void __cdecl application_core_virtual_004d3a8c(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 0: see unresolved contract evidence.
void __cdecl application_core_virtual_004d4119(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 0: see unresolved contract evidence.
void __cdecl application_core_virtual_004d52c8(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 0: see unresolved contract evidence.
void __cdecl application_core_virtual_004d5303(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 0: see unresolved contract evidence.
void __cdecl application_core_virtual_004d5319(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 4: see unresolved contract evidence.
void __cdecl application_core_virtual_004d532e(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 4: see unresolved contract evidence.
void __cdecl application_core_virtual_004d5343(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 4: see unresolved contract evidence.
void __cdecl application_core_virtual_004d53e4(ApplicationCoreCallState&, std::uint32_t target); // Cleanup 0: see unresolved contract evidence.
void* __cdecl application_core_address_005ccebc(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005cd698(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005cd6a8(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d6e78(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d70e0(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d71e0(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d7378(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d8bdc(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9158(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9320(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d932c(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9338(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9348(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9354(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9368(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9378(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9388(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9398(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93a0(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93ac(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93b8(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93c4(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93d0(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93dc(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93e4(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93ec(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93f4(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d93fc(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9408(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9414(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9420(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d942c(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9438(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9444(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005d9454(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_005e8e50(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_0061976c(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_00619800(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_00628130(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_00628c70(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_006573e8(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_00657484(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_006577d8(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_006577dc(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_00657a60(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_00657a64(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_00657e34(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_0065b330(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_0065b334(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_0065b344(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_0065b910(); // Original address view, unknown extent; no storage defined.
void* __cdecl application_core_address_0065b928(); // Original address view, unknown extent; no storage defined.
}
