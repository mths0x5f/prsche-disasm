#pragma once
#include "porsche/network_cleanup.hpp"
#include <cstdint>

namespace porsche {
// Original .data byte is 1; the lock-cell pointer is zero-filled BSS.
extern std::uint8_t network_session_stopped_005d07d0;
extern void* network_session_lock_cell_00628c78;

void __fastcall network_session_stop_connection_0048b310(void* receiver,void* unused_edx);
void __fastcall network_session_clear_list_00493130(void* list,void* unused_edx);
void __fastcall network_session_connection_destroy_0048b250(void* receiver,void* unused_edx);

// Unrecovered effects retain their exact original register/stack arguments.
void __fastcall network_session_remove_member_00492770(void* session,void* unused_edx,void* member);
void __cdecl network_session_stop_worker_0055bfd0(void* worker);
} // namespace porsche
