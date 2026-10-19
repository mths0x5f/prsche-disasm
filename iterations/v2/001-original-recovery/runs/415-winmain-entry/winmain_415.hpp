// Run 415 — WinMain and companion pre-WinMain initializers
// Original Porsche.exe:
//   004b66d0..004b66e4 (20 bytes)  winmain_set_heap_size_004b66d0
//   004b66f0..004b6703 (19 bytes)  winmain_compute_scale_004b66f0
//   004b6710..004b67a5 (149 bytes) winmain_004b6710
#ifndef PORSCHE_WINMAIN_415_HPP
#define PORSCHE_WINMAIN_415_HPP

#include <cstdint>

namespace porsche {

extern "C" {
    // 004b66d0 (20 bytes) — sets global heap buffer size (0x800000 = 8MB)
    void winmain_set_heap_size_004b66d0(void);

    // 004b66f0 (19 bytes) — computes float scale reciprocal 1.0f / *(float*)0x65b290
    void winmain_compute_scale_004b66f0(void);

    // 004b6710 (149 bytes) — WinMain standard entry point
    int __stdcall winmain_004b6710(void* hInstance, void* hPrevInstance, char* lpCmdLine, int nShowCmd);
}

} // namespace porsche

#endif // PORSCHE_WINMAIN_415_HPP
