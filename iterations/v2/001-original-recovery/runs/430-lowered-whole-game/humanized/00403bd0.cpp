/* 00403bd0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00403c00_00403bd0 {
    U call(U, U);
};

/* the original 00403c00 (thiscall) */
__declspec(naked) U Call_00403c00_00403bd0::call(U, U)
{
    __asm mov eax, 0x00403c00
    __asm jmp eax
}

struct Object_00403bd0 {
    U function_00403bd0(U a0, U a1, U a2);
};

U Object_00403bd0::function_00403bd0(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + a2 * 4u + 0x70u);
    U t2 = t1 + 1u;
    *(unsigned long *)(self + a2 * 4u + 0x70u) = (unsigned long)t2;
    *(unsigned long *)(self + 0x44u) = (unsigned long)a0;
    *(unsigned long *)(self + 0x48u) = (unsigned long)a1;
    *(unsigned long *)(self + a0 * 4u + 0x4cu) = (unsigned long)0x5u;
    U t3 = ((Call_00403c00_00403bd0 *)self)->call(a0, a1);
    return t3;
}
