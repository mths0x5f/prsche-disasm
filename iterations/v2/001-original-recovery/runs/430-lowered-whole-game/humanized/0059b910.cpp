/* 0059b910: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0059b8d0_0059b910 {
    U call(void);
};

/* the original 0059b8d0 (thiscall) */
__declspec(naked) U Call_0059b8d0_0059b910::call(void)
{
    __asm mov eax, 0x0059b8d0
    __asm jmp eax
}

struct Object_0059b910 {
    U function_0059b910(void);
};

U Object_0059b910::function_0059b910(void)
{
    U self = (U)this;
    U t1 = ((Call_0059b8d0_0059b910 *)self)->call();
    *(unsigned long *)0x006b16d4u = (unsigned long)0x597dc0u;
    *(unsigned long *)0x006b16d8u = (unsigned long)0x59c9f0u;
    *(unsigned long *)0x006b16dcu = (unsigned long)0x59c610u;
    *(unsigned long *)0x006b171cu = (unsigned long)0xa0u;
    *(unsigned long *)0x006b1720u = (unsigned long)0x128u;
    *(unsigned long *)0x006b1724u = (unsigned long)0xa8u;
    return t1;
}
