/* 0042c860: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00436740_0042c860 {
    U call(U, U, U, U);
};

/* the original 00436740 (thiscall) */
__declspec(naked) U Call_00436740_0042c860::call(U, U, U, U)
{
    __asm mov eax, 0x00436740
    __asm jmp eax
}

struct Object_0042c860 {
    U function_0042c860(U a0, U a1, U a2, U a3);
};

U Object_0042c860::function_0042c860(U a0, U a1, U a2, U a3)
{
    U self = (U)this;
    U t1 = ((Call_00436740_0042c860 *)self)->call(a0, a1, a2, a3);
    *(unsigned long *)self = (unsigned long)0x5b2ed8u;
    return self;
}
