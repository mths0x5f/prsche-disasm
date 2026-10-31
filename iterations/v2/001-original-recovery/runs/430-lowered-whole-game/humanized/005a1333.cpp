/* 005a1333: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_005a50c5_005a1333 {
    U call(U);
};

/* the original 005a50c5 (thiscall) */
__declspec(naked) U Call_005a50c5_005a1333::call(U)
{
    __asm mov eax, 0x005a50c5
    __asm jmp eax
}

struct Object_005a1333 {
    U function_005a1333(U a0);
};

U Object_005a1333::function_005a1333(U a0)
{
    U self = (U)this;
    U t1 = ((Call_005a50c5_005a1333 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5c1930u;
    return self;
}
