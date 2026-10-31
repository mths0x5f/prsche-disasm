/* 004ce8a0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7530_004ce8a0 {
    U call(void);
};

/* the original 004c7530 (thiscall) */
__declspec(naked) U Call_004c7530_004ce8a0::call(void)
{
    __asm mov eax, 0x004c7530
    __asm jmp eax
}

struct Object_004ce8a0 {
    U function_004ce8a0(void);
};

U Object_004ce8a0::function_004ce8a0(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7530_004ce8a0 *)self)->call();
    U t2 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d8df8u);
    *(unsigned long *)(self + 0x140u) = (unsigned long)t2;
    U t3 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d8decu);
    *(unsigned long *)(self + 0x144u) = (unsigned long)t3;
    return t3;
}
