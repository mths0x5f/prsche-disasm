#include "network_vtable_identity_fixture.hpp"
#include "porsche/network_workers_members.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/file_events.hpp"
#include "porsche/thread_wait.hpp"
#include "porsche/window_runtime.hpp"
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
void __cdecl network_lifecycle_wait_0053c380(std::int32_t){std::abort();}
std::uint32_t __stdcall network_lifecycle_tick_count_0048a9a0(){std::abort();}
void __cdecl network_lifecycle_unregister_00561110(std::uint32_t){std::abort();}
void __cdecl network_lifecycle_device_stop_00561b50(){std::abort();}
void __cdecl network_lifecycle_device_cancel_00561730(std::uint32_t){std::abort();}
void __cdecl network_lifecycle_device_release_005617d0(std::uint32_t){std::abort();}
void* __cdecl context_selector_pointer_005e4fec(){std::abort();}
void* __stdcall platform_create_event(void*,std::int32_t,std::int32_t,const char*){std::abort();}
std::uint32_t __stdcall platform_reset_event(void*){std::abort();}
std::uint32_t __stdcall platform_wait_events(std::uint32_t,void* const*,std::int32_t,std::uint32_t,std::int32_t){std::abort();}
std::uint32_t __stdcall platform_last_error(){std::abort();}
namespace {
using U=std::uint32_t;
constexpr U B=0x23000000,W=B,MESSAGES=B+0x1000,S=B+0x2000,D=B+0x2300,P=B+0x2400,
    G=B+0x3000,R=B+0x4000,SENDER=B+0x4020,VT=B+0x4040,
    M=B+0x5000,M2=B+0x5200,L=B+0x6000,OUTPUT=B+0x7000,C=B+0x7010,F=B+0x8000;
std::array<U,12> a{};U operation=0,enter_count=0,sleep_count=0,pool_count=0;
std::vector<std::vector<U>> events;
void* ptr(U v){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(v));}
U raw(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(U va){U v;std::memcpy(&v,ptr(va),4);return v;}
void put(U va,U v){std::memcpy(ptr(va),&v,4);}
U byte(U va){return *static_cast<std::uint8_t*>(ptr(va));}
void pb(U va,U value){*static_cast<std::uint8_t*>(ptr(va))=static_cast<std::uint8_t>(value);}
U state(){return raw(&network_worker_state_006a3b60);}
U normalize(U v){
    if(v>=state()&&v<state()+0x1d0)return 0x6a3b60+v-state();
    U thread=raw(&network_worker_thread_006a3d30);if(v>=thread&&v<thread+28)return 0x6a3d30+v-thread;
    return network_fixture_word(v);
}
void event(U id,std::initializer_list<U> args={}){
    std::vector<U> row{id};for(U value:args)row.push_back(normalize(value));
    for(U value:{get(W+0x240),get(W+0x248),network_worker_active_006a4660,get(W+0x194),get(W+0x198),
        get(state()+0x198),get(M+0x38),get(M+0xb0),get(M2+0x38),get(M2+0xb0),get(C),
        get(S+0x154),get(S+0x15c),get(P+0xa4),byte(G+0xcc3)})row.push_back(value);
    events.push_back(row);
}
U head(U group){return L+group*0x100;}
U node(U group,U i){return head(group)+0x20+i*0x10;}
void list(U group,U count,U value){
    U h=head(group);put(h,count?node(group,0):h);put(h+4,count?node(group,count-1):h);
    for(U i=0;i<count;++i){put(node(group,i),i+1<count?node(group,i+1):h);put(node(group,i)+4,i?node(group,i-1):h);
        put(node(group,i)+8,(a[5]&&i%2)?P+0x20:value);}
}
void queue(U q,U count,U lock){
    put(q,count);put(q+4,0x12340002);put(q+8,count?MESSAGES:0);put(q+0xc,count?MESSAGES+(count-1)*0x20:0);put(q+0x18,lock);
    for(U i=0;i<count;++i){put(MESSAGES+i*0x20,i+1<count?MESSAGES+(i+1)*0x20:0);put(MESSAGES+i*0x20+4,0xaaaaaaaa+i);}
}
void __fastcall send(void* sender,void*,U destination,const std::uint8_t* packet,U bytes){
    std::vector<U> row{0x24000000,raw(sender),destination,bytes};for(U i=0;i<bytes;++i)row.push_back(packet[i]);events.push_back(row);
    if(a[4]&2048)put(P+0xa4,0);
}
void initialize(){
    std::memset(ptr(B),0xcc,0x10000);std::memset(&network_worker_state_006a3b60,0xcc,sizeof(network_worker_state_006a3b60));
    std::memset(&network_worker_thread_006a3d30,0xcc,sizeof(network_worker_thread_006a3d30));
    enter_count=sleep_count=pool_count=0;network_worker_active_006a4660=a[3];
    U count=operation==8?0:a[0];queue(W+0x198,count,0x28000000);queue(W+0x1b4,0,0x28000001);put(W+0x194,0x28000002);
    queue(state()+0x198,count,0x28000010);queue(state()+0x1b4,0,0x28000011);put(state()+0x194,0x28000012);
    for(U off:{0x244u,0x260u,0x298u,0x27cu,0x2b4u})queue(W+off,0,0x28000100+off);
    put(W+0x240,a[3]);put(W+0x248,a[3]);if(operation==8)put(W+0x198,a[0]);
    if(operation==7)put(W+0x19c,a[3]);
    if(operation==5){put(W+0x19c,a[5]&1?2:0);put(W+0x1b8,a[5]&2?2:0);}
    if(operation==3&&a[5])put(W+0x198,0xffffffffu);
    put(C,M);for(U manager:{M,M2}){put(manager+0x28,manager==M?0x27000000:0x27000001);put(manager+0x38,F);put(manager+0xb0,0x26000000);}
    for(U i=0;i<6;++i){put(F+i*0x20+4,i+1<6?F+(i+1)*0x20:0);put(F+i*0x20,0xaaaaaaaa);}
    put(S,D);put(S+0xc,R);put(S+0x10,R);put(S+0x154,a[3]);put(S+0x158,0x1234);put(S+0x15c,a[3]);
    put(D+8,0x28000200);pb(D+0x14,0);put(D+0x10,R);put(D+0x18,head(0));
    for(U i=0;i<6;++i)put(S+0x164+i*4,head(i+1));
    put(P+0xa4,a[1]>=3?G:0);put(P+0xac,0x12345678);put(P+0xb4,a[2]);pb(P+0xb8,a[1]==0?1:0);pb(P+0xbd,a[1]==1?1:0);
    put(P+0xc8,head(7));put(P+0xc4,head(8));pb(G+0xcc3,a[1]==5?0:1);
    if(a[6]==1)pb(D+0x14,1);if(a[6]==2)put(D+0x10,0);
    for(U i=0;i<9;++i)list(i,operation>=9?a[0]:0,i==6?G:i==5?G+0x20:P);
    put(R,SENDER);put(R+4,0);put(SENDER,VT);put(VT,raw(reinterpret_cast<void*>(&send)));
    for(U i=0;i<8;++i)network_lifecycle_callbacks_006b7c20[i]=i%3?0x410000+i:0x00490640;
    network_cleanup_list_00628c60=nullptr;put(OUTPUT,0xdddddddd);put(OUTPUT+4,0xabcdef12);
    if(operation==14&&a[5])put(M+0x38,0);
}
}
void* __cdecl application_context_heap_state_005e4fe8(){return ptr(get(C));}
void __cdecl heap_enter_005322b0(void* lock){
    U handle=raw(lock);event(0x5322b0,{handle});++enter_count;
    if(a[4]&1){put(W+0x1b0,0x28110000+enter_count);put(W+0x1cc,0x28120000+enter_count);put(state()+0x1b0,0x28130000+enter_count);}
    if(a[4]&4){put(W+0x240,get(W+0x240)|0x100);put(W+0x248,get(W+0x248)|0x100);}
    if(handle>=0x27000000&&handle<0x27010000){++pool_count;
        if(a[4]&2)put(C,get(C)==M?M2:M);
    }
}
void __cdecl heap_leave_005322c0(void* lock){event(0x5322c0,{raw(lock)});if(a[4]&256)put(OUTPUT+4,0xabcdef01);}
void __cdecl heap_lock_destroy_005322d0(void* lock){event(0x5322d0,{raw(lock)});}
U __cdecl application_release_0059f050(void* address){event(0x59f050,{raw(address)});if(a[4]&1024)pb(G+0xcc3,0x42);return 0x13579bdf;}
U __cdecl free_00531f90(void* address){event(0x531f90,{raw(address)});return 0x2468ace0;}
std::int32_t __cdecl file_current_thread_0055f780(U zero){event(0x55f780,{zero});return static_cast<std::int32_t>(a[2]);}
U __cdecl timed_callbacks_005366e0(U zero){event(0x5366e0,{zero});if(a[4]&8){put(W+0x240,get(W+0x240)|0x200);put(W+0x248,get(W+0x248)|0x200);}return 1;}
U __stdcall platform_sleep(U milliseconds,std::int32_t alertable){
    event(0x55f740,{milliseconds,static_cast<U>(alertable)});++sleep_count;
    if(sleep_count>=a[1]){queue(W+0x198,1,0x28000000);queue(state()+0x198,1,0x28000010);}
    if(a[4]&16){network_worker_active_006a4660=7;put(W+0x194,0x28116666);}return 0x99;
}
U __stdcall platform_set_event(void* handle){event(0x55fb30,{raw(handle)});if(a[4]&32)put(W+0x194,0x28223344);return 0x17;}
U __stdcall platform_close_handle(void* handle){event(0x55fc10,{raw(handle)});return 0x18;}
U __cdecl thread_wait_0055fa10(ThreadRecord* thread,U timeout){
    event(0x55fa10,{raw(thread),timeout});
    if(a[4]&64){put(W+0x19c,0);put(W+0x1b0,0x28334455);put(W+0x1b8,2);put(W+0x1cc,0x28445566);}return 1;
}
void __cdecl application_context_new_head_0059eeb0(U kind,U mode){
    event(0x59eeb0,{kind,mode});if(kind!=1||mode)std::abort();
    put(M+0x38,F+0x80);put(M2+0x38,F+0x80);if(a[4]&512)put(C,M2);
}
void __fastcall network_member_group_remove_0048bda0(void* group,void*,void* member){
    event(0x48bda0,{raw(group),raw(member)});if(a[1]==4||(a[4]&128))pb(G+0xcc3,0);
}
}

