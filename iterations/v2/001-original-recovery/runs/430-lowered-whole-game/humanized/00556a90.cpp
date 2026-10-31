/* 00556a90: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00538a30_00556a90 {
    U call(U);
};

/* the original 00538a30 (thiscall) */
__declspec(naked) U Call_00538a30_00556a90::call(U)
{
    __asm mov eax, 0x00538a30
    __asm jmp eax
}

struct Object_00556a90 {
    U function_00556a90(U a0);
};

U Object_00556a90::function_00556a90(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00538a30_00556a90 *)self)->call(a0);
    *(unsigned long *)(self + 0x20u) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)0x5bc3f0u;
    return self;
}
