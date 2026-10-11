#include "porsche/application_services_next.hpp"

#include "porsche/application_alloc.hpp"
#include "porsche/application_heap.hpp"
#include "porsche/application_services.hpp"
#include "porsche/application_state.hpp"
#include "porsche/heap.hpp"
#include "porsche/startup_sequence.hpp"
#include "porsche/startup_services.hpp"

#include <cstring>

namespace porsche {

std::array<std::uint32_t, 0x2b8 / 4> application_audio_reset_storage_00655d48{};
std::uint32_t application_audio_secondary_active_005d1738 = 1;

namespace {
using U = std::uint32_t;
U load(const void* base, U offset) {
    U value;
    std::memcpy(&value, static_cast<const std::uint8_t*>(base) + offset, 4);
    return value;
}
void* pointer(U value) { return reinterpret_cast<void*>(static_cast<std::uintptr_t>(value)); }
std::uint8_t byte(const void* base, U offset) {
    return static_cast<const std::uint8_t*>(base)[offset];
}
void set_byte(void* base, U offset, std::uint8_t value) {
    static_cast<std::uint8_t*>(base)[offset] = value;
}
void store(void* base, U offset, U value) {
    std::memcpy(static_cast<std::uint8_t*>(base) + offset, &value, 4);
}
bool connected(void* network) {
    return network && load(network, 8) != 0 && byte(network, 0xbf) == 0;
}
std::int32_t signed_bits(U value) {
    std::int32_t result;
    std::memcpy(&result, &value, 4);
    return result;
}
}

// 004a6960..004a69f8, including wrapped SHL then signed /100. 00656510/18
// are the raw_00/raw_08 members of the existing final Run128 record.
void __cdecl application_audio_shutdown_004a6960() {
    application_audio_shutdown_channels_005659f0(-1);
    auto& record = application_audio_records_006564a0[7];
    if (record.raw_08 != 0) {
        free_00531f90(pointer(record.raw_08));
        record.raw_08 = 0;
        record.raw_00 = 0xffffffffu;
    }
    application_audio_shutdown_device_004ae310();
    if ((application_audio_active_005d1734 != 0 ||
         application_audio_secondary_active_005d1738 != 0) &&
        application_audio_buffer_00655d44 != 0) {
        application_audio_probe_finish_004ab4b0();
        const auto measured = static_cast<U>(application_audio_probe_measure_00565890());
        free_00531f90(pointer(application_audio_buffer_00655d44));
        const auto wrapped = (measured + 1u) << 18u;
        const auto reported = signed_bits(wrapped) / 100;
        application_audio_buffer_00655d44 = 0;
        startup_sequence_report_005a177b(0x005d1400u, static_cast<U>(reported));
    }
}

// 004a6e30..004a6f08. Each iteration reloads the original count, and the
// source selection is signed (including negative indices, with no clamp).
void __cdecl application_audio_reset_004a6e30() {
    auto& state = application_audio_reset_storage_00655d48;
    const auto put = [&](U va, U value) { state[(va - 0x00655d48u) / 4u] = value; };
    const auto selected = signed_bits(application_state_006573e8.word(0x0065741cu));
    const auto mode = signed_bits(application_state_006573e8.word(0x00657404u));
    for (const auto va : {0x00655e48u, 0x00655d54u, 0x00655ffcu}) put(va, 0);
    for (const auto va : {0x00655d5cu, 0x00655d48u, 0x00655d4cu, 0x00655d50u})
        put(va, 0xffffffffu);
    for (std::int32_t index = 0; index < 2; ++index) {
        const U base = 0x00655f58u + static_cast<U>(index) * 0x50u;
        const auto count = signed_bits(application_audio_source_storage_005e8bfc[0]);
        put(base - 0x20u, 0xffffffffu);
        put(base - 0x1cu, 0); put(base - 0x18u, 0);
        put(base - 8u, 0);
        put(base - 4u, 0xffffffffu); put(base, 0xffffffffu);
        put(base + 8u, 0); put(base + 0x18u, 0); put(base + 0xcu, 0x1324u);
        put(base + 0x10u, 0); put(base + 0x28u, 0); put(base + 0x2cu, 0);
        if (mode > 1) {
            if (index == 0 && selected < count)
                put(base - 8u, load(application_audio_source_storage_005e8bfc,
                    4u + static_cast<U>(selected) * 4u));
        } else if (index < count) {
            put(base - 8u, application_audio_source_storage_005e8bfc[index + 1]);
        }
    }
    for (U index = 0; index < 4; ++index) {
        const U base = 0x00655d68u + index * 0x38u;
        put(base - 8u, 0); put(base - 4u, 0xffffffffu); put(base, 0xffffffffu);
        put(base + 8u, 0); put(base + 0x18u, 0); put(base + 0xcu, 0x1324u);
        put(base + 0x10u, 0); put(base + 0x28u, 0); put(base + 0x2cu, 0);
    }
    put(0x00655e44u, 0);
}

// 0048dad0..0048dba9: lock-cell captures survive callbacks; global network
// and lock handle are reread at precisely the original access points.
void __cdecl application_network_finish_0048dad0() {
    void* network = startup_network_00628c70;
    if (!connected(network)) return;
    if (byte(network, 0xbd) == 0) {
        void* cell = pointer(load(network, 0x10));
        heap_enter_005322b0(pointer(load(cell, 0)));
        application_network_message_0048c870(pointer(load(startup_network_00628c70, 0xc)),
            nullptr, 0xb7, 0xffffffffu, 0xffffffffu, 0, 0);
        set_byte(startup_network_00628c70, 0xbd, 1);
        heap_leave_005322c0(pointer(load(cell, 0)));
        network = startup_network_00628c70;
    }
    if (connected(network)) {
        void* cell = pointer(load(network, 0x10));
        heap_enter_005322b0(pointer(load(cell, 0)));
        application_network_message_0048c870(pointer(load(startup_network_00628c70, 0xc)),
            nullptr, 0xb7, 0xfffffffeu, 0xffffffffu, 0, 0);
        set_byte(startup_network_00628c70, 0xbd, 1);
        heap_leave_005322c0(pointer(load(cell, 0)));
        network = startup_network_00628c70;
    }
    // Original writes through EAX even when the second test rejects a null
    // pointer. Do not invent a guard for callback states that would fault.
    set_byte(network, 0xbc, 1);
}

// 0048e6f0..0048e788: original thiscall receiver, RET0. The mode-zero and
// mode-two branches use the global pointer AFTER reset, not the old receiver.
void __fastcall application_network_close_0048e6f0(void* receiver, void*) {
    const auto mode = load(receiver, 0x28);
    if (mode == 0 || mode == 2) {
        application_network_reset_0048e9c0(receiver, nullptr);
        if (startup_network_00628c70)
            application_network_change_0048e1a0(startup_network_00628c70, nullptr, mode, 0, 0);
        return;
    }
    if (byte(receiver, 0xc6) != 0) {
        void* member = pointer(load(receiver, 0x14));
        if (member) {
            application_network_member_destroy_004935c0(member, nullptr);
            application_release_0059f050(member);
            store(receiver, 0x14, 0);
        }
        application_network_message_0048c870(pointer(load(receiver, 0xc)), nullptr,
            0xba, 0x80000000u, 0x80000000u, 0, 0);
        return;
    }
    application_network_reset_0048e9c0(receiver, nullptr);
}

void __cdecl application_main_function_004a6960() { application_audio_shutdown_004a6960(); }
void __cdecl application_main_function_004a6e30() { application_audio_reset_004a6e30(); }
void __cdecl application_main_function_0048dad0() { application_network_finish_0048dad0(); }
void __cdecl application_main_function_0048e6f0() {
    application_network_close_0048e6f0(startup_network_00628c70, nullptr);
}

} // namespace porsche
