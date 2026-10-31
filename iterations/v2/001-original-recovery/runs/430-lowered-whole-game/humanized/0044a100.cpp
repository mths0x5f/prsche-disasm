/* 0044a100: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0053f320_0044a100 {
    U call(U, U);
};

/* the original 0053f320 (thiscall) */
__declspec(naked) U Call_0053f320_0044a100::call(U, U)
{
    __asm mov eax, 0x0053f320
    __asm jmp eax
}

struct Object_0044a100 {
    U function_0044a100(U a0, U a1);
};

U Object_0044a100::function_0044a100(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_0053f320_0044a100 *)self)->call(a0, a1);
    *(unsigned long *)self = (unsigned long)0x5b3c44u;
    return self;
}
