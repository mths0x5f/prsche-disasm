/* 00488ff0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00488ff0 {
    U function_00488ff0(U a0, U a1);
};

U Object_00488ff0::function_00488ff0(U a0, U a1)
{
    U self = (U)this;
    U t1 = *(unsigned long *)a0;
    *(unsigned long *)self = (unsigned long)t1;
    U t2 = *(unsigned long *)a1;
    *(unsigned long *)(self + 0x4u) = (unsigned long)t2;
    return self;
}
