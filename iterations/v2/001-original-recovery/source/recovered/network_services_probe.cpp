#include "porsche/network_services.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/startup_services.hpp"
#include <windows.h>
#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace porsche {
void* startup_network_00628c70=nullptr;
namespace {
using U=std::uint32_t;
constexpr U B=0x23000000,N=B,N2=B+0x1000,R=B+0x2000,R2=B+0x2010,
    S=B+0x2100,S2=B+0x2110,V=B+0x2200,V2=B+0x2210,W=B+0x2300,
    L=B+0x3000,P=B+0x5000,M=B+0x7000,M2=B+0x8000,T=B+0xa000,
    K=B+0xb000,O=B+0xb010,Q=B+0xb014,C=B+0xb018;
std::array<U,12> a{};U operation=0,send_count=0,pool_count=0;
std::vector<std::vector<U>> events;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U va){U v;std::memcpy(&v,ptr(va),4);return v;}
void put(U va,U v){std::memcpy(ptr(va),&v,4);}
void pb(U va,U v){*static_cast<std::uint8_t*>(ptr(va))=static_cast<std::uint8_t>(v);}
U node(U group,U index){return L+group*0x100+0x20+index*0x10;}
U payload(U group,U kind){return P+group*0x40+kind*0x10;}
void event(U id,std::initializer_list<U> values={}){std::vector<U> row{id};row.insert(row.end(),values);events.push_back(row);}
void on_send(U id,void* sender,U destination,const std::uint8_t* packet,U bytes){
    std::vector<U> row{id,raw(sender),destination,bytes};row.insert(row.end(),packet,packet+bytes);events.push_back(row);
    ++send_count;
    if(send_count==1){
        if(a[6]&1){put(R,S2);put(R2,S2);}
        if(a[6]&2)put(node(0,0),L);
        if(a[6]&4)startup_network_00628c70=ptr(N2);
        if(a[6]&8)const_cast<std::uint8_t*>(packet)[0]^=0xff;
        if(a[6]&16)put(K,0x33334444);
    }
}
void __fastcall send_a(void* sender,void*,U destination,const std::uint8_t* packet,U bytes){on_send(0x24000000,sender,destination,packet,bytes);}
void __fastcall send_b(void* sender,void*,U destination,const std::uint8_t* packet,U bytes){on_send(0x24000010,sender,destination,packet,bytes);}
void init_list(U group,U count,U pattern){
    U head=L+group*0x100;put(head,count?node(group,0):head);put(head+4,count?node(group,count-1):head);
    for(U i=0;i<count;++i){U item=node(group,i);
        put(item,i+1<count?node(group,i+1):head);put(item+4,i?node(group,i-1):head);
        U value=payload(group,i%3);
        if(pattern==0)value=payload(group,i);
        if(pattern==2)value=0;
        if(pattern==3&&i%2==0)value=0;
        put(item+8,value);
    }
}
void initialize(){
    std::memset(ptr(B),0xcc,0x10000);send_count=pool_count=0;
    put(N+8,0x26000000);put(N+0xc,R);put(N+0x10,K);pb(N+0xbf,0);
    put(N2+8,0x26001000);put(N2+0xc,R2);put(N2+0x10,K);pb(N2+0xbf,0);
    put(R,S);put(R+4,W);put(R2,S);put(R2+4,W);put(S,V);put(S2,V2);
    put(V,raw(reinterpret_cast<void*>(&send_a)));put(V2,raw(reinterpret_cast<void*>(&send_b)));put(W,L);
    put(K,0x11112222);put(O,0xdddddddd);put(Q,payload(0,1));put(C,M);
    for(U base:{M,M2}){put(base+0x28,base==M?0x27000000:0x27000001);put(base+0x38,0x25000000);}
    for(U group=0;group<5;++group){init_list(group,0,0);put(N+0x254+group*4,L+group*0x100);
        for(U i=0;i<6;++i)put(payload(group,i)+4,0x25001000+group*0x100+i*0x10);}
    startup_network_00628c70=ptr(N);
    if(operation==0){
        const U count=a[5]==0xffffffffu?0:a[5];init_list(0,count,0);
        for(U i=0;i<count;++i)put(node(0,i)+8,0x12340000+i);
        if(a[5]==0xffffffffu)put(R+4,0);
        if(a[3]!=0xffffffffu){for(U i=0;i<a[3];++i)pb(T+i,0x41+i%50);pb(T+a[3],0);}
    }else if(operation==1){
        init_list(0,a[3],0);for(U i=0;i<a[3];++i)put(node(0,i)+8,0x12340000+i);
        if(a[2]==0)startup_network_00628c70=nullptr;
        if(a[2]==2)put(N+8,0);if(a[2]==3)pb(N+0xbf,1);
    }else if(operation==2||operation==3){init_list(0,a[0],1);put(Q,payload(0,a[1]));}
    else{for(U group=0;group<5;++group)init_list(group,a[0],a[1]);}
}
U normalized(U v){if(v==raw(reinterpret_cast<void*>(&send_a)))return 0x24000000;if(v==raw(reinterpret_cast<void*>(&send_b)))return 0x24000010;return v;}
}
void* __cdecl application_context_heap_state_005e4fe8(){return ptr(get(C));}
void __cdecl heap_enter_005322b0(void* lock){
    const U handle=raw(lock);event(0x5322b0,{handle,get(M+0x38),get(M2+0x38),get(L),get(C)});
    if(a[6]&32)startup_network_00628c70=ptr(N2);
    if(a[6]&16)put(K,0x33334444);
    if(handle>=0x27000000&&handle<=0x2700ffff){
        ++pool_count;U captured=get(M+0x28)==handle?M:M2;
        if(a[6]&128)put(C,get(C)==M?M2:M);
        if(a[6]&256){put(captured+0x38,0x25010000+pool_count);put(captured+0x28,0x27001000+pool_count);
            for(U g=0;g<5;++g)for(U i=0;i<6;++i)put(payload(g,i)+4,0x25008000+g*0x100+i*0x10);}
        if(a[6]&64)put(Q,payload(0,2));
    }
}
void __cdecl heap_leave_005322c0(void* lock){event(0x5322c0,{raw(lock),get(M+0x38),get(M2+0x38),get(L),get(C)});}
U __cdecl application_release_0059f050(void* address){event(0x59f050,{raw(address)});if(a[6]&512){put(N+0xdc,0x76543210);pb(N+0xc3,0x77);}return 1;}
U __cdecl free_00531f90(void* address){event(0x531f90,{raw(address)});return 1;}
void __fastcall network_services_detach_0048c430(void* receiver,void*){event(0x48c430,{raw(receiver)});}
void __fastcall network_services_destroy_004904d0(void* receiver,void*){event(0x4904d0,{raw(receiver)});}
U* __fastcall network_services_begin_004c3150(void* list,void*,U* output){event(0x4c3150,{raw(list)});*output=get(get(raw(list)));return output;}
}

