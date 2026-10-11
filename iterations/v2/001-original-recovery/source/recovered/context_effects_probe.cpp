#include "porsche/context_effects.hpp"
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace {
using U = std::uint32_t;
constexpr U B=0x24000000u, M=B+0x400u, ALT=B+0x700u, S=B+0x200u;
constexpr U N=B+0x1000u, C=B+0x1100u, T=B+0x1200u, R=B+0x1500u;
int id; U manager, selector; std::string trace;
U get(U a){ U x; std::memcpy(&x,reinterpret_cast<void*>(a),4); return x; }
void put(U a,U x){std::memcpy(reinterpret_cast<void*>(a),&x,4);}
void event(const char* name,U a,U b=0,U c=0){char line[100]; std::snprintf(line,sizeof(line),"%s:%08x:%08x:%08x;",name,a,b,c);trace+=line;}
void* __cdecl allocate(const char* src,U bytes,U heap){
    event("alloc",reinterpret_cast<U>(src),bytes,heap);
    if(id==1) manager=ALT;
    return reinterpret_cast<void*>(id==0?0:R);
}
void __cdecl release(void* block){event("release",reinterpret_cast<U>(block));if(id==21)manager=ALT;}
void tables(U a){put(a+4,reinterpret_cast<U>(&allocate));put(a+8,reinterpret_cast<U>(&release));}
void seed(){
    for(U x=0;x<0x2000u;++x)reinterpret_cast<unsigned char*>(B)[x]=static_cast<unsigned char>(x*19u+0x17u);
    manager=M;selector=S;trace.clear();
    for(U mode=0;mode<3;++mode){
        U p=M-mode*140u+0x28u;put(p,0x11110000u+mode);
        for(U k=0;k<32;++k)put(p+0xcu+k*4u,N);
        put(S-mode*4u,7u+mode);
    }
    put(ALT+0x28u,0x22220000u);
    for(U k=0;k<32;++k)put(ALT+0x34u+k*4u,T);
    tables(M);tables(ALT);
    put(N+4,C);put(C+4,T);put(T+4,0);
    if(id==6)put(M+0x28u+0xcu+3u*4u,0);
    if(id>=19){
        for(U n:{N,C,T}){put(n+8,0);put(n+0xc,0);put(n+0x10,0);put(n+0x18,0);}
        put(N+0xc,C);put(N+8,T);
        put(C+0x10,R);put(C+0x18,R+16);
        put(N+0x10,R+0x100);put(N+0x18,R+0x100+257);
        if(id==22){put(C+0x10,R);put(C+0x18,R);}
    }
}
}
namespace porsche {
void* __cdecl application_context_heap_state_005e4fe8(){return reinterpret_cast<void*>(manager);}
void* __cdecl context_selector_pointer_005e4fec(){return reinterpret_cast<void*>(selector);}
void __cdecl heap_enter_005322b0(void* lock){
    event("enter",reinterpret_cast<U>(lock));
    if(id==7){put(M+0x28u,0x55550000u);put(M+0x28u+0xcu+3u*4u,C);}
    if(id==8)manager=ALT;
    if(id==23){put(C+8,T);put(N+8,0);}
}
void __cdecl heap_leave_005322c0(void* lock){event("leave",reinterpret_cast<U>(lock));}
void __cdecl application_context_new_head_0059eeb0(U kind,U mode){
    event("refill",kind,mode);put(M-mode*140u+0x28u+0xcu+kind*4u,C);
    put(M-mode*140u+0x28u,0x77770000u);
}
}
int main(int argc,char** argv){
    if(argc!=2)return 2;id=std::atoi(argv[1]);
    if(!VirtualAlloc(reinterpret_cast<void*>(B),0x2000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 3;
    seed();U result=0;
    using namespace porsche;
    switch(id){
    case 0:case 1:result=reinterpret_cast<U>(application_context_member_block_0059ecb0(id?123:0,0x89abcdef,0x005cbdb4));break;
    case 2:context_table_release_0059ecd0(nullptr);break;
    case 3:application_context_clear_004237d0(reinterpret_cast<void*>(R),257,1);break;
    case 4:result=reinterpret_cast<U>(application_context_member_storage_004211d0(1,0));break;
    case 5:result=reinterpret_cast<U>(application_context_member_storage_004211d0(256,1));break;
    case 6:case 7:case 8:result=reinterpret_cast<U>(application_context_member_storage_004211d0(32,0));break;
    case 9:result=reinterpret_cast<U>(application_context_member_storage_004211d0(257,0));break;
    case 10:result=reinterpret_cast<U>(application_context_member_storage_004211d0(0xffffffff,2));break;
    case 11:application_context_clear_004237d0(reinterpret_cast<void*>(R),1,0);break;
    case 12:application_context_clear_004237d0(reinterpret_cast<void*>(R),256,1);break;
    case 13:application_context_clear_004237d0(reinterpret_cast<void*>(R),257,2);break;
    case 14:application_context_member_destroy_block_00441200(reinterpret_cast<void*>(R),256);break;
    case 15:application_context_member_destroy_block_00441200(reinterpret_cast<void*>(R),257);break;
    case 16:context_free_00424000(reinterpret_cast<void*>(R),0);break;
    case 17:context_free_00424000(reinterpret_cast<void*>(R),8);break;
    case 18:context_free_00424000(reinterpret_cast<void*>(R),257);break;
    default:application_context_unlink_005262e0(reinterpret_cast<void*>(B+0x1800),nullptr,id==19?0:N);break;
    }
    // Normalize only function-pointer identities, never mutated data fields.
    for(U a:{M,ALT}){put(a+4,0x006f0000);put(a+8,0x006f0010);}
    std::printf("{\"case\":%d,\"result\":\"%08x\",\"manager\":\"%08x\",\"trace\":\"%s\",\"memory\":\"",id,result,manager,trace.c_str());
    for(U x=0;x<0x2000u;++x)std::printf("%02x",reinterpret_cast<unsigned char*>(B)[x]);
    std::puts("\"}");return 0;
}
