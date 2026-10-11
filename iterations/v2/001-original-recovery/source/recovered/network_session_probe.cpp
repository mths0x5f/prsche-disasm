#include "porsche/network_session.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/startup_services.hpp"
#include <windows.h>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace porsche {
void* startup_network_00628c70=nullptr;
// Link-only dependencies of frozen, uncalled functions. Abort if a test
// unexpectedly crosses one; these are not production substitutes.
std::uint32_t timer_rate_005deb48=60;
void __cdecl network_lifecycle_wait_0053c380(std::int32_t){std::abort();}
std::uint32_t __stdcall network_lifecycle_tick_count_0048a9a0(){std::abort();}
void __cdecl network_lifecycle_unregister_00561110(std::uint32_t){std::abort();}
void __cdecl network_lifecycle_device_stop_00561b50(){std::abort();}
void __cdecl network_lifecycle_device_cancel_00561730(std::uint32_t){std::abort();}
void __cdecl network_lifecycle_device_release_005617d0(std::uint32_t){std::abort();}
void __cdecl application_context_new_head_0059eeb0(std::uint32_t,std::uint32_t){std::abort();}
void* __cdecl context_selector_pointer_005e4fec(){std::abort();}
namespace {
using U=std::uint32_t;
constexpr U B=0x23000000,S=B,S2=B+0x400,D=B+0x800,D2=B+0x900,
    N=B+0xa00,N2=B+0xb00,K=B+0x1000,K2=B+0x1010,
    M=B+0x2000,M2=B+0x2200,L=B+0x3000,P=B+0x5000,
    W=B+0x6000,TK=B+0x6020,REF=B+0x6100,C=B+0x7000;
std::array<U,12> a{};U operation=0,pool_count=0,enter_count=0;
std::vector<std::vector<U>> events;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U va){U v;std::memcpy(&v,ptr(va),4);return v;}
void put(U va,U v){std::memcpy(ptr(va),&v,4);}
U byte(U va){return *static_cast<std::uint8_t*>(ptr(va));}
void pb(U va,U value){*static_cast<std::uint8_t*>(ptr(va))=static_cast<std::uint8_t>(value);}
U head(U group){return L+group*0x100;}
U node(U group,U i){return head(group)+0x20+i*0x10;}
U payload(U group,U i){return P+group*0x100+i*0x20;}
void event(U id,std::initializer_list<U> args={}){
    std::vector<U> row{id};row.insert(row.end(),args);
    for(U value:{raw(network_lifecycle_session_00628c74),raw(network_session_lock_cell_00628c78),
        static_cast<U>(network_session_stopped_005d07d0),byte(S+0x17d),byte(S+0x17e),get(S),get(S+8),get(S+0xc),get(S+0x10),
        get(D),get(D+4),get(D+8),get(D+0xc),get(D+0x10),byte(D+0x16),get(N),get(N+8),
        get(M+0x38),get(M2+0x38),get(C)})row.push_back(value);
    events.push_back(row);
}
void init_list(U group,U count,U pattern){
    U h=head(group);put(h,count?node(group,0):h);put(h+4,count?node(group,count-1):h);
    for(U i=0;i<count;++i){U item=node(group,i);
        put(item,i+1<count?node(group,i+1):h);put(item+4,i?node(group,i-1):h);
        U value=payload(group,i);if(pattern==1)value=payload(group,i%3);
        if(pattern==2||(pattern==3&&i%2==0))value=0;put(item+8,value);
    }
}
void initialize(){
    std::memset(ptr(B),0xcc,0x10000);pool_count=enter_count=0;
    for(U session:{S,S2}){
        put(session,D);put(session+8,0x25000008);put(session+0xc,0x2500000c);put(session+0x10,0x25000010);
        for(U i=0;i<6;++i)put(session+0x164+i*4,head(i));
        pb(session+0x17d,0x55);pb(session+0x17e,a[2]);
    }
    for(U conn:{D,D2}){
        put(conn,0x11111111);put(conn+4,0x29000000);put(conn+8,0x28000088);
        put(conn+0xc,a[3]==2?N:0);put(conn+0x10,0x25000020);pb(conn+0x16,0x66);put(conn+0x18,head(6));
    }
    for(U nested:{N,N2}){
        put(nested,0x22222222);put(nested+4,0x29000001);put(nested+8,0x28000099);put(nested+0xc,head(7));
    }
    if(operation==1&&a[3]==0)put(S,0);
    put(K,0x28001000);put(K2,0x28001001);put(TK,0x28002000);put(W,head(10));put(C,M);
    for(U manager:{M,M2}){
        put(manager+0x28,manager==M?0x27000000:0x27000001);
        put(manager+0x38,manager==M?0x26000000:0x26000001);put(manager+0xb0,0x26001000);
    }
    for(U group=0;group<11;++group)init_list(group,a[0],a[1]);
    for(U i=0;i<a[0];++i){put(node(10,i)+8,REF+i*0x10);put(REF+i*0x10,payload(3,i%3));}
    network_cleanup_list_00628c60=ptr(W);network_cleanup_lock_cell_00628c64=ptr(TK);
    network_lifecycle_session_00628c74=ptr(S);network_session_lock_cell_00628c78=ptr(K);network_session_stopped_005d07d0=0;
    for(U i=0;i<8;++i)network_lifecycle_callbacks_006b7c20[i]=i%3==0?0x004906b0:0x410000+i;
}
}
void* __cdecl application_context_heap_state_005e4fe8(){return ptr(get(C));}
void __cdecl heap_enter_005322b0(void* lock){
    U handle=raw(lock);event(0x5322b0,{handle});++enter_count;
    if(enter_count==1&&(a[4]&4)){network_session_lock_cell_00628c78=ptr(K2);put(K,0x28001111);}
    if(handle>=0x27000000&&handle<0x27010000){
        ++pool_count;U captured=get(M+0x28)==handle?M:M2;
        if(a[4]&1)put(C,get(C)==M?M2:M);
        if(a[4]&2){put(captured+0x38,0x26010000+pool_count);put(captured+0xb0,0x26011000+pool_count);put(captured+0x28,0x27001000+pool_count);}
    }
}
void __cdecl heap_leave_005322c0(void* lock){
    event(0x5322c0,{raw(lock)});
    if(a[4]&512){put(D+8,0x28009999);put(N+8,0x28008888);}
}
U __cdecl application_release_0059f050(void* address){
    U value=raw(address);event(0x59f050,{value});
    if((a[4]&16)&&value==0x25000010){put(S+0xc,0x2500010c);put(S+8,0x25000108);}
    if((a[4]&64)&&value==0x25000020)put(D+0xc,N2);
    if(a[4]&1024)network_lifecycle_session_00628c74=ptr(S2);
    return 0x13579bdf;
}
U __cdecl free_00531f90(void* address){event(0x531f90,{raw(address)});return 0x2468ace0;}
void __cdecl heap_lock_destroy_005322d0(void* lock){event(0x5322d0,{raw(lock)});if(a[4]&256)network_session_lock_cell_00628c78=ptr(K);}
void __cdecl network_session_stop_worker_0055bfd0(void* worker){
    event(0x55bfd0,{raw(worker)});
    if(a[4]&8){put(D+4,0x29009999);put(D+8,0x28007777);pb(S+0x17e,0x77);}
}
void __fastcall network_session_remove_member_00492770(void* receiver,void*,void* member){
    U value=raw(member);event(0x492770,{raw(receiver),value});
    // Scripted unknown effect: remove one matching node from each requested
    // list. This fixture operation makes no claim about 00492770 semantics.
    for(U off:{0x164u,0x16cu}){
        U h=get(raw(receiver)+off),current=get(h);
        while(current!=h){if(get(current+8)==value){U next=get(current),prev=get(current+4);put(prev,next);put(next+4,prev);break;}current=get(current);}
    }
    if(a[4]&32){network_session_lock_cell_00628c78=ptr(K2);put(S,0);}
}
void __cdecl network_cleanup_stop_worker_0055d9b0(){event(0x55d9b0);}
void __cdecl network_cleanup_destroy_worker_0055d1b0(void* worker){
    event(0x55d1b0,{raw(worker)});
    if(a[4]&128){put(N+0xc,head(8));put(N2+0xc,head(8));put(N+8,0x28006666);put(N2+8,0x28006666);}
}
}

