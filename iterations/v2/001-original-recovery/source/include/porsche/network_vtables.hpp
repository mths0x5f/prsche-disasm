#pragma once
#include <cstddef>
#include <cstdint>
namespace porsche {
using NetworkSendSlot = void (__fastcall*)(void*,void*,std::uint32_t,const std::uint8_t*,std::uint32_t);
// Only the preceding COL word and one send slot are proven. RTTI objects have
// no guessed extent or production definition. These link dependencies remain open.
extern const unsigned char network_rtti_005c5190[];
extern const unsigned char network_rtti_005c51d8[];
extern const unsigned char network_rtti_005c5228[];
struct NetworkSendTable { const void* rtti; NetworkSendSlot send; };
static_assert(offsetof(NetworkSendTable,send)==4 && sizeof(NetworkSendTable)==8);
extern const NetworkSendTable network_vtable_owner_005b4968;
extern const NetworkSendTable network_vtable_owner_005b4970;
extern const NetworkSendTable network_vtable_owner_005b4978;
void __fastcall network_send_queue_0048ad70(void*,void*,std::uint32_t,const std::uint8_t*,std::uint32_t);
void __fastcall network_send_member_0048b340(void*,void*,std::uint32_t,const std::uint8_t*,std::uint32_t);
[[noreturn]] void __fastcall network_purecall_005a1056(void*,void*,std::uint32_t,const std::uint8_t*,std::uint32_t);
std::uint32_t* __fastcall network_packet_insert_0048a920(void*,void*,std::uint32_t*,std::uint32_t,const void*);
std::uint32_t* __fastcall network_packet_unlink_0048a8d0(void*,void*,std::uint32_t*,std::uint32_t);
std::uint32_t __fastcall network_member_packet_0048a3d0(void*,void*,const std::uint8_t*,std::uint32_t,void*);
std::uint32_t __cdecl network_transport_send_0055d4a0(void*,const std::uint8_t*,std::uint32_t);
void* __cdecl network_transport_owner_0055c260(void*);
std::uint32_t __cdecl network_transport_member_send_0055c270(void*,void*,const std::uint8_t*,std::uint32_t);
std::uint32_t __cdecl network_transport_packet_00560420(void*,const std::uint8_t*,std::uint32_t);
std::uint32_t __cdecl network_transport_dispatch_00586fb0(void*,std::uint32_t,const std::uint32_t*);
// Unrecovered lower transport bodies, not placeholder implementations.
std::uint32_t __cdecl network_transport_direct_00587000(void*,std::uint32_t,const std::uint32_t*);
std::uint32_t __cdecl network_transport_routed_005870b0(void*,std::uint32_t,const std::uint32_t*,std::uint32_t);
}
