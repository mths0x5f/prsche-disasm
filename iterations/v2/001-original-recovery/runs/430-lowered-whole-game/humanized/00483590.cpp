/* 00483590: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00483590 {
    U function_00483590(U a0, U a1);
};

U Object_00483590::function_00483590(U a0, U a1)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x24u) = (unsigned long)a0;
    *(unsigned long *)(self + 0x20u) = (unsigned long)a1;
    *(unsigned char *)(self + 0x1cu) = (unsigned char)0x0u;
    return a0;
}
