/* 00525310: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00525310 {
    U function_00525310(U a0);
};

U Object_00525310::function_00525310(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0xe0u);
    U t2 = *(unsigned long *)(t1 + 0x38u);
    *(unsigned long *)a0 = (unsigned long)t2;
    U t3 = *(unsigned long *)(t1 + 0x3cu);
    *(unsigned long *)(a0 + 0x4u) = (unsigned long)t3;
    return a0;
}