int main(){using namespace porsche;
    if(VirtualAlloc(ptr(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;
    std::string line;while(std::getline(std::cin,line)){
        std::istringstream in(line);in>>operation;a.fill(0);for(auto& v:a)in>>v;events.clear();initialize();U result=0;
        if(operation==0)application_network_message_0048c870(ptr(R),nullptr,a[0],a[1],a[2],a[3]==0xffffffffu?0:T,a[4]);
        else if(operation==1)application_main_network_action(static_cast<std::int32_t>(a[0]),static_cast<std::int32_t>(a[1]));
        else if(operation==2){U target=node(0,a[1]);U out=a[2]==1?target+4:a[2]==2?L:O;result=raw(network_services_unlink_0048b660(ptr(W),nullptr,static_cast<U*>(ptr(out)),target));}
        else if(operation==3)network_services_remove_matching_00493180(ptr(W),nullptr,static_cast<U*>(ptr(Q)));
        else network_lifecycle_clear_lists_0048e790(ptr(N),nullptr);
        std::cout<<"{\"result\":"<<result<<",\"trace\":[";
        for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}
        std::cout<<"],\"state\":[";bool first=true;
        const std::array<std::array<U,2>,13> ranges{{{N,0x268},{N2,0x268},{R,0x18},{S,0x14},{V,0x14},{W,4},{L,0x500},{P,0x300},{M,0x100},{M2,0x100},{T,0x400},{K,4},{O,12}}};
        for(auto range:ranges)for(U off=0;off<range[1];off+=4){if(!first)std::cout<<',';first=false;std::cout<<normalized(get(range[0]+off));}
        std::cout<<','<<raw(startup_network_00628c70)<<"]}\n";
    }VirtualFree(ptr(B),0,MEM_RELEASE);
}
