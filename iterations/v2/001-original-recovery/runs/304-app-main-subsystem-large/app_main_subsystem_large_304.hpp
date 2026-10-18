#ifndef PORSCHE_APP_MAIN_SUBSYSTEM_LARGE_304_HPP
#define PORSCHE_APP_MAIN_SUBSYSTEM_LARGE_304_HPP

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
// Function 1: 0059d650 (625 bytes) - CD-ROM Path Resolver & Game Root Discovery
// =============================================================================
extern "C" {
    extern std::uint8_t g_val_006af370;
    extern std::uint8_t g_val_006af168;
    extern char         g_val_006af26c[256];
    extern std::uint8_t g_val_006af371;

    extern const char g_str_005d1290[8];   // "%c:\\"
    extern const char g_str_005cc588[8];   // "%s%s"
    extern const char g_str_005d6e14[64];  // game relative probe path
    extern const char g_str_005e3cb8[128]; // registry key path
    extern const char g_str_005d1298[32];  // registry value name

    using PfnGetModuleFileNameA = std::uint32_t (CALL_STDCALL *)(void* hModule, char* lpFilename, std::uint32_t nSize);
    using PfnGetDriveTypeA = std::uint32_t (CALL_STDCALL *)(const char* lpRootPathName);
    using PfnMessageBoxA = int (CALL_STDCALL *)(void* hWnd, const char* lpText, const char* lpCaption, std::uint32_t uType);

    extern PfnGetModuleFileNameA g_pfn_GetModuleFileNameA_005b2064;
    extern PfnGetDriveTypeA      g_pfn_GetDriveTypeA_005b2060;
    extern PfnMessageBoxA        g_pfn_MessageBoxA_005b2270;

    int CALL_CDECL sprintf_005a0fbf(char* buffer, const char* format, ...);
    int CALL_CDECL file_exists_00561b80(const char* path);

    void CALL_CDECL cdrom_path_resolve_0059d650();
}

// =============================================================================
// Function 2: 004a88a0 (471 bytes) - Display Mode Probe & Capabilities Sync
// =============================================================================
struct DisplaySlot0065653c {
    std::int32_t field_00; // -1 when empty
    std::int32_t field_04;
    std::int32_t field_08;
    std::int32_t field_0c;
    void*        buffer_10;
    std::uint32_t field_14;
};

struct DisplaySlot00656180 {
    std::int32_t field_00;
    std::int32_t field_04;
};

struct DisplayTarget0065808c {
    std::uint32_t handle;
    std::uint32_t pad_04;
    std::uint32_t type;    // checked against 2
    std::uint8_t  pad_0c[0x580 - 0x0c];
};

extern "C" {
    extern std::uint32_t g_val_00657c94;
    extern DisplaySlot0065653c g_entries_0065653c[32];
    extern DisplaySlot00656180 g_entries_00656180[73];
    extern std::uint8_t  g_val_00656868;
    extern std::uint8_t  g_val_00656869;
    extern std::uint32_t g_val_005d1734;
    extern std::int32_t  g_val_005d1750;
    extern std::uint32_t g_val_00657a24;
    extern std::int32_t  g_count_00658080;
    extern DisplayTarget0065808c g_targets_0065808c[16];
    extern std::int32_t  g_val_005e99f4;
    extern std::uint32_t g_val_00657cb8;
    extern std::uint32_t g_val_00657cbc;

    void CALL_CDECL sub_004ad510();
    void CALL_CDECL sub_004ae3c0(std::uint32_t arg);
    void CALL_CDECL sub_004af900(std::uint32_t a1, std::uint32_t a2);
    void CALL_CDECL sub_004afd30();
    void CALL_CDECL sub_005659f0(std::uint32_t handle);
    int  CALL_CDECL heap_pool_block_free_00531f90(void* ptr);
    void CALL_CDECL sub_00565d60(std::uint32_t handle);
    void CALL_CDECL sub_00565cd0(std::uint32_t a1, std::uint32_t a2);
    void CALL_CDECL sub_004a8660();
    std::uint32_t CALL_CDECL timer_0053c2e0();
    void CALL_CDECL sub_004b0a20();
    void CALL_CDECL sub_005366e0(std::uint32_t val);
    std::int32_t CALL_CDECL sub_004a8570(std::uint32_t a1, std::uint32_t a2, std::uint32_t a3);
    std::int32_t CALL_CDECL sub_004b04d0(std::uint32_t handle, std::uint32_t flag);
    void CALL_CDECL sub_004af5c0();
    void CALL_CDECL sub_004ae470(std::uint32_t a1, void* a2);
    void CALL_CDECL sub_004ae4d0(std::uint32_t a1, std::uint32_t a2);

    void CALL_CDECL display_mode_probe_sync_004a88a0();
}

