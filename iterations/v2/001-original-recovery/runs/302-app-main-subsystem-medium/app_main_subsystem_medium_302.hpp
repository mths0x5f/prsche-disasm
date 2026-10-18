#ifndef APP_MAIN_SUBSYSTEM_MEDIUM_302_HPP
#define APP_MAIN_SUBSYSTEM_MEDIUM_302_HPP

#include <cstddef>
#include <cstdint>

#ifdef _WIN32
#define CALL_CDECL __cdecl
#define CALL_THISCALL __thiscall
#define CALL_STDCALL __stdcall
#else
#define CALL_CDECL
#define CALL_THISCALL
#define CALL_STDCALL
#endif

// =============================================================================
// Function 1: 0059d8e0 (206 bytes) - asset path locator & file opener helper
// =============================================================================
int CALL_CDECL asset_path_locate_or_open_0059d8e0(const char* filename, int flags);

extern "C" {
    extern std::uint8_t g_flag_006af370;
    extern char g_path_006af168[256];
    extern char g_path_006af26c[256];
    extern const char g_fmt_005cc588[5]; // "%s%s"
    extern void (CALL_CDECL *g_fn_006afbe4)(const char* name, int code);

    int CALL_CDECL sprintf_005a0fbf(char* buffer, const char* format, ...);
    int CALL_CDECL file_exists_00561b80(const char* path);
    int CALL_CDECL file_open_00561ca0(const char* path, int flags);
}

// =============================================================================
// Function 2: 004a6e30 (217 bytes) - display timing sync & channel resetter
// =============================================================================
void CALL_CDECL display_timing_sync_004a6e30();

struct TimingRecord50 {
    std::int32_t field_00; // eax - 0x20 (-1)
    std::int32_t field_04; // eax - 0x1c (0)
    std::int32_t field_08; // eax - 0x18 (0)
    std::uint8_t pad_0c[0x0c];
    std::int32_t field_18; // eax - 0x08 (0 or from g_table_005e8c00)
    std::int32_t field_1c; // eax - 0x04 (-1)
    std::int32_t field_20; // eax (base + 0x20) (-1)
    std::uint8_t pad_24[0x04];
    std::int32_t field_28; // eax + 0x08 (0)
    std::int32_t field_2c; // eax + 0x0c (0x1324)
    std::int32_t field_30; // eax + 0x10 (0)
    std::uint8_t pad_34[0x04];
    std::int32_t field_38; // eax + 0x18 (0)
    std::uint8_t pad_3c[0x0c];
    std::int32_t field_48; // eax + 0x28 (0)
    std::int32_t field_4c; // eax + 0x2c (0)
};

struct TimingRecord38 {
    std::int32_t field_00; // eax - 0x08 (0)
    std::int32_t field_04; // eax - 0x04 (-1)
    std::int32_t field_08; // eax (base + 0x08) (-1)
    std::uint8_t pad_0c[0x04];
    std::int32_t field_10; // eax + 0x08 (0)
    std::int32_t field_14; // eax + 0x0c (0x1324)
    std::int32_t field_18; // eax + 0x10 (0)
    std::uint8_t pad_1c[0x04];
    std::int32_t field_20; // eax + 0x18 (0)
    std::uint8_t pad_24[0x0c];
    std::int32_t field_30; // eax + 0x28 (0)
    std::int32_t field_34; // eax + 0x2c (0)
};

extern "C" {
    extern std::uint32_t g_val_0065741c;
    extern std::uint32_t g_val_00657404;
    extern std::uint32_t g_val_00655e48;
    extern std::uint32_t g_val_00655d54;
    extern std::uint32_t g_val_00655ffc;
    extern std::int32_t  g_val_00655d5c;
    extern std::int32_t  g_val_00655d48;
    extern std::int32_t  g_val_00655d4c;
    extern std::int32_t  g_val_00655d50;
    extern std::uint32_t g_val_00655e44;
    extern std::int32_t  g_count_005e8bfc;
    extern std::int32_t  g_table_005e8c00[16];
    extern TimingRecord50 g_table_00655f38[2];
    extern TimingRecord38 g_table_00655d60[4];
}

