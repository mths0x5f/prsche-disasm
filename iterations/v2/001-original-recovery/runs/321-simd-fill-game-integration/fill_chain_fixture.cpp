// Test-only full original dispatcher/backend chain. Never in the game graph.
#include "0053c290.hpp"
#include "original_bodies.hpp"
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <xmmintrin.h>

using U = std::uint32_t;
using Fn = void (__cdecl*)(void*, U, U);
namespace porsche {
// Fixture-only provider for a production cell owned by heap.cpp.
U copy_flag_005deb18 = 0;
}
static unsigned char* code;
static unsigned checks, failures, cases;
static void check(bool value) { ++checks; if (!value) ++failures; }

static void init_code() {
    code = static_cast<unsigned char*>(VirtualAlloc(nullptr, 4096,
        MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
    check(code != nullptr); if (!code) return;
    std::memcpy(code, dispatcher_bytes, sizeof(dispatcher_bytes));
    std::memcpy(code + 0x100, scalar_bytes, sizeof(scalar_bytes));
    std::memcpy(code + 0x200, mmx_bytes, sizeof(mmx_bytes));
    std::memcpy(code + 0x300, sse_bytes, sizeof(sse_bytes));
    // Only the dispatcher's original absolute data operands and CALL rel32s
    // relocate. Backend internal relative jumps retain their complete raw spans.
    const U cells[] = {0x005deb1c, 0x005deb18};
    const U offsets[] = {4, 0x23};
    const U providers[] = {U(&porsche::shared_runtime_word_005deb1c), U(&porsche::copy_flag_005deb18)};
    for (U i = 0; i < 2; ++i) {
        U old; std::memcpy(&old, code + offsets[i], 4); check(old == cells[i]);
        std::memcpy(code + offsets[i], &providers[i], 4);
    }
    const U calls[] = {0x18, 0x37, 0x43};
    const U targets[] = {0x300, 0x200, 0x100};
    const U original_targets[] = {0x005b0b00, 0x005b0a40, 0x005b0980};
    for (U i = 0; i < 3; ++i) {
        check(code[calls[i]] == 0xe8);
        U old; std::memcpy(&old, code + calls[i] + 1, 4);
        check(0x0053c290u + calls[i] + 5 + old == original_targets[i]);
        U relative = targets[i] - (calls[i] + 5);
        std::memcpy(code + calls[i] + 1, &relative, 4);
    }
    DWORD old; check(VirtualProtect(code, 4096, PAGE_EXECUTE_READ, &old) != 0);
    check(FlushInstructionCache(GetCurrentProcess(), code, 4096) != 0);
}

struct Result {
    bool abi;
    unsigned short control, status;
    unsigned char tag;
    U mxcsr;
};
static Result invoke(Fn fn, void* dst, U pattern, U count, bool populated) {
    __declspec(align(16)) unsigned char fx[512] = {};
    U before, after, saved_bx, bx2, saved_si, si2, saved_di, di2, saved_bp, bp2;
    const U saved_mxcsr = _mm_getcsr();
    _mm_setcsr(0x1f80);
    __asm { fninit }
    if (populated) { __asm { fld1 } }
    __asm {
        mov before, esp
        mov saved_bx, ebx
        mov saved_si, esi
        mov saved_di, edi
        mov saved_bp, ebp
        push count
        push pattern
        push dst
        mov eax, fn
        call eax
        add esp, 12
        mov after, esp
        mov bx2, ebx
        mov si2, esi
        mov di2, edi
        mov bp2, ebp
        // Test observation barrier after both implementations, not in either body.
        sfence
        lea eax, fx
        fxsave [eax]
        emms
        fninit
    }
    Result r{};
    r.abi = before == after && saved_bx == bx2 && saved_si == si2 && saved_di == di2 && saved_bp == bp2;
    std::memcpy(&r.control, fx, 2); std::memcpy(&r.status, fx + 2, 2);
    r.tag = fx[4]; std::memcpy(&r.mxcsr, fx + 24, 4);
    _mm_setcsr(saved_mxcsr);
    return r;
}

static void one(U mask, U alignment, U count, U pattern, bool populated) {
    __declspec(align(32)) unsigned char a[4352], b[4352];
    std::memset(a, 0x5a, sizeof(a)); std::memset(b, 0x5a, sizeof(b));
    const U sse = (mask & 2) ? 0x80000000u : 0;
    const U mmx = (mask & 1) ? 0x12345678u : 0;
    porsche::copy_flag_005deb1c = sse; porsche::copy_flag_005deb18 = mmx;
    const Result x = invoke(reinterpret_cast<Fn>(code), a + 64 + alignment, pattern, count, populated);
    const Result y = invoke(&porsche::heap_fill_0053c290, b + 64 + alignment, pattern, count, populated);
    check(x.abi && y.abi);
    check(std::memcmp(a, b, sizeof(a)) == 0);
    bool guards = true;
    for (U i = 0; i < sizeof(a); ++i)
        if ((i < 64 + alignment || i >= 64 + alignment + count) && (a[i] != 0x5a || b[i] != 0x5a)) guards = false;
    check(guards);
    check(x.control == y.control && x.status == y.status && x.tag == y.tag && x.mxcsr == y.mxcsr);
    check(x.control == 0x37f && x.mxcsr == 0x1f80);
    // MMX branch always reaches MOVD and dispatcher EMMS, including byte_count=0.
    check(x.tag == ((mmx && !sse) ? 0 : (populated ? 0x80 : 0)));
    check(porsche::copy_flag_005deb1c == sse && porsche::copy_flag_005deb18 == mmx);
    ++cases;
}

int main() {
    init_code(); if (!code || failures) return 2;
    const U lengths[] = {0,1,2,3,4,7,8,15,16,23,24,25,31,32,33,39,40,41,
                         63,64,65,95,96,97,127,128,129,255,256,257,1023,1024,1025,4095,4096,4097};
    const U patterns[] = {0,0xa1b2c3d4u,0xffffffffu};
    for (U mask = 0; mask < 4; ++mask)
        for (U alignment = 0; alignment < 32; ++alignment)
            for (U n : lengths) for (U value : patterns)
                for (U populated = 0; populated < 2; ++populated)
                    one(mask, alignment, n, value, populated != 0);
    std::printf("cases=%u checks=%u failures=%u\n", cases, checks, failures);
    return failures ? 1 : 0;
}
