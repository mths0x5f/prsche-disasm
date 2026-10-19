#include "porsche/application_pool.hpp"
#include "porsche/file_worker.hpp"
#include "porsche/file_events.hpp"
#include "porsche/file_wait.hpp"
#include "porsche/network_workers_members.hpp"
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
alignas(16) static unsigned char arena[0x4000],initial[0x4000],expected[0x4000];
static U events[2048],wanted[2048],eventCount,scenario,failures,cases,activeDevice,sleeps,popIndex,popCount;
static void duplicate305(void* destination,const void* source,U size){auto* d=static_cast<volatile unsigned char*>(destination);auto* s=static_cast<const volatile unsigned char*>(source);while(size--)*d++=*s++;}
static int differ305(const void* left,const void* right,U size){auto* a=static_cast<const volatile unsigned char*>(left);auto* b=static_cast<const volatile unsigned char*>(right);while(size--)if(*a++!=*b++)return 1;return 0;}
static U address(U offset){return reinterpret_cast<U>(arena+offset);}
static U& at(U offset){return *reinterpret_cast<U*>(arena+offset);}
static U& cell(U pointer){return *reinterpret_cast<U*>(pointer);}
static void event(U kind,U argument){if(eventCount+2>2048){++failures;return;}events[eventCount++]=kind;events[eventCount++]=argument;}
namespace porsche {
// Private fixture definitions use the exact existing declarations. No definition
// in this translation unit is part of the game object.
FileDevice* devices_006a5c7c;
IoList free_operations_006a5c58{},free_auxiliary_006a5c38{};
void* free_operation_arena_006a5c54;
void* application_pool_lock_006a5c78;
U file_shutdown_006a5c80;
IoNode* __cdecl io_pop_00580790(IoList* queue){
 event(1,reinterpret_cast<U>(queue));
 if(scenario==44)devices_006a5c7c=reinterpret_cast<FileDevice*>(address(0x1000));
 if(popIndex==popCount){queue->count=0;queue->head=nullptr;return nullptr;}
 U node=address(0x3000+popIndex*0x40);++popIndex;queue->count=static_cast<std::int32_t>(popCount-popIndex);queue->head=popIndex<popCount?reinterpret_cast<IoNode*>(address(0x3000+popIndex*0x40)):nullptr;
 return reinterpret_cast<IoNode*>(node);
}
U __cdecl file_physical_close_00592290(void* handle){event(2,reinterpret_cast<U>(handle));if(scenario==42)at(0x3000+0xc)=0x99887766;return 0x80000001;}
U __cdecl file_object_free_0056e640(void* object){
 const U value=reinterpret_cast<U>(object);event(3,value);
 if(scenario==38 && value==address(0x3200))devices_006a5c7c=reinterpret_cast<FileDevice*>(address(0x1000));
 if(scenario==45 && value==reinterpret_cast<U>(devices_006a5c7c))devices_006a5c7c=reinterpret_cast<FileDevice*>(address(0x1000));
 if(scenario==46 && value==address(0x3200))free_operation_arena_006a5c54=reinterpret_cast<void*>(address(0x3300));
 return 1;
}
U __cdecl file_event_signal_0055fb30(void* eventHandle){
 const U value=reinterpret_cast<U>(eventHandle);event(4,value);activeDevice=0;sleeps=0;
 for(U base=0;base<=0x1000;base+=0x1000)for(U i=0;i<32;++i){const U p=base+i*0x70;if(at(p)&&at(p+0x5c)==value && !activeDevice)activeDevice=address(p);}
 if(!activeDevice){++failures;return 0;}
 if(scenario!=34 && scenario!=37)cell(activeDevice)=0;
 if(scenario==35)devices_006a5c7c=reinterpret_cast<FileDevice*>(address(0x1000));
 if(scenario==40)cell(activeDevice+0x5c)=0xfedcba98;
 return 0x11223344;
}
U __cdecl file_sleep_0055f740(U milliseconds){
 event(5,milliseconds);if(!activeDevice || milliseconds || ++sleeps>3){++failures;return 0;}
 if(scenario==37)devices_006a5c7c=reinterpret_cast<FileDevice*>(address(0x1000));
 if(sleeps==(scenario==34?3u:2u))cell(activeDevice)=0;
 return 0xdeadbeef;
}
U __cdecl file_close_event_0055fc10(void* handle){
 event(6,reinterpret_cast<U>(handle));
 if(scenario==36)devices_006a5c7c=reinterpret_cast<FileDevice*>(address(0x1000));
 if(scenario==41)cell(activeDevice+0x64)=0x87654321;
 return 1;
}
U __cdecl file_signal_close_0055fc80(void* handle){event(7,reinterpret_cast<U>(handle));return 1;}
void __cdecl network_worker_queue_dispose_005806c0(IoList* queue){
 event(8,reinterpret_cast<U>(queue));queue->count=0;queue->head=nullptr;queue->tail=nullptr;
 if(scenario==39 && queue==&free_auxiliary_006a5c38)application_pool_lock_006a5c78=reinterpret_cast<void*>(0x81234567);
}
void __cdecl heap_lock_destroy_005322d0(void* lock){event(9,reinterpret_cast<U>(lock));}
}
struct Globals{porsche::FileDevice* devices;void* arenaBase;void* lock;U shutdown;porsche::IoList freeOperations,freeAuxiliary;};
static Globals globals(){return {porsche::devices_006a5c7c,porsche::free_operation_arena_006a5c54,porsche::application_pool_lock_006a5c78,porsche::file_shutdown_006a5c80,porsche::free_operations_006a5c58,porsche::free_auxiliary_006a5c38};}
static void restore(const Globals& q){porsche::devices_006a5c7c=q.devices;porsche::free_operation_arena_006a5c54=q.arenaBase;porsche::application_pool_lock_006a5c78=q.lock;porsche::file_shutdown_006a5c80=q.shutdown;porsche::free_operations_006a5c58=q.freeOperations;porsche::free_auxiliary_006a5c38=q.freeAuxiliary;}
static void initialize(U test){
 scenario=test;eventCount=0;popIndex=0;popCount=test%3;activeDevice=0;sleeps=0;
 for(U i=0;i<sizeof(arena);++i)arena[i]=static_cast<unsigned char>(0xa5+i*13);
 for(U base=0;base<=0x1000;base+=0x1000)for(U i=0;i<32;++i){U p=base+i*0x70;at(p)=0;at(p+0x5c)=0x81000000+base+i;at(p+0x64)=0x82000000+base+i;}
 if(test>=2 && test<34)at((test-2)*0x70)=0x80000000;
 if(test>=34)at(0)=0x80000000;
 if(test==34)at(31*0x70)=1;
 if(test==35 || test==36 || test==37 || test==44)at(0x1000+0x70)=1;
 if(test==47)for(U i=0;i<32;++i)at(i*0x70)=0x80000000;
 if(test==43){at(0x5c)=0;at(0x64)=0;}
 for(U i=0;i<2;++i)at(0x3000+i*0x40+0xc)=0xdead1000+i;
 porsche::devices_006a5c7c=test?reinterpret_cast<porsche::FileDevice*>(address(0)):nullptr;
 porsche::free_operation_arena_006a5c54=reinterpret_cast<void*>(address(0x3200));porsche::application_pool_lock_006a5c78=reinterpret_cast<void*>(0x83000000);porsche::file_shutdown_006a5c80=0xabcdef01;
 porsche::free_operations_006a5c58={};porsche::free_auxiliary_006a5c38={};porsche::free_auxiliary_006a5c38.count=static_cast<std::int32_t>(popCount);
 porsche::free_auxiliary_006a5c38.head=popCount?reinterpret_cast<porsche::IoNode*>(address(0x3000)):nullptr;
}
extern "C" __declspec(naked) void __cdecl capture305(void*,U*){
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
 case 0x6a5c38:return reinterpret_cast<U>(&free_auxiliary_006a5c38);case 0x6a5c58:return reinterpret_cast<U>(&free_operations_006a5c58);
 case 0x6a5c54:return reinterpret_cast<U>(&free_operation_arena_006a5c54);case 0x6a5c78:return reinterpret_cast<U>(&application_pool_lock_006a5c78);
 case 0x6a5c7c:return reinterpret_cast<U>(&devices_006a5c7c);case 0x6a5c80:return reinterpret_cast<U>(&file_shutdown_006a5c80);
 case 0x580790:return reinterpret_cast<U>(&io_pop_00580790);case 0x592290:return reinterpret_cast<U>(&file_physical_close_00592290);case 0x56e640:return reinterpret_cast<U>(&file_object_free_0056e640);
 case 0x55fb30:return reinterpret_cast<U>(&file_event_signal_0055fb30);case 0x55f740:return reinterpret_cast<U>(&file_sleep_0055f740);case 0x55fc10:return reinterpret_cast<U>(&file_close_event_0055fc10);
 case 0x55fc80:return reinterpret_cast<U>(&file_signal_close_0055fc80);case 0x5806c0:return reinterpret_cast<U>(&network_worker_queue_dispose_005806c0);case 0x5322d0:return reinterpret_cast<U>(&heap_lock_destroy_005322d0);
 default:++failures;return 0;
}}
extern "C" void __cdecl entry(){
 auto* reference=static_cast<unsigned char*>(VirtualAlloc(nullptr,sizeof(original),0x3000,0x40));if(!reference)ExitProcess(2);
 duplicate305(reference,original,sizeof(original));for(const auto& relocation:relocations){U value=target(relocation.target);if(relocation.next)value-=reinterpret_cast<U>(reference+relocation.next);duplicate305(reference+relocation.offset,&value,4);}
 for(U test=0;test<48;++test){
  initialize(test);Globals initialGlobals=globals();duplicate305(initial,arena,sizeof(arena));U originalAbi[5]{},actualAbi[5]{};
  capture305(reference,originalAbi);Globals expectedGlobals=globals();duplicate305(expected,arena,sizeof(arena));U expectedCount=eventCount;duplicate305(wanted,events,sizeof(events));
  restore(initialGlobals);duplicate305(arena,initial,sizeof(arena));eventCount=0;popIndex=0;activeDevice=0;sleeps=0;
  capture305(reinterpret_cast<void*>(&porsche::application_pool_shutdown_005678f0),actualAbi);Globals actualGlobals=globals();
  if(differ305(arena,expected,sizeof(arena))||differ305(&actualGlobals,&expectedGlobals,sizeof(Globals))||eventCount!=expectedCount||differ305(events,wanted,eventCount*4))++failures;
  for(U i=0;i<2;++i){U* abi=i?actualAbi:originalAbi;if(abi[0]||abi[1]!=0x12345678||abi[2]!=0x76543210||abi[3]!=0x89abcdef||abi[4])++failures;}
  ++cases;
 }
 const char ok[]="{\"cases\":48,\"failures\":0}\n";U written=0;if(!failures&&cases==48)WriteFile(GetStdHandle(0xfffffff5u),ok,sizeof(ok)-1,&written,nullptr);
 ExitProcess(failures||cases!=48?1:0);
}