int main(){using namespace porsche;
    if(VirtualAlloc(ptr(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=ptr(B))return 2;
    std::string line;while(std::getline(std::cin,line)){
        std::istringstream in(line);in>>operation;a.fill(0);for(auto& v:a)in>>v;events.clear();initialize();U result=0;
        if(operation==0)network_session_stop_worker_0055bfd0(ptr(W));
        else if(operation==1)network_cleanup_destroy_worker_0055d1b0(ptr(W));
        else if(operation==2)network_cleanup_stop_worker_0055d9b0();
        else if(operation==3)result=raw(network_worker_get_00580050(ptr(W)));
        else if(operation==4)result=network_worker_submit_00580080(ptr(W),a[5]?nullptr:ptr(MESSAGES));
        else if(operation==5)result=network_worker_dispose_00580020(ptr(W));
        else if(operation==6)network_worker_clear_extra_0055c060(ptr(W));
        else if(operation==7)network_worker_queue_dispose_005806c0(reinterpret_cast<IoList*>(ptr(W+0x198)));
        else if(operation==8)result=network_worker_queue_count_005809f0(reinterpret_cast<IoList*>(ptr(W+0x198)));
        else if(operation==9)network_session_remove_member_00492770(ptr(S),nullptr,ptr(P));
        else if(operation==10)network_member_connection_remove_0048b5a0(ptr(D),nullptr,ptr(P));
        else if(operation==11)network_member_destroy_0048a7a0(ptr(P),nullptr);
        else if(operation==12)result=raw(network_member_end_00529050(ptr(S+0x174),nullptr,static_cast<U*>(ptr(a[1]?S+0x174:OUTPUT))));
        else if(operation==13)result=raw(network_member_copy_0050e140(ptr(a[1]?OUTPUT+4:OUTPUT),nullptr,static_cast<U*>(ptr(OUTPUT+4))));
        else result=raw(network_member_insert_004937f0(ptr(S+0x174),nullptr,static_cast<U*>(ptr(a[1]?F+4:OUTPUT)),head(5),static_cast<U*>(ptr(OUTPUT+4))));
        std::cout<<"{\"result\":"<<result<<",\"trace\":[";
        for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<network_fixture_word(events[i][j]);}std::cout<<']';}
        std::cout<<"],\"state\":[";bool first=true;
        for(auto range:{std::pair<U,U>{W,0x300},{MESSAGES,0x200},{S,0x600},{G,0xd00},{R,0x50},{M,0x400},{L,0x900},{OUTPUT,0x20},{F,0x100},{state(),0x1d0},{raw(&network_worker_thread_006a3d30),28}})
            for(U off=0;off<range.second;off+=4){if(!first)std::cout<<',';first=false;U v=get(range.first+off);if(range.first==R&&off==0x40)v=0x24000000;std::cout<<normalize(v);}
        std::cout<<','<<network_worker_active_006a4660;for(U value:network_lifecycle_callbacks_006b7c20)std::cout<<','<<value;std::cout<<"]}\n";
    }
}
