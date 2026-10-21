#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace porsche {
// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 005e3e18..005e4fef and 006af374..006af3ff. Keep adjacent original
// fields in one object: unmasked arena indices can alias the guard/page/ID.
struct ApplicationHeapManager {
    std::uint32_t header[10];
    std::uint8_t records[0x8c0];
};
struct ApplicationHeapContexts {
    ApplicationHeapManager defaults;
    ApplicationHeapManager live;
    void* current;
    void** selectors;
};
struct ApplicationHeapRuntime {
    void* selectors[16];
    void* primary_arena;
    void* other_arenas[15];
    std::uint8_t initialized;
    std::uint8_t padding[3];
    std::uint32_t page;
    std::int32_t object_heap;
};
static_assert(sizeof(void*) == 4, "original heap layout requires x86");
static_assert(sizeof(ApplicationHeapManager) == 0x8e8);
static_assert(offsetof(ApplicationHeapContexts, live) == 0x8e8);
static_assert(offsetof(ApplicationHeapContexts, current) == 0x11d0);
static_assert(offsetof(ApplicationHeapContexts, selectors) == 0x11d4);
static_assert(sizeof(ApplicationHeapContexts) == 0x11d8);
static_assert(offsetof(ApplicationHeapRuntime, primary_arena) == 0x40);
static_assert(offsetof(ApplicationHeapRuntime, initialized) == 0x80);
static_assert(offsetof(ApplicationHeapRuntime, page) == 0x84);
static_assert(offsetof(ApplicationHeapRuntime, object_heap) == 0x88);
static_assert(sizeof(ApplicationHeapRuntime) == 0x8c);
extern ApplicationHeapContexts application_heap_contexts;
extern ApplicationHeapRuntime application_heap_runtime;
extern const char application_heap_queue_source_005e5064[10];

// Modular x86 effective addresses, followed by bytewise access. In particular,
// do not index a C++ 16-element arena array with 16 (an original guard alias).
inline void* application_heap_address(void* base, std::uint32_t offset) {
    return reinterpret_cast<void*>(reinterpret_cast<std::uintptr_t>(base) + offset);
}
inline std::uint32_t application_heap_load(const void* address) {
    std::uint32_t value;
    std::memcpy(&value, address, sizeof(value));
    return value;
}
inline void application_heap_store(void* address, std::uint32_t value) {
    std::memcpy(address, &value, sizeof(value));
}
inline std::uint32_t application_heap_word(const void* value) {
    return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(value));
}
inline void* application_heap_pointer(std::uint32_t value) {
    return reinterpret_cast<void*>(static_cast<std::uintptr_t>(value));
}
inline void* application_heap_arena_cell(std::uint32_t index) {
    return application_heap_address(&application_heap_runtime, 0x40u + index * 4u);
}

void* __cdecl application_heap_identity_0059e9b0(void*, std::int32_t);
std::uint32_t __cdecl application_heap_zero_0059e9c0(...);
void __cdecl application_heap_shutdown_0059eb20();
// Unrecovered targets, retained as link boundaries. +10/+20 prototypes are
// body-inferred; +24 also has one-DWORD indirect caller/cleanup evidence.
void* __cdecl application_heap_block_005aef20(void*);
std::uint32_t __cdecl application_heap_tag_00556680(const void*);
std::uint32_t __cdecl application_heap_measure_00569ad0(std::uint32_t);
void __cdecl application_heap_secondary_stop_0055ec30();
std::uint32_t __cdecl application_heap_destroy_005699f0(std::uint32_t);
void __cdecl application_heap_queue_clean_0059ee30(std::uint32_t);
}
