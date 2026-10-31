/* 00450c40: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0044fdd0_00450c40 {
    U call(U);
};

/* the original 0044fdd0 (thiscall) */
__declspec(naked) U Call_0044fdd0_00450c40::call(U)
{
    __asm mov eax, 0x0044fdd0
    __asm jmp eax
}

struct Object_00450c40 {
    U function_00450c40(U a0);
};

U Object_00450c40::function_00450c40(U a0)
{
    U self = (U)this;
    U t1 = ((Call_0044fdd0_00450c40 *)self)->call(a0);
    *(unsigned long *)(self + 0x10u) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)0x5b3cf0u;
    return self;
}
