"""Generate complete Run 305 fixture and experiment files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / "local/game/Porsche.exe"
data = EXE.read_bytes()

def get_bytes_c(va, sz):
    off = va - 0x400000
    b = data[off:off+sz]
    lines = []
    for i in range(0, len(b), 16):
        chunk = b[i:i+16]
        hexs = ', '.join(f'0x{byte:02x}' for byte in chunk)
        lines.append(f'    {hexs},')
    return '\n'.join(lines)

b_56a680 = get_bytes_c(0x0056a680, 38)
b_5a0f98 = get_bytes_c(0x005a0f98, 39)
b_412030 = get_bytes_c(0x00412030, 91)
b_414eb0 = get_bytes_c(0x00414eb0, 196)
b_4dd600 = get_bytes_c(0x004dd600, 1012)

FIXTURE_CPP = f"""#include "app_main_subsystem_final_pt1_305.hpp"
#include <windows.h>
#include <cstdint>
#include <cstddef>
#include <cstdarg>

extern "C" int _fltused = 0x9876;
#pragma function(memcpy, memset)
extern "C" void* memcpy(void* dst, const void* src, size_t count) {{
    auto d = static_cast<unsigned char*>(dst);
    auto s = static_cast<const unsigned char*>(src);
    for (size_t i = 0; i < count; ++i) d[i] = s[i];
    return dst;
}}
extern "C" void* memset(void* dst, int val, size_t count) {{
    auto d = static_cast<unsigned char*>(dst);
    for (size_t i = 0; i < count; ++i) d[i] = static_cast<unsigned char>(val);
    return dst;
}}

