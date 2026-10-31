/* 004c7c90: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004c7c90 {
    U function_004c7c90(void);
};

U Object_004c7c90::function_004c7c90(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x10cu);
    U t2 = (self & 0xffffff00u) | (0u & 0xffu);
    U t3 = (t1 & 0xffu) & 0x4u;
    U t4 = (t1 & 0xffffff00u) | ((t3 & 0xffu) & 0xffu);
    U t5 = (U)(0u - (U)((t2 & 0xffu) < (t4 & 0xffu)));
    U t6 = 0u - t5;
    return t6;
}
