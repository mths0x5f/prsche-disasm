#include "porsche/formatter_lowio.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

namespace {
alignas(4) std::uint8_t pool[64][0x480];
alignas(4) std::uint8_t inherited[4 + 2050 * 5];
unsigned allocated, allocations, fail_allocation;
int std_mode, inherited_pattern, type_pattern, mutation, declared_count;
bool reserved_present, pointer_present;
std::int32_t error_value;
std::uint32_t dos_error;
std::vector<std::string> events;
struct Fatal {};
std::uint32_t read32(const void* p) { std::uint32_t v; std::memcpy(&v, p, 4); return v; }
void write32(void* p, std::uint32_t v) { std::memcpy(p, &v, 4); }
std::string hex(const void* p, std::size_t n) {
    const auto* bytes = static_cast<const std::uint8_t*>(p);
    const char* digits = "0123456789abcdef";
    std::string out;
    for (std::size_t i = 0; i < n; ++i) { out += digits[bytes[i] >> 4]; out += digits[bytes[i] & 15]; }
    return out;
}
std::size_t location(const void* p) {
    const auto offset = static_cast<const std::uint8_t*>(p) - &pool[0][0];
    if (offset < 0 || offset >= static_cast<std::ptrdiff_t>(sizeof(pool))) std::abort();
    return static_cast<std::size_t>(offset);
}
void reset() {
    using namespace porsche;
    std::memset(pool, 0xa5, sizeof(pool));
    std::memset(inherited, 0xcc, sizeof(inherited));
    for (unsigned i = 0; i < 64; ++i) formatter_cleanup_handle_table_006c01e0[i] = nullptr;
    formatter_cleanup_handle_limit_006c02e0 = 0;
    allocated = allocations = 0; fail_allocation = 0;
    error_value = 41; dos_error = 0x1234;
    events.clear(); mutation = 0;
}
void seed_banks(unsigned count) {
    using namespace porsche;
    allocated = count; formatter_cleanup_handle_limit_006c02e0 = count * 32;
    for (unsigned i = 0; i < count; ++i) {
        formatter_cleanup_handle_table_006c01e0[i] = pool[i];
        for (unsigned slot = 0; slot < 32; ++slot) {
            auto* p = pool[i] + slot * 36;
            write32(p, 0x7000 + i * 32 + slot); p[4] = 1;
            write32(p + 8, 1);
        }
    }
}
void print_state(std::uint32_t value, bool fatal) {
    using namespace porsche;
    std::printf("{\"return\":%u,\"fatal\":%s,\"limit\":%u,\"errno\":%d,\"doserrno\":%u,\"table\":[",
        value, fatal ? "true" : "false", formatter_cleanup_handle_limit_006c02e0, error_value, dos_error);
    for (unsigned i = 0; i < 64; ++i) {
        const auto* p = formatter_cleanup_handle_table_006c01e0[i];
        std::printf("%s%d", i ? "," : "", p ? static_cast<int>(location(p)) : -1);
    }
    std::printf("],\"pool\":\"%s\",\"events\":[", hex(pool, allocated * 0x480).c_str());
    for (std::size_t i = 0; i < events.size(); ++i) std::printf("%s\"%s\"", i ? "," : "", events[i].c_str());
    std::puts("]}");
}
}
namespace porsche {
const std::uint8_t* formatter_cleanup_handle_table_006c01e0[64]{};
std::uint32_t formatter_cleanup_handle_limit_006c02e0;
std::int32_t formatter_app_type_005e52cc;
void* __cdecl exit_registry_malloc_005a3be5(std::uint32_t size) {
    events.push_back("malloc:" + std::to_string(size)); ++allocations;
    if (allocations == fail_allocation) return nullptr;
    if (size != 0x480 || allocated == 64) std::abort();
    return pool[allocated++];
}
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int message) {
    events.push_back("fatal:" + std::to_string(message)); throw Fatal{};
}
void __cdecl exit_registry_lock_api_005a4ba4(std::uint32_t id) {
    events.push_back("lock:" + std::to_string(id));
    if (id == 17 && mutation == 1) write32(pool[0] + 5 * 36 + 8, 2);
}
void __cdecl exit_registry_unlock_api_005a4c05(std::uint32_t id) {
    events.push_back("unlock:" + std::to_string(id));
    if (id == 17 && mutation == 4) formatter_cleanup_handle_table_006c01e0[0] = pool[1];
}
void __stdcall formatter_lowio_startup_info(FormatterLowioStartupInfo32* out) {
    events.push_back("startup"); std::memset(out, 0, sizeof(*out));
    out->reserved_bytes = reserved_present ? 1 : 0;
    out->reserved = pointer_present ? inherited : nullptr;
}
std::uint32_t __stdcall formatter_lowio_file_type(std::uint32_t handle) {
    events.push_back("type:" + std::to_string(handle));
    if (mutation == 5 && handle >= 0x1000 && handle < 0x1000 + 2050) {
        const auto id = handle - 0x1000;
        write32(inherited + 4 + declared_count + id * 4, 0x9000 + id);
        inherited[4 + id] = 0x41;
    }
    if (type_pattern == 0) return 1;
    if (type_pattern == 1) return handle % 4;
    if (type_pattern == 2) return 0x100 + handle % 4;
    return 0;
}
std::uint32_t __stdcall formatter_lowio_get_standard(std::int32_t id) {
    events.push_back("getstd:" + std::to_string(id));
    const unsigned slot = static_cast<unsigned>(-10 - id);
    if (std_mode == 0) return 0x3000 + slot;
    if (std_mode == 1) return 0xffffffff;
    return slot == 0 ? 0 : slot == 1 ? 0xffffffff : 0x3002;
}
std::uint32_t __stdcall formatter_lowio_set_count(std::uint32_t count) {
    events.push_back("count:" + std::to_string(count)); return count + 7;
}
int __stdcall formatter_lowio_set_standard(std::int32_t id, std::uint32_t handle) {
    events.push_back("setstd:" + std::to_string(id) + ":" + std::to_string(handle));
    if (mutation == 4) formatter_cleanup_handle_table_006c01e0[0] = pool[1];
    return 0;
}
void __stdcall formatter_lowio_critical_initialize(void* p) {
    events.push_back("init:" + std::to_string(location(p)));
    std::memset(p, 0x5a, 24);
    if (mutation == 3) write32(static_cast<std::uint8_t*>(p) - 4, 3);
}
void __stdcall formatter_lowio_critical_enter(void* p) {
    events.push_back("enter:" + std::to_string(location(p)));
    if (mutation == 2 && location(p) == 5 * 36 + 12) pool[0][5 * 36 + 4] |= 1;
}
void __stdcall formatter_lowio_critical_leave(void* p) {
    events.push_back("leave:" + std::to_string(location(p)));
}
std::int32_t* __cdecl formatter_lowio_errno_005a669e() { events.push_back("errno"); return &error_value; }
std::uint32_t* __cdecl formatter_lowio_doserrno_005a66a7() { events.push_back("doserrno"); return &dos_error; }
}