namespace porsche {{

using U = std::uint32_t;

struct CallTrace {{
    U count;
    U tag[1024];
    U arg1[1024];
    U arg2[1024];
    U arg3[1024];
    void* this_ptr[1024];
}};

static CallTrace g_trace;
static CallTrace s_trace_orig;
static CallTrace s_trace_cpp;

static void reset_trace() {{
    g_trace.count = 0;
    for (int i = 0; i < 1024; ++i) {{
        g_trace.tag[i] = 0;
        g_trace.arg1[i] = 0;
        g_trace.arg2[i] = 0;
        g_trace.arg3[i] = 0;
        g_trace.this_ptr[i] = nullptr;
    }}
}}

static void record_call(U tag, U a1 = 0, U a2 = 0, U a3 = 0, void* self = nullptr) {{
    if (g_trace.count < 1024) {{
        U idx = g_trace.count++;
        g_trace.tag[idx] = tag;
        g_trace.arg1[idx] = a1;
        g_trace.arg2[idx] = a2;
        g_trace.arg3[idx] = a3;
        g_trace.this_ptr[idx] = self;
    }}
}}

// -----------------------------------------------------------------------------
// Global variables
// -----------------------------------------------------------------------------

// Func 1: 0056a680
U g_val_006a5dd4 = 0;
U g_val_006a5dd8 = 0;
U g_val_006a5de0 = 0;
U g_val_006a5de4 = 0;
U g_val_006a5de8 = 0;
U g_val_006b7c40 = 0x12345678;
U g_val_006a5ddc = 0;

// Func 3: 00412030
U g_val_005e940c = 0;
U g_val_005e9410 = 0;
AudioParamEntry005e9420 g_audio_params_005e9420[16] = {{}};

void CALL_CDECL sub_005338d0(std::int32_t val) {{
    record_call(0x5338d0, static_cast<U>(val));
}}

// Func 4: 00414eb0
U g_val_00606ab8 = 0;
std::uint8_t g_val_00656858 = 0;
U g_val_00606a8c = 0;
U g_val_00606a90 = 0;
U g_val_00606a98 = 0;
U g_val_00606a9c = 0;
U g_val_00606aa0 = 0;
U g_val_00606ac0 = 0;
U g_val_00606ac4 = 0;
U g_val_00657e6c = 0;
U g_val_00657a34 = 0x55aa55aa;
U g_val_005e99b8 = 0x99887766;
U g_val_006280f0 = 0;
U g_val_00606ac8 = 0;
U g_val_006280ec = 0;
U g_val_006280e8 = 0;
U g_val_00628100 = 0;
U g_val_006280fc = 0;
U g_val_006280f8 = 0;

void CALL_CDECL sub_004a4780(U arg) {{ record_call(0x4a4780, arg); }}
void CALL_CDECL sub_0044fd00(U arg) {{ record_call(0x44fd00, arg); }}
void CALL_CDECL sub_004030b0() {{ record_call(0x4030b0); }}
void CALL_CDECL sub_004069d0() {{ record_call(0x4069d0); }}
void CALL_CDECL sub_004066d0() {{ record_call(0x4066d0); }}
void CALL_CDECL sub_004110a0() {{ record_call(0x4110a0); }}
void CALL_CDECL sub_00406710() {{ record_call(0x406710); }}
void CALL_CDECL sub_004069e0() {{ record_call(0x4069e0); }}
void CALL_CDECL sub_004690a0() {{ record_call(0x4690a0); }}
void CALL_CDECL sub_00412150() {{ record_call(0x412150); }}

// Func 5: 004dd600
static char s_mock_device[0x80] = {{}};
void* g_ptr_00628130 = s_mock_device;
static char s_mock_path_str1[32] = "tex_path1";
void* g_ptr_0065b32c = s_mock_path_str1;
static char s_mock_obj_c[16] = {{}};
static void* s_mock_obj_c_ptr[2] = {{ nullptr, s_mock_obj_c }};
void* g_ptr_0069ed0c = s_mock_obj_c_ptr;
static char s_mock_path_str2[32] = "tex_path2";
void* g_ptr_0065b334 = s_mock_path_str2;
const char g_str_005d99bc[16] = "%s.qfs";
const char g_str_005d99ac[16] = "%s.tga";

static void CALL_STDCALL mock_set_state_006bd9b0(U s) {{ record_call(0x6bd9b0, s); }}
static void CALL_STDCALL mock_sync_006bd91c() {{ record_call(0x6bd91c); }}
static void CALL_STDCALL mock_flush_006bd970() {{ record_call(0x6bd970); }}
static void CALL_STDCALL mock_lock_006bd948() {{ record_call(0x6bd948); }}
static void CALL_STDCALL mock_unlock_006bd978(U f) {{ record_call(0x6bd978, f); }}

void (CALL_STDCALL *g_pfn_006bd9b0)(U) = mock_set_state_006bd9b0;
void (CALL_STDCALL *g_pfn_006bd91c)() = mock_sync_006bd91c;
void (CALL_STDCALL *g_pfn_006bd970)() = mock_flush_006bd970;
void (CALL_STDCALL *g_pfn_006bd948)() = mock_lock_006bd948;
void (CALL_STDCALL *g_pfn_006bd978)(U) = mock_unlock_006bd978;

void CALL_STDCALL sub_00467fc0(U w, U h, U bpp, U flags) {{ record_call(0x467fc0, w, h, bpp); }}
void CALL_CDECL sub_00560030() {{ record_call(0x560030); }}
int CALL_CDECL sprintf_005a0fbf(char* buf, const char* fmt, ...) {{
    va_list ap;
    va_start(ap, fmt);
    int res = wvsprintfA(buf, fmt, ap);
    va_end(ap);
    record_call(0x5a0fbf, static_cast<U>(buf[0]));
    return res;
}}
void CALL_THISCALL TextureContextObj::sub_00536080() {{ record_call(0x536080, reinterpret_cast<U>(this)); }}
void CALL_THISCALL TextureContextObj::sub_00536050() {{ record_call(0x536050, reinterpret_cast<U>(this)); }}

static std::int32_t s_mock_file_exists_tex = 1;
std::int32_t CALL_CDECL sub_0059dc30(const char* path) {{
    record_call(0x59dc30, static_cast<U>(path[0]));
    return s_mock_file_exists_tex;
}}

static char s_mock_alloc_buf[256];
void CALL_THISCALL AllocDesc::init_00403520(U sz) {{
    record_call(0x403520, sz);
    this->start = s_mock_alloc_buf;
    this->current = s_mock_alloc_buf;
    this->end = s_mock_alloc_buf + sizeof(s_mock_alloc_buf);
    this->count = 0;
}}
void CALL_CDECL sub_0059e440(const char* path, void* p) {{ record_call(0x59e440, static_cast<U>(path[0])); }}
void CALL_CDECL sub_004dc850(void* p1, void* p2, U a3, U a4, U a5) {{ record_call(0x4dc850, a3, a4, a5); }}
void CALL_CDECL sub_004237d0(void* p1, std::size_t sz, U a3) {{ record_call(0x4237d0, static_cast<U>(sz), a3); }}
void CALL_CDECL sub_004dd4a0() {{ record_call(0x4dd4a0); }}

static char s_mock_tex_header[0x1000];
void* CALL_CDECL sub_0059d8e0(const char* fn, U a2, U a3) {{
    record_call(0x59d8e0, static_cast<U>(fn[0]), a2, a3);
    for (int i = 0; i < 0x1000 / 4; ++i) {{
        reinterpret_cast<U*>(s_mock_tex_header)[i] = 0x200;
    }}
    return s_mock_tex_header;
}}
void CALL_CDECL sub_00534540() {{ record_call(0x534540); }}
void CALL_CDECL sub_00534550() {{ record_call(0x534550); }}
void CALL_CDECL sub_00563440(void* p, std::int32_t a1, std::int32_t a2, std::int32_t a3, std::int32_t a4) {{
    record_call(0x563440, static_cast<U>(a1), static_cast<U>(a2), static_cast<U>(a3));
}}
int CALL_CDECL heap_pool_block_free_00531f90(void* p) {{
    record_call(0x531f90, reinterpret_cast<U>(p));
    return 1;
}}

}} // namespace porsche

