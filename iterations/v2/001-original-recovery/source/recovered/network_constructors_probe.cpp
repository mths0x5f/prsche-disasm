#include "porsche/network_constructors.hpp"
#include "porsche/network_groups.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/formatter_bootstrap.hpp"
#include "porsche/formatter_entry.hpp"
#include <windows.h>
#include <array>
#include <cstring>
#include <cstdlib>
#include <cstdarg>
#include <cstdio>
#include <iostream>
#include <sstream>
#include <vector>
namespace porsche {
const unsigned char network_connection_identity_005b4980[]={0x81,0x6b,0xd4,0x5c,0xe4,0xec,0xd3,0x11,0x9b,0x6a,0,0x90,0x27,0x24,0xab,0x1e};
char network_group_text_005e8e50[]="";
namespace {
using U=std::uint32_t;constexpr U B=0x23000000,S=B,C=B+0x1000,W=B+0x2000,W2=B+0x2400,M=B+0x3000,M2=B+0x3400,N=B+0x5000,K=B+0x5400,V=B+0x6000,T=B+0x8000,D=B+0x9000;
std::array<U,12>a{};U op,manager,calls;std::vector<std::vector<U>>events;
void* ptr(U p){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(p));} U raw(const void*p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U p){U v;std::memcpy(&v,ptr(p),4);return v;}void put(U p,U v){std::memcpy(ptr(p),&v,4);}void byte(U p,U v){*static_cast<unsigned char*>(ptr(p))=static_cast<unsigned char>(v);}
U norm(U p){if(p==raw(&network_vtable_owner_005b4968.send))return 0x5b4968;if(p==raw(&network_vtable_owner_005b4970.send))return 0x5b4970;if(p==raw(&network_vtable_owner_005b4978.send))return 0x5b4978;return p;}
U pointer(const void*p){U q=raw(p);return q>=B&&q<B+0x10000?q:0;}
void event(U id,std::initializer_list<U>args={}){std::vector<U>r{id};r.insert(r.end(),args);for(U p:{S,S+4,S+0xc,S+0x10,S+0x14,C,C+4,M+0x28,M+0x38,M+0xb0,M2+0x38,M2+0xb0})r.push_back(norm(get(p)));r.push_back(manager);events.push_back(r);}
void bytes_event(U id,const void*p,U n){std::vector<U>r{id};auto*s=static_cast<const unsigned char*>(p);r.insert(r.end(),s,s+n);events.push_back(r);}
void text_event(U id,const char*p){bytes_event(id,p,static_cast<U>(std::strlen(p)+1));}
void __fastcall dummy(void*,void*,U,const std::uint8_t*,U){std::abort();}
U __cdecl compare(U state,const void*first,const void*second){event(0x24000000,{state});bytes_event(1,first,20);bytes_event(2,second,20);return a[10];}
U __cdecl parse(U state,U text,U port,U out){event(0x24000010,{state,pointer(ptr(text)),port,pointer(ptr(out))});text_event(3,static_cast<char*>(ptr(text)));for(U i=0;i<5;++i)put(out+i*4,0x11110000+i+(a[10]?0:1));if(a[6]&16)put(S+4,W);return 0x87654321;}
U __cdecl address(U state,U first,U second,U third){event(0x24000020,{state,pointer(ptr(first)),pointer(ptr(second)),pointer(ptr(third))});put(first,0x99887766);std::strcpy(static_cast<char*>(ptr(second)),"192.168.0.42");put(third,30000+a[10]);if(a[6]&8)put(S+4,W2);return 0xabcdef01;}
void init(){std::memset(ptr(B),0xcc,0x10000);events.clear();manager=M;calls=0;
 for(U base:{M,M2}){put(base+0x28,base+0x80);put(base+0x38,a[5]?0:K);put(base+0xb0,a[5]?0:N);}
 put(N+4,N+0x20);put(K+4,K+0x20);put(N+0x24,0);put(K+0x24,0);
 for(U w:{W,W2}){put(w+0xbc,a[0]);put(w+0x14,V);put(w+0x18,0x87650000+(w-W));}
 put(V+0x40,raw(reinterpret_cast<void*>(&compare)));put(V+0x38,a[11]&1?raw(reinterpret_cast<void*>(&parse)):0);put(V+0x3c,a[11]&2?raw(reinterpret_cast<void*>(&address)):0);
 put(S+4,W);put(S+0xc,a[8]?C:0);put(S+0x10,D+0x200);put(S+0x1c,22);put(S+0x20,11);put(S+0x24,33);byte(S+0x14,a[7]&1);byte(S+0x15,(a[7]>>1)&1);std::strcpy(static_cast<char*>(ptr(S+0x28)),"host-key");std::strcpy(static_cast<char*>(ptr(S+0x128)),"host.example");
 const char*values[]={"left","right","suffix","extra","server.example"};for(U i=0;i<5;++i)std::strcpy(static_cast<char*>(ptr(T+i*0x100)),values[i]);
 if(a[10]&2){byte(T,0);byte(T+0x100,0);byte(T+0x200,0);byte(T+0x300,0);}
 if(op==0&&a[3]){std::memset(ptr(T),'L',a[3]);byte(T+a[3],0);std::memset(ptr(T+0x100),'R',8);byte(T+0x108,0);}
 if((op==5||op==10)&&a[3]){std::memset(ptr(T),'A',a[3]-1);byte(T+a[3]-1,0);}
 for(U i=0;i<52;++i)byte(T+0x500+i,i<10?65+i:0);for(U i=0;i<5;++i){put(D+i*4,0x11110000+i);put(D+0x40+i*4,0x11110000+i);}if(a[10]<5)put(D+0x40+a[10]*4,0xeeeeeeee);
}
}
// Private link fixtures use native callbacks; no original-VA virtual invocation.
const NetworkSendTable network_vtable_owner_005b4968{nullptr,dummy},network_vtable_owner_005b4970{nullptr,dummy},network_vtable_owner_005b4978{nullptr,dummy};
void* __cdecl application_context_heap_state_005e4fe8(){return ptr(manager);}
void* __cdecl heap_lock_create_005321f0(){event(0x5321f0);return ptr(0x26000000);}
void __cdecl heap_enter_005322b0(void*h){event(0x5322b0,{raw(h)});if(a[6]&1)manager=M2;if(a[6]&2)put(M+0x28,0x26000010);}
void __cdecl heap_leave_005322c0(void*h){event(0x5322c0,{raw(h)});}
void __cdecl application_context_new_head_0059eeb0(U kind,U zero){event(0x59eeb0,{kind,zero});put(M+0x28+(kind==31?0x88:0x10),kind==31?N:K);}
void __cdecl heap_fill_0053c290(void*p,U v,U n){event(0x53c290,{pointer(p),v,n});std::memset(p,v,n);}
void __cdecl heap_copy_dispatch_005323e0(void*d,const void*s,U n){event(0x5323e0,{pointer(d),pointer(s),n});std::memcpy(d,s,n);}
void* __cdecl network_client_worker_construct_0055c370(U first,U second,const void*identity,const void*data,U third,U last){if(identity!=network_connection_identity_005b4980)std::abort();event(0x55c370,{first,second,0x5b4980,third,last});bytes_event(4,data,92);return a[4]==2?nullptr:ptr(W);}
void* __cdecl network_host_worker_construct_0055aaa0(U first,U second,const void*identity,const void*data,U fourth,U port,U last){if(identity!=network_connection_identity_005b4980)std::abort();event(0x55aaa0,{first,second,0x5b4980,fourth,port,last});bytes_event(5,data,52);return a[4]&&(!calls++||a[4]==2)?nullptr:ptr(W);}
U __cdecl network_address_current_0055d650(void*w,void*out){event(0x55d650,{raw(w),pointer(out)});for(U i=0;i<5;++i)put(raw(out)+i*4,0x11110000+i);if(a[6]&4)put(S+4,W2);return 1;}
char* __cdecl formatter_error_copy_n_005a28a0(char*out,const char*text,U n){event(0x5a28a0,{pointer(out),pointer(text),n});std::strncpy(out,text,n);return out;}
std::int32_t __cdecl formatter_entry_005a0fbf(char*out,const char*format,...){va_list vl;va_start(vl,format);int ch=va_arg(vl,int);const char*address_=va_arg(vl,const char*);U port=va_arg(vl,U);const char*settings=va_arg(vl,const char*);event(0x5a0fbf,{pointer(out),static_cast<U>(ch),port});text_event(6,format);text_event(7,address_);bytes_event(8,settings,52);int result=std::sprintf(out,format,ch,address_,port,settings);va_end(vl);return result;}
void* __cdecl startup_network_allocate_0059ef90(U n){event(0x59ef90,{n});if(n==8&&(a[6]&32))put(S+0xc,D+0x100);if((n==20&&(a[9]&1))||(n==8&&(a[9]&2)))return nullptr;return ptr(n==20?C:D+0x200);}
U __fastcall network_client_connect_0048ac90(void*c,void*,const char*server,U port){event(0x48ac90,{raw(c),pointer(server),port});text_event(9,server);return 7;}
int main(){if(VirtualAlloc(ptr(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;std::string line;
 while(std::getline(std::cin,line)){std::istringstream in(line);in>>op;for(auto&v:a)in>>v;init();U result=0;
 switch(op){
 case 0:result=raw(network_client_construct_0048aa10(ptr(S),nullptr,11,22,33,static_cast<char*>(ptr(T)),static_cast<char*>(ptr(T+0x100)),static_cast<char*>(ptr(T+0x200)),static_cast<char*>(ptr(T+0x300)),44));break;
 case 1:result=raw(network_host_construct_0048af80(ptr(S),nullptr,11,22,a[1],33,a[2]?ptr(T+0x500):nullptr,a[3]?static_cast<char*>(ptr(T+0x400)):nullptr,1234));break;
 case 2:network_host_start_client_0048b3c0(ptr(S),nullptr);break;case 3:network_host_restart_client_0048b450(ptr(S),nullptr);break;
 case 4:result=network_address_get_0055d5a0(ptr(W),ptr(D+0x80),ptr(D+0xa0),ptr(D+0xc0));break;
 case 5:result=network_address_parse_0055d5e0(ptr(W),static_cast<char*>(ptr(T)),1234,ptr(D+0x80));break;
 case 6:result=network_address_equal_0055d6e0(ptr(W),ptr(D),ptr(D+0x40));break;case 7:result=network_address_provider_mode_0055d730(ptr(W));break;case 8:result=network_address_text_mode_0055d750(ptr(W));break;
 case 9:result=network_address_compare_dispatch_00580590(ptr(W+8),ptr(D),ptr(D+0x40));break;
 case 10:result=network_address_parse_dispatch_005805b0(ptr(W+8),T,1234,D+0x80);break;case 11:result=network_address_get_dispatch_005805e0(ptr(W+8),D+0x80,D+0xa0,D+0xc0);break;}
 put(S,norm(get(S)));put(C,norm(get(C)));put(V+0x40,0x24000000);put(V+0x38,a[11]&1?0x24000010:0);put(V+0x3c,a[11]&2?0x24000020:0);
 std::cout<<"{\"return\":"<<result<<",\"trace\":[";for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}std::cout<<"],\"state\":[";bool first=true;
 for(auto range:{std::pair<U,U>{S,0x200},{C,0x20},{M,0x100},{M2,0x100},{N,0x40},{K,0x40},{V,0x50},{D,0x220}})for(U i=0;i<range.second;i+=4){if(!first)std::cout<<',';first=false;std::cout<<get(range.first+i);}std::cout<<"]}\n";
 }VirtualFree(ptr(B),0,MEM_RELEASE);return 0;
}
} // namespace porsche
int main(){return porsche::main();}
