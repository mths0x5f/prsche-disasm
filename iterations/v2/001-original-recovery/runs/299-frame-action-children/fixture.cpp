#include "../297-frame-action/action_297.hpp"
#include <initializer_list>
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(unsigned);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,unsigned,unsigned*,void*);
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
using U=std::uint32_t;
static unsigned char original[]={
#include "original-body.inc"
};
alignas(16) static unsigned char arena[4096],initial[4096],expected[4096];
static U events[128],wanted[128],eventCount,scenario,failures,cases,groupAddress;
static void duplicate299(void* destination,const void* source,U size) {
 auto* d=static_cast<volatile unsigned char*>(destination);auto* s=static_cast<const volatile unsigned char*>(source);
 while(size--) *d++=*s++;
}
static int differ299(const void* left,const void* right,U size) {
 auto* a=static_cast<const volatile unsigned char*>(left);auto* b=static_cast<const volatile unsigned char*>(right);
 while(size--) if(*a++!=*b++) return 1;return 0;
}
static U address(U n){return reinterpret_cast<U>(arena+n);}
static U& cell(U p){return *reinterpret_cast<U*>(p);}
static U& at(U n){return cell(address(n));}
static void event(U kind,U object,U arg){if(eventCount+3>128){++failures;return;}events[eventCount++]=kind;events[eventCount++]=object;events[eventCount++]=arg;}
static void mutate299(){
 if(scenario==1)cell(groupAddress+0x34)=address(1024);
 if(scenario==2)at(0xc)=address(512);
 if(scenario==3)cell(groupAddress+0x14)=1;
 if(scenario==4)cell(groupAddress+0x14)=3;
 if(scenario==5)cell(groupAddress+0x14)=0;
 if(scenario==6){cell(groupAddress+0x34)=address(1024);at(0xc)=address(512);}
 if(scenario==7)at(768+0x18)=address(1728);
}
extern "C" U __fastcall destroy299(void* object,void*,U arg){event(1,reinterpret_cast<U>(object),arg);mutate299();return 0xdeadbeef;}
extern "C" void __fastcall update299(void* object,void*){event(2,reinterpret_cast<U>(object),0);mutate299();}
extern "C" __declspec(naked) void __cdecl capture299(void*,void*,U,U*){
 __asm {
  push ebp
  mov ebp,esp
  push ebx
  push esi
  push edi
  mov ebx,12345678h
  mov esi,76543210h
  mov edi,89abcdefh
  mov ecx,[ebp+12]
  push dword ptr [ebp+16]
  cld
  call dword ptr [ebp+8]
  mov edx,[ebp+20]
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
static void initialize(U mode,U index,U count,U variant){
 for(U i=0;i<sizeof(arena);++i)arena[i]=static_cast<unsigned char>(0xa5+i*13);
 scenario=mode;eventCount=0;at(0xc)=address(256);groupAddress=address(256+index*0x38);
 for(U table:{256u,512u})for(U j=0;j<3;++j){at(table+j*0x38+0x14)=count;at(table+j*0x38+0x34)=address(768);}
 for(U table:{768u,1024u})for(U j=0;j<3;++j){
  U record=table+j*0x18,object=1408+j*64;
  at(record)=address(object);at(record+0x10)=variant%2;
  at(object)=address(2048);arena[object+4]=static_cast<unsigned char>((variant/2)%3==0?0:((variant/2)%3==1?1:255));
 }
 at(1728)=address(2048);arena[1732]=0;
 at(2048)=reinterpret_cast<U>(&destroy299);at(2048+0x1c)=reinterpret_cast<U>(&update299);
 if(mode==8){ // Mixed deletion/update/flag paths in one list.
  arena[1408+4]=0;at(768+0x10)=0;arena[1472+4]=0;at(768+0x18+0x10)=1;arena[1536+4]=255;
 }
}
extern "C" void __cdecl entry(){
 auto* reference=static_cast<unsigned char*>(VirtualAlloc(nullptr,sizeof(original),0x3000,0x40));if(!reference)ExitProcess(2);
 duplicate299(reference,original,sizeof(original));
 auto member=&porsche::FrameActionBoundary_297::update_00476710;void* game=nullptr;static_assert(sizeof(member)==4);duplicate299(&game,&member,4);
 for(U mode=0;mode<9;++mode)for(U index=0;index<3;++index)for(U count=0;count<4;++count)for(U variant=0;variant<6;++variant){
  initialize(mode,index,count,variant);duplicate299(initial,arena,sizeof(arena));U actualAbi[5]{},originalAbi[5]{};
  capture299(reference,arena,index,originalAbi);duplicate299(expected,arena,sizeof(arena));
  U expectedCount=eventCount;duplicate299(wanted,events,sizeof(events));duplicate299(arena,initial,sizeof(arena));eventCount=0;
  capture299(game,arena,index,actualAbi);
  if(differ299(arena,expected,sizeof(arena))||eventCount!=expectedCount||differ299(events,wanted,eventCount*4))++failures;
  for(U* abi:{actualAbi,originalAbi})if(abi[0]||abi[1]!=0x12345678||abi[2]!=0x76543210||abi[3]!=0x89abcdef||abi[4])++failures;
  ++cases;
 }
 const char ok[]="{\"cases\":648,\"failures\":0}\n";U written=0;
 if(!failures&&cases==648)WriteFile(GetStdHandle(0xfffffff5u),ok,sizeof(ok)-1,&written,nullptr);
 ExitProcess(failures||cases!=648?1:0);
}
