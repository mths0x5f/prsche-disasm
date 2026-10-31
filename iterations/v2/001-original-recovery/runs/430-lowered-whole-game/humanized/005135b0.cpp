/* 005135b0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00512630_005135b0 {
    U call(U);
};

/* the original 00512630 (thiscall) */
__declspec(naked) U Call_00512630_005135b0::call(U)
{
    __asm mov eax, 0x00512630
    __asm jmp eax
}

struct Call_005135e0_005135b0 {
    U call(U);
};

/* the original 005135e0 (thiscall) */
__declspec(naked) U Call_005135e0_005135b0::call(U)
{
    __asm mov eax, 0x005135e0
    __asm jmp eax
}

struct Object_005135b0 {
    U function_005135b0(U a0, U a1);
};

U Object_005135b0::function_005135b0(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_00512630_005135b0 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5ba13cu;
    U t2 = ((Call_005135e0_005135b0 *)self)->call(a1);
    return self;
}
