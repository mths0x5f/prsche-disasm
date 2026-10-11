#include "porsche/network_cleanup.hpp"
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
constexpr U B=0x23000000,OBJ=B,WR=B+0x1000,WR2=B+0x1010,
    LOCK=B+0x1100,LOCK2=B+0x1110,L=B+0x2000,L2=B+0x2200,
    P=B+0x3000,M=B+0x4000,M2=B+0x4200,O=B+0x5000,C=B+0x5004;
std::array<U,12> a{};U operation=0,pool_count=0,enter_count=0;
std::vector<std::vector<U>> events;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U va){U v;std::memcpy(&v,ptr(va),4);return v;}
void put(U va,U v){std::memcpy(ptr(va),&v,4);}
U node(U group,U i){return L+group*0x200+0x20+i*0x10;}
U payload(U i){return P+i*0x20;}
void event(U id,std::initializer_list<U> args={}){
    std::vector<U> row{id};row.insert(row.end(),args);
    for(U value:{raw(network_cleanup_list_00628c60),raw(network_cleanup_lock_cell_00628c64),
        get(OBJ),get(OBJ+8),get(OBJ+0xc),get(WR),get(L),get(L+4),get(L2),get(L2+4),
        get(M+0x38),get(M+0xb0),get(M2+0x38),get(M2+0xb0),get(C)})row.push_back(value);
    events.push_back(row);
}
void init_list(U group,U count,U pattern){
    U head=L+group*0x200;put(head,count?node(group,0):head);put(head+4,count?node(group,count-1):head);
    for(U i=0;i<count;++i){U item=node(group,i);
        put(item,i+1<count?node(group,i+1):head);put(item+4,i?node(group,i-1):head);
        U value=payload(i);
        if(pattern==1)value=payload(i%3);
        if(pattern==2||(pattern==3&&i%2==0))value=0;
        put(item+8,value);
    }
}
void initialize(){
    std::memset(ptr(B),0xcc,0x10000);pool_count=enter_count=0;
    put(OBJ,0x11111111);put(OBJ+4,0x29000000);put(OBJ+8,0x28000088);
    put(OBJ+0xc,L);put(OBJ+0x5c,L);put(WR,L);put(WR2,L2);
    put(LOCK,0x28000000);put(LOCK2,0x28000001);put(C,M);put(O,0xdddddddd);
    for(U manager:{M,M2}){
        put(manager+0x28,manager==M?0x27000000:0x27000001);
        put(manager+0x38,manager==M?0x26000000:0x26000001);
        put(manager+0xb0,manager==M?0x26001000:0x26001001);
    }
    for(U i=0;i<8;++i){
        U target=OBJ+0x80;
        if(a[1]==1||(a[1]==2&&i%2==0))target=OBJ;
        if(a[1]==3)target=i%2?OBJ+0x80:0;
        put(payload(i),target);put(payload(i)+4,0x25001000+i*0x10);
    }
    U pattern=operation==0?0:a[1];init_list(0,a[0],pattern);init_list(1,a[0],pattern);
    network_cleanup_list_00628c60=ptr(WR);network_cleanup_lock_cell_00628c64=ptr(LOCK);
    if(a[2]==1||a[2]==3)network_cleanup_list_00628c60=nullptr;
    if(a[2]==2||a[2]==3)network_cleanup_lock_cell_00628c64=nullptr;
}
}
void* __cdecl application_context_heap_state_005e4fe8(){return ptr(get(C));}
void __cdecl heap_enter_005322b0(void* lock){
    U handle=raw(lock);event(0x5322b0,{handle});++enter_count;
    if(a[4]&16){put(LOCK,0x28112233);put(LOCK2,0x28445566);}
    if(enter_count==1&&(a[4]&4)){
        network_cleanup_list_00628c60=ptr(WR2);network_cleanup_lock_cell_00628c64=ptr(LOCK2);
    }
    if(handle>=0x27000000&&handle<0x27010000){
        ++pool_count;U captured=get(M+0x28)==handle?M:M2;
        if(a[4]&1)put(C,get(C)==M?M2:M);
        if(a[4]&2){
            put(captured+0x38,0x26010000+pool_count);put(captured+0xb0,0x26011000+pool_count);
            put(captured+0x28,0x27001000+pool_count);
            for(U i=0;i<8;++i)put(payload(i)+4,0x25008000+i*0x10+pool_count);
        }
        if(a[4]&8){network_cleanup_list_00628c60=ptr(WR2);network_cleanup_lock_cell_00628c64=ptr(LOCK2);}
    }
}
void __cdecl heap_leave_005322c0(void* lock){
    event(0x5322c0,{raw(lock)});
    if(a[4]&512){put(OBJ+8,0x28009999);put(OBJ+4,0x29009999);}
}
U __cdecl application_release_0059f050(void* address){
    event(0x59f050,{raw(address)});
    if(a[4]&128)network_cleanup_lock_cell_00628c64=ptr(LOCK2);
    return 0x13579bdf;
}
U __cdecl free_00531f90(void* address){event(0x531f90,{raw(address)});return 0x2468ace0;}
void __cdecl heap_lock_destroy_005322d0(void* lock){
    event(0x5322d0,{raw(lock)});
    if(a[4]&256){network_cleanup_list_00628c60=ptr(WR2);network_cleanup_lock_cell_00628c64=ptr(LOCK);}
}
void __cdecl network_cleanup_stop_worker_0055d9b0(){
    event(0x55d9b0);
    if(a[4]&32){network_cleanup_list_00628c60=ptr(WR2);network_cleanup_lock_cell_00628c64=ptr(LOCK2);}
}
void __cdecl network_cleanup_destroy_worker_0055d1b0(void* worker){
    event(0x55d1b0,{raw(worker)});
    if(a[4]&64){put(OBJ+0xc,L2);put(OBJ+8,0x28008888);}
}
}

int main(){using namespace porsche;
    if(VirtualAlloc(ptr(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;
    std::string line;
    while(std::getline(std::cin,line)){
        std::istringstream in(line);in>>operation;a.fill(0);for(auto& v:a)in>>v;
        events.clear();initialize();U result=0;
        if(operation==0)network_services_detach_0048c430(ptr(a[1]==3?0:OBJ),nullptr);
        else if(operation==1)network_services_destroy_004904d0(ptr(OBJ),nullptr);
        else if(operation==2){
            U output=a[3]==1?WR:a[3]==2?L:a[3]==3?node(0,0)+4:O;
            result=raw(network_services_begin_004c3150(ptr(WR),nullptr,static_cast<U*>(ptr(output))));
        }else if(operation==3)network_lifecycle_close_transport_0048c580();
        else network_lifecycle_connection_destroy_0048aed0(ptr(OBJ),nullptr);
        std::cout<<"{\"result\":"<<result<<",\"trace\":[";
        for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';
            for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}
        std::cout<<"],\"state\":[";bool first=true;
        for(auto range:{std::pair<U,U>{OBJ,0x100},{WR,0x20},{LOCK,0x20},{L,0x400},{P,0x200},{M,0x400},{O,8}})
            for(U off=0;off<range.second;off+=4){if(!first)std::cout<<',';first=false;std::cout<<get(range.first+off);}
        std::cout<<','<<raw(network_cleanup_list_00628c60)<<','<<raw(network_cleanup_lock_cell_00628c64)<<"]}\n";
    }
}
