/* 004ac170: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004ac170 {
    U function_004ac170(void);
};

U Object_004ac170::function_004ac170(void)
{
    U self = (U)this;
    U t1 = (self + 0x7cu);
    U t2 = self + 0x8u;
    U t3 = *(unsigned long *)t2;
    *(unsigned long *)t1 = (unsigned long)t3;
    U t4 = *(unsigned long *)(t2 + 0x4u);
    *(unsigned long *)(t1 + 0x4u) = (unsigned long)t4;
    U t5 = *(unsigned long *)(t2 + 0x8u);
    *(unsigned long *)(t1 + 0x8u) = (unsigned long)t5;
    return t1;
}
