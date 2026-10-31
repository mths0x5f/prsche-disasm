/* 0059b9a0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0059c1b0_0059b9a0 {
    U call(void);
};

/* the original 0059c1b0 (thiscall) */
__declspec(naked) U Call_0059c1b0_0059b9a0::call(void)
{
    __asm mov eax, 0x0059c1b0
    __asm jmp eax
}

struct Object_0059b9a0 {
    U function_0059b9a0(void);
};

U Object_0059b9a0::function_0059b9a0(void)
{
    U self = (U)this;
    U t1 = ((Call_0059c1b0_0059b9a0 *)self)->call();
    *(unsigned long *)0x006b16bcu = (unsigned long)0x597c10u;
    *(unsigned long *)0x006b16c0u = (unsigned long)0x59cc30u;
    *(unsigned long *)0x006b16c4u = (unsigned long)0x59cb50u;
    *(unsigned long *)0x006b1704u = (unsigned long)0x1cu;
    *(unsigned long *)0x006b1708u = (unsigned long)0x20u;
    *(unsigned long *)0x006b170cu = (unsigned long)0x24u;
    return t1;
}
