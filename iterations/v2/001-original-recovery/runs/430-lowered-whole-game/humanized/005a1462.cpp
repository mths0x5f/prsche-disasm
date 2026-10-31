/* 005a1462: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_005a5088_005a1462 {
    U call(U);
};

/* the original 005a5088 (thiscall) */
__declspec(naked) U Call_005a5088_005a1462::call(U)
{
    __asm mov eax, 0x005a5088
    __asm jmp eax
}

struct Object_005a1462 {
    U function_005a1462(U a0);
};

U Object_005a1462::function_005a1462(U a0)
{
    U self = (U)this;
    U t1 = ((Call_005a5088_005a1462 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5c1960u;
    return self;
}
