#include "porsche/formatter_crt_runtime.hpp"
#include <cstring>
#include <initializer_list>

namespace porsche {
alignas(4) std::uint8_t formatter_crt_lock1_006afd00[24]{};
alignas(4) std::uint8_t formatter_crt_lock17_006afd18[24]{};
alignas(4) std::uint8_t formatter_crt_lock9_006afd30[24]{};
alignas(4) std::uint8_t formatter_crt_lock13_006afd48[24]{};
void* formatter_crt_locks_005e57a8[48] = {nullptr,formatter_crt_lock1_006afd00,
 nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,formatter_crt_lock9_006afd30,
 nullptr,nullptr,nullptr,formatter_crt_lock13_006afd48,nullptr,nullptr,nullptr,
 formatter_crt_lock17_006afd18,nullptr};
std::uint32_t formatter_crt_small_limit_005e606c = 0x3f8;
std::uint32_t formatter_crt_new_mode_006afec8 = 0;
int (__cdecl* formatter_crt_new_handler_006afecc)(std::uint32_t) = nullptr;
std::uint32_t formatter_crt_heap_006c01d8 = 0;
std::uint32_t formatter_crt_header_count_006c01d0 = 0;
std::uint8_t* formatter_crt_headers_006c01d4 = nullptr;
std::uint32_t formatter_crt_tls_index_005e58b4 = 0xffffffffu;
namespace {
std::uint32_t read32(const void* p) { std::uint32_t v; std::memcpy(&v,p,4); return v; }
void write32(void* p,std::uint32_t v) { std::memcpy(p,&v,4); }
std::uint32_t address(const void* p) { return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(p)); }
void fill_store(std::uint8_t* p,std::uint32_t width,std::uint32_t value) {
#if defined(PORSCHE_CRT_MEMORY_TRACE)
 formatter_crt_memset_store(p,width,value);
#endif
 if(width==4) write32(p,value); else *p=static_cast<std::uint8_t>(value);
}
}
void* __cdecl exit_registry_malloc_005a3be5(std::uint32_t n) {
 return formatter_crt_nh_malloc_005a3bf7(n,formatter_crt_new_mode_006afec8);
}
void* __cdecl formatter_crt_nh_malloc_005a3bf7(std::uint32_t n,std::uint32_t mode) {
 if(n>0xffffffe0u) return nullptr;
 for(;;) {
  if(auto* p=formatter_crt_allocate_005a3c23(n)) return p;
  if(!mode || !formatter_crt_call_new_005ab4ab(n)) return nullptr;
 }
}
void* __cdecl formatter_crt_allocate_005a3c23(std::uint32_t n) {
 if(n<=formatter_crt_small_limit_005e606c) {
  exit_registry_lock_api_005a4ba4(9);
  void* p=formatter_crt_small_allocate_005aad00(n);
  exit_registry_unlock_api_005a4c05(9);
  if(p) return p;
 }
 if(!n) n=1;
 n=(n+15u)&0xfffffff0u;
 return formatter_crt_heap_allocate(formatter_crt_heap_006c01d8,0,n);
}
int __cdecl formatter_crt_call_new_005ab4ab(std::uint32_t n) {
 auto handler=formatter_crt_new_handler_006afecc;
 return handler && handler(n) ? 1 : 0;
}
void __cdecl formatter_crt_free_005a3b9d(void* p) {
 if(!p) return;
 exit_registry_lock_api_005a4ba4(9);
 auto* header=formatter_crt_find_header_005aa9aa(p);
 if(header) {
  formatter_crt_small_free_005aa9d5(header,p);
  exit_registry_unlock_api_005a4c05(9);
 } else {
  exit_registry_unlock_api_005a4c05(9);
  formatter_crt_heap_free(formatter_crt_heap_006c01d8,0,p);
 }
}
std::uint8_t* __cdecl formatter_crt_find_header_005aa9aa(const void* p) {
 auto cursor=address(formatter_crt_headers_006c01d4);
 const auto end=cursor+formatter_crt_header_count_006c01d0*20u;
 while(cursor<end) {
  auto* header=reinterpret_cast<std::uint8_t*>(static_cast<std::uintptr_t>(cursor));
  if(address(p)-read32(header+12)<0x100000u) return header;
  cursor+=20;
 }
 return nullptr;
}
void __cdecl formatter_crt_initialize_locks_005a4b7b() {
 formatter_lowio_critical_initialize(formatter_crt_locks_005e57a8[17]);
 formatter_lowio_critical_initialize(formatter_crt_locks_005e57a8[13]);
 formatter_lowio_critical_initialize(formatter_crt_locks_005e57a8[9]);
 formatter_lowio_critical_initialize(formatter_crt_locks_005e57a8[1]);
}
void __cdecl exit_registry_lock_api_005a4ba4(std::uint32_t id) {
 auto** cell=&formatter_crt_locks_005e57a8[id];
 if(!*cell) {
  void* allocation=exit_registry_malloc_005a3be5(24);
  if(!allocation) formatter_fatal_005a2e22(17);
  exit_registry_lock_api_005a4ba4(17);
  if(!*cell) { formatter_lowio_critical_initialize(allocation); *cell=allocation; }
  else formatter_crt_free_005a3b9d(allocation);
  exit_registry_unlock_api_005a4c05(17);
 }
 formatter_lowio_critical_enter(*cell);
}
void __cdecl exit_registry_unlock_api_005a4c05(std::uint32_t id) {
 formatter_lowio_critical_leave(formatter_crt_locks_005e57a8[id]);
}
void* __cdecl formatter_crt_calloc_005a8ea9(std::uint32_t count,std::uint32_t size) {
 const std::uint32_t bytes=count*size; // Original wraps; it has no division/overflow rejection.
 std::uint32_t rounded=bytes;
 if(rounded<=0xffffffe0u) { if(!rounded) rounded=1; rounded=(rounded+15u)&0xfffffff0u; }
 for(;;) {
  if(rounded<=0xffffffe0u) {
   if(bytes<=formatter_crt_small_limit_005e606c) {
    exit_registry_lock_api_005a4ba4(9);
    void* p=formatter_crt_small_allocate_005aad00(bytes);
    exit_registry_unlock_api_005a4c05(9);
    if(p) { formatter_crt_memset_005abe90(p,0,bytes); return p; }
   }
   if(void* p=formatter_crt_heap_allocate(formatter_crt_heap_006c01d8,8,rounded)) return p;
  }
  if(!formatter_crt_new_mode_006afec8 || !formatter_crt_call_new_005ab4ab(rounded)) return nullptr;
 }
}
void* __cdecl formatter_crt_memset_005abe90(void* destination,int value,std::uint32_t size) {
 auto* p=static_cast<std::uint8_t*>(destination);
 const auto byte=static_cast<std::uint8_t>(value);
 if(size>=4) {
  auto leading=(0u-address(p))&3u;
  size-=leading;
  while(leading--) { fill_store(p++,1,byte); }
  const std::uint32_t word=static_cast<std::uint32_t>(byte)*0x01010101u;
  auto words=size>>2; size&=3;
  while(words--) { fill_store(p,4,word); p+=4; }
 }
 while(size--) { fill_store(p++,1,byte); }
 return destination;
}
void __cdecl formatter_crt_initialize_thread_005a5449(void* pointer) {
 auto* p=static_cast<std::uint8_t*>(pointer);
 write32(p+0x50,address(formatter_crt_signal_table_005e5ec8));
 write32(p+0x14,1);
}
int __cdecl formatter_crt_initialize_tls_005a53f5() {
 formatter_crt_initialize_locks_005a4b7b();
 formatter_crt_tls_index_005e58b4=formatter_crt_tls_allocate();
 if(formatter_crt_tls_index_005e58b4==0xffffffffu) return 0;
 auto* p=static_cast<std::uint8_t*>(formatter_crt_calloc_005a8ea9(1,0x74));
 if(!p || !formatter_crt_tls_set(formatter_crt_tls_index_005e58b4,p)) return 0;
 formatter_crt_initialize_thread_005a5449(p);
 const auto id=formatter_crt_thread_id();
 write32(p+4,0xffffffffu); write32(p,id);
 return 1;
}
void* __cdecl formatter_crt_thread_005a545c() {
 const auto error=formatter_crt_get_last_error();
 auto* p=static_cast<std::uint8_t*>(formatter_crt_tls_get(formatter_crt_tls_index_005e58b4));
 if(!p) {
  p=static_cast<std::uint8_t*>(formatter_crt_calloc_005a8ea9(1,0x74));
  if(!p || !formatter_crt_tls_set(formatter_crt_tls_index_005e58b4,p)) formatter_fatal_005a2e22(16);
  formatter_crt_initialize_thread_005a5449(p);
  const auto id=formatter_crt_thread_id();
  write32(p+4,0xffffffffu); write32(p,id);
 }
 formatter_crt_set_last_error(error);
 return p;
}
std::int32_t* __cdecl formatter_lowio_errno_005a669e() {
 return reinterpret_cast<std::int32_t*>(static_cast<std::uint8_t*>(formatter_crt_thread_005a545c())+8);
}
std::uint32_t* __cdecl formatter_lowio_doserrno_005a66a7() {
 return reinterpret_cast<std::uint32_t*>(static_cast<std::uint8_t*>(formatter_crt_thread_005a545c())+12);
}
void __cdecl formatter_crt_release_thread_005a54c3(void* pointer) {
 if(formatter_crt_tls_index_005e58b4==0xffffffffu) return;
 auto* p=static_cast<std::uint8_t*>(pointer);
 if(!p) p=static_cast<std::uint8_t*>(formatter_crt_tls_get(formatter_crt_tls_index_005e58b4));
 if(p) {
  for(unsigned offset:{0x24u,0x28u,0x30u,0x38u,0x40u,0x44u})
   if(const auto value=read32(p+offset)) formatter_crt_free_005a3b9d(reinterpret_cast<void*>(static_cast<std::uintptr_t>(value)));
  const auto signal=read32(p+0x50);
  if(signal!=address(formatter_crt_signal_table_005e5ec8)) formatter_crt_free_005a3b9d(reinterpret_cast<void*>(static_cast<std::uintptr_t>(signal)));
  formatter_crt_free_005a3b9d(p);
 }
 formatter_crt_tls_set(formatter_crt_tls_index_005e58b4,nullptr);
}
}
