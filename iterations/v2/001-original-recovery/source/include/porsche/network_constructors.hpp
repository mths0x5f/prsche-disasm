#pragma once
#include "porsche/network_vtables.hpp"
#include <cstdint>
namespace porsche {
// Read4 at5b4990 is proven. Identity5b4980 remains an unsized dependency.
extern const unsigned char network_connection_identity_005b4980[];
extern const std::uint32_t network_connection_port_005b4990;
void* __fastcall network_client_construct_0048aa10(void*,void*,std::uint32_t,std::uint32_t,std::uint32_t,const char*,const char*,const char*,const char*,std::uint32_t);
void* __fastcall network_host_construct_0048af80(void*,void*,std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t,const void*,const char*,std::uint32_t);
void __fastcall network_host_start_client_0048b3c0(void*,void*);
void __fastcall network_host_restart_client_0048b450(void*,void*);
std::uint32_t __cdecl network_address_get_0055d5a0(void*,void*,void*,void*);
std::uint32_t __cdecl network_address_parse_0055d5e0(void*,const char*,std::uint32_t,void*);
std::uint32_t __cdecl network_address_equal_0055d6e0(void*,const void*,const void*);
std::uint32_t __cdecl network_address_provider_mode_0055d730(void*);
std::uint32_t __cdecl network_address_text_mode_0055d750(void*);
std::uint32_t __cdecl network_address_compare_dispatch_00580590(void*,const void*,const void*);
std::uint32_t __cdecl network_address_parse_dispatch_005805b0(void*,std::uint32_t,std::uint32_t,std::uint32_t);
std::uint32_t __cdecl network_address_get_dispatch_005805e0(void*,std::uint32_t,std::uint32_t,std::uint32_t);
// Unrecovered transport/worker effects. No production substitute supplied.
void* __cdecl network_client_worker_construct_0055c370(std::uint32_t,std::uint32_t,const void*,const void*,std::uint32_t,std::uint32_t);
void* __cdecl network_host_worker_construct_0055aaa0(std::uint32_t,std::uint32_t,const void*,const void*,std::uint32_t,std::uint32_t,std::uint32_t);
std::uint32_t __cdecl network_address_current_0055d650(void*,void*);
std::uint32_t __fastcall network_client_connect_0048ac90(void*,void*,const char*,std::uint32_t);
}
