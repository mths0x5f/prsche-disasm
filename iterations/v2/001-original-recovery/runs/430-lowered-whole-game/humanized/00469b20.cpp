/* 00469b20: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00469b20 {
    U function_00469b20(U a0);
};

U Object_00469b20::function_00469b20(U a0)
{
    U self = (U)this;
    U t1 = self + 0xb4u;
    U t2 = *(unsigned long *)t1;
    *(unsigned long *)a0 = (unsigned long)t2;
    U t3 = *(unsigned long *)(t1 + 0x4u);
    *(unsigned long *)(a0 + 0x4u) = (unsigned long)t3;
    U t4 = *(unsigned long *)(t1 + 0x8u);
    *(unsigned long *)(a0 + 0x8u) = (unsigned long)t4;
    return a0;
}
