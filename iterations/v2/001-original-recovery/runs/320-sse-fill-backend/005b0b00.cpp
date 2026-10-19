#include "005b0b00.hpp"

#include <cstdint>
#include <xmmintrin.h>

namespace porsche {

static_assert(sizeof(void*) == 4, "original SSE fill requires Win32 pointers");

namespace {
bool signed_nonnegative(std::uint32_t x) {
    return (x & 0x80000000u) == 0;
}
bool signed_ge(std::uint32_t x, std::uint32_t threshold) {
    return (x ^ 0x80000000u) >= (threshold ^ 0x80000000u);
}
void word(std::uint8_t* at, std::uint32_t value) {
    *reinterpret_cast<std::uint16_t*>(at) = static_cast<std::uint16_t>(value);
}
void dword(std::uint8_t* at, std::uint32_t value) {
    *reinterpret_cast<std::uint32_t*>(at) = value;
}
void low64(std::uint8_t* at, __m128 pattern) {
    _mm_storel_pi(reinterpret_cast<__m64*>(at), pattern);
}
void aligned128(std::uint8_t* at, __m128 pattern) {
    _mm_store_ps(reinterpret_cast<float*>(at), pattern);
}
} // namespace

void* __cdecl heap_fill_sse_005b0b00_core(void* destination,
    std::uint32_t value, std::uint32_t bytes) {
    auto* eax = static_cast<std::uint8_t*>(destination);
    std::uint32_t ecx = bytes;

    // 005b0b0c/12: MOVSS of the raw DWORD followed by SHUFPS lane broadcast.
    union { std::uint32_t bits; float raw; } input = {value};
    const __m128 scalar = _mm_load_ss(&input.raw);
    const __m128 pattern = _mm_shuffle_ps(scalar, scalar, 0);

    // 005b0b8a..ed tests each updated address and signed remaining count.
    if ((reinterpret_cast<std::uintptr_t>(eax) & 31u) != 0) {
        if ((reinterpret_cast<std::uintptr_t>(eax) & 1u) && signed_ge(ecx, 1u)) {
            *eax++ = static_cast<std::uint8_t>(value);
            ecx -= 1u;
        }
        if ((reinterpret_cast<std::uintptr_t>(eax) & 2u) && signed_ge(ecx, 2u)) {
            word(eax, value);
            eax += 2;
            ecx -= 2u;
        }
        if ((reinterpret_cast<std::uintptr_t>(eax) & 4u) && signed_ge(ecx, 4u)) {
            dword(eax, value);
            eax += 4;
            ecx -= 4u;
        }
        if ((reinterpret_cast<std::uintptr_t>(eax) & 8u) && signed_ge(ecx, 8u)) {
            low64(eax, pattern);
            eax += 8;
            ecx -= 8u;
        }
        if ((reinterpret_cast<std::uintptr_t>(eax) & 16u) && signed_ge(ecx, 16u)) {
            aligned128(eax, pattern);
            eax += 16;
            ecx -= 16u;
        }
    }

    // 005b0b1d..4d: aligned non-temporal stores, no invented production fence.
    ecx -= 32u;
    if (signed_nonnegative(ecx)) {
        do {
            _mm_stream_ps(reinterpret_cast<float*>(eax), pattern);
            _mm_stream_ps(reinterpret_cast<float*>(eax + 16), pattern);
            eax += 32;
            ecx -= 32u;
        } while (signed_nonnegative(ecx));
    }

    // 005b0b4f..5d: MOVLPS eight-byte stores.
    ecx += 24u;
    if (signed_nonnegative(ecx)) {
        do {
            low64(eax, pattern);
            eax += 8;
            ecx -= 8u;
        } while (signed_nonnegative(ecx));
    }

    // 005b0b5f..89: residual DWORD, word and byte.
    ecx += 8u;
    if (ecx == 0) return eax;
    if (ecx >= 4u) {
        dword(eax, value);
        eax += 4;
        ecx -= 4u;
    }
    if (ecx >= 2u) {
        word(eax, value);
        eax += 2;
        ecx -= 2u;
    }
    if (ecx >= 1u) *eax++ = static_cast<std::uint8_t>(value);
    return eax;
}

void __cdecl heap_fill_sse_005b0b00(void* destination,
    std::uint32_t value, std::uint32_t bytes) {
    (void)heap_fill_sse_005b0b00_core(destination, value, bytes);
}

} // namespace porsche
