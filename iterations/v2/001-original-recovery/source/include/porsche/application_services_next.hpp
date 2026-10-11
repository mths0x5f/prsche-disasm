#pragma once

#include <array>
#include <cstdint>

namespace porsche {

// Full original control-flow bodies. Return EAX is not consumed by the known
// callers. 0048e6f0 has a thiscall receiver in ECX, unlike its old app_main facade.
void __cdecl application_audio_shutdown_004a6960();
void __cdecl application_audio_reset_004a6e30();
void __cdecl application_network_finish_0048dad0();
void __fastcall application_network_close_0048e6f0(void* receiver, void* unused_edx);

// New owner of the original zero-filled BSS span. Gaps stay opaque; reset
// writes only offsets present in 004a6e30. No overlap with Run128's records.
extern std::array<std::uint32_t, 0x2b8 / 4> application_audio_reset_storage_00655d48;
extern std::uint32_t application_audio_secondary_active_005d1738;

// Original BSS count and indexed table. No table extent or production owner is
// inferred from this consumer. The unsized array remains an unresolved storage
// dependency; the private probe owns only its fixture allocation.
// Cell 0 is count; table starts at cell 1. Keeping one unbounded storage view
// also preserves selected=-1 reading the preceding count cell. No guessed
// table size or initialized production allocation is supplied here.
extern std::uint32_t application_audio_source_storage_005e8bfc[];

// Still-unrecovered effects: explicit callsite arguments, no production stubs.
void __cdecl application_audio_shutdown_channels_005659f0(std::int32_t channel);
void __cdecl application_audio_shutdown_device_004ae310();
void __fastcall application_network_message_0048c870(void* receiver, void* unused_edx,
    std::uint32_t message, std::uint32_t first, std::uint32_t second,
    std::uint32_t third, std::uint32_t fourth);
void __fastcall application_network_reset_0048e9c0(void* receiver, void* unused_edx);
void __fastcall application_network_change_0048e1a0(void* receiver, void* unused_edx,
    std::uint32_t mode, std::uint32_t first, std::uint32_t second);
void __fastcall application_network_member_destroy_004935c0(void* receiver, void* unused_edx);

// ABI-compatible facades for the already recovered app_main. Only this caller
// uses the zero-argument close facade; other callers must pass their own ECX.
void __cdecl application_main_function_004a6960();
void __cdecl application_main_function_004a6e30();
void __cdecl application_main_function_0048dad0();
void __cdecl application_main_function_0048e6f0();

} // namespace porsche
