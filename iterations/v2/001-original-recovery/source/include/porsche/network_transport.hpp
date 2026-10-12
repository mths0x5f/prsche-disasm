#pragma once
#include "porsche/network_vtables.hpp"
namespace porsche {
using NetworkRouteSend = std::uint32_t (__cdecl*)(void*,std::uint32_t,std::uint32_t,std::uint32_t*,void*);
using NetworkBufferSend = std::uint32_t (__cdecl*)(void*,const void*,std::uint32_t);
using NetworkListPredicate = std::uint32_t (__cdecl*)(void*,std::uint32_t);
std::uint32_t __cdecl network_transport_stage_00587110(void*,std::uint32_t,std::uint32_t,std::uint32_t*,void*);
std::uint32_t __cdecl network_transport_control_00586ee0(void*,std::uint32_t,std::uint32_t,std::uint32_t*,void*);
void* __cdecl network_route_at_00580b20(void*,std::uint32_t);
void* __cdecl network_route_next_00580b70(void*,std::uint32_t);
std::uint32_t __cdecl network_route_index_00580a00(void*,void*);
std::uint32_t __cdecl network_route_first_value_00580a50(void*);
}
