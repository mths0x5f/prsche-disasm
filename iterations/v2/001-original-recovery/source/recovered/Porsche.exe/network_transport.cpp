#include "porsche/network_transport.hpp"
#include "porsche/network_workers_members.hpp"
#include "porsche/heap.hpp"
#include <cstring>
#include <malloc.h>
namespace porsche {
namespace {
using U=std::uint32_t;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U get(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void put(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
}
// 00587000..005870af. Count<=1 still reads the first descriptor. Signed count
// tests, wrapping sums/flags and descriptor reloads between copy effects match
// x86. Native _alloca implements the original5a1e90 stack allocation/probe seam.
U __cdecl network_transport_direct_00587000(void* context,U count,const U* descriptors){
 U flags=0,size=0;const void* data;
 if(static_cast<std::int32_t>(count)>1){
  for(U i=0;i<count;++i){size+=descriptors[i*3+1];flags|=descriptors[i*3];}
  auto* storage=static_cast<std::uint8_t*>(_alloca((size+3u)&~3u));data=storage;
  for(U i=0;i<count;++i){const U bytes=descriptors[i*3+1];heap_copy_dispatch_005323e0(storage,ptr(descriptors[i*3+2]),bytes);storage+=bytes;}
 }else{size=descriptors[1];flags=descriptors[0];data=ptr(descriptors[2]);}
 void* table=ptr(get(context,8));auto send=reinterpret_cast<NetworkBufferSend>(static_cast<std::uintptr_t>(get(table,8)));
 return send(context,data,flags|size);
}
// 005870b0..00587108. Spare descriptor slots are deliberately uninitialized.
U __cdecl network_transport_routed_005870b0(void* context,U count,const U* descriptors,U route){
 void* routes=ptr(route);const U route_count=network_worker_queue_count_005809f0(static_cast<const IoList*>(routes));
 auto* copy=static_cast<U*>(_alloca(((route_count+count)*12u+3u)&~3u));
 heap_copy_dispatch_005323e0(copy,descriptors,count*12u);
 return network_transport_stage_00587110(context,route_count-1u,count,copy,routes);
}
// 00587110..0058716d: stage-1 terminates traversal; selected callback receives
// the original context, node+0c provider value, count, mutable descriptors,list.
U __cdecl network_transport_stage_00587110(void* context,U stage,U count,U* descriptors,void* routes){
 if(stage==0xffffffffu)return network_transport_direct_00587000(context,count,descriptors);
 put(routes,0x1c,stage);void* node=network_route_at_00580b20(routes,stage);if(!node)return 0;
 auto callback=reinterpret_cast<NetworkRouteSend>(static_cast<std::uintptr_t>(get(node,4)));
 return callback(context,get(node,0xc),count,descriptors,routes);
}
// 00586ee0..00586f45: sibling control dispatch has a distinct base callback
// context+24 and node+8 callback; termination compares stage with list count.
U __cdecl network_transport_control_00586ee0(void* context,U stage,U count,U* descriptors,void* routes){
 if(stage==network_worker_queue_count_005809f0(static_cast<const IoList*>(routes))){
  auto callback=reinterpret_cast<NetworkBufferSend>(static_cast<std::uintptr_t>(get(context,0x24)));
  return callback(context,ptr(descriptors[2]),descriptors[1]);
 }
 put(routes,0x1c,stage);void* node=network_route_at_00580b20(routes,stage);if(!node)return 0;
 auto callback=reinterpret_cast<NetworkRouteSend>(static_cast<std::uintptr_t>(get(node,8)));
 return callback(context,get(node,0xc),count,descriptors,routes);
}
// 00580b20..00580b6b: preserve captured lock, reload head after enter, unsigned
// stage>0.580b70 advances one node even for requested count0.
void* __cdecl network_route_at_00580b20(void* routes,U stage){
 void* lock=ptr(get(routes,0x18));heap_enter_005322b0(lock);void* node=ptr(get(routes,8));
 if(node&&stage)node=network_route_next_00580b70(node,stage-1u);
 heap_leave_005322c0(lock);return node;
}
void* __cdecl network_route_next_00580b70(void* node,U count){
 node=ptr(get(node));while(node){const U previous=count;--count;if(!previous)break;node=ptr(get(node));}return node;
}
// 00580a00..00580a44: null sought pointer is explicitly invalid.
U __cdecl network_route_index_00580a00(void* routes,void* sought){
 const void* lock=ptr(get(routes,0x18));heap_enter_005322b0(const_cast<void*>(lock));U index=0;
 if(sought){void* node=ptr(get(routes,8));while(node&&node!=sought){node=ptr(get(node));++index;}if(node!=sought)index=0xffffffffu;}
 else index=0xffffffffu;heap_leave_005322c0(const_cast<void*>(lock));return index;
}
// 00580a50..00580a88: callback+10 and opaque+14 read after head reload.
U __cdecl network_route_first_value_00580a50(void* routes){
 void* lock=ptr(get(routes,0x18));heap_enter_005322b0(lock);void* node=ptr(get(routes,8));U result=0xffffffffu;
 if(node){auto predicate=reinterpret_cast<NetworkListPredicate>(static_cast<std::uintptr_t>(get(routes,0x10)));result=predicate(node,get(routes,0x14));}
 heap_leave_005322c0(lock);return result;
}
//00580ad0 retains its canonical io_find owner in io_lists.cpp.
}
