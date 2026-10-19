#include "porsche/heap.hpp"
#include "porsche/input_buffer.hpp"
#include "porsche/input_snapshot.hpp"
#include "porsche/input_state.hpp"
#include "porsche/files.hpp"
#include "porsche/shared_runtime_globals.hpp"
#include "porsche/startup_input.hpp"

#include <array>
#include <cstdarg>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace porsche {
void* startup_direct_input_006a5b14{};
void* startup_keyboard_device_006a5b18{};

namespace {
struct Config {
    std::uint32_t poll_result{}, poll_retry_result{}, acquire_result{};
    std::uint32_t get_state_result{}, get_state_retry_result{}, caps_result{}, caps_boundary_result{};
    std::uint32_t seed{};
};
Config config;
std::vector<std::string> calls;
std::array<void*, 26> raw_vtable{};
InputDevice input_device{};
InputBufferDevice input_buffer_device{};
std::uint32_t direct_input_sentinel{};
std::uint32_t poll_count{}, get_state_count{};

std::string hex_bytes(const void* p, std::size_t count) {
    const auto* bytes = static_cast<const std::uint8_t*>(p);
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (std::size_t i = 0; i < count; ++i) out << std::setw(2) << static_cast<unsigned>(bytes[i]);
    return out.str();
}

std::string json_quote(const std::string& value) {
    std::string out = "\"";
    for (const auto ch : value) {
        if (ch == '\\' || ch == '"') { out.push_back('\\'); out.push_back(ch); }
        else if (ch == '\n') out += "\\n";
        else if (ch == '\r') out += "\\r";
        else if (ch == '\t') out += "\\t";
        else out.push_back(ch);
    }
    out.push_back('"');
    return out;
}

std::int32_t storage_offset(const void* p) {
    if (!p) return -1;
    const auto address = reinterpret_cast<std::uintptr_t>(p);
    const auto base = reinterpret_cast<std::uintptr_t>(&input_snapshot_storage_006a57f0);
    return static_cast<std::int32_t>(address - base);
}

std::uint32_t __stdcall mock_poll(void*) {
    const auto result = poll_count++ == 0 ? config.poll_result : config.poll_retry_result;
    calls.emplace_back("poll:" + std::to_string(result));
    return result;
}

std::uint32_t __stdcall mock_acquire(void*) {
    calls.emplace_back("acquire");
    return config.acquire_result;
}

std::uint32_t __stdcall mock_get_state(void*, std::uint32_t size, void* destination) {
    const auto result = get_state_count++ == 0 ? config.get_state_result : config.get_state_retry_result;
    calls.emplace_back("getstate:" + std::to_string(size) + ":" + std::to_string(storage_offset(destination)) + ":" + std::to_string(result));
    auto* bytes = static_cast<std::uint8_t*>(destination);
    for (std::uint32_t i = 0; i < size; ++i)
        bytes[i] = static_cast<std::uint8_t>(config.seed + i * 3u);
    return result;
}

std::uint32_t __stdcall mock_get_caps(void*, void*) {
    calls.emplace_back("getcaps:" + std::to_string(config.caps_result));
    return config.caps_result;
}

void __cdecl mock_diagnostic(const char* format, ...) {
    va_list args;
    va_start(args, format);
    const auto selector = va_arg(args, int);
    va_end(args);
    calls.emplace_back("diagnostic:" + std::string(format) + ":" + std::to_string(selector));
}

void configure_vtable() {
    raw_vtable.fill(nullptr);
    raw_vtable[0x1c / 4] = reinterpret_cast<void*>(&mock_acquire);
    raw_vtable[0x24 / 4] = reinterpret_cast<void*>(&mock_get_state);
    raw_vtable[0x3c / 4] = reinterpret_cast<void*>(&mock_get_caps);
    raw_vtable[0x64 / 4] = reinterpret_cast<void*>(&mock_poll);
    input_device.vtable = reinterpret_cast<InputVtable*>(raw_vtable.data());
    input_buffer_device.vtable = reinterpret_cast<InputBufferVtable*>(raw_vtable.data());
}
} // namespace

std::uint32_t __cdecl input_caps_success_unrecovered_0056fdf9(
    InputBufferDevice*, void*, const void*) {
    calls.emplace_back("caps-success-boundary");
    return config.caps_boundary_result;
}

// Run 423 recovered the remaining 00532e10 modes, so input_state.cpp now calls
// the diagnostic handler and fills the mode-2 caps buffer. Neither path is
// reached by these snapshot cases; both are provided here so the probe links.
static void __cdecl unreached_getstate_diagnostic(const char*) { std::abort(); }
void (__cdecl* diagnostic_handler_005debf0)(const char*) = unreached_getstate_diagnostic;
void* __cdecl input_negative_index_00532e10(std::int32_t, std::uint32_t) { std::abort(); }
void* __cdecl input_unmapped_index_00532e10(std::uint32_t, std::uint32_t) { std::abort(); }

void __cdecl heap_fill_0053c290(void* destination, std::uint32_t value, std::uint32_t bytes) {
    calls.emplace_back("fill:" + std::to_string(storage_offset(destination)) + ":" +
                       std::to_string(value) + ":" + std::to_string(bytes));
    const auto* pattern = reinterpret_cast<const std::uint8_t*>(&value);
    auto* output = static_cast<std::uint8_t*>(destination);
    for (std::uint32_t i = 0; i < bytes; ++i) output[i] = pattern[i & 3u];
}
} // namespace porsche

int main() {
    std::int32_t mode;
    std::uint32_t present, poll_result, poll_retry_result, acquire_result;
    std::uint32_t get_state_result, get_state_retry_result, caps_result, caps_boundary_result, seed;
    while (std::cin >> mode >> present >> poll_result >> poll_retry_result >> acquire_result
                    >> get_state_result >> get_state_retry_result >> caps_result
                    >> caps_boundary_result >> seed) {
        using namespace porsche;
        std::memset(&input_snapshot_storage_006a57f0, 0xa5, sizeof(input_snapshot_storage_006a57f0));
        application_diagnostic_line_005deb78 = 0x777;
        diagnostic_file_005deb74_set(nullptr);
        calls.clear();
        config = {poll_result, poll_retry_result, acquire_result, get_state_result,
                  get_state_retry_result, caps_result, caps_boundary_result, seed};
        poll_count = 0;
        get_state_count = 0;
        configure_vtable();
        startup_direct_input_006a5b14 = present ? &direct_input_sentinel : nullptr;
        startup_keyboard_device_006a5b18 = &input_device;
        input_snapshot_diagnostic_boundary = &mock_diagnostic;
        const auto result = input_snapshot_getstate_0055feb0(static_cast<std::int32_t>(mode));
        const auto* diag_file = diagnostic_file_005deb74();
        std::cout << "{\"return_offset\":" << storage_offset(result)
                  << ",\"snapshot\":\"" << hex_bytes(&input_snapshot_storage_006a57f0, sizeof(input_snapshot_storage_006a57f0))
                  << "\",\"diag_line\":" << application_diagnostic_line_005deb78
                  << ",\"diag_file\":" << json_quote(diag_file ? diag_file : "") << ",\"calls\":[";
        for (std::size_t i = 0; i < calls.size(); ++i) {
            if (i) std::cout << ',';
            std::cout << json_quote(calls[i]);
        }
        std::cout << "]}\n";
    }
    return std::cin.eof() ? 0 : 2;
}
