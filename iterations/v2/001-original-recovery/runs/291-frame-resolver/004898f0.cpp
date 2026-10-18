#include "../290-frame-service-cluster/frame_service_290.hpp"
#include <cstring>

namespace porsche {
FrameTemporary_290* __thiscall FrameResolver_290::resolve_004898f0(
    FrameTemporary_290* output, std::uint32_t argument) {
    std::uint32_t value;
    std::memcpy(&value, reinterpret_cast<const std::uint8_t*>(this) + 0x14, 4);
    const auto tag = static_cast<std::uint16_t>(argument);
    std::memcpy(output, &value, 4);
    reinterpret_cast<std::uint8_t*>(output)[4] = 0;
    std::memcpy(reinterpret_cast<std::uint8_t*>(output) + 6, &tag, 2);
    return output;
}
}
