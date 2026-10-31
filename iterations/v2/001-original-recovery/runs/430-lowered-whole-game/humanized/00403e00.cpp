/* 00403e00: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00403800_00403e00 {
    U call(U, U);
};

/* the original 00403800 (thiscall) */
__declspec(naked) U Call_00403800_00403e00::call(U, U)
{
    __asm mov eax, 0x00403800
    __asm jmp eax
}

struct Object_00403e00 {
    U function_00403e00(U a0, U a1);
};

U Object_00403e00::function_00403e00(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_00403800_00403e00 *)self)->call(a0, a1);
    *(unsigned long *)self = (unsigned long)0x5b2510u;
    *(unsigned long *)(self + 0x58u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x60u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x5cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x68u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x64u) = (unsigned long)0xffffffffu;
    return self;
}
