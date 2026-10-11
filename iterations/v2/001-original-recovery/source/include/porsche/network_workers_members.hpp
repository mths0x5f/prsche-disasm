#pragma once
#include "porsche/network_session.hpp"
#include "porsche/file_threads.hpp"
#include "porsche/files.hpp"
#include <array>
#include <cstddef>
#include <cstdint>

namespace porsche {
// 0057ffc0 initializes both 28-byte lists and the event at +194; 0055d800
// passes this exact static base. Prefix bytes remain uninterpreted.
struct NetworkWorkerState {
    std::array<std::uint8_t,0x194> opaque;
    void* event;
    IoList free_messages;
    IoList queued_messages;
};
static_assert(offsetof(NetworkWorkerState,free_messages)==0x198);
static_assert(offsetof(NetworkWorkerState,queued_messages)==0x1b4);
static_assert(sizeof(NetworkWorkerState)==0x1d0);
extern NetworkWorkerState network_worker_state_006a3b60;
extern ThreadRecord network_worker_thread_006a3d30;
extern std::uint32_t network_worker_active_006a4660;

void* __cdecl network_worker_get_00580050(void* worker);
std::uint32_t __cdecl network_worker_submit_00580080(void* worker,void* message);
std::uint32_t __cdecl network_worker_dispose_00580020(void* worker);
void __cdecl network_worker_clear_extra_0055c060(void* worker);
void __cdecl network_worker_queue_dispose_005806c0(IoList* queue);
std::uint32_t __cdecl network_worker_queue_count_005809f0(const IoList* queue);

void __fastcall network_member_connection_remove_0048b5a0(void* connection,void* unused_edx,void* member);
void __fastcall network_member_destroy_0048a7a0(void* member,void* unused_edx);
std::uint32_t* __fastcall network_member_end_00529050(void* list,void* unused_edx,std::uint32_t* output);
std::uint32_t* __fastcall network_member_copy_0050e140(void* output,void* unused_edx,const std::uint32_t* source);
std::uint32_t* __fastcall network_member_insert_004937f0(void* list,void* unused_edx,
    std::uint32_t* output,std::uint32_t before,const std::uint32_t* value);

// Explicit unrecovered group effect. Its receiver flag is reread after call.
void __fastcall network_member_group_remove_0048bda0(void* group,void* unused_edx,void* member);
} // namespace porsche
