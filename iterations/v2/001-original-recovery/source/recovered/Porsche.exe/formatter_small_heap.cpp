#include "porsche/formatter_small_heap.hpp"
#include <cstring>
namespace porsche {
std::uint32_t formatter_small_capacity_006c01c0=0;
std::uint32_t formatter_small_pending_group_006c01c4=0;
std::uint8_t* formatter_small_cursor_006c01c8=nullptr;
std::uint8_t* formatter_small_pending_006c01cc=nullptr;
namespace {
using U=std::uint32_t;
U address(const void* p) { return static_cast<U>(reinterpret_cast<std::uintptr_t>(p)); }
std::uint8_t* pointer(U p) { return reinterpret_cast<std::uint8_t*>(static_cast<std::uintptr_t>(p)); }
U read(U p) { U v; std::memcpy(&v,pointer(p),4); return v; }
void write(U p,U v) { std::memcpy(pointer(p),&v,4); }
U bit(U n) { return 0x80000000u>>(n&31u); }
int bin(U n) { const int i=static_cast<std::int32_t>(n)/16-1; return i>63?63:i; }
U group_base(U meta,U group) { return meta+0x144+group*0x204; }
void remove(U header,U meta,U group,U index,U node) {
 if(read(node+4)==read(node+8)) {
  const U mask=~bit(index);
  const U map=meta+(index<32?0x44:0xc4)+group*4;
  write(map,read(map)&mask);
  auto* count=pointer(meta+4+index); *count=static_cast<std::uint8_t>(*count-1);
  if(!*count) { const U map_header=header+(index<32?0:4); write(map_header,read(map_header)&mask); }
 }
 write(read(node+8)+4,read(node+4));
 write(read(node+4)+8,read(node+8));
}
void insert(U header,U meta,U group,U index,U node) {
 const U sentinel=group_base(meta,group)+index*8;
 write(node+4,read(sentinel+4)); write(node+8,sentinel);
 write(sentinel+4,node); write(read(node+4)+8,node);
 if(read(node+4)==read(node+8)) {
  auto* count=pointer(meta+4+index); const auto old=*count; *count=static_cast<std::uint8_t>(old+1);
  if(!old) { const U map=header+(index<32?0:4); write(map,read(map)|bit(index)); }
  const U map=meta+(index<32?0x44:0xc4)+group*4; write(map,read(map)|bit(index));
 }
}
void block(U p,U size) { write(p,size); write(p+size-4,size); }
}
int __cdecl formatter_small_initialize_005aa96c() {
 auto* allocation=static_cast<std::uint8_t*>(formatter_crt_heap_allocate(formatter_crt_heap_006c01d8,0,0x140));
 formatter_crt_headers_006c01d4=allocation;
 if(!allocation) return 0;
 formatter_small_pending_006c01cc=nullptr; formatter_crt_header_count_006c01d0=0;
 formatter_small_cursor_006c01c8=allocation; formatter_small_capacity_006c01c0=16;
 return 1;
}
int __cdecl formatter_small_heap_initialize_005a96fa(U mode) {
 formatter_crt_heap_006c01d8=formatter_small_heap_create(mode==0?1u:0u,0x1000,0);
 if(!formatter_crt_heap_006c01d8) return 0;
 if(formatter_small_initialize_005aa96c()) return 1;
 formatter_small_heap_destroy(formatter_crt_heap_006c01d8); return 0;
}
std::uint8_t* __cdecl formatter_small_new_header_005ab009() {
 if(formatter_crt_header_count_006c01d0==formatter_small_capacity_006c01c0) {
  auto* allocation=static_cast<std::uint8_t*>(formatter_small_heap_reallocate(formatter_crt_heap_006c01d8,0,
   formatter_crt_headers_006c01d4,(formatter_small_capacity_006c01c0+16)*20));
  if(!allocation) return nullptr;
  formatter_small_capacity_006c01c0+=16; formatter_crt_headers_006c01d4=allocation;
 }
 const U header=address(formatter_crt_headers_006c01d4)+formatter_crt_header_count_006c01d0*20;
 void* meta=formatter_crt_heap_allocate(formatter_crt_heap_006c01d8,8,0x41c4);
 write(header+16,address(meta)); if(!meta) return nullptr;
 void* region=formatter_small_virtual_allocate(nullptr,0x100000,0x2000,4);
 write(header+12,address(region));
 if(!region) { formatter_crt_heap_free(formatter_crt_heap_006c01d8,0,pointer(read(header+16))); return nullptr; }
 write(header+8,0xffffffffu); write(header,0); write(header+4,0);
 ++formatter_crt_header_count_006c01d0; write(read(header+16),0xffffffffu);
 return pointer(header);
}
std::int32_t __cdecl formatter_small_commit_005ab0ba(std::uint8_t* header_pointer) {
 const U header=address(header_pointer),meta=read(header+16);
 U group=0,available=read(header+8);
 while(!(available&0x80000000u)) { available<<=1; ++group; }
 const U gb=group_base(meta,group);
 for(U i=0;i<63;++i) { const U node=gb+i*8; write(node+8,node); write(node+4,node); }
 const U region=read(header+12)+(group<<15);
 if(!formatter_small_virtual_allocate(pointer(region),0x8000,0x1000,4)) return -1;
 const U last=region+0x7000;
 for(U page=region;page<=last;page+=0x1000) {
  write(page+8,0xffffffffu); write(page+0xffc,0xffffffffu);
  write(page+12,0xff0); write(page+16,page+0x100c); write(page+20,page-0xff4); write(page+0xff8,0xff0);
 }
 const U sentinel=gb+0x1f8;
 write(sentinel+4,region+12); write(region+20,sentinel);
 write(sentinel+8,last+12); write(last+16,sentinel);
 write(meta+group*4+0x44,0); write(meta+group*4+0xc4,1);
 const auto old=*pointer(meta+0x43); *pointer(meta+0x43)=static_cast<std::uint8_t>(old+1);
 if(!old) write(header+4,read(header+4)|1u);
 write(header+8,read(header+8)&~bit(group));
 return static_cast<std::int32_t>(group);
}
void* __cdecl formatter_crt_small_allocate_005aad00(U bytes) {
 const U base=address(formatter_crt_headers_006c01d4),end=base+formatter_crt_header_count_006c01d0*20;
 const U total=(bytes+23)&0xfffffff0u;
 const int index=static_cast<std::int32_t>(total)/16-1;
 const U low=index<32 ? 0xffffffffu>>(static_cast<U>(index)&31) : 0;
 const U high=index<32 ? 0xffffffffu : 0xffffffffu>>((static_cast<U>(index)-32)&31);
 const U cursor=address(formatter_small_cursor_006c01c8);
 U header=cursor;
 auto fits=[&](U p) { return ((read(p)&low)|(read(p+4)&high))!=0; };
 while(header<end&&!fits(header)) header+=20;
 if(header==end) {
  header=base; while(header<cursor&&!fits(header)) header+=20;
  if(header==cursor) {
   while(header<end&&!read(header+8)) header+=20;
   if(header==end) {
    header=base; while(header<cursor&&!read(header+8)) header+=20;
    if(header==cursor) { header=address(formatter_small_new_header_005ab009()); if(!header) return nullptr; }
   }
   const U group=static_cast<U>(formatter_small_commit_005ab0ba(pointer(header)));
   write(read(header+16),group); if(read(read(header+16))==0xffffffffu) return nullptr;
  }
 }
 formatter_small_cursor_006c01c8=pointer(header);
 const U meta=read(header+16);
 U group=read(meta);
 auto group_fits=[&](U g) { return ((read(meta+0x44+g*4)&low)|(read(meta+0xc4+g*4)&high))!=0; };
 if(group==0xffffffffu||!group_fits(group)) { group=0; while(!group_fits(group)) ++group; }
 U bits=read(meta+group*4+0x44)&low,selected=0;
 if(!bits) { bits=read(meta+group*4+0xc4)&high; selected=32; }
 while(!(bits&0x80000000u)) { bits<<=1; ++selected; }
 const U gb=group_base(meta,group),free=read(gb+selected*8+4),remaining=read(free)-total;
 const int next_bin=bin(remaining);
 if(static_cast<U>(next_bin)!=selected) {
  remove(header,meta,group,selected,free);
  if(remaining) insert(header,meta,group,static_cast<U>(next_bin),free);
 }
 if(remaining) block(free,remaining);
 const U allocated=free+remaining;
 write(allocated,total+1); write(allocated+total-4,total+1);
 const U old=read(gb); write(gb,old+1);
 if(!old&&formatter_small_pending_006c01cc==pointer(header)&&formatter_small_pending_group_006c01c4==group)
  formatter_small_pending_006c01cc=nullptr;
 write(meta,group); return pointer(allocated+4);
}
void __cdecl formatter_crt_small_free_005aa9d5(std::uint8_t* hp,void* allocation) {
 U header=address(hp),p=address(allocation),meta=read(header+16),group=(p-read(header+12))>>15;
 U size=read(p-4)-1,previous=read(p-8),node=p-4;
 const U gb=group_base(meta,group),next=read(node+size);
 if(!(next&1)) { remove(header,meta,group,static_cast<U>(bin(next)),node+size); size+=next; }
 U index=static_cast<U>(bin(size)); bool insert_needed=true;
 if(!(previous&1)) {
  node-=previous;
  const U previous_bin=static_cast<U>(bin(previous)); size+=previous; index=static_cast<U>(bin(size));
  if(previous_bin!=index) remove(header,meta,group,previous_bin,node);
  else insert_needed=false;
 }
 if(insert_needed) insert(header,meta,group,index,node);
 block(node,size); write(gb,read(gb)-1); if(read(gb)) return;
 if(formatter_small_pending_006c01cc) {
  U pending=address(formatter_small_pending_006c01cc);
  formatter_small_virtual_free(pointer(read(pending+12)+(formatter_small_pending_group_006c01c4<<15)),0x8000,0x4000);
  pending=address(formatter_small_pending_006c01cc);
  write(pending+8,read(pending+8)|bit(formatter_small_pending_group_006c01c4));
  pending=address(formatter_small_pending_006c01cc);
  write(read(pending+16)+formatter_small_pending_group_006c01c4*4+0xc4,0);
  pending=address(formatter_small_pending_006c01cc); --*pointer(read(pending+16)+0x43);
  pending=address(formatter_small_pending_006c01cc);
  if(!*pointer(read(pending+16)+0x43)) { write(pending+4,read(pending+4)&0xfffffffeu); pending=address(formatter_small_pending_006c01cc); }
  if(read(pending+8)==0xffffffffu) {
   formatter_small_virtual_free(pointer(read(pending+12)),0,0x8000);
   pending=address(formatter_small_pending_006c01cc);
   formatter_crt_heap_free(formatter_crt_heap_006c01d8,0,pointer(read(pending+16)));
   pending=address(formatter_small_pending_006c01cc);
   const U length=formatter_crt_header_count_006c01d0*20-pending+address(formatter_crt_headers_006c01d4)-20;
   context_move_005a1a40(pointer(pending),pointer(pending+20),length);
   --formatter_crt_header_count_006c01d0;
   if(header>address(formatter_small_pending_006c01cc)) header-=20;
   formatter_small_cursor_006c01c8=formatter_crt_headers_006c01d4;
  }
 }
 formatter_small_pending_006c01cc=pointer(header); formatter_small_pending_group_006c01c4=group;
}
int __cdecl formatter_small_resize_005ab1b5(std::uint8_t* hp,void* allocation,U bytes) {
 const U header=address(hp),p=address(allocation),meta=read(header+16),group=(p-read(header+12))>>15;
 const U total=(bytes+23)&0xfffffff0u,old=read(p-4)-1,next_node=p+old-4,next=read(next_node);
 if(static_cast<std::int32_t>(total)>static_cast<std::int32_t>(old)) {
  if((next&1)||static_cast<std::int32_t>(total)>static_cast<std::int32_t>(next+old)) return 0;
  remove(header,meta,group,static_cast<U>(bin(next)),next_node);
  const U remainder=next+old-total;
  if(static_cast<std::int32_t>(remainder)>0) {
   const U node=p+total-4; insert(header,meta,group,static_cast<U>(bin(remainder)),node); block(node,remainder);
  }
  write(p-4,total+1); write(p+total-8,total+1);
 } else if(static_cast<std::int32_t>(total)<static_cast<std::int32_t>(old)) {
  U remainder=old-total,node=p+total-4;
  write(p-4,total+1); write(node-4,total+1);
  if(!(next&1)) { remove(header,meta,group,static_cast<U>(bin(next)),next_node); remainder+=next; }
  insert(header,meta,group,static_cast<U>(bin(remainder)),node); block(node,remainder);
 }
 return 1;
}
void* __cdecl formatter_small_copy_005a7ad0(void* out,const void* in,U bytes) {
 // Complete original spans are identical after46 PE HIGHLOW address rebases.
 return context_move_005a1a40(out,in,bytes);
}
std::uint32_t __cdecl exit_registry_allocation_size_005a8161(const void* p) {
 exit_registry_lock_api_005a4ba4(9);
 if(formatter_crt_find_header_005aa9aa(p)) {
  const U size=read(address(p)-4)-9; exit_registry_unlock_api_005a4c05(9); return size;
 }
 exit_registry_unlock_api_005a4c05(9); return formatter_small_heap_size(formatter_crt_heap_006c01d8,0,p);
}
void* __cdecl exit_registry_reallocate_005a8029(void* p,U bytes) {
 if(!p) return exit_registry_malloc_005a3be5(bytes);
 if(!bytes) { formatter_crt_free_005a3b9d(p); return nullptr; }
 for(;;) {
  void* result=nullptr;
  if(bytes<=0xffffffe0u) {
   exit_registry_lock_api_005a4ba4(9);
   auto* header=formatter_crt_find_header_005aa9aa(p);
   if(header) {
    if(bytes<=formatter_crt_small_limit_005e606c) {
     if(formatter_small_resize_005ab1b5(header,p,bytes)) result=p;
     else if((result=formatter_crt_small_allocate_005aad00(bytes))) {
      const U old=read(address(p)-4)-1; formatter_small_copy_005a7ad0(result,p,old<bytes?old:bytes);
      formatter_crt_small_free_005aa9d5(header,p);
     }
    }
    if(!result) {
     if(!bytes) bytes=1; bytes=(bytes+15)&0xfffffff0u;
     result=formatter_crt_heap_allocate(formatter_crt_heap_006c01d8,0,bytes);
     if(result) { const U old=read(address(p)-4)-1; formatter_small_copy_005a7ad0(result,p,old<bytes?old:bytes); formatter_crt_small_free_005aa9d5(header,p); }
    }
    exit_registry_unlock_api_005a4c05(9);
   } else {
    exit_registry_unlock_api_005a4c05(9);
    if(!bytes) bytes=1; bytes=(bytes+15)&0xfffffff0u;
    result=formatter_small_heap_reallocate(formatter_crt_heap_006c01d8,0,p,bytes);
   }
  }
  if(result) return result;
  if(!formatter_crt_new_mode_006afec8||!formatter_crt_call_new_005ab4ab(bytes)) return nullptr;
 }
}
}
