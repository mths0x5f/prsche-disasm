#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <Windows.h>
#include <bcrypt.h>
#pragma comment(lib,"bcrypt.lib")
#include "porsche/formatter_small_heap.hpp"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <map>
#include <string>
#include <vector>
namespace {
using U=std::uint32_t;
constexpr U START=0x23000000,HEAD=START,META=START+0x10000,OTHER=START+0x200000,REGION=START+0x400000;
U fail_api,fail_call,mode,a,b,c,seed,metadata_next,region_next,other_next,header_size,header_target;
U handler_calls;
bool failure_enabled;
U counters[10];
std::map<U,U> ranges,sizes;
std::string snapshot();
std::vector<std::string> states,boundary_states;
struct Results:std::vector<U> { void push_back(U v) {std::vector<U>::push_back(v);states.push_back(snapshot());} } returns;
std::vector<std::string> events;
struct Fatal{};
U addr(const void* p) { return static_cast<U>(reinterpret_cast<std::uintptr_t>(p)); }
std::uint8_t* ptr(U p) { return reinterpret_cast<std::uint8_t*>(static_cast<std::uintptr_t>(p)); }
bool fail(U id) { ++counters[id]; return failure_enabled&&id==fail_api&&(!fail_call||counters[id]==fail_call); }
void track(U p,U n) { if(p) { ranges[p]=std::max(ranges[p],n); sizes[p]=n; } }
std::string hex(U p,U n) { const char* d="0123456789abcdef"; std::string s; for(U i=0;i<n;++i) {const auto v=ptr(p)[i];s+=d[v>>4];s+=d[v&15];}return s; }
std::string snapshot() {
 using namespace porsche;
 static BCRYPT_ALG_HANDLE algorithm=[](){BCRYPT_ALG_HANDLE h=nullptr;if(BCryptOpenAlgorithmProvider(&h,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)std::abort();return h;}();
 BCRYPT_HASH_HANDLE h=nullptr;std::uint8_t digest[32];
 if(BCryptCreateHash(algorithm,&h,nullptr,0,nullptr,0,0)<0)std::abort();
 auto hash=[&](const void* p,U n){if(BCryptHashData(h,const_cast<PUCHAR>(static_cast<const UCHAR*>(p)),n,0)<0)std::abort();};
 const U globals[]={formatter_crt_heap_006c01d8,formatter_small_capacity_006c01c0,formatter_crt_header_count_006c01d0,addr(formatter_crt_headers_006c01d4),addr(formatter_small_cursor_006c01c8),addr(formatter_small_pending_006c01cc),formatter_small_pending_group_006c01c4};
 hash(globals,sizeof(globals));
 for(const auto& r:ranges){const U layout[]={r.first,r.second};hash(layout,sizeof(layout));hash(ptr(r.first),r.second);}
 if(BCryptFinishHash(h,digest,sizeof(digest),0)<0)std::abort();BCryptDestroyHash(h);
 const char* digits="0123456789abcdef";std::string result;for(auto v:digest){result+=digits[v>>4];result+=digits[v&15];}return result;
}
void boundary(){boundary_states.push_back(snapshot());}
void configure_failure() { std::memset(counters,0,sizeof(counters));failure_enabled=true; }
__declspec(noinline) U abi_call(const void* function,U count,const U* arguments) {
 U result,before,after,flags,saved_bx,saved_si,saved_di,before_bp,after_bp;
 __asm {
  push ebx
  push esi
  push edi
  mov before,esp
  mov before_bp,ebp
  mov ecx,count
  mov edx,arguments
 next_argument:
  test ecx,ecx
  jz invoke_body
  dec ecx
  push dword ptr [edx+ecx*4]
  jmp next_argument
 invoke_body:
  mov ebx,12345678h
  mov esi,12345678h
  mov edi,12345678h
  cld
  call function
  mov result,eax
  mov after_bp,ebp
  mov saved_bx,ebx
  mov saved_si,esi
  mov saved_di,edi
  pushfd
  pop eax
  mov flags,eax
  mov ecx,count
  lea esp,[esp+ecx*4]
  mov after,esp
  pop edi
  pop esi
  pop ebx
 }
 if(before!=after||before_bp!=after_bp||saved_bx!=0x12345678||saved_si!=0x12345678||saved_di!=0x12345678||(flags&0x400))std::abort();
 return result;
}
U get(U n,bool direct=true) {
 void* p=direct?porsche::formatter_crt_small_allocate_005aad00(n):porsche::exit_registry_malloc_005a3be5(n);
 returns.push_back(addr(p));
 if(p) for(U j=0;j<n;++j) ptr(addr(p))[j]=static_cast<std::uint8_t>(j*17+n+seed);
 return addr(p);
}
void release(U p) { porsche::formatter_crt_free_005a3b9d(ptr(p));returns.push_back(0); }
void reset() {
 using namespace porsche;
 std::memset(ptr(START),0xa5,0x400000); ranges.clear();sizes.clear();returns.clear();events.clear();states.clear();boundary_states.clear();
 std::memset(counters,0,sizeof(counters));failure_enabled=false;metadata_next=region_next=other_next=handler_calls=0;header_size=0;header_target=HEAD+0x1000;
 formatter_crt_heap_006c01d8=0xabcdef01;formatter_crt_header_count_006c01d0=0;formatter_crt_headers_006c01d4=nullptr;
 formatter_small_capacity_006c01c0=0;formatter_small_pending_group_006c01c4=87;formatter_small_cursor_006c01c8=nullptr;formatter_small_pending_006c01cc=nullptr;
 formatter_crt_small_limit_005e606c=1016;formatter_crt_new_mode_006afec8=mode;
 std::memset(formatter_crt_lock9_006afd30,0,24);std::memset(formatter_crt_lock17_006afd18,0,24);
}
void print(bool fatal) {
 using namespace porsche;
 std::printf("{\"fatal\":%s,\"heap\":%u,\"capacity\":%u,\"count\":%u,\"base\":%u,\"cursor\":%u,\"pending\":%u,\"group\":%u,\"returns\":[",
 fatal?"true":"false",formatter_crt_heap_006c01d8,formatter_small_capacity_006c01c0,formatter_crt_header_count_006c01d0,
 addr(formatter_crt_headers_006c01d4),addr(formatter_small_cursor_006c01c8),addr(formatter_small_pending_006c01cc),formatter_small_pending_group_006c01c4);
 for(std::size_t i=0;i<returns.size();++i) std::printf("%s%u",i?",":"",returns[i]);
 std::printf("],\"events\":[");for(std::size_t i=0;i<events.size();++i)std::printf("%s\"%s\"",i?",":"",events[i].c_str());
 std::printf("],\"states\":[");for(std::size_t i=0;i<states.size();++i)std::printf("%s\"%s\"",i?",":"",states[i].c_str());
 std::printf("],\"boundary_states\":[");for(std::size_t i=0;i<boundary_states.size();++i)std::printf("%s\"%s\"",i?",":"",boundary_states[i].c_str());
 std::printf("],\"memory\":[");bool first=true;
 for(const auto& r:ranges){std::printf("%s{\"p\":%u,\"data\":\"%s\"}",first?"":",",r.first,hex(r.first,r.second).c_str());first=false;}
 std::puts("]}");
}
}
namespace porsche {
const std::uint8_t formatter_crt_signal_table_005e5ec8[1]{};
int __cdecl new_handler(std::uint32_t n) {boundary();events.push_back("handler:"+std::to_string(n));return mode==2&&++handler_calls==1?1:0;}
void* __stdcall formatter_crt_heap_allocate(U heap,U flags,U n) {
 boundary();events.push_back("ha:"+std::to_string(heap)+":"+std::to_string(flags)+":"+std::to_string(n));if(fail(1))return nullptr;
 U out;
 if(n==0x140&&!formatter_crt_headers_006c01d4){out=HEAD;header_size=n;}
 else if(n==0x41c4){if(metadata_next>=32)std::abort();out=META+metadata_next++*0x10000;}
 else {if(n>0x10000||other_next>=16)std::abort();out=OTHER+other_next++*0x10000;}
 if(flags&8)std::memset(ptr(out),0,n);track(out,n);return ptr(out);
}
int __stdcall formatter_crt_heap_free(U heap,U flags,void* p){boundary();events.push_back("hf:"+std::to_string(heap)+":"+std::to_string(flags)+":"+std::to_string(addr(p)));return fail(7)?0:1;}
void* __stdcall formatter_small_heap_reallocate(U heap,U flags,void* p,U n) {
 boundary();events.push_back("hr:"+std::to_string(heap)+":"+std::to_string(flags)+":"+std::to_string(addr(p))+":"+std::to_string(n));if(fail(2))return nullptr;
 U out;
 if(addr(p)>=HEAD&&addr(p)<HEAD+0x10000){out=header_target;header_target+=0x1000;const U amount=header_size<n?header_size:n;std::memcpy(ptr(out),p,amount);header_size=n;}
 else {out=OTHER+other_next++*0x10000;const U amount=sizes[addr(p)]<n?sizes[addr(p)]:n;std::memcpy(ptr(out),p,amount);}
 if(n>0x10000)std::abort();track(out,n);return ptr(out);
}
U __stdcall formatter_small_heap_size(U heap,U flags,const void* p){boundary();events.push_back("hs:"+std::to_string(heap)+":"+std::to_string(flags)+":"+std::to_string(addr(p)));return fail(8)?0xffffffffu:sizes.count(addr(p))?sizes[addr(p)]:0xffffffffu;}
U __stdcall formatter_small_heap_create(U flags,U initial,U maximum){boundary();events.push_back("hc:"+std::to_string(flags)+":"+std::to_string(initial)+":"+std::to_string(maximum));return fail(5)?0:0xabcdef01;}
int __stdcall formatter_small_heap_destroy(U heap){boundary();events.push_back("hd:"+std::to_string(heap));return fail(9)?0:1;}
void* __stdcall formatter_small_virtual_allocate(void* p,U n,U flags,U protect){
 boundary();events.push_back("va:"+std::to_string(addr(p))+":"+std::to_string(n)+":"+std::to_string(flags)+":"+std::to_string(protect));if(fail(flags==0x2000?3:4))return nullptr;
 if(flags==0x2000){if(region_next>=12)std::abort();return ptr(REGION+region_next++*0x100000);}
 std::memset(p,0,n);track(addr(p),n);return p;
}
int __stdcall formatter_small_virtual_free(void* p,U n,U flags){boundary();events.push_back("vf:"+std::to_string(addr(p))+":"+std::to_string(n)+":"+std::to_string(flags));return fail(6)?0:1;}
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int id){boundary();events.push_back("fatal:"+std::to_string(id));throw Fatal{};}
void __stdcall formatter_lowio_critical_initialize(void*){std::abort();}
void __stdcall formatter_lowio_critical_enter(void* p){boundary();events.push_back(p==formatter_crt_lock9_006afd30?"enter9":"enter17");}
void __stdcall formatter_lowio_critical_leave(void* p){boundary();events.push_back(p==formatter_crt_lock9_006afd30?"leave9":"leave17");}
U __stdcall formatter_crt_tls_allocate(){std::abort();}
void* __stdcall formatter_crt_tls_get(U){std::abort();}
int __stdcall formatter_crt_tls_set(U,void*){std::abort();}
U __stdcall formatter_crt_get_last_error(){std::abort();}
void __stdcall formatter_crt_set_last_error(U){std::abort();}
U __stdcall formatter_crt_thread_id(){std::abort();}
}
int main(){
 using namespace porsche;
 if(VirtualAlloc(ptr(START),0x1000000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(START))return 3;
 char kind;
 while(std::cin>>kind>>fail_api>>fail_call>>mode>>a>>b>>c>>seed){
  reset();formatter_crt_new_handler_006afecc=mode?new_handler:nullptr;bool fatal=false;
  try {
   if(kind=='V') {
    const void* functions[]={reinterpret_cast<const void*>(formatter_small_initialize_005aa96c),reinterpret_cast<const void*>(formatter_crt_small_free_005aa9d5),reinterpret_cast<const void*>(formatter_crt_small_allocate_005aad00),reinterpret_cast<const void*>(formatter_small_new_header_005ab009),reinterpret_cast<const void*>(formatter_small_commit_005ab0ba),reinterpret_cast<const void*>(formatter_small_resize_005ab1b5),reinterpret_cast<const void*>(exit_registry_reallocate_005a8029),reinterpret_cast<const void*>(exit_registry_allocation_size_005a8161),reinterpret_cast<const void*>(formatter_small_heap_initialize_005a96fa),reinterpret_cast<const void*>(formatter_small_copy_005a7ad0)};
    const U counts[]={0,2,1,0,1,3,2,1,1,3};U args[3]{};
    if(a!=0&&a!=8)returns.push_back(static_cast<U>(formatter_small_initialize_005aa96c()));
    if(a==1||a==5||a==6||a==7){const U p=get(64);args[0]=p;args[1]=96;if(a==1||a==5){args[0]=addr(formatter_crt_find_header_005aa9aa(ptr(p)));args[1]=p;args[2]=96;}}
    if(a==2)args[0]=32;
    if(a==4){args[0]=addr(formatter_small_new_header_005ab009());returns.push_back(args[0]);}
    if(a==9){for(U j=0;j<1024;++j)ptr(OTHER)[j]=static_cast<std::uint8_t>(j*13+seed);track(OTHER,1024);args[0]=OTHER+35;args[1]=OTHER+32;args[2]=127;}
    const U result=abi_call(functions[a],counts[a],args);returns.push_back(a==1?0:result);
   }
   else if(kind=='I'){configure_failure();returns.push_back(static_cast<U>(formatter_small_heap_initialize_005a96fa(a)));}
   else if(kind=='S'){configure_failure();returns.push_back(static_cast<U>(formatter_small_initialize_005aa96c()));}
   else if(kind=='M'){for(U j=0;j<1024;++j)ptr(OTHER)[j]=static_cast<std::uint8_t>(j*13+seed);track(OTHER,1024);returns.push_back(addr(formatter_small_copy_005a7ad0(ptr(OTHER+b),ptr(OTHER+a),c)));}
   else {
    returns.push_back(static_cast<U>(formatter_small_initialize_005aa96c()));
    if(kind=='H'){if(a){returns.push_back(addr(formatter_small_new_header_005ab009()));formatter_small_capacity_006c01c0=a;}configure_failure();returns.push_back(addr(formatter_small_new_header_005ab009()));}
    else if(kind=='C'){auto* h=formatter_small_new_header_005ab009();returns.push_back(addr(h));U bitmap=0x80000000u>>(a&31);std::memcpy(h+8,&bitmap,4);configure_failure();returns.push_back(static_cast<U>(formatter_small_commit_005ab0ba(h)));}
    else if(kind=='D'){
     std::vector<U> values;for(U i=0;i<a;++i){if(i){auto* h=formatter_small_new_header_005ab009();returns.push_back(addr(h));returns.push_back(static_cast<U>(formatter_small_commit_005ab0ba(h)));formatter_small_cursor_006c01c8=h;}values.push_back(get(1016));}
     configure_failure();if(b)std::reverse(values.begin(),values.end());for(U p:values)release(p);
    } else if(kind=='E'){void* p=formatter_crt_heap_allocate(formatter_crt_heap_006c01d8,0,128);for(U j=0;j<128;++j)ptr(addr(p))[j]=static_cast<std::uint8_t>(j+seed);configure_failure();returns.push_back(c?exit_registry_allocation_size_005a8161(p):addr(exit_registry_reallocate_005a8029(p,b)));}
    else if(kind=='R'||kind=='r'){
     U values[3];for(U& v:values)v=get(a);if(b&1)release(values[0]);if(b&2)release(values[2]);configure_failure();
     returns.push_back(kind=='R'?static_cast<U>(formatter_small_resize_005ab1b5(formatter_crt_find_header_005aa9aa(ptr(values[1])),ptr(values[1]),c)):addr(exit_registry_reallocate_005a8029(ptr(values[1]),c)));
    } else {
     configure_failure();std::vector<U> values;for(U i=0;i<a;++i){U n=seed?(b+i*seed)%1017:b;U p=get(n,kind!='P');if(!p)break;values.push_back(p);}
     if(kind=='F'){
      std::vector<U> order;if(c==1){order=values;std::reverse(order.begin(),order.end());}else if(c==2){for(std::size_t j=0;j<values.size();j+=2)order.push_back(values[j]);for(std::size_t j=1;j<values.size();j+=2)order.push_back(values[j]);}else order=values;
      for(U p:order)release(p);
     } else if(kind=='Z'){for(U p:values)returns.push_back(exit_registry_allocation_size_005a8161(ptr(p)));}
     else if(kind=='B'&&!values.empty()){release(values.back());get(b);}
    }
   }
  }catch(const Fatal&){fatal=true;}
  print(fatal);
 }
}
