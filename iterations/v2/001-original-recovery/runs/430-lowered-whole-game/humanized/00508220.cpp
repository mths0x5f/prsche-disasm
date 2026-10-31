/* 00508220: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7530_00508220 {
    U call(void);
};

/* the original 004c7530 (thiscall) */
__declspec(naked) U Call_004c7530_00508220::call(void)
{
    __asm mov eax, 0x004c7530
    __asm jmp eax
}

struct Object_00508220 {
    U function_00508220(void);
};

U Object_00508220::function_00508220(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7530_00508220 *)self)->call();
    *(unsigned char *)(self + 0x140u) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)(self + 0x14cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x150u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x154u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x158u) = (unsigned long)0u;
    return 0u;
}
