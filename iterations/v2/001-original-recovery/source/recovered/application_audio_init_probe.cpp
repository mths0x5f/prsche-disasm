#include "porsche/application_audio_init.hpp"

#include "porsche/application_services.hpp"
#include "porsche/application_state.hpp"
#include "porsche/file_events.hpp"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

static_assert(sizeof(void*) == 4, "Run 131 requires Win32 x86 pointers");

namespace {
struct Scenario {
    std::int32_t mode;
    std::uint32_t gate;
    std::int32_t query_result;
    std::int32_t device_result;
    std::uint32_t initial_configured;
    std::uint32_t timer_rate;
    std::uint32_t template_kind;
};
Scenario scenario{};
std::vector<std::string> calls;

void call(std::string value) { calls.push_back(std::move(value)); }

std::string hex32(std::uint32_t value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(8) << value;
    return out.str();
}

std::string descriptor_hex(const std::uint8_t* data) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (unsigned i = 0; i < 124; ++i)
        out << std::setw(2) << static_cast<unsigned>(data[i]);
    return out.str();
}

void fill_descriptor(std::uint8_t* output) {
    for (unsigned i = 0; i < 124; ++i)
        output[i] = static_cast<std::uint8_t>((i * 37u + 11u) & 0xffu);
    output[8] = scenario.template_kind == 2 ? 0 : 4;
    output[0x0a] = 4;
    output[0x0b] = 0x01;
    output[0x0c] = scenario.template_kind == 1 ? 0x02 : 0x91;
    output[0x0d] = 0x30;
    output[0x0e] = 0x00;
    output[2] = 0x44; // requested sample-rate word: 0xac44
    output[3] = 0xac;
}
}

namespace porsche {
// Fixture-local state aliases normally owned by Run 128 production source.
std::uint32_t application_audio_config_00655d34 = 0;
std::uint32_t application_audio_mode_00655d38 = 0;
std::uint8_t application_audio_flag_00655d3c = 0;
std::uint32_t application_audio_buffer_00655d44 = 0x22004000;
ApplicationAudioRecord006564a0 application_audio_records_006564a0[8]{};
std::uint32_t application_audio_active_005d1734 = 1;
std::uint32_t timer_rate_005deb48 = 1000;

void __cdecl application_audio_prepare_00565950() {
    call("prepare:00565950");
}

std::int32_t __cdecl application_audio_query_config_00565680(
    std::uint8_t* descriptor) {
    call("query:00565680:124");
    fill_descriptor(descriptor);
    return scenario.query_result;
}

std::uint32_t __cdecl application_audio_apply_config_005656d0(
    const std::uint8_t* descriptor) {
    call("apply:005656d0:" + descriptor_hex(descriptor));
    return 0;
}

std::int32_t __cdecl application_audio_create_device_00565720(
    std::uint32_t buffer, std::uint32_t size, std::uint32_t flags) {
    call("device:00565720:" + hex32(buffer) + ":" + hex32(size) + ":" +
         hex32(flags));
    return scenario.device_result;
}

void __cdecl application_audio_wait_0053c380(std::int32_t interval) {
    call("wait:0053c380:" + hex32(static_cast<std::uint32_t>(interval)));
}

void __cdecl application_audio_period_control_00565c70(
    std::uint32_t a, std::uint32_t b, std::uint32_t c,
    std::uint32_t d, std::uint32_t e) {
    call("period:00565c70:" + hex32(a) + ":" + hex32(b) + ":" +
         hex32(c) + ":" + hex32(d) + ":" + hex32(e));
}
}

int main(int argc, char** argv) {
    const auto id = argc > 1 ? static_cast<unsigned>(std::strtoul(argv[1], nullptr, 10)) : 0;
    if (id > 7) return 2;
    static const Scenario cases[] = {
        {0, 1, 0, 0, 0, 101, 0},
        {1, 1, 0, 0, 0, 100, 1},
        {2, 0, 0, 0, 1, 99, 0},
        {3, 0, -1, 0, 1, 100, 0},
        {3, 0, 0, -7, 1, 100, 0},
        {4, 0, 0, 1, 1, 100, 0},
        {0, 1, 0, 0, 0, 0xfffffffeu, 0},
        {0, 1, 0, 0, 0, 0xffffffffu, 0},
    };
    scenario = cases[id];
    calls.clear();

    porsche::application_state_006573e8.word(0x00657c98u) =
        static_cast<std::uint32_t>(scenario.mode);
    porsche::application_state_006573e8.word(0x00657c9cu) = scenario.gate;
    porsche::application_audio_device_configured_00655d40 = scenario.initial_configured;
    porsche::application_audio_buffer_00655d44 = 0x22004000;
    porsche::timer_rate_005deb48 = scenario.timer_rate;
    porsche::application_audio_post_init_byte_00656868 = 0x55;
    porsche::application_audio_post_init_byte_00656869 = 0xaa;

    const auto result = porsche::application_audio_initialize_004a66b0();
    std::cout << std::hex << "state=" << static_cast<unsigned>(result) << ','
              << porsche::application_audio_device_configured_00655d40 << ','
              << static_cast<unsigned>(porsche::application_audio_post_init_byte_00656868) << ','
              << static_cast<unsigned>(porsche::application_audio_post_init_byte_00656869) << ','
              << porsche::application_state_006573e8.word(0x00657c98u) << ','
              << porsche::application_state_006573e8.word(0x00657c9cu) << ','
              << porsche::application_audio_buffer_00655d44 << ','
              << porsche::timer_rate_005deb48 << '\n';
    std::cout << "trace=";
    for (std::size_t i = 0; i < calls.size(); ++i) {
        if (i) std::cout << ';';
        std::cout << calls[i];
    }
    std::cout << '\n';
    return 0;
}
