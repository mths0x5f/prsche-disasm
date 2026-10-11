#include "porsche/network_session.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/heap_locks.hpp"
#include <cstdint>
#include <cstring>

namespace porsche {
std::uint8_t network_session_stopped_005d07d0=1;
void* network_session_lock_cell_00628c78=nullptr;
namespace {
using U=std::uint32_t;
U load(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void store(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
std::uint8_t byte(const void* p,U off){return static_cast<const std::uint8_t*>(p)[off];}
void setbyte(void* p,U off,std::uint8_t v){static_cast<std::uint8_t*>(p)[off]=v;}
void* pointer(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U address(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
void recycle(void* node){
    auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
    heap_enter_005322b0(pointer(load(pool)));
    store(node,4,load(pool,0x10));store(pool,0x10,address(node));
    heap_leave_005322c0(pointer(load(pool)));
}
void reset_head(void* list){
    void* head=pointer(load(list));store(head,0,address(head));
    head=pointer(load(list));store(head,4,address(head));
}
void clear_and_release_sentinel(void* list){
    network_session_clear_list_00493130(list,nullptr);
    application_context_clear_004237d0(pointer(load(list)),12,0);
}
void release_list_blocks(void* list){
    void* head=pointer(load(list));void* node=pointer(load(head));
    while(node!=head){
        void* old=node;node=pointer(load(node));
        application_context_clear_004237d0(old,12,0);
        head=pointer(load(list));
    }
    reset_head(list);
    application_context_clear_004237d0(pointer(load(list)),12,0);
}
}

// 0048b310..0048b336: read worker after entering, lock after worker effect.
void __fastcall network_session_stop_connection_0048b310(void* receiver,void*){
    heap_enter_005322b0(pointer(load(receiver,8)));
    network_session_stop_worker_0055bfd0(pointer(load(receiver,4)));
    setbyte(receiver,0x16,0);
    heap_leave_005322c0(pointer(load(receiver,8)));
}

// 00492260..00492289: stop flag precedes the test; member-active is cleared
// before the tail-called connection stop, unlike session destruction below.
void __cdecl network_lifecycle_stop_session_00492260(){
    void* session=network_lifecycle_session_00628c74;
    network_session_stopped_005d07d0=1;
    if(byte(session,0x17e)){
        setbyte(session,0x17e,0);
        network_session_stop_connection_0048b310(pointer(load(network_lifecycle_session_00628c74)),nullptr);
    }
}

// 00493130..0049317e: recycle nodes only, retain an empty sentinel.
void __fastcall network_session_clear_list_00493130(void* list,void*){
    void* head=pointer(load(list));void* node=pointer(load(head));
    while(node!=head){
        void* old=node;node=pointer(load(node));recycle(old);
        head=pointer(load(list));
    }
    reset_head(list);
}

// 0048b250..0048b30f: nested connection is reread after buffer release.
// The two literal vtable identities remain an explicit relocation backlog.
void __fastcall network_session_connection_destroy_0048b250(void* receiver,void*){
    U nested=load(receiver,0xc);store(receiver,0,0x005b4978);
    if(nested){
        application_release_0059f050(pointer(load(receiver,0x10)));
        nested=load(receiver,0xc);store(receiver,0x10,0);
        if(nested){
            network_lifecycle_connection_destroy_0048aed0(pointer(nested),nullptr);
            application_release_0059f050(pointer(nested));
        }
        store(receiver,0xc,0);
    }
    auto* list=static_cast<std::uint8_t*>(receiver)+0x18;
    network_session_clear_list_00493130(list,nullptr);
    recycle(pointer(load(list)));
    void* lock=pointer(load(receiver,8));store(receiver,0,0x005b4970);
    heap_lock_destroy_005322d0(lock);
}

// 00491fc0..00492257: complete session teardown, preserving all list orders,
// callback effects, indirect reloads and final pooled-release sequence.
void __fastcall network_lifecycle_session_destroy_00491fc0(void* receiver,void*){
    auto* session=static_cast<std::uint8_t*>(receiver);
    network_session_stopped_005d07d0=1;
    void* cell=network_session_lock_cell_00628c78;
    heap_enter_005322b0(pointer(load(cell)));
    heap_leave_005322c0(pointer(load(cell)));
    setbyte(receiver,0x17d,0);
    network_lifecycle_remove_callback_00560180(0x004906b0);
    if(byte(receiver,0x17e)){
        network_session_stop_connection_0048b310(pointer(load(receiver)),nullptr);
        setbyte(receiver,0x17e,0);
    }
    for(U offset:{0x164u,0x16cu}){
        void* list=session+offset;void* head=pointer(load(list));
        while(load(head)!=address(head)){
            head=pointer(load(list));
            void* member=pointer(load(pointer(load(head,4)),8));
            network_session_remove_member_00492770(receiver,nullptr,member);
            head=pointer(load(list));
        }
    }
    void* list=session+0x170;void* head=pointer(load(list));
    while(load(head)!=address(head)){
        head=pointer(load(list));const U value=load(pointer(load(head,4)),8);
        void* node=pointer(load(head));
        while(node!=head){
            const U item=load(node,8);void* next=pointer(load(node));
            if(item==value){U output;network_services_unlink_0048b660(list,nullptr,&output,address(node));}
            node=next;
        }
        if(value){network_services_detach_0048c430(pointer(value),nullptr);application_release_0059f050(pointer(value));}
        head=pointer(load(list));
    }
    application_release_0059f050(pointer(load(receiver,0x10)));
    application_release_0059f050(pointer(load(receiver,0xc)));
    application_release_0059f050(pointer(load(receiver,8)));
    void* connection=pointer(load(receiver));
    if(connection){
        network_session_connection_destroy_0048b250(connection,nullptr);
        application_release_0059f050(connection);
    }
    cell=network_session_lock_cell_00628c78;
    if(cell){heap_lock_destroy_005322d0(pointer(load(cell)));application_release_0059f050(cell);}
    network_session_lock_cell_00628c78=nullptr;
    clear_and_release_sentinel(session+0x178);
    clear_and_release_sentinel(session+0x174);
    clear_and_release_sentinel(session+0x170);
    release_list_blocks(session+0x16c);
    release_list_blocks(session+0x168);
    release_list_blocks(session+0x164);
}
} // namespace porsche
