/* 00513aa0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00512630_00513aa0 {
    U call(U);
};

/* the original 00512630 (thiscall) */
__declspec(naked) U Call_00512630_00513aa0::call(U)
{
    __asm mov eax, 0x00512630
    __asm jmp eax
}

struct Call_00513ad0_00513aa0 {
    U call(U, U);
};

/* the original 00513ad0 (thiscall) */
__declspec(naked) U Call_00513ad0_00513aa0::call(U, U)
{
    __asm mov eax, 0x00513ad0
    __asm jmp eax
}

struct Object_00513aa0 {
    U function_00513aa0(U a0, U a1, U a2);
};

U Object_00513aa0::function_00513aa0(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_00512630_00513aa0 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5ba190u;
    U t2 = ((Call_00513ad0_00513aa0 *)self)->call(a1, a2);
    return self;
}
