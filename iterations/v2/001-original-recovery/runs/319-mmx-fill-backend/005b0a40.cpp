#include "005b0a40.hpp"

#include <cstdint>
#include <mmintrin.h>

namespace porsche {

// Original Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 005b0a40..005b0aef: cdecl destination, repeated DWORD value, byte count.
// This body leaves MMX/x87 tag state dirty. Caller 0053c290 executes EMMS;
// adding EMMS here would change observable behavior of direct callers.
static_assert(sizeof(void*) == 4, "original MMX fill requires Win32 pointers");

namespace {
bool signed_nonnegative(std::uint32_t ecx) {
    return (ecx & 0x80000000u) == 0;
}
bool signed_ge(std::uint32_t ecx, std::uint32_t threshold) {
    return (ecx ^ 0x80000000u) >= (threshold ^ 0x80000000u);
}
void write_word(std::uint8_t* at, std::uint32_t value) {
    *reinterpret_cast<std::uint16_t*>(at) = static_cast<std::uint16_t>(value);
}
void write_dword(std::uint8_t* at, std::uint32_t value) {
    *reinterpret_cast<std::uint32_t*>(at) = value;
}
void write_qword(std::uint8_t* at, __m64 pattern) {
    *reinterpret_cast<__m64*>(at) = pattern;
}
}

void* __cdecl heap_fill_mmx_005b0a40_core(void* destination,
    std::uint32_t value, std::uint32_t bytes) {
    auto* eax = static_cast<std::uint8_t*>(destination);
    std::uint32_t ecx = bytes;

    // 005b0ab2..005b0aeb peels low byte, word and optional DWORD. The tests
    // use the updated EAX address and signed ECX comparisons.
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

    // 005b0a53..005b0a56 executes even for a zero-byte fill. Intrinsics keep
    // the original MMX register state rather than replacing the stores with
    // integer copies or silently clearing it.
    __m64 mm0 = _mm_cvtsi32_si64(static_cast<int>(value));
    mm0 = _mm_unpacklo_pi32(mm0, mm0);

    // 005b0a59..005b0a75: four MOVQ stores for each 32-byte iteration.
    ecx -= 32u;
    if (signed_nonnegative(ecx)) {
        do {
            ecx -= 32u;
            write_qword(eax, mm0);
            write_qword(eax + 8, mm0);
            write_qword(eax + 16, mm0);
            write_qword(eax + 24, mm0);
            eax += 32;
        } while (signed_nonnegative(ecx));
    }

    // 005b0a77..005b0a85: remaining 8-byte MOVQ stores.
    ecx += 24u;
    if (signed_nonnegative(ecx)) {
        do {
            write_qword(eax, mm0);
            eax += 8;
            ecx -= 8u;
        } while (signed_nonnegative(ecx));
    }

    // 005b0a87..005b0ab1: DWORD/word/byte residual stores. No EMMS.
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

void __cdecl heap_fill_mmx_005b0a40(void* destination,
    std::uint32_t value, std::uint32_t bytes) {
    (void)heap_fill_mmx_005b0a40_core(destination, value, bytes);
}

} // namespace porsche
