#include "../290-frame-service-cluster/frame_service_290.hpp"
#include "original_bytes_295.hpp"

extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(unsigned);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,unsigned,unsigned*,void*);

namespace porsche {
extern const float frame_limit_005b47d8 = 8000.0f;
extern const float frame_step_005b2764 = 10000.0f;
}

using U = std::uint32_t;
using Fn = void (__fastcall *)(void*);

static void copyBytes(void* destination,const void* source,U size) {
    auto* d=static_cast<volatile unsigned char*>(destination);
    auto* s=static_cast<const volatile unsigned char*>(source);
    for(U i=0;i<size;++i)d[i]=s[i];
}
static void zeroBytes(void* destination,U size) {
    auto* d=static_cast<volatile unsigned char*>(destination);
    for(U i=0;i<size;++i)d[i]=0;
}
static bool equalBytes(const void* left,const void* right,U size) {
    auto* a=static_cast<const volatile unsigned char*>(left);
    auto* b=static_cast<const volatile unsigned char*>(right);
    for(U i=0;i<size;++i)if(a[i]!=b[i])return false;
    return true;
}

static Fn copy_original(const unsigned char* bytes, U size, bool floats) {
    auto* p = static_cast<unsigned char*>(VirtualAlloc(nullptr,4096,0x3000,0x40));
    if (!p) ExitProcess(2);
    copyBytes(p,bytes,size);
    if (floats) {
        U replacements=0;
        for (U i=0;i+4<=size;++i) {
            U address=0; copyBytes(&address,p+i,4);
            if (address==0x005b47d8u) {
                address=reinterpret_cast<U>(&porsche::frame_limit_005b47d8);
                copyBytes(p+i,&address,4); ++replacements;
            } else if (address==0x005b2764u) {
                address=reinterpret_cast<U>(&porsche::frame_step_005b2764);
                copyBytes(p+i,&address,4); ++replacements;
            }
        }
        if (replacements!=2) ExitProcess(3);
    }
    return reinterpret_cast<Fn>(p);
}

template<class M> static Fn method(M member) {
    static_assert(sizeof(M)==sizeof(Fn),"single-inheritance x86 member pointer");
    Fn function; copyBytes(&function,&member,sizeof(function)); return function;
}

extern "C" void __cdecl entry() {
    U failures=0,cases=0;
    Fn iter=method(&porsche::FrameIterator_290::advance_00423840);
    Fn tail=method(&porsche::FrameTail_290::invoke_00482e50);
    Fn ref_iter=copy_original(original_00423840,sizeof(original_00423840),false);
    Fn ref_tail=copy_original(original_00482e50,sizeof(original_00482e50),true);
    alignas(4) U nodes[5][4];
    U ptr[5]; for(U i=0;i<5;++i)ptr[i]=reinterpret_cast<U>(nodes[i]);
    for(U variant=0;variant<6;++variant) {
        zeroBytes(nodes,sizeof(nodes));
        // +4 parent, +8 right, +12 left: exact original offsets.
        nodes[0][1]=ptr[1];nodes[1][1]=ptr[2];nodes[2][1]=ptr[3];nodes[3][1]=ptr[3];
        if (variant==0) {nodes[0][3]=ptr[1];nodes[1][2]=ptr[2];}
        if (variant==1) nodes[0][3]=ptr[1];
        if (variant==2) nodes[1][3]=ptr[0];
        if (variant==3) {nodes[1][3]=ptr[0];nodes[2][3]=ptr[1];}
        if (variant==4) {nodes[1][3]=ptr[0];nodes[2][3]=ptr[1];nodes[3][3]=ptr[2];}
        if (variant==5) nodes[0][2]=ptr[4];
        U a=ptr[0],b=ptr[0];iter(&a);ref_iter(&b);
        if (a!=b)++failures;
        ++cases;
    }
    constexpr U stride=0x38;
    for(U variant=0;variant<5;++variant) {
        alignas(4) unsigned char a[stride*4],b[stride*4];
        zeroBytes(a,sizeof(a));zeroBytes(b,sizeof(b));
        constexpr U value[4]={0x45f9f800u,0x45fa0000u,0x45fa0400u,0x7fc12345u};
        for(U i=0;i<4;++i) {
            copyBytes(a+i*stride+4,value+i,4);
            a[i*stride+0x34]=variant==1?0:1;
        }
        copyBytes(b,a,sizeof(a));
        U sa[17],sb[17];zeroBytes(sa,sizeof(sa));zeroBytes(sb,sizeof(sb));
        sa[6]=sb[6]=variant==0?0:variant==2?1:variant==3?3:4;
        sa[16]=reinterpret_cast<U>(a);sb[16]=reinterpret_cast<U>(b);
        tail(sa);ref_tail(sb);
        // The sole allowed self difference is the array pointer at +0x40.
        if (!equalBytes(a,b,sizeof(a))||!equalBytes(sa,sb,0x40))++failures;
        ++cases;
    }
    if (cases!=11)++failures;
    const char ok[]="{\"cases\":11,\"failures\":0}\n";U written=0;
    if (!failures) WriteFile(GetStdHandle(0xfffffff5u),ok,sizeof(ok)-1,&written,nullptr);
    ExitProcess(failures?1:0);
}
