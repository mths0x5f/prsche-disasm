#include "copy_backends.hpp"

#include <cstdint>

namespace porsche {

// Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Indexed ranges: 005b0100..0124+0140..0281, 005b02c0..02e4+0302..0461,
// 005b0480..049e+04a0..058b. The helpers below retain the original load/store
// grouping, including the observable x87, MMX and XMM state. Control flow stays
// in C++; none of the three original bodies calls another function.
static_assert(sizeof(void*) == 4, "original copy backend requires Win32");

namespace {
using B = std::uint8_t;
using U = std::uint32_t;

bool nonnegative(U n) { return (n & 0x80000000u) == 0; }
bool signed_ge(U n, U x) { return static_cast<std::int32_t>(n) >= static_cast<std::int32_t>(x); }

template<class T> void scalar(B*& d, const B*& s, U& n) {
    const T value = *reinterpret_cast<const volatile T*>(s);
    *reinterpret_cast<volatile T*>(d) = value;
    d += sizeof(T); s += sizeof(T); n -= sizeof(T);
}

// These small hardware helpers are necessary because integer qword copies do
// not execute FILD/FISTP, and compiler-selected MMX/XMM registers change state.
void x87_128(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        fild qword ptr [edx]
        fild qword ptr [edx+20h]
        fild qword ptr [edx+40h]
        fild qword ptr [edx+60h]
        fxch st(3)
        fild qword ptr [edx+10h]
        fild qword ptr [edx+8]
        fild qword ptr [edx+18h]
        fxch st(3)
        fistp qword ptr [eax]
        fistp qword ptr [eax+8]
        fistp qword ptr [eax+10h]
        fistp qword ptr [eax+18h]
        fxch
        fild qword ptr [edx+30h]
        fild qword ptr [edx+28h]
        fild qword ptr [edx+38h]
        fxch st(3)
        fistp qword ptr [eax+20h]
        fistp qword ptr [eax+28h]
        fistp qword ptr [eax+30h]
        fistp qword ptr [eax+38h]
        fild qword ptr [edx+50h]
        fild qword ptr [edx+48h]
        fild qword ptr [edx+58h]
        fxch st(3)
        fistp qword ptr [eax+40h]
        fistp qword ptr [eax+48h]
        fistp qword ptr [eax+50h]
        fistp qword ptr [eax+58h]
        fild qword ptr [edx+70h]
        fild qword ptr [edx+68h]
        fild qword ptr [edx+78h]
        fxch st(3)
        fistp qword ptr [eax+60h]
        fistp qword ptr [eax+68h]
        fistp qword ptr [eax+70h]
        fistp qword ptr [eax+78h]
    }
}
void x87_32(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        fild qword ptr [edx]
        fild qword ptr [edx+8]
        fxch
        fistp qword ptr [eax]
        fistp qword ptr [eax+8]
        fild qword ptr [edx+10h]
        fild qword ptr [edx+18h]
        fxch
        fistp qword ptr [eax+10h]
        fistp qword ptr [eax+18h]
    }
}
void x87_8(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        fild qword ptr [edx]
        fistp qword ptr [eax]
    }
}
void mmx_128(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        movq mm0,qword ptr [edx]
        movq mm4,qword ptr [edx+20h]
        movq mm5,qword ptr [edx+40h]
        movq mm6,qword ptr [edx+60h]
        movq mm1,qword ptr [edx+8]
        movq mm2,qword ptr [edx+10h]
        movq mm3,qword ptr [edx+18h]
        movq qword ptr [eax],mm0
        movq qword ptr [eax+8],mm1
        movq qword ptr [eax+10h],mm2
        movq qword ptr [eax+18h],mm3
        movq mm1,qword ptr [edx+28h]
        movq mm2,qword ptr [edx+30h]
        movq mm3,qword ptr [edx+38h]
        movq qword ptr [eax+20h],mm4
        movq qword ptr [eax+28h],mm1
        movq qword ptr [eax+30h],mm2
        movq qword ptr [eax+38h],mm3
        movq mm1,qword ptr [edx+48h]
        movq mm2,qword ptr [edx+50h]
        movq mm3,qword ptr [edx+58h]
        movq qword ptr [eax+40h],mm5
        movq qword ptr [eax+48h],mm1
        movq qword ptr [eax+50h],mm2
        movq qword ptr [eax+58h],mm3
        movq mm1,qword ptr [edx+68h]
        movq mm2,qword ptr [edx+70h]
        movq mm3,qword ptr [edx+78h]
        movq qword ptr [eax+60h],mm6
        movq qword ptr [eax+68h],mm1
        movq qword ptr [eax+70h],mm2
        movq qword ptr [eax+78h],mm3
    }
}
void mmx_32(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        movq mm0,qword ptr [edx]
        movq mm1,qword ptr [edx+8]
        movq mm2,qword ptr [edx+10h]
        movq mm3,qword ptr [edx+18h]
        movq qword ptr [eax],mm0
        movq qword ptr [eax+8],mm1
        movq qword ptr [eax+10h],mm2
        movq qword ptr [eax+18h],mm3
    }
}
void mmx_8(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        movq mm0,qword ptr [edx]
        movq qword ptr [eax],mm0
    }
}
void sse_32(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        movups xmm0,xmmword ptr [edx]
        movups xmm1,xmmword ptr [edx+10h]
        movntps xmmword ptr [eax],xmm0
        movntps xmmword ptr [eax+10h],xmm1
    }
}
void sse_16(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        movups xmm0,xmmword ptr [edx]
        movaps xmmword ptr [eax],xmm0
    }
}
void sse_8(B* d, const B* s) {
    __asm {
        mov eax,d
        mov edx,s
        movlps xmm0,qword ptr [edx]
        movlps qword ptr [eax],xmm0
    }
}

