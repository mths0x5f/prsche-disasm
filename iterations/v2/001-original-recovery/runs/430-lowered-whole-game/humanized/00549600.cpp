/* 00549600: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00549600 {
    U function_00549600(U a0);
};

U Object_00549600::function_00549600(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)a0;
    *(unsigned long *)self = (unsigned long)t1;
    U t2 = *(unsigned short *)(a0 + 0x4u);
    U t3 = (t1 & 0xffff0000u) | (t2 & 0xffffu);
    *(unsigned short *)(self + 0x4u) = (unsigned short)(t3 & 0xffffu);
    U t4 = *(unsigned short *)(a0 + 0x6u);
    U t5 = (t3 & 0xffff0000u) | (t4 & 0xffffu);
    *(unsigned short *)(self + 0x6u) = (unsigned short)(t5 & 0xffffu);
    U t6 = *(unsigned short *)(a0 + 0x8u);
    U t7 = (a0 & 0xffff0000u) | (t6 & 0xffffu);
    *(unsigned short *)(self + 0x8u) = (unsigned short)(t7 & 0xffffu);
    return self;
}
