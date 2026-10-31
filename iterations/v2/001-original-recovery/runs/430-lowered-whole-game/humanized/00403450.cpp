/* 00403450: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00403450 {
    U function_00403450(U a0, U a1);
};

U Object_00403450::function_00403450(U a0, U a1)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x58u);
    U t2 = *(unsigned long *)(t1 + a0 * 8u);
    *(unsigned long *)a1 = (unsigned long)t2;
    U t3 = *(unsigned long *)(t1 + a0 * 8u + 0x4u);
    *(unsigned long *)(a1 + 0x4u) = (unsigned long)t3;
    return t3;
}
