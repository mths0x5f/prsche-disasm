/* 0052b9c0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00526880_0052b9c0 {
    U call(U, U, U);
};

/* the original 00526880 (thiscall) */
__declspec(naked) U Call_00526880_0052b9c0::call(U, U, U)
{
    __asm mov eax, 0x00526880
    __asm jmp eax
}

struct Object_0052b9c0 {
    U function_0052b9c0(U a0, U a1);
};

U Object_0052b9c0::function_0052b9c0(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_00526880_0052b9c0 *)self)->call(a0, a1, 0x104u);
    *(unsigned long *)self = (unsigned long)0x5bb208u;
    return self;
}
