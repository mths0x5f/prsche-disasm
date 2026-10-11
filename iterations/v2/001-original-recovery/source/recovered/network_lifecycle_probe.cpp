#include "porsche/network_lifecycle.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/file_events.hpp"
#include "porsche/heap_locks.hpp"
#include "porsche/startup_services.hpp"
#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace porsche {
void* startup_network_00628c70 = nullptr;
std::uint32_t timer_rate_005deb48 = 0;
namespace {
using U = std::uint32_t;
std::array<U, 0x268/4> net{}, other{};
std::array<U, 16> member{};
std::array<U, 128> lists{};
std::array<U, 64> manager_a{}, manager_b{};
U lock_cell = 0x44440000, manager_index = 0, pool_enters = 0;
std::array<U, 12> args{};
std::vector<std::vector<U>> events;
U operation = 0;
U raw(const void* p) { return static_cast<U>(reinterpret_cast<std::uintptr_t>(p)); }
U norm(U value) {
    const std::array<std::array<U,3>,6> ranges{{
        {raw(net.data()),static_cast<U>(sizeof(net)),0x23000000},
        {raw(other.data()),static_cast<U>(sizeof(other)),0x23001000},
        {raw(member.data()),static_cast<U>(sizeof(member)),0x23002000},
        {raw(lists.data()),static_cast<U>(sizeof(lists)),0x23005000},
        {raw(manager_a.data()),static_cast<U>(sizeof(manager_a)),0x23007000},
        {raw(manager_b.data()),static_cast<U>(sizeof(manager_b)),0x23008000}}};
    if(value==raw(&lock_cell))return 0x23004000;
    for(const auto& r:ranges)if(value>=r[0]&&value-r[0]<r[1])return r[2]+value-r[0];
    return value;
}
U load(const void* p,U off=0){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+off,4);return v;}
void put(void* p,U off,U v){std::memcpy(static_cast<std::uint8_t*>(p)+off,&v,4);}
U byte(const void* p,U off){return static_cast<const std::uint8_t*>(p)[off];}
void putbyte(void* p,U off,U v){static_cast<std::uint8_t*>(p)[off]=static_cast<std::uint8_t>(v);}
void event(U id,std::initializer_list<U> a={}) {
    std::vector<U> row{id};row.insert(row.end(),a);
    for(auto off:{8u,0xcu,0x14u})row.push_back(norm(load(net.data(),off)));
    for(auto off:{0xc2u,0xc3u,0xc7u})row.push_back(byte(net.data(),off));
    row.push_back(byte(member.data(),0x10));
    row.push_back(norm(raw(network_lifecycle_member_00628c7c)));
    row.push_back(norm(raw(network_lifecycle_session_00628c74)));
    row.push_back(manager_index);
    events.push_back(row);
}
void init_list(U offset,U count,U stride) {
    auto* head=reinterpret_cast<std::uint8_t*>(lists.data())+offset;
    put(head,0,count?raw(head+0x20):raw(head));
    put(head,4,count?raw(head+0x20+(count-1)*stride):raw(head));
    for(U i=0;i<count;++i){auto* node=head+0x20+i*stride;
        put(node,0,i+1<count?raw(node+stride):raw(head));
        put(node,4,i?raw(node-stride):raw(head));}
}
void initialize() {
    net.fill(0xABABABAB);other.fill(0xCDCDCDCD);member.fill(0xD0D0D0D0);
    lists.fill(0xE0E0E0E0);manager_a.fill(0xF0F0F0F0);manager_b.fill(0xF1F1F1F1);
    lock_cell=0x44440000;manager_index=args[10]&1;pool_enters=0;
    const U flags=args[0];
    put(net.data(),8,(flags&8)?0x26000000:0);put(net.data(),0xc,(flags&16)?0x26001000:0);
    put(net.data(),0x10,raw(&lock_cell));put(net.data(),0x14,(flags&4)?raw(member.data()):0);
    put(net.data(),0x28,args[1]);putbyte(net.data(),0xc7,flags&1);
    putbyte(net.data(),0xc2,(flags&2)?1:0);putbyte(net.data(),0xbf,0);
    putbyte(net.data(),0x106,(flags&32)?1:0);put(net.data(),0xdc,0x12345678);
    put(other.data(),8,args[2]==2?0:0x26002000);put(other.data(),0xc,0x26004000);
    putbyte(other.data(),0xbf,args[2]==3?1:0);put(other.data(),0xdc,0x87654321);
    startup_network_00628c70=args[2]?other.data():net.data();
    network_lifecycle_session_00628c74=(flags&64)?reinterpret_cast<void*>(0x26003000):nullptr;
    network_lifecycle_member_00628c7c=member.data();
    timer_rate_005deb48=args[3];
    init_list(0,args[6],0x10);init_list(0x100,args[7],0x18);
    put(member.data(),0,raw(lists.data())+0x100);put(member.data(),4,raw(lists.data()));
    put(member.data(),8,0x11112222);putbyte(member.data(),0x10,args[8]);
    put(member.data(),0x14,0x33334444);put(member.data(),0x1c,args[9]?0x25002000:0);
    put(member.data(),0x20,0x25003000);
    for(U index=0;index<2;++index){auto* m=index?manager_b.data():manager_a.data();
        put(m,0x28,0x27000000+index);put(m,0x38,0x25001000+index);put(m,0x3c,0x25001100+index);}
    network_lifecycle_callbacks_006b7c20={0x48ee90,0x11111111,0x48ee90,0x22222222,0,0x33333333,0x44444444,0x55555555};
}
}
void* __cdecl application_context_heap_state_005e4fe8(){return manager_index?manager_b.data():manager_a.data();}
void __cdecl heap_enter_005322b0(void* lock) {
    const U handle=raw(lock);event(0x5322b0,{norm(handle)});
    if(handle==lock_cell&&(args[5]&8))lock_cell=0x44441111;
    if(handle>=0x27000000&&handle<=0x2700ffff){
        ++pool_enters;
        auto* captured=load(manager_a.data(),0x28)==handle?manager_a.data():manager_b.data();
        if(args[5]&512)manager_index^=1;
        if(args[5]&1024){put(captured,0x38,0x25100000+pool_enters);put(captured,0x3c,0x25200000+pool_enters);put(captured,0x28,0x27001000+pool_enters);}
    }
}
void __cdecl heap_leave_005322c0(void* lock){event(0x5322c0,{norm(raw(lock))});}
void __cdecl heap_lock_destroy_005322d0(void* lock){event(0x5322d0,{norm(raw(lock))});}
void __cdecl network_lifecycle_unregister_00561110(U callback){event(0x561110,{callback});}
void __cdecl network_lifecycle_device_stop_00561b50(){event(0x561b50);if(args[5]&64)put(member.data(),0x1c,0x25002100);}
U __cdecl free_00531f90(void* p){event(0x531f90,{norm(raw(p))});return 1;}
void __cdecl network_lifecycle_device_cancel_00561730(U handle){event(0x561730,{handle});if(args[5]&128)put(member.data(),8,0x11113333);}
void __cdecl network_lifecycle_device_release_005617d0(U handle){event(0x5617d0,{handle});}
void __cdecl network_lifecycle_close_transport_0048c580(){event(0x48c580);if(args[5]&1)putbyte(net.data(),0xc2,0);}
void __fastcall application_network_message_0048c870(void* p,void*,U m,U a,U b,U c,U d){event(0x48c870,{norm(raw(p)),m,a,b,c,d});}
void __cdecl network_lifecycle_wait_0053c380(std::int32_t interval){event(0x53c380,{static_cast<U>(interval)});if(args[5]&2)putbyte(net.data(),0xc2,0);}
void __cdecl network_lifecycle_stop_session_00492260(){event(0x492260);}
U __cdecl application_release_0059f050(void* p){event(0x59f050,{norm(raw(p))});if(args[5]&4)put(net.data(),8,0x26006000);return 1;}
void __fastcall network_lifecycle_connection_destroy_0048aed0(void* p,void*){event(0x48aed0,{norm(raw(p))});}
void __fastcall network_lifecycle_session_destroy_00491fc0(void* p,void*){event(0x491fc0,{norm(raw(p))});if(args[5]&32)network_lifecycle_session_00628c74=reinterpret_cast<void*>(0x26007000);}
void __fastcall network_lifecycle_clear_lists_0048e790(void* p,void*){event(0x48e790,{norm(raw(p))});if(args[5]&16){putbyte(net.data(),0xc2,1);putbyte(net.data(),0xc0,0x77);put(net.data(),0xe0,0x98765432);}}
U __stdcall network_lifecycle_tick_count_0048a9a0(){event(0x48a9a0);return args[4];}
}

