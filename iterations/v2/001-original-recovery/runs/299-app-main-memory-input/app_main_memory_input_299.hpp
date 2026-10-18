#pragma once

#include <cstdint>
#include <cstddef>

namespace porsche {

// -----------------------------------------------------------------------------
// Function 1: 00556640 (8 PE body bytes, 16 bytes allocated)
// Buffer header prefix reader (retrieves length/capacity field at offset -12).
// -----------------------------------------------------------------------------
std::uint32_t __cdecl application_main_function_00556640(const void* buffer_ptr);

// -----------------------------------------------------------------------------
// Function 2: 005a246e (17 PE body bytes, 32 bytes allocated)
// Default-arguments forwarder invoking callee_005a2490(arg0, 0, 0).
// -----------------------------------------------------------------------------
std::uint32_t __cdecl callee_005a2490(std::uint32_t arg0, std::uint32_t arg1, std::uint32_t arg2);
std::uint32_t __cdecl application_main_function_005a246e(std::uint32_t arg0);

// -----------------------------------------------------------------------------
// Function 3: 0059ed90 (19 PE body bytes, 32 bytes allocated)
// Win32 VirtualFree wrapper releasing memory via MEM_RELEASE (0x8000).
// -----------------------------------------------------------------------------
std::int32_t __stdcall win32_virtual_free_005b2148(void* address, std::uint32_t size, std::uint32_t free_type);
std::int32_t __cdecl application_main_function_0059ed90(void* ptr);

// -----------------------------------------------------------------------------
// Function 4: 004d1ba0 (46 PE body bytes, 48 bytes allocated)
// SessionObject virtual destructor: resets vtable to 0x005b683c, destroys & frees
// sub-object at offset +0xd4 if non-null, and invokes base destructor 0x00525ec0.
// -----------------------------------------------------------------------------
struct SessionSubObject_005295b0 {
    void __thiscall destructor_005295b0();
};

void __cdecl operator_delete_0059f050(void* ptr);

struct SessionObject_004d1ba0 {
    const void* vtable; // 0x00
    std::uint8_t pad_04[0xd0]; // 0x04..0xd3
    SessionSubObject_005295b0* sub_object_d4; // 0xd4

    void __thiscall destructor_base_00525ec0();
    void __thiscall destructor_004d1ba0();
};

// Standalone fastcall wrapper receiving this in ECX
void __fastcall application_main_function_004d1ba0(SessionObject_004d1ba0* self);

// -----------------------------------------------------------------------------
// Function 5: 005a177b (65 PE body bytes, 80 bytes allocated)
// Scoped lock and context wrapper around engine render dispatch callee_005a4371.
// -----------------------------------------------------------------------------
struct RenderContext_005e5508 {
    std::uint32_t state_flags;
};
extern RenderContext_005e5508 g_render_context_5e5508;

void __cdecl render_context_acquire_005a3719(std::uint32_t mode, RenderContext_005e5508* ctx);
std::uint32_t __cdecl render_context_save_state_005a533e(RenderContext_005e5508* ctx);
std::uint32_t __cdecl render_context_op_005a4371(RenderContext_005e5508* ctx, std::uint32_t arg0, std::uint32_t* p_arg1);
void __cdecl render_context_restore_state_005a53cb(std::uint32_t state, RenderContext_005e5508* ctx);
void __cdecl render_context_release_005a376b(std::uint32_t mode, RenderContext_005e5508* ctx);

std::uint32_t __cdecl application_main_function_005a177b(std::uint32_t arg0, std::uint32_t arg1);

// -----------------------------------------------------------------------------
// Function 6: 0059ed40 (75 PE body bytes, 80 bytes allocated)
// System page-aligned virtual memory allocator using GetSystemInfo and VirtualAlloc.
// -----------------------------------------------------------------------------
struct Win32SystemInfo_0059ed40 {
    std::uint32_t dwOemId;
    std::uint32_t dwPageSize;
    void* lpMinimumApplicationAddress;
    void* lpMaximumApplicationAddress;
    std::uint32_t dwActiveProcessorMask;
    std::uint32_t dwNumberOfProcessors;
    std::uint32_t dwProcessorType;
    std::uint32_t dwAllocationGranularity;
    std::uint16_t wProcessorLevel;
    std::uint16_t wProcessorRevision;
};

extern std::uint32_t g_system_page_size_006af3f8;

void __stdcall win32_get_system_info_005b21b0(Win32SystemInfo_0059ed40* info);
void* __stdcall win32_virtual_alloc_005b2144(void* address, std::uint32_t size, std::uint32_t allocation_type, std::uint32_t protect);

void* __cdecl application_main_function_0059ed40(std::uint32_t* p_size);

} // namespace porsche
