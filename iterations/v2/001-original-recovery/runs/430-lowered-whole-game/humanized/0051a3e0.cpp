/* 0051a3e0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004f0980_0051a3e0 {
    U call(U, U, U);
};

/* the original 004f0980 (thiscall) */
__declspec(naked) U Call_004f0980_0051a3e0::call(U, U, U)
{
    __asm mov eax, 0x004f0980
    __asm jmp eax
}

struct Object_0051a3e0 {
    U function_0051a3e0(U a0, U a1, U a2);
};

U Object_0051a3e0::function_0051a3e0(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_004f0980_0051a3e0 *)self)->call(a0, a1, a2);
    *(unsigned long *)self = (unsigned long)0x5baa24u;
    return self;
}