int main() {
    using namespace porsche;
    char kind;
    while (std::cin >> kind) {
        reset(); std::uint32_t result = 0; bool fatal = false;
        if (kind == 'i') {
            int reserved, pointer;
            std::cin >> reserved >> pointer >> declared_count >> fail_allocation >> std_mode >> inherited_pattern >> type_pattern >> mutation;
            reserved_present = reserved != 0; pointer_present = pointer != 0;
            write32(inherited, static_cast<std::uint32_t>(declared_count));
            if (declared_count > 0) {
                for (int i = 0; i < declared_count; ++i) {
                    const unsigned pattern = static_cast<unsigned>(i) % 5;
                    inherited[4 + i] = inherited_pattern == 0 ? 1 : pattern == 1 ? 0 : pattern == 2 ? 9 : pattern == 3 ? 0xc1 : 0x21;
                    write32(inherited + 4 + declared_count + i * 4,
                            inherited_pattern && pattern == 0 ? 0xffffffffu : 0x1000 + i);
                }
            }
            try { result = formatter_lowio_initialize_005a953e(); } catch (const Fatal&) { fatal = true; }
        } else if (kind == 'a') {
            unsigned scenario;
            std::cin >> scenario;
            if (scenario == 0) {}
            else if (scenario == 6) seed_banks(64);
            else if (scenario == 11) seed_banks(2);
            else seed_banks(1);
            if (scenario == 1 || scenario == 2 || scenario == 3 || scenario == 4 || scenario == 9 || scenario == 10) {
                const unsigned slot = scenario == 9 ? 0 : 5;
                pool[0][slot * 36 + 4] = 0;
                write32(pool[0] + slot * 36 + 8, scenario == 2 ? 1 : 0);
            }
            if (scenario == 3) mutation = 1;
            if (scenario == 4) { mutation = 2; pool[0][6 * 36 + 4] = 0; write32(pool[0] + 6 * 36 + 8, 0); }
            if (scenario == 7) fail_allocation = 1;
            if (scenario == 10) mutation = 3;
            if (scenario == 11) { mutation = 4; pool[0][31 * 36 + 4] = 0; write32(pool[0] + 31 * 36 + 8, 0); }
            result = static_cast<std::uint32_t>(formatter_lowio_allocate_005ab4c6());
        } else if (kind == 'l') {
            unsigned operation, id, old_handle, flags, lock_state;
            std::cin >> operation >> id >> formatter_app_type_005e52cc >> old_handle >> flags >> lock_state >> mutation;
            seed_banks(2);
            if (id < 64) {
                auto* p = pool[id >> 5] + (id & 31) * 36;
                write32(p, old_handle); p[4] = static_cast<std::uint8_t>(flags); write32(p + 8, lock_state);
            }
            if (operation == 0) result = static_cast<std::uint32_t>(formatter_lowio_attach_005ab5e9(id, 0x87654321));
            else if (operation == 1) result = static_cast<std::uint32_t>(formatter_lowio_detach_005ab665(id));
            else if (operation == 2) result = formatter_lowio_handle_005ab6e4(id);
            else if (operation == 3) formatter_lowio_lock_005ab726(id);
            else formatter_lowio_unlock_005ab785(id);
        } else return 2;
        print_state(result, fatal);
    }
}
