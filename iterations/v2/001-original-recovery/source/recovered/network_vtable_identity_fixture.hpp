#pragma once
#include "porsche/network_vtables.hpp"
#include <cstdlib>
#include <initializer_list>

// Private linkage only for destructor/member probes that never dispatch a send.
// Actual production owners and send targets are exercised by network_vtables_probe.
namespace porsche {
namespace {
void __fastcall network_fixture_unreached_send(void*,void*,std::uint32_t,const std::uint8_t*,std::uint32_t) { std::abort(); }
}
const NetworkSendTable network_vtable_owner_005b4968{nullptr,network_fixture_unreached_send};
const NetworkSendTable network_vtable_owner_005b4970{nullptr,network_fixture_unreached_send};
const NetworkSendTable network_vtable_owner_005b4978{nullptr,network_fixture_unreached_send};
inline std::uint32_t network_fixture_word(std::uint32_t value) {
    // Raw original addresses must not silently pass as relocated native pointers.
    for (const auto* table : {&network_vtable_owner_005b4968,&network_vtable_owner_005b4970,&network_vtable_owner_005b4978}) {
        const auto identity = table==&network_vtable_owner_005b4968 ? 0x005b4968u : table==&network_vtable_owner_005b4970 ? 0x005b4970u : 0x005b4978u;
        if (value==identity) std::abort();
        if (value==reinterpret_cast<std::uint32_t>(&table->send)) return identity;
    }
    return value;
}
}
