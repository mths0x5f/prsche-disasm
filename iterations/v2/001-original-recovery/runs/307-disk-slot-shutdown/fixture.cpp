#include "porsche/application_pool.hpp"
#include "porsche/disk_open.hpp"
#include "porsche/heap_locks.hpp"
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(unsigned);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,unsigned,unsigned*,void*);
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
using U=std::uint32_t;
static unsigned char original[]={
#include "original-body.inc"
};
struct Relocation{U offset,next,target;};
static const Relocation relocations[]={
#include "relocations.inc"
};
alignas(16) static unsigned char arena[4096],initial[4096],expected[4096];
static U events[256],wanted[256],eventCount,scenario,failures,cases,closeCount;
static void duplicate307(void* destination,const void* source,U size){auto* d=static_cast<volatile unsigned char*>(destination);auto* s=static_cast<const volatile unsigned char*>(source);while(size--)*d++=*s++;}
static int differ307(const void* left,const void* right,U size){auto* a=static_cast<const volatile unsigned char*>(left);auto* b=static_cast<const volatile unsigned char*>(right);while(size--)if(*a++!=*b++)return 1;return 0;}
static U address(U n){return reinterpret_cast<U>(arena+n);}
static void event(U kind,U argument){if(eventCount+2>256){++failures;return;}events[eventCount++]=kind;events[eventCount++]=argument;}
namespace porsche {
PhysicalFile* physical_files_006af084;
std::int32_t physical_count_006af080;
void* disk_slot_mutex_006af07c;
void* disk_mutexes_006aeffc[32];
void __cdecl heap_enter_005322b0(void* mutex){
 event(1,reinterpret_cast<U>(mutex));
 if(scenario==36){physical_files_006af084=reinterpret_cast<PhysicalFile*>(address(512));physical_count_006af080=4;}
 if(scenario==45)disk_slot_mutex_006af07c=reinterpret_cast<void*>(0x85000001);
}
void __cdecl heap_leave_005322c0(void* mutex){event(2,reinterpret_cast<U>(mutex));if(scenario==44)disk_slot_mutex_006af07c=reinterpret_cast<void*>(0x86000002);}
void __cdecl heap_lock_destroy_005322d0(void* mutex){
 U value=reinterpret_cast<U>(mutex);event(3,value);
 if(scenario==41 && value==0x81000000)disk_mutexes_006aeffc[1]=reinterpret_cast<void*>(0x88000003);
 if(scenario==42 && value==0x81000000)disk_mutexes_006aeffc[0]=reinterpret_cast<void*>(0x89000004);
 if(scenario==43)disk_slot_mutex_006af07c=reinterpret_cast<void*>(0x87000005);
}
U __cdecl file_physical_close_00592290(void* handle){
 event(4,reinterpret_cast<U>(handle));++closeCount;
 if(scenario==37)physical_count_006af080=1;
 if(scenario==38)physical_count_006af080=5;
 if(scenario==39)physical_files_006af084=reinterpret_cast<PhysicalFile*>(address(512));
 // Model a real closer's active-byte update through its current global table.
 U index=~reinterpret_cast<U>(handle);reinterpret_cast<unsigned char*>(physical_files_006af084)[index*0x20]=0;
 return 0x80000001;
}
U __cdecl file_object_free_0056e640(void* pointer){event(5,reinterpret_cast<U>(pointer));if(scenario==40)physical_files_006af084=reinterpret_cast<PhysicalFile*>(address(512));return 1;}
}
struct Globals{porsche::PhysicalFile* table;std::int32_t count;void* mutex;void* slots[32];};
static Globals globals(){Globals q{};q.table=porsche::physical_files_006af084;q.count=porsche::physical_count_006af080;q.mutex=porsche::disk_slot_mutex_006af07c;duplicate307(q.slots,porsche::disk_mutexes_006aeffc,128);return q;}
static void restore(const Globals& q){porsche::physical_files_006af084=q.table;porsche::physical_count_006af080=q.count;porsche::disk_slot_mutex_006af07c=q.mutex;duplicate307(porsche::disk_mutexes_006aeffc,q.slots,128);}
static void initialize(U test){
 scenario=test;eventCount=0;closeCount=0;
 for(U i=0;i<sizeof(arena);++i)arena[i]=static_cast<unsigned char>(0xa5+i*13);
 for(U base=0;base<=512;base+=512)for(U i=0;i<8;++i)arena[base+i*0x20]=static_cast<unsigned char>(i%2?0:0x80);
 for(U i=0;i<32;++i)porsche::disk_mutexes_006aeffc[i]=nullptr;
 if(test==2)for(U i=0;i<32;++i)porsche::disk_mutexes_006aeffc[i]=reinterpret_cast<void*>(0x81000000+i);
 if(test>=4 && test<36)porsche::disk_mutexes_006aeffc[test-4]=reinterpret_cast<void*>(0x81000000+test-4);
 if(test>=36)porsche::disk_mutexes_006aeffc[0]=reinterpret_cast<void*>(0x81000000);
 porsche::physical_files_006af084=test?reinterpret_cast<porsche::PhysicalFile*>(address(0)):nullptr;
 porsche::physical_count_006af080=test==1?-3:(test==2?0:3);
 if(test==38)porsche::physical_count_006af080=1;
 if(test==46)porsche::physical_count_006af080=static_cast<std::int32_t>(0x80000000);
 if(test==47)for(U i=0;i<3;++i)arena[i*0x20]=255;
 if(test==39){arena[512+0x20]=0x80;arena[512+0x40]=0;}
 porsche::disk_slot_mutex_006af07c=reinterpret_cast<void*>(test==3?0:0x84000000);
}
extern "C" __declspec(naked) void __cdecl capture307(void*,U*){
 __asm {
  push ebp
  mov ebp,esp
  push ebx
  push esi
  push edi
  mov ebx,12345678h
  mov esi,76543210h
  mov edi,89abcdefh
  cld
  call dword ptr [ebp+8]
  mov edx,[ebp+12]
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
static U target(U va){using namespace porsche;switch(va){
 case 0x6af084:return reinterpret_cast<U>(&physical_files_006af084);case 0x6af080:return reinterpret_cast<U>(&physical_count_006af080);
 case 0x6af07c:return reinterpret_cast<U>(&disk_slot_mutex_006af07c);case 0x6aeffc:return reinterpret_cast<U>(disk_mutexes_006aeffc);
 case 0x5322b0:return reinterpret_cast<U>(&heap_enter_005322b0);case 0x5322c0:return reinterpret_cast<U>(&heap_leave_005322c0);case 0x5322d0:return reinterpret_cast<U>(&heap_lock_destroy_005322d0);
 case 0x592290:return reinterpret_cast<U>(&file_physical_close_00592290);case 0x56e640:return reinterpret_cast<U>(&file_object_free_0056e640);
 default:++failures;return 0;
}}
extern "C" void __cdecl entry(){
 auto* reference=static_cast<unsigned char*>(VirtualAlloc(nullptr,sizeof(original),0x3000,0x40));if(!reference)ExitProcess(2);
 duplicate307(reference,original,sizeof(original));for(const auto& relocation:relocations){U value=target(relocation.target);if(relocation.offset==136)value=reinterpret_cast<U>(porsche::disk_mutexes_006aeffc+32);if(relocation.next)value-=reinterpret_cast<U>(reference+relocation.next);duplicate307(reference+relocation.offset,&value,4);}
 for(U test=0;test<48;++test){
  initialize(test);Globals initialGlobals=globals();duplicate307(initial,arena,sizeof(arena));U originalAbi[5]{},actualAbi[5]{};
  capture307(reference,originalAbi);Globals expectedGlobals=globals();duplicate307(expected,arena,sizeof(arena));U expectedCount=eventCount;duplicate307(wanted,events,sizeof(events));
  restore(initialGlobals);duplicate307(arena,initial,sizeof(arena));eventCount=0;closeCount=0;
  capture307(reinterpret_cast<void*>(&porsche::application_pool_disk_slots_release_005918c0),actualAbi);Globals actualGlobals=globals();
  if(differ307(arena,expected,sizeof(arena))||differ307(&actualGlobals,&expectedGlobals,sizeof(Globals))||eventCount!=expectedCount||differ307(events,wanted,eventCount*4))++failures;
  for(U i=0;i<2;++i){U* abi=i?actualAbi:originalAbi;if(abi[0]||abi[1]!=0x12345678||abi[2]!=0x76543210||abi[3]!=0x89abcdef||abi[4])++failures;}
  ++cases;
 }
 const char ok[]="{\"cases\":48,\"failures\":0}\n";U written=0;if(!failures&&cases==48)WriteFile(GetStdHandle(0xfffffff5u),ok,sizeof(ok)-1,&written,nullptr);
 ExitProcess(failures||cases!=48?1:0);
}
