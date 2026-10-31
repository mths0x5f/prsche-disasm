/* 0052b260: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0052a0e0_0052b260 {
    U call(U, U);
};

/* the original 0052a0e0 (thiscall) */
__declspec(naked) U Call_0052a0e0_0052b260::call(U, U)
{
    __asm mov eax, 0x0052a0e0
    __asm jmp eax
}

struct Object_0052b260 {
    U function_0052b260(U a0, U a1);
};

U Object_0052b260::function_0052b260(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_0052a0e0_0052b260 *)self)->call(a0, a1);
    *(unsigned long *)self = (unsigned long)0x5bb240u;
    return self;
}