// -----------------------------------------------------------------------------
// Slab memory & patch setup
// -----------------------------------------------------------------------------
#define require(cond) do {{ if (!(cond)) ExitProcess(static_cast<unsigned long>(__LINE__)); }} while(0)

const porsche::U OFF_0056a680 = 0x0000;
const porsche::U OFF_005a0f98 = 0x0100;
const porsche::U OFF_00412030 = 0x0200;
const porsche::U OFF_00414eb0 = 0x0300;
const porsche::U OFF_004dd600 = 0x0500;

alignas(4096) static std::uint8_t s_static_slab[0x1000];
static std::uint8_t* g_slab = nullptr;
static int g_cases_passed = 0;

static void mem_fill(void* dst, std::uint8_t val, std::size_t sz) {{
    auto d = static_cast<std::uint8_t*>(dst);
    for (std::size_t i = 0; i < sz; ++i) d[i] = val;
}}

static void write_u32_raw(std::uint8_t* dst, porsche::U val) {{
    dst[0] = static_cast<std::uint8_t>(val & 0xFF);
    dst[1] = static_cast<std::uint8_t>((val >> 8) & 0xFF);
    dst[2] = static_cast<std::uint8_t>((val >> 16) & 0xFF);
    dst[3] = static_cast<std::uint8_t>((val >> 24) & 0xFF);
}}

template<typename Mfn>
inline porsche::U mfn_to_u32(Mfn mfn) {{
    union {{
        Mfn f;
        porsche::U u;
    }} cvt;
    cvt.f = mfn;
    return cvt.u;
}}

