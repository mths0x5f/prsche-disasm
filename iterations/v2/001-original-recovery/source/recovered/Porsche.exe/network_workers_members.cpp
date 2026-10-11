#include "porsche/network_workers_members.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/file_wait.hpp"
#include "porsche/file_events.hpp"
#include "porsche/file_worker.hpp"
#include "porsche/heap_locks.hpp"
#include "porsche/thread_wait.hpp"
#include "porsche/window_runtime.hpp"
#include "porsche/fe_stream.hpp"
#include <cstdint>
#include <cstring>

namespace porsche {
NetworkWorkerState network_worker_state_006a3b60{};
ThreadRecord network_worker_thread_006a3d30{};
std::uint32_t network_worker_active_006a4660=0;
namespace {
using U=std::uint32_t;
U load(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void store(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
std::uint8_t byte(const void* p,U off){return static_cast<const std::uint8_t*>(p)[off];}
void setbyte(void* p,U off,std::uint8_t v){static_cast<std::uint8_t*>(p)[off]=v;}
void* pointer(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U address(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
IoList* queue(void* worker,U offset){return reinterpret_cast<IoList*>(static_cast<std::uint8_t*>(worker)+offset);}
void remove_matches(void* list,U value){network_services_remove_matching_00493180(list,nullptr,&value);}
void recycle(void* node,U offset){
    auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
    heap_enter_005322b0(pointer(load(pool)));
    store(node,4,load(pool,offset));store(pool,offset,address(node));
    heap_leave_005322c0(pointer(load(pool)));
}
void dispose_member_list(void* list){
    void* head=pointer(load(list));void* node=pointer(load(head));
    while(node!=head){void* old=node;node=pointer(load(node));recycle(old,0x88);head=pointer(load(list));}
    head=pointer(load(list));store(head,0,address(head));
    head=pointer(load(list));store(head,4,address(head));
    recycle(pointer(load(list)),0x88);
}
void* wait_for_message(void* worker,bool pump){
    void* message=network_worker_get_00580050(worker);
    while(!message){
        if(pump&&file_current_thread_0055f780(0))timed_callbacks_005366e0(0);
        file_sleep_0055f740(1);
        message=network_worker_get_00580050(worker);
    }
    return message;
}
}

// 005809f0..005809f6. Preserve unsigned comparison at the get caller.
U __cdecl network_worker_queue_count_005809f0(const IoList* list){return load(list);}
// 005806c0..005806df: dispose only an owned lock, always clear the lock field.
void __cdecl network_worker_queue_dispose_005806c0(IoList* list){
    if(byte(list,4)&2)heap_lock_destroy_005322d0(pointer(load(list,0x18)));
    store(list,0x18,0);
}
// 00580050..0058007b; 00580080..005800a6; 00580020..0058004d.
void* __cdecl network_worker_get_00580050(void* worker){
    IoList* list=queue(worker,0x198);
    return network_worker_queue_count_005809f0(list)>0?io_pop_00580790(list):nullptr;
}
U __cdecl network_worker_submit_00580080(void* worker,void* message){
    io_prepend_005806e0(queue(worker,0x1b4),static_cast<IoNode*>(message));
    return file_event_signal_0055fb30(pointer(load(worker,0x194)));
}
U __cdecl network_worker_dispose_00580020(void* worker){
    network_worker_queue_dispose_005806c0(queue(worker,0x198));
    network_worker_queue_dispose_005806c0(queue(worker,0x1b4));
    return file_close_event_0055fc10(pointer(load(worker,0x194)));
}
// 0055c060..0055c0a5: this order differs from ascending field offsets.
void __cdecl network_worker_clear_extra_0055c060(void* worker){
    for(U offset:{0x244u,0x260u,0x298u,0x27cu,0x2b4u})network_worker_queue_dispose_005806c0(queue(worker,offset));
}
// 0055bfd0..0055c057. The active bit is cleared before obtaining a message.
void __cdecl network_session_stop_worker_0055bfd0(void* worker){
    if(!(byte(worker,0x240)&1))return;
    store(worker,0x240,load(worker,0x240)&0xfffffffeu);
    void* message=wait_for_message(worker,true);store(message,4,6);
    network_worker_submit_00580080(worker,message);
    thread_wait_0055fa10(reinterpret_cast<ThreadRecord*>(static_cast<std::uint8_t*>(worker)+0x208),0);
    network_worker_dispose_00580020(worker);
    network_worker_clear_extra_0055c060(worker);
    free_00531f90(worker);
}
// 0055d1b0..0055d232. The active bit is cleared after obtaining a message.
void __cdecl network_cleanup_destroy_worker_0055d1b0(void* worker){
    if(!(byte(worker,0x248)&1))return;
    void* message=wait_for_message(worker,true);
    store(worker,0x248,load(worker,0x248)&0xfffffffeu);store(message,4,6);
    network_worker_submit_00580080(worker,message);
    thread_wait_0055fa10(reinterpret_cast<ThreadRecord*>(static_cast<std::uint8_t*>(worker)+0x22c),0);
    network_worker_dispose_00580020(worker);free_00531f90(worker);
}
// 0055d9b0..0055da0d. Static worker stop never pumps timed callbacks.
void __cdecl network_cleanup_stop_worker_0055d9b0(){
    if(!network_worker_active_006a4660)return;
    network_worker_active_006a4660=0;
    void* message=wait_for_message(&network_worker_state_006a3b60,false);
    store(message,4,6);network_worker_submit_00580080(&network_worker_state_006a3b60,message);
    thread_wait_0055fa10(&network_worker_thread_006a3d30,0);
}

// 00529050/0050e140: thiscall RET4, output pointer in EAX.
U* __fastcall network_member_end_00529050(void* list,void*,U* output){*output=load(list);return output;}
U* __fastcall network_member_copy_0050e140(void* output,void*,const U* source){const U value=*source;store(output,0,value);return static_cast<U*>(output);}
// 004937f0..0049385a: receiver unused; RET12. Read the value only after leave.
U* __fastcall network_member_insert_004937f0(void*,void*,U* output,U before,const U* value){
    auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
    heap_enter_005322b0(pointer(load(pool)));
    if(!load(pool,0x10))application_context_new_head_0059eeb0(1,0);
    const U node=load(pool,0x10);store(pool,0x10,load(pointer(node),4));
    heap_leave_005322c0(pointer(load(pool)));
    const U payload=node+8u;if(payload)store(pointer(payload),0,*value);
    store(pointer(node),0,before);store(pointer(node),4,load(pointer(before),4));
    store(pointer(load(pointer(before),4)),0,node);store(pointer(before),4,node);
    *output=node;return output;
}
// 0048b5a0..0048b604. Original signed +b4 test follows lock entry.
void __fastcall network_member_connection_remove_0048b5a0(void* connection,void*,void* member){
    heap_enter_005322b0(pointer(load(connection,8)));
    if(static_cast<std::int32_t>(load(member,0xb4))>0)remove_matches(static_cast<std::uint8_t*>(connection)+0x18,address(member));
    heap_leave_005322c0(pointer(load(connection,8)));
}
// 0048a7a0..0048a8ba: c8 list first, c4 second, both use +88 pool chain.
void __fastcall network_member_destroy_0048a7a0(void* member,void*){
    dispose_member_list(static_cast<std::uint8_t*>(member)+0xc8);
    dispose_member_list(static_cast<std::uint8_t*>(member)+0xc4);
}
// 00492770..004929a9: complete member-removal control flow. Unrecovered
// group effect remains typed; original flags and pointers are reread after it.
void __fastcall network_session_remove_member_00492770(void* session,void*,void* member){
    auto* object=static_cast<std::uint8_t*>(session);
    network_member_connection_remove_0048b5a0(pointer(load(session)),nullptr,member);
    if(byte(member,0xb8)){
        remove_matches(object+0x16c,address(member));
        application_network_message_0048c870(pointer(load(session,0x10)),nullptr,0xb9,load(member,0xac),0x80000000u,0,0);
    }else{
        U output;U* first=network_services_begin_004c3150(object+0x164,nullptr,&output);
        void* head=pointer(load(object+0x164));void* node=pointer(*first);
        while(node!=head){const U item=load(node,8);void* next=pointer(load(node));
            if(item==address(member)){U ignored;network_services_unlink_0048b660(object+0x164,nullptr,&ignored,address(node));}node=next;}
        if(!byte(member,0xbd)){
            const U count=load(session,0x154)-1u;store(session,0x154,count);
            void* connection=pointer(load(session));
            if(!byte(connection,0x14)&&load(connection,0x10)){
                const U combined=(load(session,0x158)<<16u)+count;
                application_network_message_0048c870(pointer(load(connection,0x10)),nullptr,0xb8,0,combined,0,0);
            }
            void* group=pointer(load(member,0xa4));
            if(!group){
                remove_matches(object+0x168,address(member));
                application_network_message_0048c870(pointer(load(session,0xc)),nullptr,0xb1,load(member,0xac),0x80000000u,0,0);
            }else{
                const std::uint8_t old=byte(group,0xcc3);
                network_member_group_remove_0048bda0(group,nullptr,member);
                if(old&&!byte(group,0xcc3)){
                    const U count2=load(session,0x15c)-1u;store(session,0x15c,count2);
                    if(!count2)network_lifecycle_remove_callback_00560180(0x00490640);
                    remove_matches(object+0x178,address(group));
                    U end,copy,result;U* selected=network_member_end_00529050(object+0x174,nullptr,&end);
                    network_member_copy_0050e140(&copy,nullptr,selected);
                    const U value=address(group);network_member_insert_004937f0(object+0x174,nullptr,&result,copy,&value);
                }
            }
        }
    }
    if(member){network_member_destroy_0048a7a0(member,nullptr);application_release_0059f050(member);}
}
} // namespace porsche
