/* 00513920: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00512390_00513920 {
    U call(U);
};

/* the original 00512390 (thiscall) */
__declspec(naked) U Call_00512390_00513920::call(U)
{
    __asm mov eax, 0x00512390
    __asm jmp eax
}

struct Call_00513ad0_00513920 {
    U call(U, U);
};

/* the original 00513ad0 (thiscall) */
__declspec(naked) U Call_00513ad0_00513920::call(U, U)
{
    __asm mov eax, 0x00513ad0
    __asm jmp eax
}

struct Object_00513920 {
    U function_00513920(U a0, U a1, U a2);
};

U Object_00513920::function_00513920(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_00512390_00513920 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5ba190u;
    U t2 = ((Call_00513ad0_00513920 *)self)->call(a1, a2);
    return self;
}