namespace porsche {{

void init_slab() {{
    g_slab = s_static_slab;
    mem_fill(g_slab, 0xcc, sizeof(s_static_slab));

    HANDLE hFile = CreateFileA("Porsche.exe", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {{
        hFile = CreateFileA("../../local/game/Porsche.exe", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    }}
    if (hFile == INVALID_HANDLE_VALUE) {{
        hFile = CreateFileA("D:\\\\projetos\\\\prsche-disasm\\\\local\\\\game\\\\Porsche.exe", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    }}
    require(hFile != INVALID_HANDLE_VALUE);

    auto load_pe = [hFile](U va, U off_slab, U sz) {{
        DWORD read_sz = 0;
        SetFilePointer(hFile, va - 0x400000, NULL, FILE_BEGIN);
        ReadFile(hFile, g_slab + off_slab, sz, &read_sz, NULL);
        require(read_sz == sz);
    }};

    load_pe(0x0056a680, OFF_0056a680, 38);
    load_pe(0x005a0f98, OFF_005a0f98, 39);
    load_pe(0x00412030, OFF_00412030, 91);
    load_pe(0x00414eb0, OFF_00414eb0, 196);
    load_pe(0x004dd600, OFF_004dd600, 1012);

    CloseHandle(hFile);

    // 1) 0056a680 (38 bytes)
    write_u32_raw(g_slab + OFF_0056a680 + 0x03, reinterpret_cast<U>(&g_val_006a5dd4));
    write_u32_raw(g_slab + OFF_0056a680 + 0x08, reinterpret_cast<U>(&g_val_006a5dd8));
    write_u32_raw(g_slab + OFF_0056a680 + 0x0d, reinterpret_cast<U>(&g_val_006a5de0));
    write_u32_raw(g_slab + OFF_0056a680 + 0x12, reinterpret_cast<U>(&g_val_006a5de4));
    write_u32_raw(g_slab + OFF_0056a680 + 0x17, reinterpret_cast<U>(&g_val_006a5de8));
    write_u32_raw(g_slab + OFF_0056a680 + 0x1c, reinterpret_cast<U>(&g_val_006b7c40));
    write_u32_raw(g_slab + OFF_0056a680 + 0x21, reinterpret_cast<U>(&g_val_006a5ddc));

    // 2) 005a0f98 (39 bytes) - no relocations

    // 3) 00412030 (91 bytes)
    write_u32_raw(g_slab + OFF_00412030 + 0x01, reinterpret_cast<U>(&g_val_005e940c));
    write_u32_raw(g_slab + OFF_00412030 + 0x0a, reinterpret_cast<U>(&g_val_005e9410));
    write_u32_raw(g_slab + OFF_00412030 + 0x12, reinterpret_cast<U>(&g_audio_params_005e9420[0].val_24));
    U c3_1 = reinterpret_cast<U>(g_slab + OFF_00412030 + 0x17);
    write_u32_raw(g_slab + OFF_00412030 + 0x18, reinterpret_cast<U>(&sub_005338d0) - (c3_1 + 5));
    write_u32_raw(g_slab + OFF_00412030 + 0x1e, reinterpret_cast<U>(&g_val_005e9410));
    write_u32_raw(g_slab + OFF_00412030 + 0x26, reinterpret_cast<U>(&g_audio_params_005e9420[0].val_22));
    U c3_2 = reinterpret_cast<U>(g_slab + OFF_00412030 + 0x2b);
    write_u32_raw(g_slab + OFF_00412030 + 0x2c, reinterpret_cast<U>(&sub_005338d0) - (c3_2 + 5));
    write_u32_raw(g_slab + OFF_00412030 + 0x32, reinterpret_cast<U>(&g_val_005e9410));
    write_u32_raw(g_slab + OFF_00412030 + 0x3a, reinterpret_cast<U>(&g_audio_params_005e9420[0].val_20));
    U c3_3 = reinterpret_cast<U>(g_slab + OFF_00412030 + 0x3f);
    write_u32_raw(g_slab + OFF_00412030 + 0x40, reinterpret_cast<U>(&sub_005338d0) - (c3_3 + 5));
    write_u32_raw(g_slab + OFF_00412030 + 0x45, reinterpret_cast<U>(&g_val_005e9410));
    write_u32_raw(g_slab + OFF_00412030 + 0x4d, reinterpret_cast<U>(&g_audio_params_005e9420[0].val_26));
    U c3_4 = reinterpret_cast<U>(g_slab + OFF_00412030 + 0x52);
    write_u32_raw(g_slab + OFF_00412030 + 0x53, reinterpret_cast<U>(&sub_005338d0) - (c3_4 + 5));

    // 4) 00414eb0 (196 bytes)
    write_u32_raw(g_slab + OFF_00414eb0 + 0x04, reinterpret_cast<U>(&g_val_00606ab8));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x0d, reinterpret_cast<U>(&g_val_00656858));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x12, reinterpret_cast<U>(&g_val_00606a8c));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x17, reinterpret_cast<U>(&g_val_00606a90));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x1c, reinterpret_cast<U>(&g_val_00606a98));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x21, reinterpret_cast<U>(&g_val_00606a9c));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x26, reinterpret_cast<U>(&g_val_00606aa0));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x2b, reinterpret_cast<U>(&g_val_00606ac0));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x30, reinterpret_cast<U>(&g_val_00606ac4));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x35, reinterpret_cast<U>(&g_val_00657e6c));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x3a, reinterpret_cast<U>(&g_val_00657a34));
    U c4_1 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x3f);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x40, reinterpret_cast<U>(&sub_004a4780) - (c4_1 + 5));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x46, reinterpret_cast<U>(&g_val_00657a34));
    U c4_2 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x4b);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x4c, reinterpret_cast<U>(&sub_0044fd00) - (c4_2 + 5));
    U c4_3 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x53);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x54, reinterpret_cast<U>(&sub_004030b0) - (c4_3 + 5));
    U c4_4 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x58);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x59, reinterpret_cast<U>(&sub_004069d0) - (c4_4 + 5));
    U c4_5 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x5d);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x5e, reinterpret_cast<U>(&sub_004066d0) - (c4_5 + 5));
    U c4_6 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x62);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x63, reinterpret_cast<U>(&sub_004110a0) - (c4_6 + 5));
    U c4_7 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x67);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x68, reinterpret_cast<U>(&sub_00406710) - (c4_7 + 5));
    U c4_8 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x6c);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x6d, reinterpret_cast<U>(&sub_004069e0) - (c4_8 + 5));
    U c4_9 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x71);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x72, reinterpret_cast<U>(&sub_004690a0) - (c4_9 + 5));
    U c4_10 = reinterpret_cast<U>(g_slab + OFF_00414eb0 + 0x76);
    write_u32_raw(g_slab + OFF_00414eb0 + 0x77, reinterpret_cast<U>(&sub_00412150) - (c4_10 + 5));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x7d, reinterpret_cast<U>(&g_val_005e99b8));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x83, reinterpret_cast<U>(&g_val_006280f0));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x8d, reinterpret_cast<U>(&g_val_00606ac8));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x93, reinterpret_cast<U>(&g_val_006280ec));
    write_u32_raw(g_slab + OFF_00414eb0 + 0x9d, reinterpret_cast<U>(&g_val_006280e8));
    write_u32_raw(g_slab + OFF_00414eb0 + 0xa7, reinterpret_cast<U>(&g_val_00628100));
    write_u32_raw(g_slab + OFF_00414eb0 + 0xb1, reinterpret_cast<U>(&g_val_006280fc));
    write_u32_raw(g_slab + OFF_00414eb0 + 0xbb, reinterpret_cast<U>(&g_val_006280f8));

    // 5) 004dd600 (1012 bytes)
    write_u32_raw(g_slab + OFF_004dd600 + 0x0b, reinterpret_cast<U>(&g_ptr_00628130));
    U c5_1 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x1f);
    write_u32_raw(g_slab + OFF_004dd600 + 0x20, reinterpret_cast<U>(&sub_00467fc0) - (c5_1 + 5));
    U c5_2 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x24);
    write_u32_raw(g_slab + OFF_004dd600 + 0x25, reinterpret_cast<U>(&sub_00560030) - (c5_2 + 5));
    write_u32_raw(g_slab + OFF_004dd600 + 0x2b, reinterpret_cast<U>(&g_ptr_0065b32c));
    write_u32_raw(g_slab + OFF_004dd600 + 0x3e, reinterpret_cast<U>(g_str_005d99bc));
    U c5_3 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x43);
    write_u32_raw(g_slab + OFF_004dd600 + 0x44, reinterpret_cast<U>(&sprintf_005a0fbf) - (c5_3 + 5));
    write_u32_raw(g_slab + OFF_004dd600 + 0x49, reinterpret_cast<U>(&g_ptr_0069ed0c));
    U c5_4 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x53);
    write_u32_raw(g_slab + OFF_004dd600 + 0x54, mfn_to_u32(&TextureContextObj::sub_00536080) - (c5_4 + 5));
    U c5_5 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x5f);
    write_u32_raw(g_slab + OFF_004dd600 + 0x60, reinterpret_cast<U>(&sub_0059dc30) - (c5_5 + 5));
    U c5_6 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x7f);
    write_u32_raw(g_slab + OFF_004dd600 + 0x80, mfn_to_u32(&AllocDesc::init_00403520) - (c5_6 + 5));
    U c5_7 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x95);
    write_u32_raw(g_slab + OFF_004dd600 + 0x96, reinterpret_cast<U>(&sub_0059e440) - (c5_7 + 5));
    write_u32_raw(g_slab + OFF_004dd600 + 0xa6, reinterpret_cast<U>(&g_pfn_006bd9b0));
    write_u32_raw(g_slab + OFF_004dd600 + 0xac, reinterpret_cast<U>(&g_pfn_006bd91c));
    write_u32_raw(g_slab + OFF_004dd600 + 0xb2, reinterpret_cast<U>(&g_pfn_006bd970));
    write_u32_raw(g_slab + OFF_004dd600 + 0xb8, reinterpret_cast<U>(&g_pfn_006bd948));
    write_u32_raw(g_slab + OFF_004dd600 + 0xbf, reinterpret_cast<U>(&g_pfn_006bd978));
    U c5_8 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0xd5);
    write_u32_raw(g_slab + OFF_004dd600 + 0xd6, reinterpret_cast<U>(&sub_004dc850) - (c5_8 + 5));
    U c5_9 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0xf0);
    write_u32_raw(g_slab + OFF_004dd600 + 0xf1, reinterpret_cast<U>(&sub_004237d0) - (c5_9 + 5));
    write_u32_raw(g_slab + OFF_004dd600 + 0xfa, reinterpret_cast<U>(&g_ptr_0069ed0c));
    U c5_10 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x101);
    write_u32_raw(g_slab + OFF_004dd600 + 0x102, mfn_to_u32(&TextureContextObj::sub_00536050) - (c5_10 + 5));
    U c5_11 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x106);
    write_u32_raw(g_slab + OFF_004dd600 + 0x107, reinterpret_cast<U>(&sub_004dd4a0) - (c5_11 + 5));
    write_u32_raw(g_slab + OFF_004dd600 + 0x10d, reinterpret_cast<U>(&g_ptr_00628130));
    U c5_12 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x11f);
    write_u32_raw(g_slab + OFF_004dd600 + 0x120, reinterpret_cast<U>(&sub_00467fc0) - (c5_12 + 5));
    write_u32_raw(g_slab + OFF_004dd600 + 0x126, reinterpret_cast<U>(&g_ptr_0065b334));
    write_u32_raw(g_slab + OFF_004dd600 + 0x132, reinterpret_cast<U>(g_str_005d99ac));
    U c5_13 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x137);
    write_u32_raw(g_slab + OFF_004dd600 + 0x138, reinterpret_cast<U>(&sprintf_005a0fbf) - (c5_13 + 5));
    U c5_14 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x143);
    write_u32_raw(g_slab + OFF_004dd600 + 0x144, reinterpret_cast<U>(&sub_0059dc30) - (c5_14 + 5));
    U c5_15 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x15d);
    write_u32_raw(g_slab + OFF_004dd600 + 0x15e, reinterpret_cast<U>(&sub_0059d8e0) - (c5_15 + 5));
    U c5_16 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x186);
    write_u32_raw(g_slab + OFF_004dd600 + 0x187, reinterpret_cast<U>(&sub_00534540) - (c5_16 + 5));
    U c5_17 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x1cf);
    write_u32_raw(g_slab + OFF_004dd600 + 0x1d0, reinterpret_cast<U>(&sub_00563440) - (c5_17 + 5));
    U c5_18 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x249);
    write_u32_raw(g_slab + OFF_004dd600 + 0x24a, reinterpret_cast<U>(&sub_00563440) - (c5_18 + 5));
    U c5_19 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x2bb);
    write_u32_raw(g_slab + OFF_004dd600 + 0x2bc, reinterpret_cast<U>(&sub_00563440) - (c5_19 + 5));
    U c5_20 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x32a);
    write_u32_raw(g_slab + OFF_004dd600 + 0x32b, reinterpret_cast<U>(&sub_00563440) - (c5_20 + 5));
    U c5_21 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x3ab);
    write_u32_raw(g_slab + OFF_004dd600 + 0x3ac, reinterpret_cast<U>(&sub_00563440) - (c5_21 + 5));
    U c5_22 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x3c7);
    write_u32_raw(g_slab + OFF_004dd600 + 0x3c8, reinterpret_cast<U>(&sub_00534550) - (c5_22 + 5));
    write_u32_raw(g_slab + OFF_004dd600 + 0x3ce, reinterpret_cast<U>(&g_pfn_006bd948));
    U c5_23 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x3e0);
    write_u32_raw(g_slab + OFF_004dd600 + 0x3e1, reinterpret_cast<U>(&heap_pool_block_free_00531f90) - (c5_23 + 5));
    U c5_24 = reinterpret_cast<U>(g_slab + OFF_004dd600 + 0x3e9);
    write_u32_raw(g_slab + OFF_004dd600 + 0x3ea, reinterpret_cast<U>(&sub_00560030) - (c5_24 + 5));
}}

