/* 00403620: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00403650_00403620 {
    U call(U);
};

/* the original 00403650 (thiscall) */
__declspec(naked) U Call_00403650_00403620::call(U)
{
    __asm mov eax, 0x00403650
    __asm jmp eax
}

struct Object_00403620 {
    U function_00403620(U a0, U a1, U a2);
};

U Object_00403620::function_00403620(U a0, U a1, U a2)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x4u) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)a2;
    U t1 = ((Call_00403650_00403620 *)self)->call(a1);
    return self;
}
