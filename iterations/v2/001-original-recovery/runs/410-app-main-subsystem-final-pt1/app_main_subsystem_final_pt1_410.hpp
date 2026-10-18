#ifndef PORSCHE_APP_MAIN_SUBSYSTEM_FINAL_PT1_410_HPP
#define PORSCHE_APP_MAIN_SUBSYSTEM_FINAL_PT1_410_HPP

#include <cstdint>
#include <cstddef>

#ifndef CALL_CDECL
#define CALL_CDECL __cdecl
#endif

#ifndef CALL_STDCALL
#define CALL_STDCALL __stdcall
#endif

#ifndef CALL_THISCALL
#define CALL_THISCALL __thiscall
#endif

#ifndef CALL_FASTCALL
#define CALL_FASTCALL __fastcall
#endif

namespace porsche {

// =============================================================================
// Function 1: 0056a680 (38 bytes) - Render Frame Counters Initialization
// =============================================================================
extern "C" {
    extern std::uint32_t g_val_006a5dd4;
    extern std::uint32_t g_val_006a5dd8;
    extern std::uint32_t g_val_006a5de0;
    extern std::uint32_t g_val_006a5de4;
    extern std::uint32_t g_val_006a5de8;
    extern std::uint32_t g_val_006b7c40;
    extern std::uint32_t g_val_006a5ddc;

    void CALL_CDECL render_counters_init_0056a680();
}

// =============================================================================
// Function 2: 005a0f98 (39 bytes) - Fast Float-to-Integer Truncation (__ftol)
// =============================================================================
extern "C" {
    std::int64_t CALL_CDECL ftol_005a0f98();
}

// =============================================================================
// Function 3: 00412030 (91 bytes) - Audio Parameters Quad-Value Sync
// =============================================================================
#pragma pack(push, 1)
struct AudioParamEntry005e9420 {
    std::int16_t val_20;
    std::int16_t val_22;
    std::int16_t val_24;
    std::int16_t val_26;
};
#pragma pack(pop)
static_assert(sizeof(AudioParamEntry005e9420) == 8, "AudioParamEntry005e9420 size must be 8");

extern "C" {
    extern std::uint32_t g_val_005e940c;
    extern std::uint32_t g_val_005e9410;
    extern AudioParamEntry005e9420 g_audio_params_005e9420[16];

    void CALL_CDECL sub_005338d0(std::int32_t val);

    void CALL_CDECL audio_parameters_sync_00412030();
}

// =============================================================================
// Function 4: 00414eb0 (196 bytes) - Session & Frame State Initialization
// =============================================================================
extern "C" {
    extern std::uint32_t g_val_00606ab8;
    extern std::uint8_t  g_val_00656858;
    extern std::uint32_t g_val_00606a8c;
    extern std::uint32_t g_val_00606a90;
    extern std::uint32_t g_val_00606a98;
    extern std::uint32_t g_val_00606a9c;
    extern std::uint32_t g_val_00606aa0;
    extern std::uint32_t g_val_00606ac0;
    extern std::uint32_t g_val_00606ac4;
    extern std::uint32_t g_val_00657e6c;
    extern std::uint32_t g_val_00657a34;
    extern std::uint32_t g_val_005e99b8;
    extern std::uint32_t g_val_006280f0;
    extern std::uint32_t g_val_00606ac8;
    extern std::uint32_t g_val_006280ec;
    extern std::uint32_t g_val_006280e8;
    extern std::uint32_t g_val_00628100;
    extern std::uint32_t g_val_006280fc;
    extern std::uint32_t g_val_006280f8;

    void CALL_CDECL sub_004a4780(std::uint32_t arg);
    void CALL_CDECL sub_0044fd00(std::uint32_t arg);
    void CALL_CDECL sub_004030b0();
    void CALL_CDECL sub_004069d0();
    void CALL_CDECL sub_004066d0();
    void CALL_CDECL sub_004110a0();
    void CALL_CDECL sub_00406710();
    void CALL_CDECL sub_004069e0();
    void CALL_CDECL sub_004690a0();
    void CALL_CDECL sub_00412150();

    void CALL_CDECL session_state_init_00414eb0();
}

// =============================================================================
// Function 5: 004dd600 (1012 bytes) - Texture Subsystem Surface & Config Setup
// =============================================================================
struct TextureDriverDispatch {
    void (CALL_STDCALL *pfn_set_state_006bd9b0)(std::uint32_t state);
    void (CALL_STDCALL *pfn_sync_006bd91c)();
    void (CALL_STDCALL *pfn_flush_006bd970)();
    void (CALL_STDCALL *pfn_lock_006bd948)();
    void (CALL_STDCALL *pfn_unlock_006bd978)(std::uint32_t flags);
};

struct TextureHeaderObject {
    std::uint8_t pad[0x14];
    std::uint32_t offset_14;
    std::uint8_t pad_18[0xb4 - 0x18];
    std::uint32_t offset_b4;
};

extern "C" {
    extern void* g_ptr_00628130;
    extern void* g_ptr_0065b32c;
    extern void* g_ptr_0069ed0c;
    extern void* g_ptr_0065b334;
    extern const char g_str_005d99bc[16];
    extern const char g_str_005d99ac[16];

    extern void (CALL_STDCALL *g_pfn_006bd9b0)(std::uint32_t);
    extern void (CALL_STDCALL *g_pfn_006bd91c)();
    extern void (CALL_STDCALL *g_pfn_006bd970)();
    extern void (CALL_STDCALL *g_pfn_006bd948)();
    extern void (CALL_STDCALL *g_pfn_006bd978)(std::uint32_t);

    void CALL_STDCALL sub_00467fc0(std::uint32_t w, std::uint32_t h, std::uint32_t bpp, std::uint32_t flags);
    void CALL_CDECL sub_00560030();
    int  CALL_CDECL sprintf_005a0fbf(char* buf, const char* fmt, ...);
    std::int32_t CALL_CDECL sub_0059dc30(const char* path);
    void CALL_CDECL sub_0059e440(const char* path, void* p);
    void CALL_CDECL sub_004dc850(void* p1, void* p2, std::uint32_t a3, std::uint32_t a4, std::uint32_t a5);
    void CALL_CDECL sub_004237d0(void* p1, std::size_t sz, std::uint32_t a3);
    void CALL_CDECL sub_004dd4a0();
    void* CALL_CDECL sub_0059d8e0(const char* filename, std::uint32_t a2, std::uint32_t a3);
    void CALL_CDECL sub_00534540();
    void CALL_CDECL sub_00534550();
    void CALL_CDECL sub_00563440(void* p, std::int32_t a1, std::int32_t a2, std::int32_t a3, std::int32_t a4);
    int  CALL_CDECL heap_pool_block_free_00531f90(void* p);

    struct AllocDesc {
        void* start;
        void* current;
        void* end;
        std::uint32_t count;

        void CALL_THISCALL init_00403520(std::uint32_t sz);
    };

    struct TextureContextObj {
        void CALL_THISCALL sub_00536080();
        void CALL_THISCALL sub_00536050();
    };

    void CALL_CDECL texture_subsystem_config_004dd600();
}

} // namespace porsche

#endif // PORSCHE_APP_MAIN_SUBSYSTEM_FINAL_PT1_410_HPP
