#pragma once

#include "porsche/application_context.hpp"
#include "porsche/heap.hpp"

#include <cstdint>

namespace porsche {

struct ApplicationContextRange16 { std::uint32_t words[4]; };
static_assert(sizeof(ApplicationContextRange16) == 0x10);

// Small original helpers in the 005294c0/005295b0 closure.
void __fastcall application_context_range_link_00529a20(
    void* object, void* unused_edx, const std::uint32_t* first);
void __stdcall application_context_initialize_blocks_00529a40(
    std::uint32_t* first, std::uint32_t* last);
void* __fastcall application_context_copy_range_005299d0(
    void* destination, void* unused_edx, const void* source);

// Typed effect boundaries reached by the recovered bodies. These declarations
// describe the native probe seam; they do not claim the original callees are
// no-ops.
// Returns the current pointer stored at 005e4fe8, not **005e4fe8.
void* __cdecl application_context_heap_state_005e4fe8();
std::uint32_t __cdecl application_context_heap_selector_005e4fec();
void __cdecl application_context_new_head_0059eeb0(
    std::uint32_t kind, std::uint32_t slot);
void __fastcall application_context_unlink_005262e0(
    void* root, void* unused_edx, std::uint32_t key);
void* __fastcall application_context_release_node_004e4560(
    void* member, void* unused_edx, std::uint32_t flags);
void __cdecl application_context_notify_node_004d7da0(
    void* node, std::uint32_t flags);
void __cdecl application_context_clear_004237d0(
    void* address, std::uint32_t bytes, std::uint32_t value);
void* __cdecl application_context_member_storage_004211d0(
    std::uint32_t bytes, std::uint32_t mode);
void* __cdecl application_context_member_block_0059ecb0(
    std::uint32_t bytes, std::uint32_t heap, std::uint32_t source_va);
void __cdecl application_context_compare_ranges_00529c20(
    ApplicationContextRange16 first_range, ApplicationContextRange16 second_range,
    std::uint32_t zero);
void __cdecl application_context_member_destroy_block_00441200(
    void* block, std::uint32_t bytes);

} // namespace porsche
