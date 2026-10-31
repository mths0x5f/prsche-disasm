/* 00489160: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00489160 {
    U function_00489160(U a0, U a1);
};

U Object_00489160::function_00489160(U a0, U a1)
{
    U self = (U)this;
    *(unsigned char *)(self + 0x4u) = (unsigned char)(0u & 0xffu);
    *(unsigned char *)(self + 0x5u) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)(self + 0x8u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xcu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x10u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x14u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x18u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x1cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x20u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x24u) = (unsigned long)a0;
    U t1 = *(unsigned long *)0x005d0608u;
    *(unsigned long *)(self + 0x28u) = (unsigned long)t1;
    U t2 = *(unsigned long *)0x005d0608u;
    U t3 = t2 + 1u;
    *(unsigned long *)0x005d0608u = (unsigned long)t3;
    *(unsigned long *)(self + 0x2cu) = (unsigned long)a1;
    return self;
}
