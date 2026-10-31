/* 0051a060: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7530_0051a060 {
    U call(void);
};

/* the original 004c7530 (thiscall) */
__declspec(naked) U Call_004c7530_0051a060::call(void)
{
    __asm mov eax, 0x004c7530
    __asm jmp eax
}

struct Object_0051a060 {
    U function_0051a060(void);
};

U Object_0051a060::function_0051a060(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7530_0051a060 *)self)->call();
    U t2 = ((U (__stdcall *)(U))0x004c8b30u)(0x5dd290u);
    *(unsigned long *)(self + 0x144u) = (unsigned long)t2;
    return t2;
}
