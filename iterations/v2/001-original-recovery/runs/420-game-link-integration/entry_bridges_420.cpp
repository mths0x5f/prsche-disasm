#include <cstdint>

// Forward declarations for 418 and 419 functions
namespace porsche {
    void __cdecl frame_root_init_00471b70();
    void __cdecl frame_root_teardown_00471c40();
    extern void* g_frame_service_root_00628960;

    // 419 Bridge: provide frame_service_root_00628960 cell for 00471b60.obj
    std::uint32_t frame_service_root_00628960 = 0;

    // 419 Bridge: startup_sequence_call_00471b70 called by startup_sequence.obj
    void __cdecl startup_sequence_call_00471b70() {
        frame_root_init_00471b70();
    }

    // 418 Bridge: Heap State cells and context accessors
    std::uint32_t printf_initialized_006a57cc = 0;
    std::uint8_t default_heap_state_005e3e18[0x8e8] = {0};
    static std::int32_t g_heap_selector_array[16] = {0};
    void* heap_state_005e4fe8 = default_heap_state_005e3e18;
    std::int32_t* heap_selector_005e4fec = g_heap_selector_array;

    void* __cdecl application_context_heap_state_005e4fe8() {
        return heap_state_005e4fe8;
    }

    unsigned int __cdecl application_context_heap_selector_005e4fec() {
        return reinterpret_cast<unsigned int>(heap_selector_005e4fec);
    }

    void* __cdecl context_selector_pointer_005e4fec() {
        return heap_selector_005e4fec;
    }
}

// 419 / 408 Bridge: C-linkage pipe_00471c40 called by app_loop_post_tick_pipeline_004b68f0
extern "C" {
    void __cdecl pipe_00471c40() {
        porsche::frame_root_teardown_00471c40();
    }

    // 408 C-linkage function
    void __cdecl app_loop_post_tick_pipeline_004b68f0();
}

// 408 Bridge: C++ mangled bridge for entry_bridges_417.obj to forward to the C-linkage implementation
namespace porsche {
    void __cdecl app_loop_post_tick_pipeline_004b68f0() {
        ::app_loop_post_tick_pipeline_004b68f0();
    }
}
