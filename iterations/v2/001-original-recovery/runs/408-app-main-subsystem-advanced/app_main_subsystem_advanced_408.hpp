#ifndef PORSCHE_APP_MAIN_SUBSYSTEM_ADVANCED_408_HPP
#define PORSCHE_APP_MAIN_SUBSYSTEM_ADVANCED_408_HPP

#include <cstdint>
#include <cstddef>

#ifndef CALL_CDECL
#define CALL_CDECL __cdecl
#endif

#ifndef CALL_THISCALL
#define CALL_THISCALL __thiscall
#endif

#ifndef CALL_STDCALL
#define CALL_STDCALL __stdcall
#endif

namespace porsche {

// =============================================================================
// Function 1: 00531f90 (270 bytes) - Heap Pool Block Deallocator
// =============================================================================
struct HeapBlockHeader {
    std::uint16_t magic;         // +0x00: 'FB' (0x4246) when free
    std::uint16_t flags;         // +0x02: bit 14 (0x4000) = free, low 4 bits = pool index
    std::uint32_t size;          // +0x04: payload size
    HeapBlockHeader* prev_phys;  // +0x08: physical previous block in arena
    HeapBlockHeader* next_phys;  // +0x0c: physical next block in arena
    HeapBlockHeader* free_prev;  // +0x10: free-list previous link
    HeapBlockHeader* free_next;  // +0x14: free-list next link
};

struct HeapPoolDescriptor {
    std::uint8_t pad_00[0x10];       // +0x00..0x0f
    HeapBlockHeader free_head;       // +0x10..0x27: free list sentinel / root node
    std::uint8_t pad_28[0x38 - 0x28];// +0x28..0x37
    void* lock;                      // +0x38: lock handle passed to lock_acquire/release
};

extern "C" {
    extern HeapPoolDescriptor* g_heap_pools_006b4f20[16];
    void CALL_CDECL lock_acquire_005322b0(void* lock_handle);
    void CALL_CDECL lock_release_005322c0(void* lock_handle);
    int CALL_CDECL heap_pool_block_free_00531f90(void* user_ptr);
}

// =============================================================================
// Function 2: 004a6840 (279 bytes) - Display Device Mode Transition Manager
// =============================================================================
struct DisplayDeviceEntry {
    std::int32_t field_00;   // initialized to -1 (0xffffffff)
    std::uint32_t pad_04;
    std::uint32_t field_08;  // initialized to 0
    std::uint32_t pad_0c;
};

extern "C" {
    extern std::uint32_t g_val_00657c98;
    extern std::uint32_t g_val_00657c9c;
    extern std::uint32_t g_val_00657c94;
    extern std::uint32_t g_val_00655d38;
    extern std::uint8_t  g_val_00655d3c;
    extern std::uint32_t g_val_00655d34;
    extern void*         g_val_00655d44;
    extern std::uint32_t g_val_005d1734;
    extern DisplayDeviceEntry g_devices_006564a0[8];

    extern const char g_str_tag_005d13ec[12];
    extern const char g_str_tag_005d13f8[12];

    void* CALL_CDECL heap_pool_alloc_00531ca0(const char* tag, std::uint32_t size, std::uint32_t flags);
    std::uint8_t CALL_CDECL display_mode_probe_004a66b0();
    void CALL_CDECL display_init_mode_004ae100(std::uint32_t mode, std::uint32_t arg2, const char* tag);
    void CALL_CDECL display_subsystem_004a8b80();
    void CALL_CDECL display_subsystem_004ae2b0();
    void CALL_CDECL display_subsystem_004ab4b0();
    void CALL_CDECL display_subsystem_00565890();

    void CALL_CDECL display_device_transition_004a6840(std::uint32_t mode, std::uint32_t arg2);
}

// =============================================================================
// Function 3: 004b67b0 (303 bytes) - Pre-Simulation-Tick Loop Pipeline
// =============================================================================
struct SimSubsystem_00536080 {
    void CALL_THISCALL step_00536080();
};

struct PreTickTargetSubsystem {
    std::uint32_t pad_00;
    SimSubsystem_00536080* handle_04;
};

struct InputSubsystem_408 {
    std::uint8_t pad_00[8];
    void* queue_08;
    std::uint8_t pad_0c[0xbf - 0x0c];
    std::uint8_t flag_bf;
};

extern "C" {
    extern PreTickTargetSubsystem* g_ptr_0069ed0c;
    extern std::uint32_t g_val_00606ac0;
    extern std::uint32_t g_val_00606ac4;
    extern const char g_str_005d6e3c[16];
    extern InputSubsystem_408* g_input_subsystem_00628c70;
    extern void* g_data_00657444;

    void CALL_CDECL pipe_004690f0();
    void CALL_CDECL pipe_0044dfb0();
    void CALL_CDECL pipe_0056a490();
    void CALL_CDECL pipe_00516950();
    void CALL_CDECL pipe_00413cf0();
    void CALL_CDECL pipe_00427a60();
    void CALL_CDECL phase_notify_004a4a70(int phase);
    void CALL_CDECL pipe_004a4700();
    void CALL_CDECL pipe_004b0d70();
    void CALL_CDECL pipe_004affd0();
    void CALL_CDECL pipe_00468fb0();
    void CALL_CDECL pipe_00471b70();
    void CALL_CDECL pipe_004a8cd0();
    void CALL_CDECL pipe_00414db0();
    void CALL_CDECL pipe_004690d0();
    void CALL_CDECL pipe_00434a90();
    void CALL_CDECL pipe_00424460();
    void CALL_CDECL pipe_00415dc0();
    void CALL_CDECL pipe_004b0fa0();
    void CALL_CDECL pipe_004121b0();
    std::uint32_t CALL_CDECL pipe_00569a90();
    void CALL_CDECL heap_trace_log_005a177b(const char* tag, std::uint32_t val);
    void CALL_CDECL input_poll_update_0048cdf0();
    void CALL_CDECL pipe_0044df10(void* param);
    void CALL_CDECL pipe_004691c0();

    void CALL_CDECL app_loop_pre_tick_pipeline_004b67b0();
}

// =============================================================================
// Function 4: 004b4b80 (331 bytes) - Window / Engine Event Filter & Dispatcher
// =============================================================================
struct EventRoutingEntry {
    std::uint32_t id;
    std::uint8_t* destination_buffer;
    void* unk_handler;
};

struct EventCallbackEntry {
    void (CALL_CDECL *callback)(std::uint32_t param);
    std::uint32_t pad_04;
    std::uint32_t pad_08;
};

extern "C" {
    extern const EventRoutingEntry g_event_routes_005d1e40[16];
    extern std::uint32_t g_event_history_005e9130[256];
    extern const EventCallbackEntry g_event_callbacks_005cc5d0[32];

    void CALL_CDECL window_event_filter_dispatch_004b4b80(const std::uint32_t* msg);
}

// =============================================================================
// Function 5: 004b68f0 (337 bytes) - Post-Simulation-Tick Loop Pipeline
// =============================================================================
struct PostTickSubObject {
    std::uint32_t field_00;
    std::uint32_t pad_04;
    std::uint32_t field_08;
    std::uint8_t  pad_0c[0x17c - 0x0c];
    char name_17c[256];
    std::uint8_t  pad_27c[0x534 - 0x27c];
    char text_534[256];
};

struct PostTickTargetObject {
    std::uint8_t  pad_00[0x52c];
    std::uint32_t field_52c;
    std::uint8_t  pad_530[0x558 - 0x530];
    PostTickSubObject* sub_558;
    std::uint8_t  pad_55c[0xad4 - 0x55c];
    union {
        std::uint32_t payload_ad4[150]; // 0x96 dwords (600 bytes) at +0xad4
        struct {
            std::uint8_t  pad_ad4[0xb6c - 0xad4];
            std::uint32_t field_b6c;              // +0xb6c
            std::uint32_t field_b70;              // +0xb70
            std::uint32_t field_b74;              // +0xb74
            char          name_b78[64];           // +0xb78
            char          text_bb8[64];           // +0xbb8
        };
    };
};

extern "C" {
    extern std::int32_t g_count_00658080;
    extern PostTickTargetObject* g_ptrs_005e8b34[16];
    extern std::uint32_t g_data_005e75a0[16 * 150]; // 16 entries of 600 bytes
    extern const char g_str_005d6e68[16];
    extern const char g_str_005d6e60[16];

    void CALL_CDECL pipe_00413fd0();
    void CALL_CDECL pipe_004a8a80();
    void CALL_CDECL pipe_004afe50();
    void CALL_CDECL pipe_004a4760();
    void CALL_CDECL pipe_00414f80();
    void CALL_CDECL pipe_00471c40();
    void CALL_CDECL pipe_004642f0();
    void CALL_CDECL pipe_00425330();
    void CALL_CDECL pipe_00412cd0();
    void CALL_CDECL pipe_00412e60();

    void CALL_CDECL app_loop_post_tick_pipeline_004b68f0();
}

} // namespace porsche

#endif // PORSCHE_APP_MAIN_SUBSYSTEM_ADVANCED_408_HPP
