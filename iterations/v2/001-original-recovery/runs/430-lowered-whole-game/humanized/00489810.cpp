/* 00489810: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00489810 {
    U function_00489810(U a0, U a1);
};

U Object_00489810::function_00489810(U a0, U a1)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x1cu);
    U t2 = *(unsigned long *)(t1 + a1 * 8u);
    *(unsigned long *)a0 = (unsigned long)t2;
    return a0;
}
