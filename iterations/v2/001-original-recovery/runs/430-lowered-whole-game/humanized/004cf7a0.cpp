/* 004cf7a0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7530_004cf7a0 {
    U call(void);
};

/* the original 004c7530 (thiscall) */
__declspec(naked) U Call_004c7530_004cf7a0::call(void)
{
    __asm mov eax, 0x004c7530
    __asm jmp eax
}

struct Object_004cf7a0 {
    U function_004cf7a0(void);
};

U Object_004cf7a0::function_004cf7a0(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7530_004cf7a0 *)self)->call();
    U t2 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d8f74u);
    *(unsigned long *)(self + 0x140u) = (unsigned long)t2;
    return t2;
}
