#include "porsche/network_vtables.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/formatter_bootstrap.hpp"
#include <windows.h>
#include <array>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <vector>
namespace porsche {
const unsigned char network_rtti_005c5190[1]={}; // Private link fixtures only.
const unsigned char network_rtti_005c51d8[1]={};
const unsigned char network_rtti_005c5228[1]={};
namespace {
using U=std::uint32_t;constexpr U B=0x23000000,S=B,P=B+0x1000,T=B+0x2000,M=B+0x3000,M2=B+0x3400,L=B+0x4000,N=B+0x5000,N2=B+0x5200,K=B+0x5400,SRC=B+0x8000,OUTPUT_CELL=B+0x9000,C=B+0x9100;
std::array<U,11>a{};std::vector<std::vector<U>>events;U op,locks=0;bool fatal=false;
void* ptr(U x){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(x));}
U raw(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U p){U v;std::memcpy(&v,ptr(p),4);return v;}
void put(U p,U v){std::memcpy(ptr(p),&v,4);}
U byte(U p){return *static_cast<unsigned char*>(ptr(p));}
void pb(U p,U v){*static_cast<unsigned char*>(ptr(p))=static_cast<unsigned char>(v);}
void event(U va,std::initializer_list<U> values={}){
 std::vector<U>row{va};row.insert(row.end(),values);for(U x:{get(P+0xb4),byte(P+0xbe),byte(S+0x10),byte(S+0x16),get(S+8),get(M+0xb0),get(M2+0xb0),get(C),get(L),get(L+4)})row.push_back(x);events.push_back(row);
}
void init(){
 std::memset(ptr(B),0xcc,0x10000);events.clear();locks=0;fatal=false;
 put(S+4,T);put(S+8,0x26000001);put(S+0xc,L);pb(S+0x10,a[3]);pb(S+0x16,a[4]);put(S+0x18,L+0x100);
 put(P,P+0x400);put(P+0xb4,a[2]);pb(P+0xbe,a[3]);put(P+0xc4,L);put(P+0x3fc+0xdc,a[5]);
 for(U x:{L,L+0x100}){put(x,x);put(x+4,x);}
 if(a[1]){put(L,L+0x200);put(L+4,L+0x200);put(L+0x200,L);put(L+0x204,L);put(L+0x208,17);for(U i=0;i<240;++i)pb(L+0x20c+i,0x50+i);}
 for(U m:{M,M2}){put(m+0x28,0x26000002+(m==M2));put(m+0xb0,a[8]?0:N);put(m+0x38,K);}
 put(N+4,N2);put(N2+4,0);put(K+4,0);put(C,M);
 for(U i=0;i<244;++i)pb(SRC+i,0x21+i);
 pb(T+0x2c8,a[4]);put(T+0x254+0x28,a[5]);put(T+0x254+0x34,a[6]);
 put(P+0x3fc+0x68+0x28,a[5]);put(P+0x3fc+0x68+0x34,a[6]);
 put(T+0x28,a[5]);put(T+0x34,a[6]);if(!a[9])put(P,0);
}
U boundary(U va,void* transport,U count,const U* desc,U route){
 std::vector<U>row{va,raw(transport),count,route};for(U i=0;i<count;++i){const U* d=desc+i*3;row.insert(row.end(),d,d+3);if((d[1]&0xffffffu)<=240&&d[2]){auto* p=static_cast<const unsigned char*>(ptr(d[2]));row.insert(row.end(),p,p+(d[1]&0xffffffu));}}events.push_back(row);event(0x24000000);
 if(a[7]&16){put(P+0xb4,0);pb(P+0xbe,7);}
 if(a[7]&32){put(S+8,0x26001000);put(L,N);}
 return a[10];
}
struct Fatal {};
}
void* __cdecl application_context_heap_state_005e4fe8(){return ptr(get(C));}
void __cdecl heap_enter_005322b0(void* h){
 event(0x5322b0,{raw(h)});++locks;const U captured=get(C);
 if(a[7]&1)put(C,captured==M?M2:M);
 if(a[7]&2)put(captured+0x28,0x26002000+locks);
 if(a[7]&4){pb(S+0x16,0);pb(P+0xbe,1);}
}
void __cdecl heap_leave_005322c0(void* h){event(0x5322c0,{raw(h)});if(a[7]&8)put(P+0xb4,0xffffffffu);}
void __cdecl application_context_new_head_0059eeb0(U kind,U slot){event(0x59eeb0,{kind,slot});put(M+0xb0,N);put(M2+0xb0,N);put(M+0x38,K);put(M2+0x38,K);}
void __cdecl heap_copy_dispatch_005323e0(void* d,const void* s,U n){event(0x5323e0,{raw(s),n});std::memcpy(d,s,n);}
U __cdecl network_transport_direct_00587000(void* t,U n,const U* d){return boundary(0x587000,t,n,d,0);}
U __cdecl network_transport_routed_005870b0(void* t,U n,const U* d,U r){return boundary(0x5870b0,t,n,d,r);}
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int n){event(0x5a2e22,{static_cast<U>(n)});fatal=true;throw Fatal{};}
int main(){
 if(VirtualAlloc(ptr(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;
 if(network_vtable_owner_005b4968.rtti!=network_rtti_005c5190||network_vtable_owner_005b4970.rtti!=network_rtti_005c51d8||network_vtable_owner_005b4978.rtti!=network_rtti_005c5228)return 3;
 std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);in>>op;for(auto&v:a)in>>v;init();U result=0;
  const U outputs[]={OUTPUT_CELL,OUTPUT_CELL+4,L,L+4,L+0x200,L+0x204,N+4,M+0xb0};
  const U sources[]={SRC,N+4,N+12,N+8};
  if(op<3){const NetworkSendTable* owner=op==0?&network_vtable_owner_005b4968:op==1?&network_vtable_owner_005b4978:&network_vtable_owner_005b4970;put(S,raw(&owner->send));}
  try{switch(op){
   case 0:case 1:case 2:(*static_cast<const NetworkSendSlot*>(ptr(get(S))))(ptr(S),nullptr,P,static_cast<const std::uint8_t*>(ptr(SRC)),a[0]);break;
   case 3:result=raw(network_packet_insert_0048a920(ptr(S),nullptr,static_cast<U*>(ptr(outputs[a[9]])),L,ptr(sources[a[0]<4?a[0]:0])));break;
   case 4:result=raw(network_packet_unlink_0048a8d0(ptr(S),nullptr,static_cast<U*>(ptr(outputs[a[9]])),L+0x200));break;
   case 5:result=network_member_packet_0048a3d0(ptr(P),nullptr,static_cast<const std::uint8_t*>(ptr(SRC)),a[0],a[4]?ptr(T):nullptr);break;
   case 6:result=network_transport_send_0055d4a0(ptr(T),static_cast<const std::uint8_t*>(ptr(SRC)),a[0]);break;
   case 7:result=raw(network_transport_owner_0055c260(ptr(a[0])));break;
   case 8:result=network_transport_member_send_0055c270(ptr(T),ptr(P+0x400),static_cast<const std::uint8_t*>(ptr(SRC)),a[0]);break;
   case 9:result=network_transport_packet_00560420(ptr(T),static_cast<const std::uint8_t*>(ptr(SRC)),a[0]);break;
   case 10:{U desc[3]={a[0]&0xff000000u,a[0]&0xffffffu,SRC};result=network_transport_dispatch_00586fb0(a[4]?ptr(T):nullptr,1,desc);break;}
  }}catch(Fatal&){}
  if(op<3)put(S,0xcccccccc); // Native vptr corresponds to the original slot address.
  // Stack residue copied beyond initialized packet prefix is intentionally
  // unspecified. Exclude those bytes identically in both executors.
  if(op==0||op==1||op==5)for(U n:{N,N2})for(U i=4+a[0];i<244;++i)pb(n+8+i,0);
  std::cout<<"{\"return\":"<<result<<",\"fatal\":"<<(fatal?"true":"false")<<",\"trace\":[";
  for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}
  std::cout<<"],\"state\":[";for(U i=0;i<0x10000;i+=4){if(i)std::cout<<',';std::cout<<get(B+i);}std::cout<<"]}\n";
 }
 VirtualFree(ptr(B),0,MEM_RELEASE);return 0;
}
}
int main(){return porsche::main();}
