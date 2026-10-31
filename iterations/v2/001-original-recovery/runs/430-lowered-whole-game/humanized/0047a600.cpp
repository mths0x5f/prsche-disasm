/* 0047a600: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0047a600 {
    U function_0047a600(U a0);
};

U Object_0047a600::function_0047a600(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)a0;
    *(unsigned long *)self = (unsigned long)t1;
    U t2 = *(unsigned long *)(a0 + 0x4u);
    *(unsigned long *)(self + 0x4u) = (unsigned long)t2;
    U t3 = *(unsigned long *)(a0 + 0x8u);
    *(unsigned long *)(self + 0x8u) = (unsigned long)t3;
    U t4 = *(unsigned long *)(a0 + 0xcu);
    *(unsigned long *)(self + 0xcu) = (unsigned long)t4;
    return self;
}
