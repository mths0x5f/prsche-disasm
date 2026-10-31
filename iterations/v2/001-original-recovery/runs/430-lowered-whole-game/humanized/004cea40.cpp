/* 004cea40: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7530_004cea40 {
    U call(void);
};

/* the original 004c7530 (thiscall) */
__declspec(naked) U Call_004c7530_004cea40::call(void)
{
    __asm mov eax, 0x004c7530
    __asm jmp eax
}

struct Call_004c7e80_004cea40 {
    U call(void);
};

/* the original 004c7e80 (thiscall) */
__declspec(naked) U Call_004c7e80_004cea40::call(void)
{
    __asm mov eax, 0x004c7e80
    __asm jmp eax
}

struct Object_004cea40 {
    U function_004cea40(void);
};

U Object_004cea40::function_004cea40(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7530_004cea40 *)self)->call();
    U t2 = ((Call_004c7e80_004cea40 *)self)->call();
    U t3 = ((U (__stdcall *)(U))0x004c8b30u)(0x5d8e30u);
    *(unsigned long *)(self + 0x148u) = (unsigned long)t3;
    U t4 = *(unsigned long *)(self + 0xd0u);
    U t5 = ((U (__cdecl *)(U, U, U, U, U))0x005a134bu)(t4, 0x0u, 0x5d75c8u, 0x5d8370u, 0x0u);
    *(unsigned long *)(self + 0x150u) = (unsigned long)t5;
    return t5;
}
