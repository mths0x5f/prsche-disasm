#pragma once
#include <cstdint>

namespace porsche {
// The original global is a 32-bit pointer cell. Its storage owner is unrecovered.
extern std::uint32_t frame_service_root_00628960;

struct FrameTemporary_290 { std::uint32_t object; std::uint8_t flag; std::uint8_t untouched; std::uint16_t tag; };
static_assert(sizeof(FrameTemporary_290)==8);
static_assert(sizeof(void*)==4, "original x86 pointer ABI");

// External original callees: declarations preserve ECX/stack and return contracts.
struct FrameResolver_290 { FrameTemporary_290* __thiscall resolve_004898f0(FrameTemporary_290*,std::uint32_t); };
struct FrameAction_290 { void __thiscall invoke_00476170(); };
struct FrameIterator_290 { void __thiscall advance_00423840(); };
struct FrameTail_290 { void __thiscall invoke_00482e50(); };
struct FrameService_290 { void __thiscall execute_00487e20(); };
void __cdecl application_main_function_00471b60();
}
