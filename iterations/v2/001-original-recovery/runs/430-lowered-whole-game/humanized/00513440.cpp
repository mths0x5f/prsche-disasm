/* 00513440: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00512390_00513440 {
    U call(U);
};

/* the original 00512390 (thiscall) */
__declspec(naked) U Call_00512390_00513440::call(U)
{
    __asm mov eax, 0x00512390
    __asm jmp eax
}

struct Call_005135e0_00513440 {
    U call(U);
};

/* the original 005135e0 (thiscall) */
__declspec(naked) U Call_005135e0_00513440::call(U)
{
    __asm mov eax, 0x005135e0
    __asm jmp eax
}

struct Object_00513440 {
    U function_00513440(U a0, U a1);
};

U Object_00513440::function_00513440(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_00512390_00513440 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5ba13cu;
    U t2 = ((Call_005135e0_00513440 *)self)->call(a1);
    return self;
}