int main(){using namespace porsche;
    if(VirtualAlloc(ptr(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;
    std::string line;while(std::getline(std::cin,line)){
        std::istringstream in(line);in>>operation;a.fill(0);for(auto& v:a)in>>v;
        events.clear();initialize();
        if(operation==0)network_lifecycle_stop_session_00492260();
        else if(operation==1)network_lifecycle_session_destroy_00491fc0(ptr(S),nullptr);
        else if(operation==2)network_session_stop_connection_0048b310(ptr(D),nullptr);
        else if(operation==3){put(W,head(0));network_session_clear_list_00493130(ptr(W),nullptr);}
        else network_session_connection_destroy_0048b250(ptr(D),nullptr);
        std::cout<<"{\"trace\":[";
        for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';
            for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}
        std::cout<<"],\"state\":[";bool first=true;
        for(auto range:{std::pair<U,U>{B,0xc20},{K,0x20},{M,0x400},{L,0x1000},{P,0x800},{W,0x160},{C,4}})
            for(U off=0;off<range.second;off+=4){if(!first)std::cout<<',';first=false;std::cout<<get(range.first+off);}
        for(U value:{raw(network_lifecycle_session_00628c74),raw(network_session_lock_cell_00628c78),static_cast<U>(network_session_stopped_005d07d0)})std::cout<<','<<value;
        for(U value:network_lifecycle_callbacks_006b7c20)std::cout<<','<<value;
        std::cout<<"]}\n";
    }
}
