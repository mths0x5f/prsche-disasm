/* 00574ab0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0053f320_00574ab0 {
    U call(U, U);
};

/* the original 0053f320 (thiscall) */
__declspec(naked) U Call_0053f320_00574ab0::call(U, U)
{
    __asm mov eax, 0x0053f320
    __asm jmp eax
}

struct Object_00574ab0 {
    U function_00574ab0(U a0);
};

U Object_00574ab0::function_00574ab0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_0053f320_00574ab0 *)self)->call(0x2u, a0);
    *(unsigned long *)self = (unsigned long)0x5c0898u;
    return self;
}
