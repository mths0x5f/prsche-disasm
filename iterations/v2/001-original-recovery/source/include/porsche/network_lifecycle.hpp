#pragma once
#include "porsche/application_services_next.hpp"
#include <array>
#include <cstdint>

namespace porsche {

// Complete original bodies. Both original member entries take ECX, RET0.
// Reset's final EAX is retained by the explicit entry; the older Run141
// facade has void ABI because those callers discard it.
std::uint32_t __fastcall network_lifecycle_reset_0048e9c0(void* receiver, void* unused_edx);
void __fastcall application_network_reset_0048e9c0(void* receiver, void* unused_edx);
void __fastcall application_network_member_destroy_004935c0(void* receiver, void* unused_edx);
void __cdecl network_lifecycle_remove_callback_00560180(std::uint32_t callback_va);

// Source .data zero-fill. Callback removal scans exactly eight DWORD slots.
extern void* network_lifecycle_session_00628c74;
extern void* network_lifecycle_member_00628c7c;
extern std::array<std::uint32_t, 8> network_lifecycle_callbacks_006b7c20;

// Original effects not recovered by this packet. Argument registers/stack
// are explicit; no fake production effects are supplied.
void __cdecl network_lifecycle_close_transport_0048c580();
void __cdecl network_lifecycle_stop_session_00492260();
void __cdecl network_lifecycle_wait_0053c380(std::int32_t interval);
void __fastcall network_lifecycle_connection_destroy_0048aed0(void* receiver, void* unused_edx);
void __fastcall network_lifecycle_session_destroy_00491fc0(void* receiver, void* unused_edx);
void __fastcall network_lifecycle_clear_lists_0048e790(void* receiver, void* unused_edx);
std::uint32_t __stdcall network_lifecycle_tick_count_0048a9a0();
void __cdecl network_lifecycle_unregister_00561110(std::uint32_t callback_va);
void __cdecl network_lifecycle_device_stop_00561b50();
void __cdecl network_lifecycle_device_cancel_00561730(std::uint32_t handle);
void __cdecl network_lifecycle_device_release_005617d0(std::uint32_t handle);

} // namespace porsche
