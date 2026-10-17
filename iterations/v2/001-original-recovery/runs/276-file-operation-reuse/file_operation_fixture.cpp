#define PORSCHE_DEFINE_SHARED_RUNTIME_GLOBALS_FIXTURE
#include "porsche/files.hpp"
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
std::uint32_t __cdecl FUN_00568200(std::int32_t);
std::int32_t __cdecl FUN_005682a0(std::uint32_t,std::uint8_t,std::uint32_t,std::uint32_t);
using U=std::uint32_t;
static constexpr U DEV=0x03001000u,OP=0x03002000u,CONTEXT=0x03003000u,EVENT=0x03004000u;
struct Ev {U kind,a,b;};
struct Case {const char* name;U queue,index,serial,initialized,op_id,pop,eax,line,event_count;const char *op_before,*dev_before,*op_after,*dev_after;Ev events[4];};
static const Case cases[]={
{"queue_high_id",1,1,3,1,3735928545,1,3735928545,0,2,"cccccccce1beaddecccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","01000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003cccccccccccccccc03000000cccccccc","cccccccce1beaddecccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","01000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003cccccccccccccccc03000000cccccccc",{{2,50335892,50339840},{3,50348032,0},{0,0,0},{0,0,0}}},
{"allocate_wrap",0,1,16777215,1,3435973836,1,50339840,0,3,"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","01000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003ccccccccccccccccffffff00cccccccc","cccccccce1ffff1f07000000c0cccccc00d7cccc00000000000000000030000300000000000000000000000000000000","01000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003cccccccccccccccc01000000cccccccc",{{1,0,0},{5,50335892,0},{6,50335892,305441741},{0,0,0}}},
{"allocate_start",0,0,2,0,3435973836,1,50339840,0,4,"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","00000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003cccccccccccccccc02000000cccccccc","cccccccc4000000007000000c0cccccc00d7cccc00000000000000000030000300000000000000000000000000000000","01000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003cccccccccccccccc03000000cccccccc",{{1,0,0},{4,0,0},{5,50335780,0},{6,50335780,305441741}}},
{"allocate_empty",0,1,9,1,3435973836,0,0,209,2,"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","01000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003cccccccccccccccc09000000cccccccc","cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","01000000cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc00400003cccccccccccccccc09000000cccccccc",{{1,0,0},{7,0,0},{0,0,0},{0,0,0}}}
};
static U fail=0,events_count=0,pop_available=0,current_index=0;
static Ev events[8];
static unsigned char* arena=nullptr;
static U digit(char c){return c>='0'&&c<='9'?U(c-'0'):c>='a'&&c<='f'?U(c-'a'+10):99u;}
static void decode(unsigned char* p,const char* s,U n){for(U i=0;i<n;++i)p[i]=static_cast<unsigned char>((digit(s[i*2])<<4)|digit(s[i*2+1]));}
static void compare(const unsigned char* p,const char* s,U n){for(U i=0;i<n;++i)if(p[i]!=((digit(s[i*2])<<4)|digit(s[i*2+1])))++fail;}
static bool equal(const char* a,const char* b){while(*a&&*b){if(*a++!=*b++)return false;}return *a==*b;}
static void record(U k,U a=0,U b=0){if(events_count>=8){++fail;return;}events[events_count++]={k,a,b};}
namespace porsche {
FileDevice* devices_006a5c7c=nullptr;
IoList free_operations_006a5c58{};
void (__cdecl* diagnostic_handler_005debf0)(const char*)=nullptr;
IoNode* __cdecl io_pop_00580790(IoList* list){if(list!=&free_operations_006a5c58)++fail;record(1);return pop_available?reinterpret_cast<IoNode*>(OP):nullptr;}
void __cdecl io_sorted_00580850(IoList* list,IoNode* node){if(list!=&devices_006a5c7c[current_index].queued||reinterpret_cast<U>(node)!=OP)++fail;record(2,reinterpret_cast<U>(list),reinterpret_cast<U>(node));}
U __cdecl file_event_signal_0055fb30(void* event){record(3,reinterpret_cast<U>(event));return 1;}
void __cdecl file_start_device_00568390(U index){record(4,index);devices_006a5c7c[index].initialized=1;}
U __cdecl io_lock_00580ea0(IoList* list){record(5,reinterpret_cast<U>(list));return 0x1234abcdu;}
void __cdecl io_unlock_00580ec0(IoList* list,U token){record(6,reinterpret_cast<U>(list),token);}
}
static void diagnostic(const char* message){if(!equal(message,"FILE_allocateop - NO FREE OPS LEFT TO ALLOCATE.\n"))++fail;record(7);}
extern "C" void __cdecl entry(){
 arena=static_cast<unsigned char*>(VirtualAlloc(reinterpret_cast<void*>(0x03000000u),0x10000u,0x3000u,4u));
 if(reinterpret_cast<U>(arena)!=0x03000000u)ExitProcess(101);
 porsche::devices_006a5c7c=reinterpret_cast<porsche::FileDevice*>(DEV);
 porsche::diagnostic_handler_005debf0=diagnostic;
 for(U c=0;c<sizeof(cases)/sizeof(cases[0]);++c)for(U mode=0;mode<2;++mode){
  const Case& q=cases[c];current_index=q.index;pop_available=q.pop;events_count=0;
  unsigned char* op=arena+0x2000;unsigned char* dev=arena+0x1000+q.index*0x70;
  for(U i=0;i<0x70*2;++i)arena[0x1000+i]=0xcc;
  decode(op,q.op_before,48);decode(dev,q.dev_before,0x70);
  porsche::shared_runtime_word_005deb74=0;porsche::diagnostic_line_005deb78=0;
  U result;
  if(q.queue)result=mode?FUN_00568200(static_cast<std::int32_t>(OP)):porsche::operation_queue_00568200(reinterpret_cast<porsche::FileOperation*>(OP));
  else result=mode?static_cast<U>(FUN_005682a0(7,0xd7u,CONTEXT,q.index)):reinterpret_cast<U>(porsche::operation_allocate_005682a0(7,0xd7u,reinterpret_cast<void*>(CONTEXT),q.index));
  if(result!=q.eax||porsche::diagnostic_line_005deb78!=q.line)++fail;
  if(q.line){if(!equal(porsche::diagnostic_file_005deb74(),"\\real\\pc\\nfile.c"))++fail;}
  else if(porsche::diagnostic_file_005deb74()!=nullptr)++fail;
  compare(op,q.op_after,48);compare(dev,q.dev_after,0x70);
  if(events_count!=q.event_count)++fail;
  for(U i=0;i<q.event_count&&i<events_count;++i)if(events[i].kind!=q.events[i].kind||events[i].a!=q.events[i].a||events[i].b!=q.events[i].b)++fail;
 }
 ExitProcess(fail?1:0);
}
