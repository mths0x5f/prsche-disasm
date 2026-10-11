#include "porsche/formatter_crt_runtime.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <initializer_list>
#include <string>
#include <vector>

namespace {
alignas(16) std::uint8_t arena[0xc000];
std::uint32_t a,b,threshold,small_success,mode,retries,tls_mode,race,length;
int heap_fail;
unsigned heap_calls,handler_calls,heap_next,target_lock;
std::uint32_t last_error;
void* tls_value;
std::vector<std::string> events;
struct Fatal{};
std::uint32_t addr(const void* p) { return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(p)); }
void write32(void* p,std::uint32_t v) { std::memcpy(p,&v,4); }
int loc(const void* p) {
 using namespace porsche;
 if(!p) return -1;
 if(p==formatter_crt_signal_table_005e5ec8) return -2;
 if(p==formatter_crt_lock1_006afd00) return -100;
 if(p==formatter_crt_lock17_006afd18) return -124;
 if(p==formatter_crt_lock9_006afd30) return -148;
 if(p==formatter_crt_lock13_006afd48) return -172;
 return static_cast<std::int32_t>(addr(p)-addr(arena));
}
std::string hex(const void* p,std::size_t n) {
 const char* digits="0123456789abcdef"; const auto* s=static_cast<const std::uint8_t*>(p); std::string out;
 for(std::size_t i=0;i<n;++i) { out+=digits[s[i]>>4]; out+=digits[s[i]&15]; }
 return out;
}
int __cdecl handler(std::uint32_t size) {
 events.push_back("handler:"+std::to_string(size)); ++handler_calls;
 if(race==4) porsche::formatter_crt_new_mode_006afec8=0;
 if(race==5) porsche::formatter_crt_new_handler_006afecc=nullptr;
 last_error=0x39;
 return handler_calls<=retries ? -7 : 0;
}
void reset() {
 using namespace porsche;
 std::memset(arena,0xa5,sizeof(arena));
 std::memset(formatter_crt_lock1_006afd00,0xcc,24); std::memset(formatter_crt_lock17_006afd18,0xcc,24);
 std::memset(formatter_crt_lock9_006afd30,0xcc,24); std::memset(formatter_crt_lock13_006afd48,0xcc,24);
 for(unsigned i=0;i<26;++i) formatter_crt_locks_005e57a8[i]=arena+0x9000+i*32;
 formatter_crt_locks_005e57a8[1]=formatter_crt_lock1_006afd00;
 formatter_crt_locks_005e57a8[17]=formatter_crt_lock17_006afd18;
 formatter_crt_locks_005e57a8[9]=formatter_crt_lock9_006afd30;
 formatter_crt_locks_005e57a8[13]=formatter_crt_lock13_006afd48;
 formatter_crt_small_limit_005e606c=threshold;
 formatter_crt_new_mode_006afec8=mode;
 formatter_crt_new_handler_006afecc=mode ? handler : nullptr;
 formatter_crt_heap_006c01d8=0x76543210;
 formatter_crt_header_count_006c01d0=4;
 formatter_crt_headers_006c01d4=arena+0xb000;
 for(unsigned i=0;i<4;++i) write32(arena+0xb000+i*20+12,addr(arena)+0x1000+i*0x100000);
 formatter_crt_tls_index_005e58b4=tls_mode==5 ? 0xffffffffu : 7;
 tls_value=tls_mode==0 ? arena+0x7000 : nullptr;
 last_error=77; heap_calls=handler_calls=0; heap_next=0x2000; target_lock=a;
 events.clear();
}
void print_state(int result,bool fatal) {
 using namespace porsche;
 // Normalize only original pointer fields; all surrounding bytes remain compared.
 auto normalized=std::vector<std::uint8_t>(arena,arena+sizeof(arena));
 for(unsigned i=0;i<4;++i) write32(normalized.data()+0xb000+i*20+12,0x1000+i*0x100000);
 for(unsigned off:{0x7000u,0x2000u,0x1000u}) {
  std::uint32_t value; std::memcpy(&value,arena+off+0x50,4);
  if(value==addr(formatter_crt_signal_table_005e5ec8)) write32(normalized.data()+off+0x50,0x5e5ec8);
 }
 // Cleanup fixture pointer fields use original arena-relative addresses.
 for(unsigned off:{0x24u,0x28u,0x30u,0x38u,0x40u,0x44u,0x50u}) {
  std::uint32_t value; std::memcpy(&value,arena+0x7000+off,4);
  if(value>=addr(arena)&&value<addr(arena)+sizeof(arena)) write32(normalized.data()+0x7000+off,value-addr(arena)+0x2210000);
 }
 std::printf("{\"return\":%d,\"fatal\":%s,\"error\":%u,\"tls_index\":%u,\"tls\":%d,\"heap\":%u,\"mode\":%u,\"handler\":%s,\"locks\":[",
 result,fatal?"true":"false",last_error,formatter_crt_tls_index_005e58b4,loc(tls_value),formatter_crt_heap_006c01d8,
 formatter_crt_new_mode_006afec8,formatter_crt_new_handler_006afecc?"true":"false");
 for(unsigned i=0;i<26;++i) std::printf("%s%d",i?",":"",loc(formatter_crt_locks_005e57a8[i]));
 std::printf("],\"arena\":\"%s\",\"static\":\"%s%s%s%s\",\"events\":[",hex(normalized.data(),normalized.size()).c_str(),
 hex(formatter_crt_lock1_006afd00,24).c_str(),hex(formatter_crt_lock17_006afd18,24).c_str(),
 hex(formatter_crt_lock9_006afd30,24).c_str(),hex(formatter_crt_lock13_006afd48,24).c_str());
 for(std::size_t i=0;i<events.size();++i) std::printf("%s\"%s\"",i?",":"",events[i].c_str());
 std::puts("]}");
}
}
namespace porsche {
const std::uint8_t formatter_crt_signal_table_005e5ec8[1]{};
void* __cdecl formatter_crt_small_allocate_005aad00(std::uint32_t n) {
 events.push_back("small:"+std::to_string(n)); last_error=0x32;
 return small_success ? arena+0x1000 : nullptr;
}
void __cdecl formatter_crt_small_free_005aa9d5(std::uint8_t* h,void* p) {
 events.push_back("smallfree:"+std::to_string(loc(h))+":"+std::to_string(loc(p))); last_error=0x33;
}
void* __stdcall formatter_crt_heap_allocate(std::uint32_t heap,std::uint32_t flags,std::uint32_t n) {
 events.push_back("heapalloc:"+std::to_string(heap)+":"+std::to_string(flags)+":"+std::to_string(n));
 last_error=0x31; ++heap_calls;
 if(heap_fail<0 || heap_calls<=static_cast<unsigned>(heap_fail) || tls_mode==2) return nullptr;
 if(n>0x200 || heap_next+0x200>0x7000) std::abort();
 auto* p=arena+heap_next; heap_next+=0x200;
 if(flags&8) std::memset(p,0,n);
 return p;
}
int __stdcall formatter_crt_heap_free(std::uint32_t heap,std::uint32_t flags,void* p) {
 events.push_back("heapfree:"+std::to_string(heap)+":"+std::to_string(flags)+":"+std::to_string(loc(p))); last_error=0x34;
 if(race==6) write32(arena+0x7000+0x28,addr(arena)+0x6000);
 if(race==7) formatter_crt_tls_index_005e58b4=33;
 return 0;
}
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int id) { events.push_back("fatal:"+std::to_string(id)); throw Fatal{}; }
void __stdcall formatter_lowio_critical_initialize(void* p) {
 events.push_back("init:"+std::to_string(loc(p))); std::memset(p,0x5a,24); last_error=0x41;
 if(race==2) formatter_crt_locks_005e57a8[target_lock]=arena+0x9700;
 if(race==9 && p==formatter_crt_lock17_006afd18) {
  formatter_crt_locks_005e57a8[13]=arena+0x9700; formatter_crt_locks_005e57a8[9]=arena+0x9800; formatter_crt_locks_005e57a8[1]=arena+0x9900;
 }
}
void __stdcall formatter_lowio_critical_enter(void* p) {
 events.push_back("enter:"+std::to_string(loc(p))); last_error=0x42;
 if(race==1 && p==formatter_crt_lock17_006afd18) formatter_crt_locks_005e57a8[target_lock]=arena+0x9700;
}
void __stdcall formatter_lowio_critical_leave(void* p) {
 events.push_back("leave:"+std::to_string(loc(p))); last_error=0x43;
 if(race==3 && p==formatter_crt_lock17_006afd18) formatter_crt_locks_005e57a8[target_lock]=arena+0x9700;
 if(race==8) formatter_crt_heap_006c01d8=0x12345601;
}
std::uint32_t __stdcall formatter_crt_tls_allocate() { events.push_back("tlsalloc"); last_error=0x47; return tls_mode==4 ? 0xffffffffu : 7; }
void* __stdcall formatter_crt_tls_get(std::uint32_t id) { events.push_back("tlsget:"+std::to_string(id)); last_error=0x44; return tls_value; }
int __stdcall formatter_crt_tls_set(std::uint32_t id,void* p) {
 events.push_back("tlsset:"+std::to_string(id)+":"+std::to_string(loc(p))); last_error=0x45;
 if(tls_mode==3) return 0;
 if(race==10) formatter_crt_tls_index_005e58b4=33;
 tls_value=p; return 1;
}
std::uint32_t __stdcall formatter_crt_get_last_error() { events.push_back("geterror"); return last_error; }
void __stdcall formatter_crt_set_last_error(std::uint32_t v) { events.push_back("seterror:"+std::to_string(v)); last_error=v; }
std::uint32_t __stdcall formatter_crt_thread_id() {
 events.push_back("threadid"); last_error=0x46;
 if(race==11) { write32(static_cast<std::uint8_t*>(tls_value)+4,0x1234); tls_value=arena+0x7200; }
 return 0x24681357;
}
#if defined(PORSCHE_CRT_MEMORY_TRACE)
void __cdecl formatter_crt_memset_store(const void* p,std::uint32_t width,std::uint32_t value) {
 events.push_back("store:"+std::to_string(loc(p))+":"+std::to_string(width)+":"+std::to_string(value));
}
#endif
}
int main() {
 using namespace porsche;
 std::printf("{\"initial\":[%u,%u,%u,%u,%u,%d,%d],\"locks\":[",formatter_crt_small_limit_005e606c,formatter_crt_new_mode_006afec8,
 formatter_crt_heap_006c01d8,formatter_crt_header_count_006c01d0,formatter_crt_tls_index_005e58b4,
 formatter_crt_new_handler_006afecc?1:0,formatter_crt_headers_006c01d4?1:0);
 for(unsigned i=0;i<26;++i) std::printf("%s%d",i?",":"",loc(formatter_crt_locks_005e57a8[i]));
 std::printf("],\"static\":\"%s%s%s%s\"}\n",hex(formatter_crt_lock1_006afd00,24).c_str(),hex(formatter_crt_lock17_006afd18,24).c_str(),
 hex(formatter_crt_lock9_006afd30,24).c_str(),hex(formatter_crt_lock13_006afd48,24).c_str());
 char op;
 while(std::cin>>op>>a>>b>>threshold>>small_success>>heap_fail>>mode>>retries>>tls_mode>>race>>length) {
  reset(); int result=0; bool fatal=false;
  if(op=='l' && b==0) formatter_crt_locks_005e57a8[a]=nullptr;
  if(op=='f') formatter_crt_header_count_006c01d0=threshold;
  if(op=='q') formatter_crt_header_count_006c01d0=threshold;
  if(op=='x') {
   const unsigned offsets[]={0x24,0x28,0x30,0x38,0x40,0x44};
   for(unsigned i=0;i<6;++i) write32(arena+0x7000+offsets[i],a&(1u<<i) ? addr(arena)+0x5000+i*0x100 : 0);
   write32(arena+0x7000+0x50,(a&64) ? addr(arena)+0x6800 : addr(formatter_crt_signal_table_005e5ec8));
  }
  try {
   if(op=='m') result=loc(exit_registry_malloc_005a3be5(a));
   else if(op=='n') result=loc(formatter_crt_nh_malloc_005a3bf7(a,b));
   else if(op=='r') result=loc(formatter_crt_allocate_005a3c23(a));
   else if(op=='c') result=loc(formatter_crt_calloc_005a8ea9(a,b));
   else if(op=='h') result=formatter_crt_call_new_005ab4ab(a);
   else if(op=='f') formatter_crt_free_005a3b9d(a==0xffffffffu ? nullptr : reinterpret_cast<void*>(static_cast<std::uintptr_t>(addr(arena)+a)));
   else if(op=='q') result=loc(formatter_crt_find_header_005aa9aa(reinterpret_cast<void*>(static_cast<std::uintptr_t>(addr(arena)+a))));
   else if(op=='l') exit_registry_lock_api_005a4ba4(a);
   else if(op=='u') exit_registry_unlock_api_005a4c05(a);
   else if(op=='i') formatter_crt_initialize_locks_005a4b7b();
   else if(op=='t') result=formatter_crt_initialize_tls_005a53f5();
   else if(op=='d') formatter_crt_initialize_thread_005a5449(arena+0x7000);
   else if(op=='g') result=loc(formatter_crt_thread_005a545c());
   else if(op=='e') result=loc(formatter_lowio_errno_005a669e());
   else if(op=='o') result=loc(formatter_lowio_doserrno_005a66a7());
   else if(op=='x') formatter_crt_release_thread_005a54c3(b ? arena+0x7000 : nullptr);
   else if(op=='s') result=loc(formatter_crt_memset_005abe90(arena+a,static_cast<int>(b),length));
   else return 2;
  } catch(const Fatal&) { fatal=true; }
  print_state(result,fatal);
 }
}