// -----------------------------------------------------------------------------
// Test cases
// -----------------------------------------------------------------------------

// Cases 1..2: 0056a680
void test_0056a680() {{
    using Fn = void (CALL_CDECL*)();
    auto pfn_orig = reinterpret_cast<Fn>(g_slab + OFF_0056a680);

    // Case 1: Initial zero state
    {{
        g_val_006a5dd4 = 0x11;
        g_val_006a5dd8 = 0x22;
        g_val_006a5de0 = 0x33;
        g_val_006a5de4 = 0x44;
        g_val_006a5de8 = 0x55;
        g_val_006b7c40 = 0x99887766;
        g_val_006a5ddc = 0;

        reset_trace();
        pfn_orig();
        s_trace_orig = g_trace;

        U orig_dd4 = g_val_006a5dd4;
        U orig_dd8 = g_val_006a5dd8;
        U orig_de0 = g_val_006a5de0;
        U orig_de4 = g_val_006a5de4;
        U orig_de8 = g_val_006a5de8;
        U orig_ddc = g_val_006a5ddc;

        g_val_006a5dd4 = 0x11;
        g_val_006a5dd8 = 0x22;
        g_val_006a5de0 = 0x33;
        g_val_006a5de4 = 0x44;
        g_val_006a5de8 = 0x55;
        g_val_006b7c40 = 0x99887766;
        g_val_006a5ddc = 0;

        reset_trace();
        render_counters_init_0056a680();
        s_trace_cpp = g_trace;

        require(g_val_006a5dd4 == orig_dd4 && g_val_006a5dd4 == 0);
        require(g_val_006a5dd8 == orig_dd8 && g_val_006a5dd8 == 0);
        require(g_val_006a5de0 == orig_de0 && g_val_006a5de0 == 0);
        require(g_val_006a5de4 == orig_de4 && g_val_006a5de4 == 0);
        require(g_val_006a5de8 == orig_de8 && g_val_006a5de8 == 0);
        require(g_val_006a5ddc == orig_ddc && g_val_006a5ddc == 0x99887766);
        ++g_cases_passed;
    }}

    // Case 2: Different counter value assignment
    {{
        g_val_006b7c40 = 0x55aa3311;
        pfn_orig();
        U orig_ddc = g_val_006a5ddc;

        g_val_006a5ddc = 0;
        render_counters_init_0056a680();
        require(g_val_006a5ddc == orig_ddc && g_val_006a5ddc == 0x55aa3311);
        ++g_cases_passed;
    }}
}}

