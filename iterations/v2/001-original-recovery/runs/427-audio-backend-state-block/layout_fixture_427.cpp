// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Native layout fixture for the audio state block (Run 427). It is linked with
// audio_backend_state_427.obj and the declarations of the canonical headers and
// Runs 421/425, so a type mismatch between a header and the block fails here.
#include "porsche/application_audio_device.hpp"
#include "audio_backend_lock_pool_421.hpp"
#include "audio_voice_stop_425.hpp"

namespace porsche {
extern std::uint8_t audio_system_active_006b499c;  // as declared by Run 400
}

extern "C" std::uint8_t audio_state_block_006b00c0[];
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(unsigned long);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*, const void*, unsigned long, unsigned long*, void*);
extern "C" __declspec(dllimport) void __stdcall ExitProcess(unsigned int);

namespace {

constexpr std::uint32_t kBlockBegin = 0x006b00c0u;
constexpr std::uint32_t kBlockEnd = 0x006b4a44u;
unsigned failures = 0;

void put(const char* s) {
    unsigned long n = 0, w = 0;
    while (s[n]) ++n;
    WriteFile(GetStdHandle(static_cast<unsigned long>(-11)), s, n, &w, nullptr);
}

void check(bool ok, const char* what) {
    put(what);
    put(ok ? " OK\n" : " FAIL\n");
    if (!ok) ++failures;
}

// Original VA of a block address.
std::uint32_t va_of(const void* p) {
    return kBlockBegin + static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(p) -
                                                    reinterpret_cast<std::uintptr_t>(audio_state_block_006b00c0));
}

} // namespace

extern "C" void __cdecl entry() {
    using namespace porsche;
    // 1. Every name sits at its original VA relative to the block.
    check(va_of(audio_backend_lock_cs_006b1800) == 0x006b1800u, "lock cs at 006b1800");
    check(va_of(&audio_voice_table_006b489c) == 0x006b489cu, "voice table at 006b489c");
    check(va_of(application_audio_device_state_006b48c0.preceding_data()) == 0x006b48b0u, "device backing at 006b48b0");
    check(va_of(application_audio_device_state_006b48c0.data()) == 0x006b48c0u, "device data at 006b48c0");
    check(va_of(&audio_system_active_006b499c) == 0x006b499cu, "system active at 006b499c");
    check(va_of(&audio_backend_lock_depth_006b499f) == 0x006b499fu, "lock depth at 006b499f");
    check(va_of(&audio_backend_channel_count_006b49a4) == 0x006b49a4u, "channel count at 006b49a4");
    check(va_of(&audio_backend_stamp_006b49a8) == 0x006b49a8u, "stamp at 006b49a8");
    check(va_of(&audio_backend_channels_006b4a00) == 0x006b4a00u, "channel table at 006b4a00");
    check(va_of(&audio_backend_pool_006b4a18) == 0x006b4a18u, "pool at 006b4a18");
    check(reinterpret_cast<std::uintptr_t>(audio_state_block_006b00c0) % 64u == 0u, "block 64-byte aligned");

    // 2. The whole block starts zero, like the original .data zero-fill tail.
    bool zero = true;
    for (std::uint32_t i = 0; i < kBlockEnd - kBlockBegin; ++i) zero = zero && audio_state_block_006b00c0[i] == 0;
    check(zero, "block initially zero");

    // 3. Writes through one name are seen through the device state view and back.
    audio_system_active_006b499c = 0x5a;
    check(application_audio_device_state_006b48c0[0xdc] == 0x5a, "system active aliases device[0xdc]");
    application_audio_device_state_006b48c0[0xdf] = 0x03;
    check(audio_backend_lock_depth_006b499f == 0x03, "device[0xdf] aliases lock depth");
    audio_backend_channel_count_006b49a4 = static_cast<std::int16_t>(0x1234);
    check(application_audio_device_state_006b48c0[0xe4] == 0x34 && application_audio_device_state_006b48c0[0xe5] == 0x12,
          "channel count aliases device[0xe4..0xe5]");
    application_audio_device_state_006b48c0[0x140] = 0x78;
    application_audio_device_state_006b48c0[0x141] = 0x56;
    check(audio_backend_channels_006b4a00 == 0x5678u, "device[0x140] aliases channel table");
    audio_backend_pool_006b4a18 = 0xa1b2c3d4u;
    check(application_audio_device_state_006b48c0[0x158] == 0xd4 && application_audio_device_state_006b48c0[0x15b] == 0xa1,
          "pool aliases device[0x158..0x15b]");
    // The 16-byte records at 006b4a08 (index & 0x1f) reach the pool cell: record 1, +0.
    std::uint8_t* records_4a08 = application_audio_device_state_006b48c0.data() + (0x006b4a08u - 0x006b48c0u);
    check(va_of(records_4a08 + 0x10) == 0x006b4a18u && records_4a08[0x10] == 0xd4, "record[1] of 006b4a08 is the pool");
    // The byte array at 006b4886 (index & 0x1f) reaches the voice table pointer at index 0x16.
    audio_voice_table_006b489c = 0x11223344u;
    std::uint8_t* bytes_4886 = reinterpret_cast<std::uint8_t*>(&audio_voice_table_006b489c) - 0x16;
    check(va_of(bytes_4886) == 0x006b4886u && bytes_4886[0x16] == 0x44, "byte[0x16] of 006b4886 is the voice table");

    put(failures ? "RESULT FAIL\n" : "RESULT PASS\n");
    ExitProcess(failures ? 1u : 0u);
}
