#include "porsche/network_vtables.hpp"
#include "porsche/network_workers_members.hpp"
#include "porsche/network_services.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/formatter_bootstrap.hpp"
#include <cstring>
namespace porsche {
namespace {
using U=std::uint32_t;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void put(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
std::uint8_t byte(const void* p,U off){return static_cast<const std::uint8_t*>(p)[off];}
void pb(void* p,U off,std::uint8_t v){static_cast<std::uint8_t*>(p)[off]=v;}
struct Packet { U size; std::uint8_t bytes[240]; };
static_assert(sizeof(Packet)==244);
}
// Original COL and function words are HIGHLOW relocated, not raw VA identities.
const NetworkSendTable network_vtable_owner_005b4968{network_rtti_005c5190,network_send_queue_0048ad70};
const NetworkSendTable network_vtable_owner_005b4970{network_rtti_005c51d8,network_purecall_005a1056};
const NetworkSendTable network_vtable_owner_005b4978{network_rtti_005c5228,network_send_member_0048b340};
// 0048a920..0048a998. Captured pool, reload after refill/leave; forward MOVSD.
U* __fastcall network_packet_insert_0048a920(void*,void*,U* output,U before,const void* value){
 auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
 heap_enter_005322b0(ptr(get(pool)));
 if(!get(pool,0x88))application_context_new_head_0059eeb0(31,0);
 const U node=get(pool,0x88);put(pool,0x88,get(ptr(node),4));
 heap_leave_005322c0(ptr(get(pool)));
 const U payload=node+8u;
 if(payload)for(U i=0;i<61;++i)put(ptr(payload),i*4,get(value,i*4));
 put(ptr(node),0,before);put(ptr(node),4,get(ptr(before),4));
 put(ptr(get(ptr(before),4)),0,node);put(ptr(before),4,node);*output=node;return output;
}
// 0048a8d0..0048a917. Unlink before manager lookup; output can alias links.
U* __fastcall network_packet_unlink_0048a8d0(void*,void*,U* output,U node){
 const U previous=get(ptr(node),4),next=get(ptr(node));put(ptr(previous),0,next);put(ptr(next),4,previous);
 auto* pool=static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8())+0x28;
 heap_enter_005322b0(ptr(get(pool)));put(ptr(node),4,get(pool,0x88));put(pool,0x88,node);
 heap_leave_005322c0(ptr(get(pool)));*output=next;return output;
}
// 0048a3d0..0048a4d1. Uninitialized packet tail is copied as in the original;
// only size bytes constitute packet content. Original callers require size<=240.
U __fastcall network_member_packet_0048a3d0(void* member,void*,const std::uint8_t* packet,U size,void* transport){
 Packet p;p.size=size;heap_copy_dispatch_005323e0(p.bytes,packet,size);
 auto* list=static_cast<std::uint8_t*>(member)+0xc4;U end,copy,result;
 network_member_copy_0050e140(&copy,nullptr,network_member_end_00529050(list,nullptr,&end));
 network_packet_insert_0048a920(list,nullptr,&result,copy,&p);
 const U count=get(member,0xb4)+1u;const auto active=byte(member,0xbe);put(member,0xb4,count);
 if(!active)return count==1?0:count;
 if(transport){
  const U node=get(ptr(get(list)));const U bytes=get(ptr(node),8);
  if(network_transport_member_send_0055c270(transport,ptr(get(member)),static_cast<const std::uint8_t*>(ptr(node+12)),bytes)){
   U begin;const U selected=*network_services_begin_004c3150(list,nullptr,&begin);
   network_packet_unlink_0048a8d0(list,nullptr,&result,selected);put(member,0xb4,get(member,0xb4)-1u);
  }
 }
 const U remaining=get(member,0xb4);pb(member,0xbe,0);return remaining?remaining:1;
}
// 0048ad70..0048ae2b: destination intentionally unused.
void __fastcall network_send_queue_0048ad70(void* sender,void*,U,const std::uint8_t* packet,U size){
 Packet p;heap_enter_005322b0(ptr(get(sender,8)));p.size=size;heap_copy_dispatch_005323e0(p.bytes,packet,size);
 auto* list=static_cast<std::uint8_t*>(sender)+0xc;U end,copy,result;
 network_member_copy_0050e140(&copy,nullptr,network_member_end_00529050(list,nullptr,&end));
 network_packet_insert_0048a920(list,nullptr,&result,copy,&p);
 const U node=get(ptr(get(list)));const auto active=byte(sender,0x10);
 if(active){
  if(network_transport_send_0055d4a0(ptr(get(sender,4)),static_cast<const std::uint8_t*>(ptr(node+12)),get(ptr(node),8))){
   U begin;const U selected=*network_services_begin_004c3150(list,nullptr,&begin);
   network_packet_unlink_0048a8d0(list,nullptr,&result,selected);
  }pb(sender,0x10,0);
 }heap_leave_005322c0(ptr(get(sender,8)));
}
// 0048b340..0048b3b9: dereference destination before taking lock.
void __fastcall network_send_member_0048b340(void* sender,void*,U destination,const std::uint8_t* packet,U size){
 void* member=ptr(destination);if(!get(member))return;
 heap_enter_005322b0(ptr(get(sender,8)));
 void* transport=byte(sender,0x16)?ptr(get(sender,4)):nullptr;
 if(network_member_packet_0048a3d0(member,nullptr,packet,size,transport)==1){
  auto* list=static_cast<std::uint8_t*>(sender)+0x18;U end,copy,result;
  network_member_copy_0050e140(&copy,nullptr,network_member_end_00529050(list,nullptr,&end));
  network_member_insert_004937f0(list,nullptr,&result,copy,&destination);
 }heap_leave_005322c0(ptr(get(sender,8)));
}
// 005a1056..005a105e; fatal25 never returns. No fabricated RET12 path.
[[noreturn]] void __fastcall network_purecall_005a1056(void*,void*,U,const std::uint8_t*,U){formatter_fatal_005a2e22(25);}
U __cdecl network_transport_send_0055d4a0(void* t,const std::uint8_t* p,U n){
 if(!(byte(t,0x2c8)&1))return 0;return network_transport_packet_00560420(static_cast<std::uint8_t*>(t)+0x254,p,n);
}
void* __cdecl network_transport_owner_0055c260(void* p){return ptr(raw(p)-4u);}
U __cdecl network_transport_member_send_0055c270(void*,void* member,const std::uint8_t* p,U n){
 void* owner=network_transport_owner_0055c260(member);if(!(byte(owner,0xdc)&1))return 0;
 return network_transport_packet_00560420(static_cast<std::uint8_t*>(owner)+0x68,p,n);
}
U __cdecl network_transport_packet_00560420(void* t,const std::uint8_t* p,U n){
 const U descriptor[3]={n&0xff000000u,n&0x00ffffffu,raw(p)};return network_transport_dispatch_00586fb0(t,1,descriptor);
}
U __cdecl network_transport_dispatch_00586fb0(void* t,U count,const U* descriptor){
 if(!t||!get(t,0x28))return 0;const U route=get(t,0x34);
 return route?network_transport_routed_005870b0(t,count,descriptor,route):network_transport_direct_00587000(t,count,descriptor);
}
}
