#include "porsche/network_groups.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/startup_services.hpp"
#include "porsche/heap.hpp"
#include <windows.h>
#include <array>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
namespace porsche {
char network_group_text_005e8e50[256]{}; // Private fixture, not production storage.
void* startup_network_00628c70=nullptr;
namespace {
using U=std::uint32_t;
constexpr U B=0x23000000,G=B,P=B+0x1000,S=B+0x2000,M=B+0x3000,M2=B+0x3200,L=B+0x4000,SENDER=B+0x6000,SENDER2=B+0x6020,VT=B+0x6040,VT2=B+0x6050,C=B+0x6100;
std::array<U,12>a{};U operation=0,send_count=0,lock_count=0;std::vector<std::vector<U>> events;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U v){U n;std::memcpy(&n,ptr(v),4);return n;}
void put(U v,U n){std::memcpy(ptr(v),&n,4);}
U byte(U v){return *static_cast<std::uint8_t*>(ptr(v));}
void pb(U v,U n){*static_cast<std::uint8_t*>(ptr(v))=static_cast<std::uint8_t>(n);}
U head(U g){return L+g*0x200;}
U node(U g,U i){return head(g)+0x20+i*0x30;}
U peer(U i){return i%2?P+0x200+i*0x100:P;}
void event(U id,std::initializer_list<U> values={}){
 std::vector<U> row{id};row.insert(row.end(),values);for(U v:{get(P+0xac),get(P+0xa4),get(G+0xac),byte(G+0xcc0),byte(G+0xcc2),byte(G+0xcc3),get(M+0x38),get(M+0xb0),get(M2+0x38),get(M2+0xb0),get(C)})row.push_back(v);events.push_back(row);
}
void on_send(U id,void* sender,U dest,const std::uint8_t* packet,U size){
 std::vector<U> row{id,raw(sender),dest,size};row.insert(row.end(),packet,packet+size);events.push_back(row);event(0x24000020);++send_count;
 if(send_count==1){
  if(a[6]&1)put(P+0xac,0x89abcdef);
  if(a[6]&2){pb(G+0xcc0,0xa5);pb(G+0xcc2,5);}
  if(a[6]&4)put(node(0,0),head(0));
  if(a[6]&8)put(G+0x64,SENDER2);
  if(a[6]&16)put(node(1,0),head(1));
  if(a[6]&256)put(G+0xac,0x76543210);
 }
}
void __fastcall send1(void* s,void*,U d,const std::uint8_t* p,U n){on_send(0x24000000,s,d,p,n);}
void __fastcall send2(void* s,void*,U d,const std::uint8_t* p,U n){on_send(0x24000010,s,d,p,n);}
void list(U g,U count){
 U h=head(g);put(h,count?node(g,0):h);put(h+4,count?node(g,count-1):h);
 for(U i=0;i<count;++i){U n=node(g,i);put(n,i+1<count?node(g,i+1):h);put(n+4,i?node(g,i-1):h);put(n+8,g==0?peer(i):g==1?0x12340000+i:3+i);
  for(U j=0;j<16;++j)pb(n+12+j,0x40+g+i+j);
 }
}
void initialize(){
 std::memset(ptr(B),0xcc,0x10000);events.clear();send_count=lock_count=0;
 for(U g=0;g<9;++g)list(g,a[0]);
 put(G+0x60,S);put(G+0x64,SENDER);put(G+0x68,0);put(G+0x70,0x89abcdef);put(G+0xa8,head(0));put(G+0xac,a[8]);
 for(U i=0;i<52;++i)pb(G+0x74+i,0x21+i);pb(G+0xcc0,a[3]);pb(G+0xcc2,a[4]);pb(G+0xcc3,a[5]);put(S+0x164,head(1));
 for(U i=0;i<6;++i){U p=peer(i);put(p,a[7]);put(p+0xa4,G);put(p+0xac,0x12340000+i);put(p+0xc8,head(2+i));}
 put(P+0xac,a[1]);put(P+0xc8,head(2));
 put(SENDER,VT);put(SENDER2,VT2);put(VT,raw(reinterpret_cast<void*>(&send1)));put(VT2,raw(reinterpret_cast<void*>(&send2)));put(C,M);
 for(U m:{M,M2}){put(m+0x28,m==M?0x27000000:0x27000001);put(m+0x38,0x26000000);put(m+0xb0,0x26001000);}
 std::memset(network_group_text_005e8e50,0,sizeof(network_group_text_005e8e50));for(U i=0;i<a[9];++i)network_group_text_005e8e50[i]=static_cast<char>(0x41+i%26);
}
}
void* __cdecl application_context_heap_state_005e4fe8(){return ptr(get(C));}
void __cdecl heap_enter_005322b0(void* lock){
 U handle=raw(lock);event(0x5322b0,{handle});++lock_count;U captured=get(C);
 if(a[6]&32)put(C,captured==M?M2:M);
 if(a[6]&64){put(captured+0x28,0x27001000+lock_count);put(captured+0x38,0x26010000+lock_count);put(captured+0xb0,0x26011000+lock_count);}
}
void __cdecl heap_leave_005322c0(void* lock){event(0x5322c0,{raw(lock)});}
void __cdecl heap_fill_0053c290(void* p,U pattern,U size){event(0x53c290,{pattern,size});std::memset(p,0,size);if(a[6]&128)put(G+0xac,0xabcdef01);}
void __cdecl heap_copy_dispatch_005323e0(void* d,const void* s,U size){event(0x5323e0,{raw(s),size});std::memcpy(d,s,size);if(a[6]&512)put(G+0x64,SENDER2);}
U __cdecl application_release_0059f050(void*){std::abort();}
U __cdecl free_00531f90(void*){std::abort();}
void __fastcall network_services_detach_0048c430(void*,void*){std::abort();}
void __fastcall network_services_destroy_004904d0(void*,void*){std::abort();}
U* __fastcall network_services_begin_004c3150(void*,void*,U*){std::abort();}
}
int main(){using namespace porsche;if(!VirtualAlloc(reinterpret_cast<void*>(0x23000000),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 2;
 std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);in>>operation;for(auto&v:a)in>>v;initialize();
 switch(operation){case 0:network_member_group_remove_0048bda0(ptr(G),nullptr,ptr(P));break;
 case 1:network_group_acknowledge_0048c220(ptr(G),nullptr,ptr(P),a[2],0x11223344);break;
 case 2:network_group_clear_member_messages_0048c300(ptr(P+0xc8),nullptr);break;
 case 3:network_group_publish_00490b70(ptr(S),nullptr,ptr(G));break;
 case 4:network_group_send_member_messages_0048a390(ptr(P),nullptr,ptr(G+0x64),P);break;
 case 5:network_group_send_state_0048baa0(ptr(G),nullptr,P);break;default:return 3;}
 std::vector<U> state;for(auto range:std::vector<std::pair<U,U>>{{G,0xd00},{P,0x1000},{S,0x200},{M,0x400},{L,0x1200},{C,4}})for(U i=0;i<range.second;i+=4)state.push_back(get(range.first+i));
 std::cout<<"{\"trace\":[";for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}
 std::cout<<"],\"state\":[";for(std::size_t i=0;i<state.size();++i){if(i)std::cout<<',';std::cout<<state[i];}std::cout<<"]}\n";
 }
}
