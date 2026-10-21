#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "startup_context_bindings.hpp"

using U = std::uint32_t;
static_assert(sizeof(void*) == 4, "x86 ABI required");
static U expected_kind, expected_a, expected_b, expected_c, calls, errors, mutate;
static unsigned char arena[64];

static void observe(U kind, U a, U b, U c) {
    ++calls;
    if (kind != expected_kind || a != expected_a || b != expected_b || c != expected_c)
        ++errors;
    if (mutate && kind == 2)
        arena[16] = 0x12;
}

namespace porsche {
void __cdecl timer_setup_00565030(std::uint32_t value) {
    observe(1, value, 0, 0);
}
void __cdecl application_context_clear_004237d0(
    void* begin, std::uint32_t bytes, std::uint32_t mode) {
    observe(2, reinterpret_cast<U>(begin), bytes, mode);
}
}

struct Result { U esp0, esp1, ebp0, ebp1, ebx0, ebx1, esi0, esi1, edi0, edi1; };
static Result invoke(const void* fn, U kind, U a, U b, U c) {
    Result r{};
    __asm {
        lea eax, r
        mov [eax], esp
        mov [eax+8], ebp
        mov ebx, 13579bdfh
        mov esi, 2468ace0h
        mov edi, 6a31c5e7h
        mov [eax+16], ebx
        mov [eax+24], esi
        mov [eax+32], edi
        cmp kind, 1
        je timer_call
        push c
        push b
        push a
        mov ecx, fn
        call ecx
        add esp, 12
        jmp captured
    timer_call:
        push a
        mov ecx, fn
        call ecx
        add esp, 4
    captured:
        lea edx, r
        mov [edx+4], esp
        mov [edx+12], ebp
        mov [edx+20], ebx
        mov [edx+28], esi
        mov [edx+36], edi
    }
    return r;
}

static bool check(U kind, U a, U b, U c, U memory_mode) {
    expected_kind = kind; expected_a = a;
    expected_b = kind == 2 ? b : 0; expected_c = kind == 2 ? c : 0;
    calls = errors = 0; mutate = memory_mode;
    std::memset(arena, 0xa7, sizeof(arena));
    const void* fn = kind == 1
        ? reinterpret_cast<const void*>(&porsche::startup_capacity_00565030)
        : reinterpret_cast<const void*>(&porsche::game_setup_movie_delta_004237d0);
    const Result r = invoke(fn, kind, a, b, c);
    bool memory_ok = true;
    for (U i = 0; i < sizeof(arena); ++i)
        if (arena[i] != ((memory_mode && i == 16) ? 0x12 : 0xa7)) memory_ok = false;
    const bool pass = r.esp0 == r.esp1 && r.ebp0 == r.ebp1 &&
        r.ebx0 == r.ebx1 && r.esi0 == r.esi1 && r.edi0 == r.edi1 &&
        calls == 1 && errors == 0 && memory_ok;
    if (!pass) std::printf("divergence kind=%u a=%08x b=%08x c=%08x calls=%u errors=%u memory=%u\n",
        kind, a, b, c, calls, errors, memory_ok);
    return pass;
}

int main() {
    const U values[] = {0, 1, 0x80, 0x100, 0x7fffffff, 0x80000000, 0xffffffff, 0x12345678};
    U passed = 0;
    for (U a : values) {
        if (!check(1, a, 0, 0, 0)) return 10;
        ++passed;
    }
    for (U a : values) for (U b : values) for (U c : values) {
        if (!check(2, a, b, c, 0)) return 10;
        ++passed;
    }
    for (U b : values) for (U c : values) {
        if (!check(2, reinterpret_cast<U>(arena + 16), b, c, 1)) return 10;
        ++passed;
    }
    std::printf("cases=%u failures=0 args_order_mutation_ESP_nonvolatiles=PASS bridge_O2=PASS\n", passed);
    return passed == 584 ? 0 : 93;
}