// =============================================================================
// Function 3: 0048dad0 (218 bytes) - input message dequeue & post dispatcher
// =============================================================================
void CALL_CDECL input_msg_dequeue_0048dad0();

struct InputMsgLock {
    void* lock_handle;
};

struct InputEventDispatcher {
    void CALL_THISCALL post_event_0048c870(
        std::uint32_t cmd,
        std::uint32_t param1,
        std::uint32_t param2,
        std::uint32_t param3,
        std::uint32_t param4
    );
};

struct InputSubsystem {
    std::uint8_t pad_00[8];
    std::uint32_t field_08;
    InputEventDispatcher* event_dispatcher_0c;
    InputMsgLock* lock_10;
    std::uint8_t pad_14[0x00bc - 0x14];
    std::uint8_t flag_bc;
    std::uint8_t flag_bd;
    std::uint8_t pad_be;
    std::uint8_t flag_bf;
};

extern "C" {
    extern InputSubsystem* g_input_subsystem_00628c70;
    void CALL_CDECL lock_acquire_005322b0(void* lock_handle);
    void CALL_CDECL lock_release_005322c0(void* lock_handle);
}

// =============================================================================
// Function 4: 004a5c30 (231 bytes) - CD-ROM drive detector & launcher spawner
// =============================================================================
void CALL_CDECL cdrom_launcher_spawn_004a5c30();

struct StartupInfoA_004a5c30 {
    std::uint32_t cb;
    char* lpReserved;
    char* lpDesktop;
    char* lpTitle;
    std::uint32_t dwX;
    std::uint32_t dwY;
    std::uint32_t dwXSize;
    std::uint32_t dwYSize;
    std::uint32_t dwXCountChars;
    std::uint32_t dwYCountChars;
    std::uint32_t dwFillAttribute;
    std::uint32_t dwFlags;
    std::uint16_t wShowWindow;
    std::uint16_t cbReserved2;
    std::uint8_t* lpReserved2;
    void* hStdInput;
    void* hStdOutput;
    void* hStdError;
};

struct ProcessInformation_004a5c30 {
    void* hProcess;
    void* hThread;
    std::uint32_t dwProcessId;
    std::uint32_t dwThreadId;
};

typedef unsigned long (CALL_STDCALL *PFN_GetModuleFileNameA_005b2064)(void* hModule, char* lpFilename, unsigned long nSize);
typedef unsigned int (CALL_STDCALL *PFN_GetDriveTypeA_005b2060)(const char* lpRootPathName);
typedef int (CALL_STDCALL *PFN_CreateProcessA_005b204c)(
    const char* lpApplicationName,
    char* lpCommandLine,
    void* lpProcessAttributes,
    void* lpThreadAttributes,
    int bInheritHandles,
    unsigned long dwCreationFlags,
    void* lpEnvironment,
    const char* lpCurrentDirectory,
    StartupInfoA_004a5c30* lpStartupInfo,
    ProcessInformation_004a5c30* lpProcessInformation
);

extern "C" {
    extern const char g_str_porsche_005d1298[8];  // "Porsche"
    extern const char g_fmt_drive_005d1290[5];    // "%c:\\"
    extern char g_fmt_autorun_005d1280[14];       // "%sAutorun.exe"

    extern PFN_GetModuleFileNameA_005b2064 win32_get_module_file_name_005b2064;
    extern PFN_GetDriveTypeA_005b2060 win32_get_drive_type_005b2060;
    extern PFN_CreateProcessA_005b204c win32_create_process_005b204c;

    void CALL_CDECL reg_delete_or_set_005655f0(const char* name);
    int CALL_CDECL isalpha_005a2c24(int c);
    void CALL_CDECL exit_005a246e(int code);
}

#endif // APP_MAIN_SUBSYSTEM_MEDIUM_302_HPP
