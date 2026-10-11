#include "porsche/network_cleanup.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/heap_locks.hpp"
#include <cstdint>
#include <cstring>

namespace porsche {
void* network_cleanup_list_00628c60 = nullptr;
void* network_cleanup_lock_cell_00628c64 = nullptr;
namespace {
using U = std::uint32_t;
U load(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void store(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
void* pointer(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U address(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
void recycle(void* node,U offset){
    auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
    heap_enter_005322b0(pointer(load(pool)));
    store(node,4,load(pool,offset));store(pool,offset,address(node));
    heap_leave_005322c0(pointer(load(pool)));
}
void reset_head(void* list){
    void* head=pointer(load(list));store(head,0,address(head));
    head=pointer(load(list));store(head,4,address(head));
}
}

// 0048c430..0048c482: capture lock cell, then reload the global list after
// locking. Matching indirect object slots are cleared without unlinking.
void __fastcall network_services_detach_0048c430(void* receiver,void*){
    if(!network_cleanup_list_00628c60)return;
    void* cell=network_cleanup_lock_cell_00628c64;
    heap_enter_005322b0(pointer(load(cell)));
    void* head=pointer(load(network_cleanup_list_00628c60));
    void* node=pointer(load(head));
    if(node!=head){
        do{
            void* item=pointer(load(node,8));
            if(load(item)==address(receiver))store(item,0,0);
            void* wrapper=network_cleanup_list_00628c60;
            node=pointer(load(node));
            head=pointer(load(wrapper));
        }while(node!=head);
    }
    heap_leave_005322c0(pointer(load(cell)));
}

// 004c3150..004c315c: thiscall RET4, EAX returns the supplied output pointer.
std::uint32_t* __fastcall network_services_begin_004c3150(void* list,void*,U* output){
    const U first=load(pointer(load(list)));
    *output=first;
    return output;
}

// 004904d0..0049059b: remove duplicate payloads as a group, then recycle
// the list sentinel. The residual-node loop is preserved from the source.
void __fastcall network_services_destroy_004904d0(void* receiver,void*){
    auto* list=static_cast<std::uint8_t*>(receiver)+0x5c;
    void* head=pointer(load(list));
    while(load(head)!=address(head)){
        head=pointer(load(list));
        const U value=load(pointer(load(head,4)),8);
        void* node=pointer(load(head));
        while(node!=head){
            const U item=load(node,8);
            void* next=pointer(load(node));
            if(item==value){U output;network_services_unlink_0048b660(list,nullptr,&output,address(node));}
            node=next;
        }
        if(value){
            free_00531f90(pointer(load(pointer(value),4)));
            application_release_0059f050(pointer(value));
        }
        head=pointer(load(list));
    }
    head=pointer(load(list));
    void* node=pointer(load(head));
    while(node!=head){
        void* old=node;node=pointer(load(node));
        recycle(old,0x10);
        head=pointer(load(list));
    }
    reset_head(list);
    recycle(pointer(load(list)),0x10);
}

// 0048c580..0048c630: stop precedes the global reads. Capture the list
// allocation, but capture/reload the lock cell only after list disposal.
void __cdecl network_lifecycle_close_transport_0048c580(){
    network_cleanup_stop_worker_0055d9b0();
    void* list=network_cleanup_list_00628c60;
    if(list){
        void* head=pointer(load(list));
        void* node=pointer(load(head));
        while(node!=head){
            void* old=node;node=pointer(load(node));
            recycle(old,0x10);
            head=pointer(load(list));
        }
        reset_head(list);
        recycle(pointer(load(list)),0x10);
        application_release_0059f050(list);
    }
    void* cell=network_cleanup_lock_cell_00628c64;
    network_cleanup_list_00628c60=nullptr;
    if(cell){
        heap_lock_destroy_005322d0(pointer(load(cell)));
        application_release_0059f050(cell);
    }
    network_cleanup_lock_cell_00628c64=nullptr;
}

// 0048aed0..0048af75: both original vtable writes and the different +0x88
// pool chain are observable. List and lock fields are reloaded after effects.
void __fastcall network_lifecycle_connection_destroy_0048aed0(void* receiver,void*){
    auto* list=static_cast<std::uint8_t*>(receiver)+0xc;
    void* worker=pointer(load(receiver,4));
    store(receiver,0,0x005b4968);
    network_cleanup_destroy_worker_0055d1b0(worker);
    void* head=pointer(load(list));
    void* node=pointer(load(head));
    while(node!=head){
        void* old=node;node=pointer(load(node));
        recycle(old,0x88);
        head=pointer(load(list));
    }
    reset_head(list);
    recycle(pointer(load(list)),0x88);
    void* lock=pointer(load(receiver,8));
    store(receiver,0,0x005b4970);
    heap_lock_destroy_005322d0(lock);
}
} // namespace porsche
