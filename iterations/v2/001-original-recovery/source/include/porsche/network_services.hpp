#pragma once
#include "porsche/application_services_next.hpp"
#include <cstdint>

namespace porsche {

// 0048c870 serializes a bounded packet and invokes sender vtable slot0.
// Third is a nullable original string address; fourth is the destination ID.
void __fastcall application_network_message_0048c870(void* receiver, void* unused_edx,
    std::uint32_t message, std::uint32_t first, std::uint32_t second,
    std::uint32_t third, std::uint32_t fourth);
void __cdecl network_services_action_0048da60(std::uint32_t first, std::uint32_t second);
void __cdecl application_main_network_action(std::int32_t first, std::int32_t second);

// Original thiscall list ABI, including output iterator and callee-pop stack
// arguments. EAX from unlink is the output pointer; remove_matching is RET4.
std::uint32_t* __fastcall network_services_unlink_0048b660(void* list,
    void* unused_edx, std::uint32_t* output, std::uint32_t node);
void __fastcall network_services_remove_matching_00493180(void* list,
    void* unused_edx, const std::uint32_t* value);
void __fastcall network_lifecycle_clear_lists_0048e790(void* receiver, void* unused_edx);

// Unrecovered effects keep the exact receiver and pointer arguments. The
// iterator boundary returns a pointer which the caller really dereferences.
void __fastcall network_services_detach_0048c430(void* receiver, void* unused_edx);
void __fastcall network_services_destroy_004904d0(void* receiver, void* unused_edx);
std::uint32_t* __fastcall network_services_begin_004c3150(void* list,
    void* unused_edx, std::uint32_t* output);

} // namespace porsche
