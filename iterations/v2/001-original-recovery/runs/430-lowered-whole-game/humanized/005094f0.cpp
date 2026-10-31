/* 005094f0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0050c130_005094f0 {
    U call(U);
};

/* the original 0050c130 (thiscall) */
__declspec(naked) U Call_0050c130_005094f0::call(U)
{
    __asm mov eax, 0x0050c130
    __asm jmp eax
}

struct Object_005094f0 {
    U function_005094f0(U a0);
};

U Object_005094f0::function_005094f0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_0050c130_005094f0 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5b8edcu;
    return self;
}
