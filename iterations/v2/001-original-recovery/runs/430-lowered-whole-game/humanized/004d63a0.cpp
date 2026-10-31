/* 004d63a0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004d63a0 {
    U function_004d63a0(void);
};

U Object_004d63a0::function_004d63a0(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0xd8u);
    U t2 = *(unsigned long *)(t1 + 0x4u);
    U t3 = *(unsigned long *)t1;
    U t4 = t2 - t3;
    U t5 = t4 & 0xfffffffcu;
    U t6 = (t1 & 0xffffff00u) | ((U)(t5 == 0x4u) & 0xffu);
    return t6;
}
