/* 0046f0f0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0046f0f0 {
    U function_0046f0f0(U a0);
};

U Object_0046f0f0::function_0046f0f0(U a0)
{
    U self = (U)this;
    U t1 = self + 0xc8u;
    U t2 = *(unsigned long *)t1;
    *(unsigned long *)a0 = (unsigned long)t2;
    U t3 = *(unsigned long *)(t1 + 0x4u);
    *(unsigned long *)(a0 + 0x4u) = (unsigned long)t3;
    U t4 = *(unsigned long *)(t1 + 0x8u);
    *(unsigned long *)(a0 + 0x8u) = (unsigned long)t4;
    return a0;
}
