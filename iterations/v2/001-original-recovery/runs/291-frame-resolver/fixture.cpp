#include "../290-frame-service-cluster/frame_service_290.hpp"
#include <cstring>
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(unsigned);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,unsigned,unsigned*,void*);
using U=std::uint32_t;

extern "C" __declspec(naked) void* __fastcall reference291(void*,void*,void*,U) {
    __asm {
        mov eax,[esp+4]
        mov ecx,[ecx+14h]
        mov dx,word ptr [esp+8]
        mov [eax],ecx
        mov byte ptr [eax+4],0
        mov [eax+6],dx
        ret 8
    }
}

// Capture the ABI around the raw ECX/two-stack-slot call, preserving host registers.
extern "C" __declspec(naked) void __cdecl capture291(void*,void*,void*,U,U*) {
    __asm {
        push ebp
        mov ebp,esp
        push ebx
        push esi
        push edi
        mov eax,[ebp+24]
        mov [eax+24],ebp
        mov ebx,12345678h
        mov esi,76543210h
        mov edi,89abcdefh
        push dword ptr [ebp+20]
        push dword ptr [ebp+16]
        mov ecx,[ebp+12]
        cld
        call dword ptr [ebp+8]
        mov edx,[ebp+24]
        mov [edx],eax
        lea eax,[ebp-12]
        sub eax,esp
        mov [edx+4],eax
        mov [edx+8],ebx
        mov [edx+12],esi
        mov [edx+16],edi
        pushfd
        pop eax
        and eax,400h
        mov [edx+20],eax
        mov [edx+28],ebp
        pop edi
        pop esi
        pop ebx
        pop ebp
        ret
    }
}

extern "C" void __cdecl entry() {
    constexpr U values[]={0,1,0x7fffffff,0x80000000,0xffffffff,0x81234567,0xfedcba98,0x00010000};
    constexpr U tags[]={0,1,0x7fff,0x8000,0xffff,0xabcd1234,0xaaaa0000,0xffffffff};
    constexpr U offsets[]={0,16,32,48,52,56,64,80};
    auto member=&porsche::FrameResolver_290::resolve_004898f0;
    static_assert(sizeof(member)==sizeof(void*));
    void* game;std::memcpy(&game,&member,4);
    U failures=0,cases=0;
    for(U value:values)for(U tag:tags)for(U offset:offsets) {
        alignas(4) unsigned char a[128],b[128];
        for(U i=0;i<128;++i)a[i]=b[i]=static_cast<unsigned char>(0xa5u+i*13u);
        std::memcpy(a+52,&value,4);std::memcpy(b+52,&value,4);
        U ca[8]{},cb[8]{};
        capture291(game,a+32,a+offset,tag,ca);
        capture291(reinterpret_cast<void*>(&reference291),b+32,b+offset,tag,cb);
        for(U i=0;i<128;++i)if(a[i]!=b[i])++failures;
        if(ca[0]!=reinterpret_cast<U>(a+offset)||cb[0]!=reinterpret_cast<U>(b+offset))++failures;
        for(U j=0;j<2;++j) {
            const U* state=j?cb:ca;
            if(state[1]||state[2]!=0x12345678||state[3]!=0x76543210||state[4]!=0x89abcdef||state[5]||state[6]!=state[7])++failures;
        }
        ++cases;
    }
    if(cases!=512)++failures;
    const char ok[]="{\"cases\":512,\"failures\":0}\n";U written=0;
    if(!failures)WriteFile(GetStdHandle(0xfffffff5u),ok,sizeof(ok)-1,&written,nullptr);
    ExitProcess(failures?1:0);
}
