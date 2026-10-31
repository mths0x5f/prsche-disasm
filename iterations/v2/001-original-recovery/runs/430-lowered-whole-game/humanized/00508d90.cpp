/* 00508d90: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7530_00508d90 {
    U call(void);
};

/* the original 004c7530 (thiscall) */
__declspec(naked) U Call_004c7530_00508d90::call(void)
{
    __asm mov eax, 0x004c7530
    __asm jmp eax
}

struct Object_00508d90 {
    U function_00508d90(void);
};

U Object_00508d90::function_00508d90(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7530_00508d90 *)self)->call();
    U t2 = ((U (__stdcall *)(U))0x004c8b00u)(0x5db308u);
    *(unsigned long *)(self + 0x140u) = (unsigned long)t2;
    return t2;
}
