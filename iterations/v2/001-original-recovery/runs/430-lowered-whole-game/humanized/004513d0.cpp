/* 004513d0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0044fdd0_004513d0 {
    U call(U);
};

/* the original 0044fdd0 (thiscall) */
__declspec(naked) U Call_0044fdd0_004513d0::call(U)
{
    __asm mov eax, 0x0044fdd0
    __asm jmp eax
}

struct Object_004513d0 {
    U function_004513d0(U a0);
};

U Object_004513d0::function_004513d0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_0044fdd0_004513d0 *)self)->call(a0);
    *(unsigned long *)(self + 0x10u) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)0x5b3d28u;
    return self;
}
