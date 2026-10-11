#pragma once
#include "porsche/network_workers_members.hpp"
#include <cstdint>
namespace porsche {
// Original 005e8e50 string address. Owner/extent and prior aliases remain unresolved.
extern char network_group_text_005e8e50[];
void __fastcall network_group_acknowledge_0048c220(void*,void*,void* member,std::uint32_t value,std::uint32_t ignored);
void __fastcall network_group_clear_member_messages_0048c300(void*,void*);
void __fastcall network_group_publish_00490b70(void* session,void*,void* group);
void __fastcall network_group_send_member_messages_0048a390(void* member,void*,void* receiver,std::uint32_t destination);
void __fastcall network_group_send_state_0048baa0(void* group,void*,std::uint32_t destination);
} // namespace porsche
