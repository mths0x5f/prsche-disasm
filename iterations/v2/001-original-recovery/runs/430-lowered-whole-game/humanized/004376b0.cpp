/* 004376b0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004376b0 {
    U function_004376b0(U a0, U a1);
};

U Object_004376b0::function_004376b0(U a0, U a1)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x130u) = (unsigned long)a0;
    *(unsigned long *)(self + 0x134u) = (unsigned long)a1;
    return a0;
}
