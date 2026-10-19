#include "005b0980.hpp"

#include <cstdint>

namespace porsche {

// Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Original 005b0980..005b099d + 005b09a0..005b0a39, 184 indexed bytes.
// Input: cdecl(dst, repeated little-endian DWORD, byte count). EAX returns
// the advanced destination pointer. No calls or global storage in this body.
static_assert(sizeof(void*) == 4, "original scalar fill requires Win32 pointers");

namespace {
void write_word(std::uint8_t* at, std::uint32_t value) {
    *reinterpret_cast<std::uint16_t*>(at) = static_cast<std::uint16_t>(value);
}
void write_dword(std::uint8_t* at, std::uint32_t value) {
    *reinterpret_cast<std::uint32_t*>(at) = value;
}
bool signed_nonnegative(std::uint32_t ecx) {
    return (ecx & 0x80000000u) == 0;
}
bool signed_ge(std::uint32_t ecx, std::uint32_t threshold) {
    return (ecx ^ 0x80000000u) >= (threshold ^ 0x80000000u);
}
}

void* __cdecl heap_fill_scalar_005b0980_core(void* destination,
    std::uint32_t value, std::uint32_t bytes) {
    auto* eax = static_cast<std::uint8_t*>(destination);
    std::uint32_t ecx = bytes;

    // 005b09fc..005b0a35: peel one byte, one word, and optionally one DWORD.
    // The original tests each updated EAX, including its 0x4 address bit.
    if ((reinterpret_cast<std::uintptr_t>(eax) & 3u) != 0) {
        if ((reinterpret_cast<std::uintptr_t>(eax) & 1u) != 0 && signed_ge(ecx, 1u)) {
            *eax++ = static_cast<std::uint8_t>(value);
            ecx -= 1u;
        }
        if ((reinterpret_cast<std::uintptr_t>(eax) & 2u) != 0 && signed_ge(ecx, 2u)) {
            write_word(eax, value);
            eax += 2;
            ecx -= 2u;
        }
        if ((reinterpret_cast<std::uintptr_t>(eax) & 4u) != 0 && signed_ge(ecx, 4u)) {
            write_dword(eax, value);
            eax += 4;
            ecx -= 4u;
        }
    }

    // 005b0997..005b09bd: subtract before entering; each 32-byte iteration
    // subtracts again before eight DWORD stores, then advances EAX by 32.
    ecx -= 32u;
    if (signed_nonnegative(ecx)) {
        do {
            ecx -= 32u;
            for (std::uint32_t i = 0; i != 32; i += 4)
                write_dword(eax + i, value);
            eax += 32;
        } while (signed_nonnegative(ecx));
    }

    // 005b09bf..005b09cf: 8-byte pairs, retaining exact signed-flag flow.
    ecx += 24u;
    if (signed_nonnegative(ecx)) {
        do {
            write_dword(eax, value);
            write_dword(eax + 4, value);
            eax += 8;
            ecx -= 8u;
        } while (signed_nonnegative(ecx));
    }

    // 005b09d1..005b09fb: residual DWORD, word, and byte. The original
    // returns immediately on zero residual and otherwise compares unsigned.
    ecx += 8u;
    if (ecx == 0)
        return eax;
    if (ecx >= 4u) {
        write_dword(eax, value);
        eax += 4;
        ecx -= 4u;
    }
    if (ecx >= 2u) {
        write_word(eax, value);
        eax += 2;
        ecx -= 2u;
    }
    if (ecx >= 1u) {
        *eax++ = static_cast<std::uint8_t>(value);
        --ecx;
    }
    return eax;
}

void __cdecl heap_fill_scalar_005b0980(void* destination,
    std::uint32_t value, std::uint32_t bytes) {
    (void)heap_fill_scalar_005b0980_core(destination, value, bytes);
}

} // namespace porsche
