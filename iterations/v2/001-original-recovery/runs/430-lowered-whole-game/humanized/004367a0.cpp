/* 004367a0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004367a0 {
    U function_004367a0(U a0);
};

U Object_004367a0::function_004367a0(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x4u);
    *(unsigned long *)a0 = (unsigned long)t1;
    U t2 = *(unsigned long *)(self + 0x8u);
    *(unsigned long *)(a0 + 0x4u) = (unsigned long)t2;
    return a0;
}