// =============================================================================
// Function 3: 004640b0 (564 bytes) - Audio Listener & Emitter Transform Sync
// =============================================================================
struct AudioEmitterObject {
    std::uint8_t  pad_00[0x330];
    float         position[3];     // +0x330
    float         pad_33c[10];     // +0x33c..0x363
    float         orientation[9];  // +0x364
    std::uint8_t  pad_388[0x10e8 - 0x388];
    float         listener_pos[3]; // +0x10e8
    float         listener_vel[3]; // +0x10f4
};

struct AudioContextObject {
    std::uint8_t data[0x30];

    void ctor_00473100(std::uint32_t flag);
    void copy_00473190(void* src);
};

struct AudioListenerSlot {
    AudioEmitterObject* emitter_prev; // offset 0x00 (ebp - 0x14)
    AudioEmitterObject* emitter_curr; // offset 0x04 (ebp - 0x10)
    std::uint8_t        pad_08[12];   // offset 0x08..0x13
    float               pos1[3];      // offset 0x14 (ebp + 0x00)
    std::uint32_t       field_0c;     // offset 0x20 (ebp + 0x0c)
    float               pos2[3];      // offset 0x24 (ebp + 0x10)
    std::uint32_t       field_1c;     // offset 0x30 (ebp + 0x1c)
    float               val_20;       // offset 0x34 (ebp + 0x20)
    float               val_24;       // offset 0x38 (ebp + 0x24)
    float               val_28;       // offset 0x3c (ebp + 0x28)
    float               val_2c;       // offset 0x40 (ebp + 0x2c)
    std::uint8_t        pad_30[0x44 - 0x30]; // offset 0x44..0x57
    float               val_44;       // offset 0x58 (ebp + 0x44)
    float               val_48;       // offset 0x5c (ebp + 0x48)
    std::uint8_t        pad_4c[0x64 - 0x4c]; // offset 0x60..0x77
    float               val_64;       // offset 0x78 (ebp + 0x64)
    float               matrix[9];    // offset 0x7c (ebp + 0x68)
    std::uint32_t       field_8c;     // offset 0xa0 (ebp + 0x8c)
    float               pos3[3];      // offset 0xa4 (ebp + 0x90)
    float               pos4[3];      // offset 0xb0 (ebp + 0x9c)
    std::uint16_t       field_a8;     // offset 0xbc (ebp + 0xa8)
    std::uint16_t       field_aa;     // offset 0xbe (ebp + 0xaa)
    std::uint8_t        field_ac;     // offset 0xc0 (ebp + 0xac)
    std::uint8_t        field_ad;     // offset 0xc1 (ebp + 0xad)
    std::uint8_t        field_ae;     // offset 0xc2 (ebp + 0xae)
    std::uint8_t        field_af;     // offset 0xc3 (ebp + 0xaf)
    std::uint16_t       field_b0;     // offset 0xc4 (ebp + 0xb0)
    std::uint16_t       field_b2;     // offset 0xc6 (ebp + 0xb2)
    std::uint16_t       field_b4;     // offset 0xc8 (ebp + 0xb4)
    std::uint8_t        field_b6;     // offset 0xca (ebp + 0xb6)
    std::uint8_t        pad_b7;       // offset 0xcb
    float               field_b8;     // offset 0xcc (ebp + 0xb8)
    std::uint32_t       field_bc;     // offset 0xd0 (ebp + 0xbc)
    std::uint8_t        field_c0;     // offset 0xd4 (ebp + 0xc0)
    std::uint8_t        pad_c1[3];    // offset 0xd5..0xd7
    std::uint32_t       field_c4;     // offset 0xd8 (ebp + 0xc4)
    AudioContextObject  ctx_c8;       // offset 0xdc (ebp + 0xc8)
};
static_assert(sizeof(AudioListenerSlot) == 0x10c, "AudioListenerSlot must be 0x10c bytes");

