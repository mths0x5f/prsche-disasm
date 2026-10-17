#include "frame_service_290.hpp"
#include <cstring>
namespace porsche {
namespace {
std::uint32_t read32(std::uintptr_t address) {
    std::uint32_t value;
    std::memcpy(&value,reinterpret_cast<const void*>(address),sizeof(value));
    return value;
}
}
void __thiscall FrameService_290::execute_00487e20() {
    const auto self=reinterpret_cast<std::uintptr_t>(this);
    std::uint32_t iterator=read32(read32(read32(self+0x14))+0x08);
    while(iterator!=read32(read32(self+0x14))) {
        FrameTemporary_290 temporary;
        auto* resolver=reinterpret_cast<FrameResolver_290*>(read32(iterator+0x14));
        auto* returned=resolver->resolve_004898f0(&temporary,0);
        const auto action=read32(reinterpret_cast<std::uintptr_t>(returned));
        if(action) reinterpret_cast<FrameAction_290*>(action)->invoke_00476170();
        reinterpret_cast<FrameIterator_290*>(&iterator)->advance_00423840();
    }
    const auto tail=read32(self+0x1c);
    if(tail) reinterpret_cast<FrameTail_290*>(tail)->invoke_00482e50();
}
}
