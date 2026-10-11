#include "porsche/context_move.hpp"
#include <windows.h>
#include <intrin.h>
#include <cstdio>

namespace {
using U=std::uint32_t;
constexpr U B=0x27000000u,WATCH=B+0x1000u;
struct Access{U address,width,value,opcode;bool write;};
Access accesses[8192];U access_count;bool armed,pending,failed;
U reg(const CONTEXT* c,U index){
    const U values[]={c->Eax,c->Ecx,c->Edx,c->Ebx,c->Esp,c->Ebp,c->Esi,c->Edi};return values[index];
}
LONG CALLBACK observe(EXCEPTION_POINTERS* info){
    if(!armed)return EXCEPTION_CONTINUE_SEARCH;
    auto* record=info->ExceptionRecord;auto* context=info->ContextRecord;
    if(record->ExceptionCode==EXCEPTION_GUARD_PAGE){
        const U direction=static_cast<U>(record->ExceptionInformation[0]);
        const U address=static_cast<U>(record->ExceptionInformation[1]);
        if(direction>1||address<WATCH||address>=WATCH+0x1000u)return EXCEPTION_CONTINUE_SEARCH;
        auto* code=reinterpret_cast<const unsigned char*>(record->ExceptionAddress);
        U width=0,opcode=code[0],reg_index=0;
        if(code[0]==0x8b||code[0]==0x89){width=4;reg_index=(code[1]>>3u)&7u;}
        else if(code[0]==0x8a||code[0]==0x88){width=1;reg_index=(code[1]>>3u)&7u;}
        else if(code[0]==0x0f&&code[1]==0xb6){width=1;opcode=0x0fb6;reg_index=(code[2]>>3u)&7u;}
        if(!width||access_count>=8192){failed=true;return EXCEPTION_CONTINUE_SEARCH;}
        U value;
        if(direction){
            value=reg(context,reg_index);
            if(width==1){value=reg(context,reg_index&3u);value=(value>>(reg_index>=4u?8u:0u))&255u;}
        }else if(width==1)value=*reinterpret_cast<volatile const unsigned char*>(address);
        else value=*reinterpret_cast<volatile const U*>(address);
        accesses[access_count++]={address,width,value,opcode,direction!=0};
        pending=true;context->EFlags|=0x100u;return EXCEPTION_CONTINUE_EXECUTION;
    }
    if(record->ExceptionCode==EXCEPTION_SINGLE_STEP&&pending){
        DWORD prior;VirtualProtect(reinterpret_cast<void*>(WATCH),0x1000u,PAGE_READWRITE|PAGE_GUARD,&prior);
        pending=false;context->EFlags&=~0x100u;return EXCEPTION_CONTINUE_EXECUTION;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}
}
int main(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!VirtualAlloc(reinterpret_cast<void*>(B),0x3000u,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 2;
    auto handler=AddVectoredExceptionHandler(1,&observe);if(!handler)return 3;
    U id,source,destination,bytes;
    while(scanf_s("%u %x %x %u",&id,&source,&destination,&bytes)==4){
        for(U i=0;i<0x3000u;++i)reinterpret_cast<unsigned char*>(B)[i]=static_cast<unsigned char>(i*29u+id*7u+0x31u);
        access_count=0;pending=failed=false;armed=true;DWORD prior;
        if(!VirtualProtect(reinterpret_cast<void*>(WATCH),0x1000u,PAGE_READWRITE|PAGE_GUARD,&prior))return 4;
        const U result=reinterpret_cast<U>(porsche::context_move_005a1a40(
            reinterpret_cast<void*>(destination),reinterpret_cast<void*>(source),bytes));
        const U flags=static_cast<U>(__readeflags());
        VirtualProtect(reinterpret_cast<void*>(WATCH),0x1000u,PAGE_READWRITE,&prior);
        armed=false;if(failed)return 5;
        std::printf("{\"case\":%u,\"result\":\"%08x\",\"direction_flag_clear\":%s,\"memory\":\"",id,result,(flags&0x400u)?"false":"true");
        for(U i=0;i<0x3000u;++i)std::printf("%02x",reinterpret_cast<unsigned char*>(B)[i]);
        std::printf("\",\"accesses\":[");
        for(U i=0;i<access_count;++i){const auto& a=accesses[i];
            std::printf("%s{\"op\":\"%c\",\"va\":\"%08x\",\"bytes\":%u,\"value\":\"%08x\",\"native_opcode\":\"%04x\"}",i?",":"",a.write?'w':'r',a.address,a.width,a.value,a.opcode);}
        std::puts("]}");
    }
    RemoveVectoredExceptionHandler(handler);return 0;
}
