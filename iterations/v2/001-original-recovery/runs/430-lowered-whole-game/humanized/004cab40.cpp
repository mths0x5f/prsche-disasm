/* 004cab40: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004d00c0_004cab40 {
    U call(void);
};

/* the original 004d00c0 (thiscall) */
__declspec(naked) U Call_004d00c0_004cab40::call(void)
{
    __asm mov eax, 0x004d00c0
    __asm jmp eax
}

struct Object_004cab40 {
    U function_004cab40(void);
};

U Object_004cab40::function_004cab40(void)
{
    U self = (U)this;
    U t1 = ((Call_004d00c0_004cab40 *)self)->call();
    U t2 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d882cu);
    *(unsigned long *)(self + 0x15cu) = (unsigned long)t2;
    U t3 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d881cu);
    *(unsigned long *)(self + 0x160u) = (unsigned long)t3;
    U t4 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d880cu);
    *(unsigned long *)(self + 0x164u) = (unsigned long)t4;
    U t5 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d87fcu);
    *(unsigned long *)(self + 0x168u) = (unsigned long)t5;
    return t5;
}