// Cases 3..4: 005a0f98 (__ftol)
void test_005a0f98() {{
    using Fn = std::int64_t (CALL_CDECL*)();
    auto pfn_orig = reinterpret_cast<Fn>(g_slab + OFF_005a0f98);

    // Case 3: Positive float truncation
    {{
        double val = 123.75;
        std::int64_t res_orig = 0;
        std::int64_t res_cpp = 0;
        __asm {{
            fld val
        }}
        res_orig = pfn_orig();

        __asm {{
            fld val
        }}
        res_cpp = ftol_005a0f98();

        require(res_orig == res_cpp && res_orig == 123);
        ++g_cases_passed;
    }}

    // Case 4: Negative float truncation
    {{
        double val = -456.99;
        std::int64_t res_orig = 0;
        std::int64_t res_cpp = 0;
        __asm {{
            fld val
        }}
        res_orig = pfn_orig();

        __asm {{
            fld val
        }}
        res_cpp = ftol_005a0f98();

        require(res_orig == res_cpp && res_orig == -456);
        ++g_cases_passed;
    }}
}}

// Cases 5..6: 00412030
void test_00412030() {{
    using Fn = void (CALL_CDECL*)();
    auto pfn_orig = reinterpret_cast<Fn>(g_slab + OFF_00412030);

    // Case 5: Disabled audio params (0 calls)
    {{
        g_val_005e940c = 0;
        reset_trace();
        pfn_orig();
        s_trace_orig = g_trace;

        reset_trace();
        audio_parameters_sync_00412030();
        s_trace_cpp = g_trace;

        require(s_trace_orig.count == 0 && s_trace_cpp.count == 0);
        ++g_cases_passed;
    }}

    // Case 6: Enabled audio params (4 calls)
    {{
        g_val_005e940c = 1;
        g_val_005e9410 = 2;
        g_audio_params_005e9420[2].val_20 = 10;
        g_audio_params_005e9420[2].val_22 = 20;
        g_audio_params_005e9420[2].val_24 = 30;
        g_audio_params_005e9420[2].val_26 = 40;

        reset_trace();
        pfn_orig();
        s_trace_orig = g_trace;

        reset_trace();
        audio_parameters_sync_00412030();
        s_trace_cpp = g_trace;

        require(s_trace_orig.count == 4 && s_trace_cpp.count == 4);
        for (U i = 0; i < 4; ++i) {{
            require(s_trace_orig.tag[i] == s_trace_cpp.tag[i]);
            require(s_trace_orig.arg1[i] == s_trace_cpp.arg1[i]);
        }}
        require(s_trace_orig.arg1[0] == 30);
        require(s_trace_orig.arg1[1] == 20);
        require(s_trace_orig.arg1[2] == 10);
        require(s_trace_orig.arg1[3] == 40);
        ++g_cases_passed;
    }}
}}

