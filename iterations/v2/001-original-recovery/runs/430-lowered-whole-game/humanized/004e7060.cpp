/* 004e7060: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004e7060 {
    U function_004e7060(U a0);
};

U Object_004e7060::function_004e7060(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x58u);
    *(unsigned long *)a0 = (unsigned long)t1;
    U t2 = *(unsigned long *)(self + 0x5cu);
    *(unsigned long *)(a0 + 0x4u) = (unsigned long)t2;
    return a0;
}