int main(){using namespace porsche;std::string line;
    while(std::getline(std::cin,line)){
        std::istringstream in(line);in>>operation;args.fill(0);for(auto& v:args)in>>v;
        events.clear();initialize();U result=0;
        if(operation==0)result=network_lifecycle_reset_0048e9c0(net.data(),nullptr);
        else if(operation==1)application_network_member_destroy_004935c0(member.data(),nullptr);
        else if(operation==2)network_lifecycle_remove_callback_00560180(args[0]);
        else application_network_reset_0048e9c0(net.data(),nullptr);
        std::cout<<"{\"result\":"<<result<<",\"trace\":[";
        for(std::size_t i=0;i<events.size();++i){if(i)std::cout<<',';std::cout<<'[';
            for(std::size_t j=0;j<events[i].size();++j){if(j)std::cout<<',';std::cout<<events[i][j];}std::cout<<']';}
        std::cout<<"],\"state\":[";bool first=true;
        const auto emit=[&](U v){if(!first)std::cout<<',';first=false;std::cout<<norm(v);};
        for(auto v:net)emit(v);for(auto v:other)emit(v);for(auto v:member)emit(v);for(auto v:lists)emit(v);
        for(auto v:manager_a)emit(v);for(auto v:manager_b)emit(v);
        for(auto v:network_lifecycle_callbacks_006b7c20)emit(v);
        emit(raw(startup_network_00628c70));emit(raw(network_lifecycle_session_00628c74));emit(raw(network_lifecycle_member_00628c7c));
        emit(lock_cell);emit(manager_index);std::cout<<"]}\n";
    }
}
