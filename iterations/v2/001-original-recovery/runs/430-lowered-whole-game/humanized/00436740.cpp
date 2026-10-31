/* 00436740: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00436740 {
    U function_00436740(U a0, U a1, U a2, U a3);
};

U Object_00436740::function_00436740(U a0, U a1, U a2, U a3)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x4u) = (unsigned long)a0;
    *(unsigned long *)(self + 0x8u) = (unsigned long)a1;
    *(unsigned long *)(self + 0xcu) = (unsigned long)a2;
    *(unsigned long *)(self + 0x10u) = (unsigned long)a3;
    *(unsigned long *)self = (unsigned long)0x5b34bcu;
    return self;
}