extern "C" {
    extern std::uint32_t g_val_00657404;
    extern std::uint32_t g_val_0065741c;
    extern AudioEmitterObject* g_emitters_005e8c00[16];
    extern AudioListenerSlot g_listeners_00627e94[8];
    extern std::uint8_t  g_val_005cf5d8;
    extern void*         g_val_005cf760;
    extern void*         g_val_00657444;
    extern float         g_val_005cf620[3];
    extern float         g_val_00627ecc[3];
    extern std::uint32_t g_val_005cf584;

    void CALL_CDECL sub_00465cf0(std::uint32_t index);
    std::int32_t CALL_CDECL sub_005ae3c0(void* p1, void* p2);
    void CALL_CDECL sub_00463c30();
    void CALL_CDECL pipe_00516950();

    void CALL_CDECL audio_listener_update_004640b0();
}

// =============================================================================
// Function 4: 00467470 (642 bytes) - User Input Subsystem & Controller Init
// =============================================================================
struct InputContextVtable {
    void (CALL_FASTCALL *virtual_action_00)(void* self);
};

struct InputContext {
    InputContextVtable* vtable;
    std::uint8_t pad[0x118 - sizeof(void*)];

    InputContext* ctor_00467700(void* p1, void* p2);
    void sub_004b7240(std::uint32_t id, void* buffer);
    std::uint32_t sub_004b7340(std::uint32_t id);
    void sub_004b7220();
};

struct ControllerDevice {
    std::uint8_t pad_00[0x74];
    std::uint32_t field_74;
    std::uint32_t pad_78;
    std::uint32_t field_7c;

    ControllerDevice* ctor_004677e0(void* dev_name, std::uint32_t b1, std::uint32_t b2, void* buf);
};

extern "C" {
    extern void* g_str_005d6f20;
    extern void* g_str_005d6f1c;
    extern InputContext* g_ptr_0065b39c;
    extern char g_str_00657a38[64];
    extern const char g_str_005cf7bc[64];
    extern const char g_str_005cf7b4[64];
    extern const char g_str_005cf78c[64];
    extern const char g_str_005cf788[64];
    extern const char g_str_005ccc2c[64];
    extern const char g_str_005cf784[64];
    extern std::uint32_t g_val_00657a4c;
    extern std::uint32_t g_val_00657a48;
    extern std::uint32_t g_val_00657a58;
    extern const char g_str_005cf77c[64];
    extern const char* g_str_0065b304;
    extern ControllerDevice* g_ptr_00628130;

    void* CALL_CDECL operator_new_0059ef90(std::size_t size);
    void CALL_CDECL sub_005a246e(std::uint32_t code);
    void CALL_CDECL sub_004b70d0(std::uint32_t a1, std::uint32_t a2);
    void CALL_CDECL sub_00465df0();
    void CALL_CDECL sub_00449b40();

    void CALL_CDECL input_subsystem_init_00467470();
}

} // namespace porsche

#endif // PORSCHE_APP_MAIN_SUBSYSTEM_LARGE_304_HPP
