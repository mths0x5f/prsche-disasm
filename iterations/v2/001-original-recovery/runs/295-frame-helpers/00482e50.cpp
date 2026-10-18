#include "../290-frame-service-cluster/frame_service_290.hpp"

namespace porsche {
// Original read-only PE cells; the game data owner is a separate link boundary.
extern const float frame_limit_005b47d8;
extern const float frame_step_005b2764;

void __thiscall FrameTail_290::invoke_00482e50() {
    auto* self = reinterpret_cast<std::uint8_t*>(this);
    for (std::uint32_t i = 0, offset = 0;
         i < *reinterpret_cast<const volatile std::uint32_t*>(self + 0x18);
         ++i, offset += 0x38) {
        auto const base = *reinterpret_cast<const std::uint32_t*>(self + 0x40);
        auto* entry = reinterpret_cast<std::uint8_t*>(static_cast<std::uintptr_t>(base) + offset);
        if (!entry[0x34]) continue;
        auto* value = reinterpret_cast<float*>(entry + 4);
        const auto* limit = &frame_limit_005b47d8;
        const auto* step = &frame_step_005b2764;
        std::uint16_t status;
        __asm {
            mov edx, value
            mov eax, limit
            fld dword ptr [edx]
            fcomp dword ptr [eax]
            fnstsw ax
            mov status, ax
        }
        if (status & 0x4100u) {
            __asm {
                mov edx, value
                mov eax, step
                fld dword ptr [edx]
                fadd dword ptr [eax]
                fstp dword ptr [edx]
            }
        }
    }
}
}
