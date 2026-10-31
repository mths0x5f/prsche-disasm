/* 004367c0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004367c0 {
    U function_004367c0(U a0, U a1);
};

U Object_004367c0::function_004367c0(U a0, U a1)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x4u) = (unsigned long)a0;
    *(unsigned long *)(self + 0x8u) = (unsigned long)a1;
    return a0;
}
