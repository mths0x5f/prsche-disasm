#include "heap_slot_release_304.hpp"
#include "porsche/heap.hpp"
#include "porsche/heap_locks.hpp"
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(unsigned);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,unsigned,unsigned*,void*);
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
using U=std::uint32_t;
static unsigned char original[]={
#include "original-body.inc"
};
alignas(16) static unsigned char arena[4096],initial[4096],expected[4096];
static U initialTable[16],expectedTable[16],events[32],wanted[32];
static U eventCount,mode,selected,failures,cases;
static void duplicate304(void* destination,const void* source,U size){
 auto* d=static_cast<volatile unsigned char*>(destination);auto* s=static_cast<const volatile unsigned char*>(source);
 while(size--)*d++=*s++;
}
static int differ304(const void* left,const void* right,U size){
 auto* a=static_cast<const volatile unsigned char*>(left);auto* b=static_cast<const volatile unsigned char*>(right);
 while(size--)if(*a++!=*b++)return 1;return 0;
}
static U address(U n){return reinterpret_cast<U>(arena+n);}
static U& at(U n){return *reinterpret_cast<U*>(arena+n);}
static void event(U kind,U a,U b,U c){if(eventCount+4>32){++failures;return;}events[eventCount++]=kind;events[eventCount++]=a;events[eventCount++]=b;events[eventCount++]=c;}
namespace porsche {
// Only callees are controlled. The table allocation is linked unchanged from272.
void __cdecl heap_lock_destroy_005322d0(void* lock){
 event(1,reinterpret_cast<U>(lock),0,0);
 if(mode==1)heaps_006b4f20[selected]=reinterpret_cast<OriginalHeap*>(address(256));
 if(mode==2)at(64+0x38)=0xabcdef01;
 if(mode==4)heaps_006b4f20[selected]=nullptr;
}
void __cdecl heap_fill_0053c290(void* object,U value,U count){
 event(2,reinterpret_cast<U>(object),value,count);
 auto* bytes=static_cast<volatile unsigned char*>(object);for(U i=0;i<count;++i)bytes[i]=static_cast<unsigned char>(value);
 if(mode==3){heaps_006b4f20[selected]=reinterpret_cast<OriginalHeap*>(address(256));heaps_006b4f20[(selected+1)&15]=reinterpret_cast<OriginalHeap*>(address(512));arena[512]=0x79;}
}
}
extern "C" __declspec(naked) void __cdecl capture304(void*,U,U*){
 __asm {
  push ebp
  mov ebp,esp
  push ebx
  push esi
  push edi
  mov ebx,12345678h
  mov esi,76543210h
  mov edi,89abcdefh
  push dword ptr [ebp+12]
  cld
  call dword ptr [ebp+8]
  add esp,4
  mov edx,[ebp+16]
  mov [edx+20],eax
  lea eax,[ebp-12]
  sub eax,esp
  mov [edx],eax
  mov [edx+4],ebx
  mov [edx+8],esi
  mov [edx+12],edi
  pushfd
  pop eax
  and eax,400h
  mov [edx+16],eax
  pop edi
  pop esi
  pop ebx
  pop ebp
  ret
 }
}
static void initialize(U scenario,U slot,U presence){
 mode=scenario;selected=slot;eventCount=0;
 for(U i=0;i<sizeof(arena);++i)arena[i]=static_cast<unsigned char>(0xa5+i*13);
 for(U i=0;i<16;++i)porsche::heaps_006b4f20[i]=reinterpret_cast<porsche::OriginalHeap*>(address(1024+i*64));
 porsche::heaps_006b4f20[slot]=presence?reinterpret_cast<porsche::OriginalHeap*>(address(64)):nullptr;
 at(64+0x38)=presence==2?0x81234567:0;
}
extern "C" void __cdecl entry(){
 auto* reference=static_cast<unsigned char*>(VirtualAlloc(nullptr,sizeof(original),0x3000,0x40));if(!reference)ExitProcess(2);
 duplicate304(reference,original,sizeof(original));
 const U table=reinterpret_cast<U>(porsche::heaps_006b4f20);
 duplicate304(reference+14,&table,4);duplicate304(reference+21,&table,4);
 U displacement=reinterpret_cast<U>(&porsche::heap_lock_destroy_005322d0)-reinterpret_cast<U>(reference+42);duplicate304(reference+38,&displacement,4);
 displacement=reinterpret_cast<U>(&porsche::heap_fill_0053c290)-reinterpret_cast<U>(reference+55);duplicate304(reference+51,&displacement,4);
 const U high[]={0,0x10,0x80000000,0xfffffff0};
 for(U scenario=0;scenario<5;++scenario)for(U slot=0;slot<16;++slot)for(U bits:high)for(U presence=0;presence<3;++presence){
  initialize(scenario,slot,presence);duplicate304(initial,arena,sizeof(arena));duplicate304(initialTable,porsche::heaps_006b4f20,64);
  U actualAbi[6]{},originalAbi[6]{};const U id=bits|slot;
  capture304(reference,id,originalAbi);duplicate304(expected,arena,sizeof(arena));duplicate304(expectedTable,porsche::heaps_006b4f20,64);
  U expectedCount=eventCount;duplicate304(wanted,events,sizeof(events));duplicate304(arena,initial,sizeof(arena));duplicate304(porsche::heaps_006b4f20,initialTable,64);eventCount=0;
  capture304(reinterpret_cast<void*>(&porsche::heap_slot_release_005699f0),id,actualAbi);
  if(differ304(arena,expected,sizeof(arena))||differ304(porsche::heaps_006b4f20,expectedTable,64)||eventCount!=expectedCount||differ304(events,wanted,eventCount*4))++failures;
  for(U i=0;i<2;++i){U* abi=i?actualAbi:originalAbi;if(abi[0]||abi[1]!=0x12345678||abi[2]!=0x76543210||abi[3]!=0x89abcdef||abi[4]||abi[5]!=(presence?1u:0u))++failures;}
  ++cases;
 }
 const char ok[]="{\"cases\":960,\"failures\":0}\n";U written=0;
 if(!failures&&cases==960)WriteFile(GetStdHandle(0xfffffff5u),ok,sizeof(ok)-1,&written,nullptr);
 ExitProcess(failures||cases!=960?1:0);
}