// Cases 7..8: 00414eb0
void test_00414eb0() {{
    using Fn = void (CALL_CDECL*)();
    auto pfn_orig = reinterpret_cast<Fn>(g_slab + OFF_00414eb0);

    // Case 7: Session init resets & calls
    {{
        g_val_005e99b8 = 0x11223344;
        g_val_00657a34 = 0x55667788;
        g_val_00606ab8 = 0;
        g_val_00656858 = 1;
        g_val_00606ac8 = 0;

        reset_trace();
        pfn_orig();
        s_trace_orig = g_trace;

        g_val_00606ab8 = 0;
        g_val_00656858 = 1;
        g_val_00606ac8 = 0;

        reset_trace();
        session_state_init_00414eb0();
        s_trace_cpp = g_trace;

        require(s_trace_orig.count == 10 && s_trace_cpp.count == 10);
        for (U i = 0; i < 10; ++i) {{
            require(s_trace_orig.tag[i] == s_trace_cpp.tag[i]);
            require(s_trace_orig.arg1[i] == s_trace_cpp.arg1[i]);
        }}
        require(g_val_00606ab8 == 1);
        require(g_val_00656858 == 0);
        require(g_val_00606ac8 == 0x11223344);
        require(g_val_006280f0 == 0);
        require(g_val_006280f8 == 0);
        ++g_cases_passed;
    }}

    // Case 8: Repeated init with alternate seed
    {{
        g_val_005e99b8 = 0xAABBCCDD;
        pfn_orig();
        require(g_val_00606ac8 == 0xAABBCCDD);

        g_val_00606ac8 = 0;
        session_state_init_00414eb0();
        require(g_val_00606ac8 == 0xAABBCCDD);
        ++g_cases_passed;
    }}
}}

