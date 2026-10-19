#include "porsche/input_state.hpp"
#include "porsche/files.hpp"
#include "porsche/input_buffer.hpp"
#include <cstring>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {
using namespace porsche;
std::uint32_t poll_first, poll_retry, get_first, get_retry, acquire_poll, acquire_get;
int poll_calls, get_calls;
char phase;
std::vector<std::string> calls;
void bytes(const std::uint8_t* p, std::size_t count) {
    for (std::size_t i = 0; i < count; ++i)
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<unsigned>(p[i]);
}
std::uint32_t __stdcall poll(void*) {
    phase = 'P'; calls.emplace_back("P");
    return poll_calls++ ? poll_retry : poll_first;
}
std::uint32_t __stdcall acquire(void*) {
    calls.emplace_back("A");
    return phase == 'P' ? acquire_poll : acquire_get;
}
std::uint32_t __stdcall get_state(void*, std::uint32_t size, void* destination) {
    phase = 'G';
    const auto ordinal = ++get_calls;
    const auto same = destination == input_slots_006be040[0].state_0c;
    calls.push_back("G" + std::to_string(size) + (same ? "s" : "x"));
    std::memset(destination, 0x40 + ordinal, size);
    return ordinal == 1 ? get_first : get_retry;
}
InputVtable table{};
InputDevice device{&table};
}
namespace porsche {
// Run 423 replaced the two boundaries this probe used to hook (the unrecovered
// modes and the invalid-type report) with the real callees. They are hooked
// here instead; "D" still marks the diagnostic call, as in the Unicorn trace.
std::uint8_t input_caps_buffer_006bde20[0x21c];
std::uint32_t __cdecl input_caps_0056fdb0(InputBufferDevice*, void*) { calls.emplace_back("C"); return 0; }
std::uint32_t __cdecl input_property_mode8_0056fff0(InputBufferDevice*) { calls.emplace_back("M"); return 0; }
static void __cdecl probe_diagnostic(const char*) { calls.emplace_back("D"); }
void (__cdecl* diagnostic_handler_005debf0)(const char*) = probe_diagnostic;
static const char* probe_diagnostic_file;
static std::uint32_t probe_diagnostic_line;
void diagnostic_file_005deb74_set(const char* value) noexcept { probe_diagnostic_file = value; }
std::uint32_t& diagnostic_line_005deb78 = probe_diagnostic_line;
void* __cdecl input_negative_index_00532e10(std::int32_t, std::uint32_t) {
    calls.emplace_back("N"); return nullptr;
}
void* __cdecl input_unmapped_index_00532e10(std::uint32_t, std::uint32_t) {
    calls.emplace_back("X"); return nullptr;
}
}
int main() {
    table.acquire_1c = acquire;
    table.get_state_24 = get_state;
    table.poll_64 = poll;
    std::uint32_t kind, index, count, present, type, ap, ag;
    while (std::cin >> kind >> index >> count >> present >> type
                    >> poll_first >> poll_retry >> ap >> get_first >> get_retry >> ag) {
        acquire_poll = ap; acquire_get = ag;
        calls.clear(); poll_calls = get_calls = 0; phase = 0;
        std::memset(input_slots_006be040, 0, sizeof(input_slots_006be040));
        input_count_0069cb0c = static_cast<std::int32_t>(count);
        auto& slot = input_slots_006be040[0];
        slot.device = present ? &device : nullptr;
        slot.flags_04 = 0x87654321u;
        slot.type_08 = type;
        std::memset(slot.state_0c, 0xa5, sizeof(slot.state_0c));
        std::uint32_t returned = 0;
        if (kind == 0) {
            auto* result = fe_input_getstate_00532e10(index, 6);
            returned = result == &slot.type_08 ? 1 : result == nullptr ? 0 : 2;
        } else if (kind == 1) returned = input_poll_0056fd00(&device);
        else if (kind == 2) returned = input_read_0056fd30(&device, type, slot.state_0c);
        else if (kind == 3) returned = input_poll_read_0056fce0(&device, slot.state_0c, type);
        else return 2;
        std::cout << std::dec << returned << ' ';
        const auto* raw = reinterpret_cast<const std::uint8_t*>(input_slots_006be040);
        for (std::size_t i = 0; i < 32; ++i) bytes(raw + i * sizeof(InputSlot) + 4, sizeof(InputSlot) - 4);
        std::cout << ' ';
        if (calls.empty()) std::cout << '-';
        else {
            for (std::size_t i = 0; i < calls.size(); ++i) {
                if (i) std::cout << ',';
                std::cout << calls[i];
            }
        }
        std::cout << '\n';
    }
}
