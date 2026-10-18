#include "action_297.hpp"
#include <cstring>
#include <initializer_list>
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(unsigned);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,unsigned,unsigned*,void*);
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
using U=std::uint32_t;
static unsigned char original[]={
#include "original-body.inc"
};
alignas(16) static unsigned char arena[4096],initial[4096],expected[4096];
static U events[128],wanted[128],eventCount,scenario,failures,cases;
static void copyBytes(void* destination,const void* source,U size) {
    auto* d=static_cast<volatile unsigned char*>(destination);
    auto* s=static_cast<const volatile unsigned char*>(source);
    while(size--) *d++=*s++;
}
static int compareBytes(const void* left,const void* right,U size) {
    auto* a=static_cast<const volatile unsigned char*>(left);
    auto* b=static_cast<const volatile unsigned char*>(right);
    while(size--) if(*a++!=*b++) return 1;
    return 0;
}
static U address(unsigned n) { return reinterpret_cast<U>(arena+n); }
static U& cell(U p) { return *reinterpret_cast<U*>(p); }
static U& at(unsigned n) { return cell(address(n)); }
static void event(U id,U a,U b) { if(eventCount+3>128) { ++failures;return; } events[eventCount++]=id;events[eventCount++]=a;events[eventCount++]=b; }
// Test providers are excluded from the game COFF. Their side effects exercise
// precisely the state the original reloads after direct and virtual calls.
void __thiscall porsche::FrameActionBoundary_297::update_00476710(U index) {
    event(1,reinterpret_cast<U>(this),index);
    if(index==0) {
        if(scenario==1) at(0xc)=address(768);
        if(scenario==2) at(4)=address(96);
        if(scenario==3) at(64+0x18)=1;
        if(scenario==4) at(64+0x18)=3;
        if(scenario==5) at(256+0x1c)=address(1600);
    }
}
extern "C" U __fastcall destroy297(void* object,void*,U arg) {
    event(2,reinterpret_cast<U>(object),arg);
    if(scenario==6) at(0xc)=address(768);
    if(scenario==7) at(4)=address(96);
    if(scenario==8) at(64+0x18)=1;
    return 0xdeadbeef;
}
extern "C" void __fastcall update297(void* object,void*) {
    event(3,reinterpret_cast<U>(object),0);
    if(scenario==9) at(0xc)=address(768);
    if(scenario==10) at(4)=address(96);
}
// ABI capture: no stack parameters, original ECX self, RET0, preserved x86
// nonvolatiles and DF=0. EAX/ECX/EDX/condition flags are caller-clobbered.
extern "C" __declspec(naked) void __cdecl capture297(void*,void*,U*) {
    __asm {
        push ebp
        mov ebp,esp
        push ebx
        push esi
        push edi
        mov ebx,12345678h
        mov esi,76543210h
        mov edi,89abcdefh
        mov ecx,[ebp+12]
        cld
        call dword ptr [ebp+8]
        mov edx,[ebp+16]
        lea eax,[ebp-12]
        sub eax,esp
        mov [edx],eax
        mov [edx+4],ebx
        mov [edx+8],esi
        mov [edx+12],edi
        pushfd
        pop eax
        and eax,400h
        mov [edx+16],eax
        pop edi
        pop esi
        pop ebx
        pop ebp
        ret
    }
}
static void initialize(U mode,U count,U variant) {
    for(U i=0;i<sizeof(arena);++i) arena[i]=static_cast<unsigned char>(0xa5+i*13);
    scenario=mode;eventCount=0;
    at(4)=address(64);at(0xc)=address(256);at(64+0x18)=count;at(96+0x18)=2;
    for(U table: {256u,768u}) for(U i=0;i<3;++i) {
        const U slot=table+i*0x38,object=1408+i*64;
        at(slot+0x1c)=address(object);at(slot+0x2c)=variant%2;
        at(slot+0x34)=address(2304+i*64);
        at(object)=address(2048);arena[object+4]=static_cast<unsigned char>((variant/2)%3==0?0:((variant/2)%3==1?1:255));
    }
    at(1600)=address(2048);arena[1604]=0;
    at(2048)=reinterpret_cast<U>(&destroy297);at(2048+0x1c)=reinterpret_cast<U>(&update297);
    if(mode==11) at(256+0x1c)=0;
    if(mode>=12) {
        // REP MOVSD identity and overlap in both directions; copied pointer
        // and fields must be read again on each forward iteration.
        const U deltas[]={0,4,8,12,16,20,0xfffffffcu,0xfffffff8u};
        at(256+0x34)=address(256+0x1c)+deltas[mode-12];
        at(64+0x18)=1;
    }
}
extern "C" void __cdecl entry() {
    auto* reference=static_cast<unsigned char*>(VirtualAlloc(nullptr,sizeof(original),0x3000,0x40));
    if(!reference) ExitProcess(2);
    copyBytes(reference,original,sizeof(original));
    auto member=&porsche::FrameActionBoundary_297::update_00476710;
    U boundary=0;static_assert(sizeof(member)==4);copyBytes(&boundary,&member,4);
    // The only relocated bytes are the original CALL00476710 REL32 operand.
    const U displacement=boundary-reinterpret_cast<U>(reference+48);
    copyBytes(reference+44,&displacement,4);
    auto action=&porsche::FrameAction_290::invoke_00476170;
    void* game=nullptr;copyBytes(&game,&action,4);
    for(U mode=0;mode<20;++mode)for(U count=0;count<4;++count)for(U variant=0;variant<6;++variant) {
        initialize(mode,count,variant);
        copyBytes(initial,arena,sizeof(arena));
        U actualAbi[5]{},originalAbi[5]{};
        capture297(reference,arena,originalAbi);
        copyBytes(expected,arena,sizeof(arena));
        U expectedCount=eventCount;copyBytes(wanted,events,sizeof(events));
        copyBytes(arena,initial,sizeof(arena));eventCount=0;
        capture297(game,arena,actualAbi);
        if(compareBytes(arena,expected,sizeof(arena))||eventCount!=expectedCount||compareBytes(events,wanted,eventCount*4)) ++failures;
        for(U* abi: {actualAbi,originalAbi}) if(abi[0]||abi[1]!=0x12345678||abi[2]!=0x76543210||abi[3]!=0x89abcdef||abi[4]) ++failures;
        ++cases;
    }
    const char ok[]="{\"cases\":480,\"failures\":0}\n";U written=0;
    if(!failures&&cases==480) WriteFile(GetStdHandle(0xfffffff5u),ok,sizeof(ok)-1,&written,nullptr);
    ExitProcess(failures||cases!=480?1:0);
}
