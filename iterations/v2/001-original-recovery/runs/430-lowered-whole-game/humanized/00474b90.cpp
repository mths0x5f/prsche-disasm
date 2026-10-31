/* 00474b90: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00474ac0_00474b90 {
    U call(U);
};

/* the original 00474ac0 (thiscall) */
__declspec(naked) U Call_00474ac0_00474b90::call(U)
{
    __asm mov eax, 0x00474ac0
    __asm jmp eax
}

struct Object_00474b90 {
    U function_00474b90(U a0);
};

U Object_00474b90::function_00474b90(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00474ac0_00474b90 *)self)->call(a0);
    *(unsigned long *)(self + 0x8u) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)0x5b4674u;
    return self;
}
