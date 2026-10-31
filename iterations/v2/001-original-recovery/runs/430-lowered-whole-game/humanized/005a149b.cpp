/* 005a149b: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_005a50c5_005a149b {
    U call(U);
};

/* the original 005a50c5 (thiscall) */
__declspec(naked) U Call_005a50c5_005a149b::call(U)
{
    __asm mov eax, 0x005a50c5
    __asm jmp eax
}

struct Object_005a149b {
    U function_005a149b(U a0);
};

U Object_005a149b::function_005a149b(U a0)
{
    U self = (U)this;
    U t1 = ((Call_005a50c5_005a149b *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5c1960u;
    return self;
}
