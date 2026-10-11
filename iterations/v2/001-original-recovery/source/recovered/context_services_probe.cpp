#include "porsche/context_services.hpp"
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace {
using U=std::uint32_t;
constexpr U B=0x26000000u,OBJ=B+0x1000u,SRC=B+0x1100u,STR=B+0x1400u,BLOCK=B+0x2000u,ALT=B+0x2800u,M=B+0x400u;
int id;std::string trace;
U get(U a){U x;std::memcpy(&x,reinterpret_cast<void*>(a),4);return x;}
void put(U a,U x){std::memcpy(reinterpret_cast<void*>(a),&x,4);}
void event(const char* name,U a,U b=0,U c=0){char line[100];std::snprintf(line,sizeof(line),"%s:%08x:%08x:%08x;",name,a,b,c);trace+=line;}
U text_size(){return id==4||id==9?0u:id==5?1u:id==6||id==10||id==18?255u:id==61?511u:7u;}
void seed(){
    for(U i=0;i<0x5000u;++i)reinterpret_cast<unsigned char*>(B)[i]=static_cast<unsigned char>(i*17u+0x29u);
    trace.clear();put(OBJ,BLOCK);put(OBJ+4,BLOCK+7);put(OBJ+8,BLOCK+8);
    put(SRC,STR);put(SRC+4,STR+7);put(SRC+8,STR+20);
    for(U i=0;i<text_size();++i)reinterpret_cast<unsigned char*>(STR)[i]=static_cast<unsigned char>('A'+i%26u);
    reinterpret_cast<unsigned char*>(STR)[text_size()]=0;
    put(M+0x28,0x11110000u);
    for(U k=0;k<32;++k)put(M+0x34+k*4,ALT);
    if(id==25)put(SRC+4,STR);
    if(id==27)put(OBJ-4,0);
    if(id==30)put(OBJ,0);
    if(id==31)put(OBJ+8,BLOCK);
    if(id==33)put(OBJ+8,BLOCK+256);
    if(id==34)put(OBJ+8,BLOCK+257);
    if(id==35)put(OBJ+8,BLOCK-1);
    if(id==37){put(OBJ,OBJ);put(OBJ+8,OBJ+32);}
    if(id>=38&&id<=44){const U difference[]={0,4,7,0xffffffff,0xfffffffc,0x80000000,0x7fffffff};put(OBJ+4,BLOCK+difference[id-38]);}
    if(id>=50&&id<=52){const U ends[]={0,7,0xffffffff};put(OBJ+4,ends[id-50]);}
    if(id>=53&&id<=57){const U a[]={0,0xffffffff,0,0xffffffff,0x12345678},b[]={0,0xffffffff,1,0,0x87654321};put(SRC,a[id-53]);put(SRC+4,b[id-53]);}
    if(id==60){put(SRC+1,STR+1);put(SRC+5,STR+6);}
}
}
namespace porsche {
void* __cdecl application_context_heap_state_005e4fe8(){return reinterpret_cast<void*>(M);}
void* __cdecl application_context_member_storage_004211d0(U bytes,U mode){
    event("allocate",bytes,mode);
    if(id==12||id==22)*reinterpret_cast<unsigned char*>(STR)=0;
    if(id==13){put(OBJ,ALT);put(OBJ+4,ALT);put(OBJ+8,ALT);put(OBJ+12,0x13572468);}
    if(id==28){put(SRC,ALT);put(SRC+4,ALT);}
    return reinterpret_cast<void*>(id==15||id==23?OBJ:id==19?STR+2:BLOCK);
}
void* __cdecl context_move_005a1a40(void* dest,const void* source,U bytes){
    event("copy",reinterpret_cast<U>(dest),reinterpret_cast<U>(source),bytes);
    if(id==14||id==21||id==29){put(OBJ,ALT);put(OBJ+4,0x12345678);put(OBJ+8,0x87654321);}
    if(bytes&&bytes<0x10000u)std::memmove(dest,source,bytes);
    return dest;
}
void __cdecl context_table_release_0059ecd0(void* block){event("table_release",reinterpret_cast<U>(block));}
void __cdecl heap_enter_005322b0(void* lock){event("enter",reinterpret_cast<U>(lock));
    if(id==36){put(OBJ,0);put(OBJ+8,0);put(M+0x28,0x88880000);}}
void __cdecl heap_leave_005322c0(void* lock){event("leave",reinterpret_cast<U>(lock));}
}
int main(int argc,char** argv){
    if(argc!=2)return 2;id=std::atoi(argv[1]);SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!VirtualAlloc(reinterpret_cast<void*>(B),0x5000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 3;
    seed();U result=0;using namespace porsche;auto object=reinterpret_cast<void*>(OBJ);
    if(id<2)result=reinterpret_cast<U>(context_identity_00423610(id?object:nullptr,nullptr));
    else if(id<4||id==63)result=reinterpret_cast<U>(context_empty_range_00505810(reinterpret_cast<void*>(OBJ+(id==3?1:0)),nullptr,id==63?OBJ:0xffffffff));
    else if(id<8||id==61)result=context_strlen_004d55c0(reinterpret_cast<const char*>(STR+(id==7?1:0)));
    else if(id<16||id==58){result=reinterpret_cast<U>(context_string_construct_004d64a0(object,nullptr,reinterpret_cast<const char*>(id==11?OBJ:STR),0xdeadbeef));if(id==58)context_string_destroy_00429840(object,nullptr);}
    else if(id<24||id==59){U first=STR,last=STR+(id==16?0u:id==18?255u:7u);if(id==20){first=STR;last=STR-2;}
        result=reinterpret_cast<U>(context_string_assign_range_004298a0(object,nullptr,reinterpret_cast<void*>(first),reinterpret_cast<void*>(last)));
        if(id==59)result=static_cast<U>(context_vector_count_004d6510(object,nullptr));}
    else if(id<30||id==60)result=reinterpret_cast<U>(context_string_copy_00429bf0(object,nullptr,reinterpret_cast<void*>(id==26?OBJ:id==27?OBJ-4:id==60?SRC+1:SRC)));
    else if(id<38)context_string_destroy_00429840(object,nullptr);
    else if(id<45)result=static_cast<U>(context_vector_count_004d6510(object,nullptr));
    else if(id<50){const U index[]={0,1,0xffffffff,0x40000000,0x80000001};result=reinterpret_cast<U>(context_vector_at_004d6520(object,nullptr,index[id-45]));}
    else if(id<53)context_vector_pop_004d6530(object,nullptr);
    else result=context_word_not_equal_004d67b0(reinterpret_cast<void*>(SRC),reinterpret_cast<void*>(id==62?SRC:SRC+4));
    std::printf("{\"case\":%d,\"result\":\"%08x\",\"trace\":\"%s\",\"memory\":\"",id,result,trace.c_str());
    for(U i=0;i<0x5000u;++i)std::printf("%02x",reinterpret_cast<unsigned char*>(B)[i]);
    std::puts("\"}");return 0;
}
