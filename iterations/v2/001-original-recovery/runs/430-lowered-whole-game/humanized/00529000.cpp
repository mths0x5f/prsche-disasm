/* 00529000: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00529000 {
    U function_00529000(void);
};

U Object_00529000::function_00529000(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x10cu);
    U t2 = *(unsigned long *)(t1 + 0x4u);
    U t3 = *(unsigned long *)t1;
    U t4 = t2 - t3;
    U t5 = (U)((long)t4 >> 0x2u);
    return t5;
}
