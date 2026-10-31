/* 0044bf40: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0059f2f0_0044bf40 {
    U call(U);
};

/* the original 0059f2f0 (thiscall) */
__declspec(naked) U Call_0059f2f0_0044bf40::call(U)
{
    __asm mov eax, 0x0059f2f0
    __asm jmp eax
}

struct Object_0044bf40 {
    U function_0044bf40(U a0);
};

U Object_0044bf40::function_0044bf40(U a0)
{
    U self = (U)this;
    U t1 = ((Call_0059f2f0_0044bf40 *)self)->call(a0);
    U t2 = *(unsigned long *)(a0 + 0x10u);
    *(unsigned long *)(self + 0x10u) = (unsigned long)t2;
    *(unsigned long *)(self + 0x14u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x1cu) = (unsigned long)0u;
    U t3 = *(unsigned long *)(a0 + 0x20u);
    *(unsigned long *)(self + 0x28u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x2cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x20u) = (unsigned long)t3;
    return self;
}
