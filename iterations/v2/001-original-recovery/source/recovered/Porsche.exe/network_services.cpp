#include "porsche/network_services.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/startup_services.hpp"
#include <cstdint>
#include <cstring>

namespace porsche {
namespace {
using U = std::uint32_t;
U load(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void store(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
std::uint8_t byte(const void* p,U off){return static_cast<const std::uint8_t*>(p)[off];}
void setbyte(void* p,U off,std::uint8_t v){static_cast<std::uint8_t*>(p)[off]=v;}
void* pointer(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U address(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
using Send = void (__fastcall*)(void* sender,void* unused_edx,U destination,
    const std::uint8_t* packet,U bytes);
void send(void* receiver,U destination,const std::uint8_t* packet,U bytes){
    void* sender=pointer(load(receiver));
    void* vtable=pointer(load(sender));
    reinterpret_cast<Send>(static_cast<std::uintptr_t>(load(vtable)))(
        sender,nullptr,destination,packet,bytes);
}
}

// 0048c870..0048c97b. Only initialized prefix bytes are observable through
// the send callback. Source uses 0x80000000 as omission token and appends a
// NUL only when the third (string) argument is nonzero.
void __fastcall application_network_message_0048c870(void* receiver,void*,
    U message,U first,U second,U third,U fourth){
    std::uint8_t packet[0xc8];
    U bytes=1;packet[0]=static_cast<std::uint8_t>(message);
    if(first!=0x80000000u){
        packet[bytes++]=static_cast<std::uint8_t>(first>>16u);
        packet[bytes++]=static_cast<std::uint8_t>(first>>8u);
        packet[bytes++]=static_cast<std::uint8_t>(first);
    }
    if(second!=0x80000000u){
        packet[bytes++]=static_cast<std::uint8_t>(second>>24u);
        packet[bytes++]=static_cast<std::uint8_t>(second>>16u);
        packet[bytes++]=static_cast<std::uint8_t>(second>>8u);
        packet[bytes++]=static_cast<std::uint8_t>(second);
    }
    if(third){
        auto* text=static_cast<const std::uint8_t*>(pointer(third));
        while(bytes<0xc7u&&*text){packet[bytes++]=*text++;}
        packet[bytes++]=0;
    }
    if(fourth==0&&load(receiver,4)!=0){
        void* head=pointer(load(pointer(load(receiver,4))));
        void* node=pointer(load(head));
        if(node==head)return;
        do{
            send(receiver,load(node,8),packet,bytes);
            void* wrapper=pointer(load(receiver,4));
            node=pointer(load(node));
            head=pointer(load(wrapper));
        }while(node!=head);
        return;
    }
    send(receiver,fourth,packet,bytes);
}

// 0048da60..0048dac2. The lock cell is captured, while global network,
// receiver and the handle used for leave are reloaded after effects.
void __cdecl network_services_action_0048da60(U first,U second){
    void* network=startup_network_00628c70;
    if(!network||load(network,8)==0||byte(network,0xbf)!=0)return;
    void* cell=pointer(load(network,0x10));
    heap_enter_005322b0(pointer(load(cell)));
    application_network_message_0048c870(pointer(load(startup_network_00628c70,0xc)),
        nullptr,0xb7,first,second,0,0);
    setbyte(startup_network_00628c70,0xbd,1);
    heap_leave_005322c0(pointer(load(cell)));
}
void __cdecl application_main_network_action(std::int32_t first,std::int32_t second){
    network_services_action_0048da60(static_cast<U>(first),static_cast<U>(second));
}

// 0048b660..0048b6a1. Unlink precedes the manager lookup and locking. Output
// can alias node/list storage, so the final store occurs after recycling.
U* __fastcall network_services_unlink_0048b660(void*,void*,U* output,U node_va){
    void* node=pointer(node_va);
    void* previous=pointer(load(node,4));
    const U next=load(node);
    store(previous,0,next);store(pointer(next),4,address(previous));
    auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
    heap_enter_005322b0(pointer(load(pool)));
    store(node,4,load(pool,0x10));store(pool,0x10,node_va);
    heap_leave_005322c0(pointer(load(pool)));
    *output=next;
    return output;
}

// 00493180..004931bb. Cache the sentinel and next node, but reread the
// pointed-to match value each iteration, including after callbacks.
void __fastcall network_services_remove_matching_00493180(void* list,void*,const U* value){
    void* head=pointer(load(list));
    void* node=pointer(load(head));
    while(node!=head){
        const U item=load(node,8);
        const U match=*value;
        void* next=pointer(load(node));
        if(item==match){U output;network_services_unlink_0048b660(list,nullptr,&output,address(node));}
        node=next;
    }
}

// 0048e790..0048e9b8. Groups are selected using the last node's value;
// every matching node is removed before that group's object is released.
void __fastcall network_lifecycle_clear_lists_0048e790(void* receiver,void*){
    auto* object=static_cast<std::uint8_t*>(receiver);
    for(U group=0;group<4;++group){
        void* list=object+0x254u+group*4u;
        void* head=pointer(load(list));
        while(load(head)!=address(head)){
            head=pointer(load(list));
            const U value=load(pointer(load(head,4)),8);
            void* node;
            if(group==3){
                U output;
                node=pointer(*network_services_begin_004c3150(list,nullptr,&output));
                head=pointer(load(list));
            }else node=pointer(load(head));
            while(node!=head){
                const U item=load(node,8);
                void* next=pointer(load(node));
                if(item==value){U output;network_services_unlink_0048b660(list,nullptr,&output,address(node));}
                node=next;
            }
            if(group==0)application_release_0059f050(pointer(value));
            else if(value){
                if(group==3)network_services_destroy_004904d0(pointer(value),nullptr);
                else network_services_detach_0048c430(pointer(value),nullptr);
                application_release_0059f050(pointer(value));
            }
            head=pointer(load(list));
        }
    }
    void* list=object+0x264u;
    void* head=pointer(load(list));
    while(load(head)!=address(head)){
        head=pointer(load(list));
        U value=load(pointer(load(head,4)),8);
        network_services_remove_matching_00493180(list,nullptr,&value);
        if(value){
            free_00531f90(pointer(load(pointer(value),4)));
            application_release_0059f050(pointer(value));
        }
        head=pointer(load(list));
    }
    store(receiver,0xb8,0);store(receiver,0xdc,0xfffffffeu);
    setbyte(receiver,0xbe,0);setbyte(receiver,0xbc,1);setbyte(receiver,0xc4,0);
    setbyte(receiver,0xe4,0);setbyte(receiver,0xe5,0);
    const std::uint16_t zero=0;std::memcpy(object+0xe6,&zero,2);
    setbyte(receiver,0xc3,0);store(receiver,0x28,1);
}
} // namespace porsche