// Cases 9..10: 004dd600
void test_004dd600() {{
    using Fn = void (CALL_CDECL*)();
    auto pfn_orig = reinterpret_cast<Fn>(g_slab + OFF_004dd600);

    // Case 9: Texture file not found (early exit path)
    {{
        s_mock_file_exists_tex = 0;
        reset_trace();
        pfn_orig();
        s_trace_orig = g_trace;

        reset_trace();
        texture_subsystem_config_004dd600();
        s_trace_cpp = g_trace;

        require(s_trace_orig.count == s_trace_cpp.count);
        for (U i = 0; i < s_trace_orig.count; ++i) {{
            require(s_trace_orig.tag[i] == s_trace_cpp.tag[i]);
        }}
        ++g_cases_passed;
    }}

    // Case 10: Texture file found (full loop & blit path)
    {{
        s_mock_file_exists_tex = 1;
        reset_trace();
        pfn_orig();
        s_trace_orig = g_trace;

        reset_trace();
        texture_subsystem_config_004dd600();
        s_trace_cpp = g_trace;

        require(s_trace_orig.count == s_trace_cpp.count);
        for (U i = 0; i < s_trace_orig.count; ++i) {{
            require(s_trace_orig.tag[i] == s_trace_cpp.tag[i]);
            require(s_trace_orig.arg1[i] == s_trace_cpp.arg1[i]);
        }}
        ++g_cases_passed;
    }}
}}

}} // namespace porsche

extern "C" void entry() {{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
    porsche::init_slab();

    porsche::test_0056a680();
    porsche::test_005a0f98();
    porsche::test_00412030();
    porsche::test_00414eb0();
    porsche::test_004dd600();

    require(g_cases_passed == 10);
    ExitProcess(0);
}}
"""

out_dir = ROOT / "local/experiments/v2-app-main-305"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "app_main_fixture.cpp").write_text(FIXTURE_CPP, encoding="utf-8")
print(f"Generated {out_dir / 'app_main_fixture.cpp'}")
