#include "rectangle.hpp"
#include "../381-pixel-draw-helpers/pixel_draw_helpers.hpp"
#include "porsche/render_display.hpp"
#include <cstdint>
// Canonical original1.0f readonly owner: Run221 original_scalars.cpp.
extern float _DAT_005b24a8;
namespace porsche {
std::uint32_t rectangle_state_006a6404[5]{};
std::uint32_t rectangle_limits_005dfa08[5]={0x3f800000u,0x3f800000u,0x3f800000u,0x44200000u,0x43f00000u};
const float rectangle_zero_005b23f8=0.0f;
static_assert(sizeof(void*)==4&&sizeof(float)==4,"Original x86 FLOAT32 geometry");
namespace {
using U=std::uint32_t;
// Retain native extended intermediates and the original FSTP32 boundaries.
// C++ owns branching/vertex layout; these helpers preserve x87 instruction order.
bool positive(U bits){std::uint16_t status;
    __asm {
        fld dword ptr bits
        fcomp rectangle_zero_005b23f8
        fnstsw status
    }
    return (status&0x4100u)==0;
}
void clip_low(U* position,U* extent,U boundary,U* near_uv,U far_uv){
    __asm {
        mov ecx,position
        mov edx,extent
        fld dword ptr boundary
        fsub dword ptr [ecx]
        fcom rectangle_zero_005b23f8
        fnstsw ax
        test ah,41h
        jnz low_finished
        fdiv dword ptr [edx]
        mov eax,boundary
        mov [ecx],eax
        fsubr _DAT_005b24a8
        fld st(0)
        fmul dword ptr [edx]
        fstp dword ptr [edx]
        mov ecx,near_uv
        fld dword ptr far_uv
        fsub dword ptr [ecx]
        fmul st(0),st(1)
        fsubr dword ptr far_uv
        fstp dword ptr [ecx]
    low_finished:
        fstp st(0)
    }
}
void clip_high(U position,U* extent,U boundary,U near_uv,U* far_uv){
    __asm {
        mov edx,extent
        fld dword ptr position
        fadd dword ptr [edx]
        fsub dword ptr boundary
        fcom rectangle_zero_005b23f8
        fnstsw ax
        test ah,41h
        jnz high_finished
        fdiv dword ptr [edx]
        fsubr _DAT_005b24a8
        fld st(0)
        fmul dword ptr [edx]
        fstp dword ptr [edx]
        mov ecx,far_uv
        fld dword ptr [ecx]
        fsub dword ptr near_uv
        fmul st(0),st(1)
        fadd dword ptr near_uv
        fstp dword ptr [ecx]
    high_finished:
        fstp st(0)
    }
}
U coordinate(U position,U extent,bool add){U result;
    __asm {
        fld dword ptr position
        cmp add,0
        je coordinate_store
        fadd dword ptr extent
    coordinate_store:
        fstp dword ptr result
    }return result;
}
U float_store(U bits){U result;
    __asm {
        fld dword ptr bits
        fstp dword ptr result
    }return result;
}
}
void __cdecl render_draw_rectangle_bits_0056daf0(U x,U y,U width,U height,U pixel){
    U u0=rectangle_state_006a6404[1],v0=rectangle_state_006a6404[2];
    U u1=rectangle_limits_005dfa08[1],v1=rectangle_limits_005dfa08[2];
    if(!positive(width)||!positive(height))return;
    clip_low(&x,&width,rectangle_state_006a6404[3],&u0,u1);
    clip_high(x,&width,rectangle_limits_005dfa08[3],u0,&u1);
    clip_low(&y,&height,rectangle_state_006a6404[4],&v0,v1);
    clip_high(y,&height,rectangle_limits_005dfa08[4],v0,&v1);
    if(!positive(width)||!positive(height))return;
    U vertices[4][8];
    for(U i=0;i<4;++i){
        const bool right=((i+1)&2u)!=0,bottom=(i&2u)!=0;
        vertices[i][0]=coordinate(x,width,right);
        vertices[i][1]=coordinate(y,height,bottom);
        vertices[i][2]=rectangle_state_006a6404[0];
        vertices[i][3]=rectangle_limits_005dfa08[0];
        vertices[i][4]=pixel;vertices[i][5]=0;
        vertices[i][6]=float_store(right?u1:u0);
        vertices[i][7]=float_store(bottom?v1:v0);
    }
    render_display_draw_quad_006bd9a8(vertices[0],vertices[1],vertices[2],vertices[3]);
}
}
