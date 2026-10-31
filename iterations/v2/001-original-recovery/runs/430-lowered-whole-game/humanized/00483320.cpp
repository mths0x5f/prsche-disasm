/* 00483320: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00483320 {
    U function_00483320(void);
};

U Object_00483320::function_00483320(void)
{
    U self = (U)this;
    *(unsigned long *)(self + 0xcu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x10u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x14u) = (unsigned long)0u;
    *(unsigned char *)(self + 0x1cu) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)(self + 0x20u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x24u) = (unsigned long)0u;
    U t1 = *(unsigned long *)0x005bb2b0u;
    U t2 = (self + 0x58u);
    *(unsigned long *)(self + 0x58u) = (unsigned long)t1;
    U t3 = *(unsigned long *)0x005bb2b4u;
    *(unsigned long *)(t2 + 0x4u) = (unsigned long)t3;
    U t4 = *(unsigned long *)0x005bb2b8u;
    *(unsigned long *)(t2 + 0x8u) = (unsigned long)t4;
    return self;
}
