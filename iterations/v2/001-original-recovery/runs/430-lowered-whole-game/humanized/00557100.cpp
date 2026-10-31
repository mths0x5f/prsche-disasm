/* 00557100: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00538a30_00557100 {
    U call(U);
};

/* the original 00538a30 (thiscall) */
__declspec(naked) U Call_00538a30_00557100::call(U)
{
    __asm mov eax, 0x00538a30
    __asm jmp eax
}

struct Object_00557100 {
    U function_00557100(U a0);
};

U Object_00557100::function_00557100(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00538a30_00557100 *)self)->call(a0);
    *(unsigned long *)(self + 0x20u) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)0x5bc41cu;
    return self;
}
