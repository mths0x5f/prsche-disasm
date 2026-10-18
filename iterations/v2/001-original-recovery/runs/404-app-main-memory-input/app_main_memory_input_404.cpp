#include "app_main_memory_input_404.hpp"

namespace porsche {

// 00556640: buffer header prefix reader
std::uint32_t __cdecl application_main_function_00556640(const void* buffer_ptr) {
    const auto* byte_ptr = static_cast<const std::uint8_t*>(buffer_ptr);
    const auto* field_ptr = reinterpret_cast<const std::uint32_t*>(byte_ptr - 12);
    return *field_ptr;
}

// 005a246e: forwarder with default zero arguments
std::uint32_t __cdecl application_main_function_005a246e(std::uint32_t arg0) {
    return callee_005a2490(arg0, 0u, 0u);
}

// 0059ed90: VirtualFree wrapper
std::int32_t __cdecl application_main_function_0059ed90(void* ptr) {
    return win32_virtual_free_005b2148(ptr, 0u, 0x8000u /* MEM_RELEASE */);
}

// 004d1ba0: SessionObject destructor
void __thiscall SessionObject_004d1ba0::destructor_004d1ba0() {
    this->vtable = reinterpret_cast<const void*>(0x005b683cu);
    if (this->sub_object_d4 != nullptr) {
        this->sub_object_d4->destructor_005295b0();
        operator_delete_0059f050(this->sub_object_d4);
    }
    this->destructor_base_00525ec0();
}

void __fastcall application_main_function_004d1ba0(SessionObject_004d1ba0* self) {
    self->destructor_004d1ba0();
}

// 005a177b: scoped render context lock & op wrapper
std::uint32_t __cdecl application_main_function_005a177b(std::uint32_t arg0, std::uint32_t arg1) {
    RenderContext_005e5508* ctx = &g_render_context_5e5508;
    render_context_acquire_005a3719(1u, ctx);
    const std::uint32_t saved_state = render_context_save_state_005a533e(ctx);
    const std::uint32_t result = render_context_op_005a4371(ctx, arg0, &arg1);
    render_context_restore_state_005a53cb(saved_state, ctx);
    render_context_release_005a376b(1u, ctx);
    return result;
}

// 0059ed40: page-aligned virtual alloc
void* __cdecl application_main_function_0059ed40(std::uint32_t* p_size) {
    std::uint32_t page_size = g_system_page_size_006af3f8;
    if (page_size == 0u) {
        Win32SystemInfo_0059ed40 info;
        win32_get_system_info_005b21b0(&info);
        page_size = info.dwPageSize;
        g_system_page_size_006af3f8 = page_size;
    }

    const std::uint32_t requested_size = *p_size;
    const std::uint32_t aligned_size = ((requested_size + page_size - 1u) / page_size) * page_size;
    *p_size = aligned_size;

    return win32_virtual_alloc_005b2144(nullptr, aligned_size, 0x3000u /* MEM_COMMIT | MEM_RESERVE */, 0x04u /* PAGE_READWRITE */);
}

} // namespace porsche
