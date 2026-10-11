#include "porsche/network_groups.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/heap.hpp"
#include <cstring>
namespace porsche {
namespace {
using U=std::uint32_t;
U get(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void put(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U va(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
std::uint8_t& byte(void* p,U off){return static_cast<std::uint8_t*>(p)[off];}
U index(void* p){return static_cast<U>(static_cast<std::int32_t>(static_cast<std::int8_t>(byte(p,0xac))));}
std::uint8_t bit(U count){return static_cast<std::uint8_t>(1u<<(count&31u));}
using Send=void (__fastcall*)(void*,void*,U,const std::uint8_t*,U);
void send(void* receiver,U destination,const std::uint8_t* packet,U size){
    void* sender=ptr(get(receiver));
    reinterpret_cast<Send>(static_cast<std::uintptr_t>(get(ptr(get(sender)))))(sender,nullptr,destination,packet,size);
}
}
// 0048a390..0048a3cc: next and sentinel are reloaded after each virtual call.
void __fastcall network_group_send_member_messages_0048a390(void* member,void*,void* receiver,U destination){
    void* head=ptr(get(member,0xc8));void* node=ptr(get(head));
    while(node!=head){
        send(receiver,destination,static_cast<std::uint8_t*>(node)+12,get(node,8));
        node=ptr(get(node));head=ptr(get(member,0xc8));
    }
}
// 0048baa0..0048bb25: three-byte identity, zero reserved bytes, 52-byte name,
// then the original little-endian count. Count is captured before fill/copy.
void __fastcall network_group_send_state_0048baa0(void* group,void*,U destination){
    std::uint8_t packet[80];packet[0]=0xb4;
    const U identity=get(group,0x70),count=get(group,0xac);
    packet[1]=static_cast<std::uint8_t>(identity>>16);packet[2]=static_cast<std::uint8_t>(identity>>8);packet[3]=static_cast<std::uint8_t>(identity);
    heap_fill_0053c290(packet+4,0,76);
    heap_copy_dispatch_005323e0(packet+24,static_cast<std::uint8_t*>(group)+0x74,52);
    packet[76]=static_cast<std::uint8_t>(count);packet[77]=static_cast<std::uint8_t>(count>>8);
    packet[78]=static_cast<std::uint8_t>(count>>16);packet[79]=static_cast<std::uint8_t>(count>>24);
    send(static_cast<std::uint8_t*>(group)+0x64,destination,packet,80);
}
// 00490b70..00490ba1: next is cached before the state send.
void __fastcall network_group_publish_00490b70(void* session,void*,void* group){
    void* head=ptr(get(session,0x164));void* node=ptr(get(head));
    while(node!=head){void* old=node;node=ptr(get(node));network_group_send_state_0048baa0(group,nullptr,get(old,8));head=ptr(get(session,0x164));}
}
// 0048c300..0048c354: recycle pool +88 nodes, retain and reset sentinel.
void __fastcall network_group_clear_member_messages_0048c300(void* list,void*){
    void* head=ptr(get(list));void* node=ptr(get(head));
    while(node!=head){
        void* old=node;node=ptr(get(node));
        void* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
        heap_enter_005322b0(ptr(get(pool)));put(old,4,get(pool,0x88));put(pool,0x88,va(old));heap_leave_005322c0(ptr(get(pool)));
        head=ptr(get(list));
    }
    head=ptr(get(list));put(head,0,va(head));head=ptr(get(list));put(head,4,va(head));
}
// 0048c220..0048c2a6: third stack argument is ignored but RET12 is preserved.
void __fastcall network_group_acknowledge_0048c220(void* group,void*,void* member,U value,U){
    const U slot=index(member);auto* receiver=static_cast<std::uint8_t*>(group)+0x64;
    application_network_message_0048c870(receiver,nullptr,0xb7,slot,value,0,0);
    if(value!=0xfffffffeu)return;
    byte(group,0xcc2)|=bit(slot);
    if((byte(group,0xcc0)&byte(group,0xcc2))==byte(group,0xcc0))byte(group,0xcc3)=0;
    void* head=ptr(get(group,0xa8));void* node=ptr(get(head));
    while(node!=head){
        network_group_send_member_messages_0048a390(ptr(get(node,8)),nullptr,receiver,va(member));
        node=ptr(get(node));head=ptr(get(group,0xa8));
    }
}
// 0048bda0..0048bed6: old member index survives acknowledgement callbacks.
void __fastcall network_member_group_remove_0048bda0(void* group,void*,void* member){
    const std::uint8_t old=byte(member,0xac);
    if(byte(group,0xcc3)!=0&&(byte(group,0xcc2)&bit(old))==0)
        network_group_acknowledge_0048c220(group,nullptr,member,0xfffffffeu,0xffffffffu);
    const U slot=static_cast<U>(static_cast<std::int32_t>(static_cast<std::int8_t>(old)));
    byte(group,0xcc0)&=static_cast<std::uint8_t>(~bit(slot));
    auto* receiver=static_cast<std::uint8_t*>(group)+0x64;
    application_network_message_0048c870(receiver,nullptr,0xb1,slot,0x80000000u,0,0);
    void* list=static_cast<std::uint8_t*>(group)+0xa8;
    void* head=ptr(get(list));void* node=ptr(get(head));
    while(node!=head){
        void* next=ptr(get(node));
        if(get(node,8)==va(member)){U output;network_services_unlink_0048b660(list,nullptr,&output,va(node));}
        node=next;
    }
    put(member,0xa4,0);network_group_clear_member_messages_0048c300(static_cast<std::uint8_t*>(member)+0xc8,nullptr);
    if(get(member)!=0){
        head=ptr(get(list));node=ptr(get(head));
        while(node!=head){
            application_network_message_0048c870(receiver,nullptr,0xb1,get(ptr(get(node,8)),0xac),0x80000000u,0,va(member));
            node=ptr(get(node));head=ptr(get(list));
        }
        application_network_message_0048c870(receiver,nullptr,0xb2,0xfffffffeu,0x80000000u,va(network_group_text_005e8e50),va(member));
    }
    put(group,0xac,get(group,0xac)-1u);network_group_publish_00490b70(ptr(get(group,0x60)),nullptr,group);
}
} // namespace porsche