using Chunk = void (*)(B*, const B*);
void block(B*& d, const B*& s, U& n, U width, Chunk copy) {
    copy(d,s); d += width; s += width; n -= width;
}
void peel(B*& d, const B*& s, U& n, bool sse) {
    const U alignment = sse ? 31u : 7u;
    if ((reinterpret_cast<U>(d) & alignment) == 0) return;
    if ((reinterpret_cast<U>(d) & 1u) && signed_ge(n,1)) scalar<B>(d,s,n);
    if ((reinterpret_cast<U>(d) & 2u) && signed_ge(n,2)) scalar<std::uint16_t>(d,s,n);
    if ((reinterpret_cast<U>(d) & 4u) && signed_ge(n,4)) scalar<U>(d,s,n);
    if (sse) {
        if ((reinterpret_cast<U>(d) & 8u) && signed_ge(n,8)) block(d,s,n,8,sse_8);
        if ((reinterpret_cast<U>(d) & 16u) && signed_ge(n,16)) block(d,s,n,16,sse_16);
    }
}
void tail(B*& d, const B*& s, U& n) {
    if (n >= 4) scalar<U>(d,s,n);
    if (n >= 2) scalar<std::uint16_t>(d,s,n);
    if (n >= 1) scalar<B>(d,s,n);
}
void* copy_large(void* destination,const void* source,U n,Chunk wide,Chunk medium,Chunk small,bool sse) {
    B* d=static_cast<B*>(destination);
    const B* s=static_cast<const B*>(source);
    peel(d,s,n,sse);
    const U wide_size=sse?32u:128u;
    // Signed JNS tests in the original, including wraparound for large counts.
    n-=wide_size;
    while(nonnegative(n)) { block(d,s,n,wide_size,wide); }
    n+=sse?24u:96u;
    if(!sse) {
        while(nonnegative(n)) { block(d,s,n,32,medium); }
        n+=24u;
    }
    while(nonnegative(n)) { block(d,s,n,8,small); }
    n+=8u;
    if(n) tail(d,s,n);
    return d;
}
} // namespace

void* __cdecl heap_copy_x87_005b0100_core(void* d,const void* s,U n) {
    return copy_large(d,s,n,x87_128,x87_32,x87_8,false);
}
void* __cdecl heap_copy_mmx_005b02c0_core(void* d,const void* s,U n) {
    return copy_large(d,s,n,mmx_128,mmx_32,mmx_8,false);
}
void* __cdecl heap_copy_sse_005b0480_core(void* d,const void* s,U n) {
    return copy_large(d,s,n,sse_32,nullptr,sse_8,true);
}
void __cdecl heap_copy_005b0100(void* d,const void* s,U n) { (void)heap_copy_x87_005b0100_core(d,s,n); }
void __cdecl heap_copy_005b02c0(void* d,const void* s,U n) { (void)heap_copy_mmx_005b02c0_core(d,s,n); }
void __cdecl heap_copy_005b0480(void* d,const void* s,U n) { (void)heap_copy_sse_005b0480_core(d,s,n); }

} // namespace porsche

