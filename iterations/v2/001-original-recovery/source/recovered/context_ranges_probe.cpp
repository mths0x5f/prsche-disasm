#include "porsche/context_ranges.hpp"
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace {
using U=std::uint32_t;
constexpr U B=0x25000000u,M=B+0x400u,ALT=B+0x700u,S=B+0x200u;
constexpr U OBJ=B+0x1000u,BLOCK=B+0x1500u,ARR=B+0x1800u,P=B+0x2000u,Q=B+0x4000u,Z=B+0x6000u;
U manager,selector;int id,enters,leaves,copies;std::string trace;
U range_reads[8],range_read_count;bool guarded,guard_pending;
LONG CALLBACK watch_range_reads(EXCEPTION_POINTERS* info){
    if(!guarded)return EXCEPTION_CONTINUE_SEARCH;
    const auto code=info->ExceptionRecord->ExceptionCode;
    if(code==EXCEPTION_GUARD_PAGE && info->ExceptionRecord->ExceptionInformation[0]==0){
        const U address=static_cast<U>(info->ExceptionRecord->ExceptionInformation[1]);
        if(address<B+0x1000u||address>=B+0x2000u)return EXCEPTION_CONTINUE_SEARCH;
        if(range_read_count<8)range_reads[range_read_count++]=address;
        guard_pending=true;info->ContextRecord->EFlags|=0x100u;
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    if(code==EXCEPTION_SINGLE_STEP && guard_pending){
        DWORD prior;VirtualProtect(reinterpret_cast<void*>(B+0x1000u),0x1000u,PAGE_READWRITE|PAGE_GUARD,&prior);
        guard_pending=false;info->ContextRecord->EFlags&=~0x100u;
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}
U get(U a){U x;std::memcpy(&x,reinterpret_cast<void*>(a),4);return x;}
void put(U a,U x){std::memcpy(reinterpret_cast<void*>(a),&x,4);}
void event(const char* name,U a,U b=0,U c=0){char line[100];std::snprintf(line,sizeof(line),"%s:%08x:%08x:%08x;",name,a,b,c);trace+=line;}
U mode(){return id==22?1u:id==35?2u:0u;}
U kind(){return id==22||id==32?0u:id==33?31u:id==35?1u:3u;}
U state(){return M-mode()*140u+0x28u;}
void* __cdecl allocate(const char* src,U bytes,U heap){
    event("alloc",reinterpret_cast<U>(src),bytes,heap);
    if(id==27)put(M+0x2cu,Q);
    if(id==28)porsche::application_page_size_006af3f8=64;
    return reinterpret_cast<void*>(P);
}
void seed(){
    for(U x=0;x<0x7000u;++x)reinterpret_cast<unsigned char*>(B)[x]=static_cast<unsigned char>(x*13u+0x35u);
    manager=M;selector=S;enters=leaves=copies=0;trace.clear();range_read_count=0;
    porsche::application_page_size_006af3f8=(id==22?24u:(id==23||id==24||id==36)?8u:id==35?40u:4096u);
    for(U m=0;m<3;++m){U s=M-m*140u+0x28u;put(s,0x11110000u+m);put(s+4,P);put(s+8,Z);
        for(U k=0;k<32;++k)put(s+0xcu+k*4u,BLOCK);}
    put(ALT+0x28u,0x22220000u);put(ALT+0x2cu,Q);put(S,7);
    put(M+4,reinterpret_cast<U>(&allocate));put(ALT+4,reinterpret_cast<U>(&allocate));
    put(OBJ,BLOCK);put(OBJ+8,BLOCK+32);put(P+4,Q);put(Q+4,0);
    put(ARR+4,Q);put(ARR+8,Z);
    if(id==8)put(OBJ,0);
    if(id==9)put(OBJ+8,BLOCK);
    if(id==11)put(OBJ+8,BLOCK+257);
    if(id==12)put(OBJ+8,BLOCK-4);
    if(id==21||id==23||id==27||id==28||id==29||id==32||id==34)put(state()+4,0);
    if(id==36)put(state()+4,state()-4u);
    if(id==37){put(OBJ,OBJ);put(OBJ+8,OBJ+32);}
}
}
namespace porsche {
U application_page_size_006af3f8;
void* __cdecl application_context_heap_state_005e4fe8(){return reinterpret_cast<void*>(manager);}
U __cdecl application_context_heap_selector_005e4fec(){return get(selector);}
void __cdecl heap_enter_005322b0(void* lock){
    event("enter",reinterpret_cast<U>(lock));++enters;
    if(id==14){put(OBJ,0);put(OBJ+8,0xffffffff);put(M+0x28,0x88880000);}
    if(id==25)put(state()+4,Q);
    if(id==26)manager=ALT;
    if(id==27&&enters==2)manager=ALT;
    if(id==30)put(state(),0x99990000);
    if(id==34&&enters==2)put(S,99);
}
void __cdecl heap_leave_005322c0(void* lock){
    event("leave",reinterpret_cast<U>(lock));++leaves;
    if(id==29&&leaves==1)put(state()+4,Q);
}
void* __cdecl application_context_member_block_0059ecb0(U bytes,U heap,U source){
    auto callback=reinterpret_cast<void* (__cdecl*)(const char*,U,U)>(get(manager+4));
    return callback(reinterpret_cast<const char*>(source),bytes,heap);
}
void __cdecl context_table_release_0059ecd0(void* block){event("table_release",reinterpret_cast<U>(block));}
U __cdecl application_release_0059f050(void* block){event("heap_release",reinterpret_cast<U>(block));return 0xcafe0071;}
void* __fastcall application_context_copy_range_005299d0(void* dst,void*,const void* src){
    const U source=reinterpret_cast<U>(src),dest=reinterpret_cast<U>(dst);
    event("copy01",get(source),get(source+4),get(source+8));event("copy3",get(source+12));
    ++copies;
    if(id==1&&copies==1)put(source,0xabcdef12);
    if(id==2&&copies==2)put(source+8,0x31415926);
    for(U off=0;off<16;off+=4)put(dest+off,get(source+off));
    return dst;
}
#if defined(CONTEXT_RANGES_EXTERNAL_WALK)
void __cdecl context_range_walk_00529c50(ApplicationContextRange16 first,ApplicationContextRange16 last,U captured){
    event("walk01",first.words[0],first.words[1],first.words[2]);event("walk3",first.words[3]);
    event("walk45",last.words[0],last.words[1],last.words[2]);event("walk7",last.words[3],captured);
}
#endif
}
int main(int argc,char** argv){
    if(argc!=2)return 2;id=std::atoi(argv[1]);
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!VirtualAlloc(reinterpret_cast<void*>(B),0x7000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 3;
    seed();U result=0;using namespace porsche;
    if(id<4){ApplicationContextRange16 a{{P+0x1fcu,0x11223344,P+0x200u,ARR}},b{{Z+4u,0x55667788,0x99aabbcc,0xdeadbeef}};
        if(id==3){a={};b={};}application_context_compare_ranges_00529c20(a,b,0x98765432);}
    else if(id<8){ApplicationContextRange16 a{{P,0,P+0x200u,ARR}},b{{P,0,0,0}};
        if(id==5)b.words[0]=P+16u;
        if(id==6){a.words[0]=P+0x1fcu;b.words[0]=Q+8u;}
        if(id==7){a.words[0]=P+0x1fcu;b.words[0]=Z+4u;}
        auto handler=AddVectoredExceptionHandler(1,&watch_range_reads);
        if(!handler)return 4;
        DWORD prior;guarded=true;
        if(!VirtualProtect(reinterpret_cast<void*>(B+0x1000u),0x1000u,PAGE_READWRITE|PAGE_GUARD,&prior))return 5;
        context_range_walk_00529c50(a,b,0x98765432);
        VirtualProtect(reinterpret_cast<void*>(B+0x1000u),0x1000u,PAGE_READWRITE,&prior);
        guarded=false;RemoveVectoredExceptionHandler(handler);}
    else if(id<15||id==37){U flags=id==9?1u:id==11?3u:id==13?0x100u:id==37?1u:0u;
        result=reinterpret_cast<U>(application_context_release_node_004e4560(reinterpret_cast<void*>(OBJ),nullptr,flags));}
    else if(id<20){const U counts[]={0,1,8,9,0x08000001};application_context_notify_node_004d7da0(reinterpret_cast<void*>(BLOCK),counts[id-15]);}
    else application_context_new_head_0059eeb0(kind(),mode());
    put(M+4,0x006f0000);put(ALT+4,0x006f0000);
    std::printf("{\"case\":%d,\"result\":\"%08x\",\"manager\":\"%08x\",\"page_size\":\"%08x\",\"trace\":\"%s\",\"memory\":\"",id,result,manager,application_page_size_006af3f8,trace.c_str());
    for(U x=0;x<0x7000u;++x)std::printf("%02x",reinterpret_cast<unsigned char*>(B)[x]);
    std::printf("\",\"range_node_reads\":[");
    for(U i=0;i<range_read_count;++i)std::printf("%s{\"va\":\"%08x\",\"bytes\":4}",i?",":"",range_reads[i]);
    std::puts("]}");return 0;
}
