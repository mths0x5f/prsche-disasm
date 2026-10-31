/* 004d1780: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004d1780 {
    U function_004d1780(U a0);
};

U Object_004d1780::function_004d1780(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x8u);
    U t2 = *(unsigned long *)(t1 + 0x558u);
    *(unsigned long *)(t2 + 0x224u) = (unsigned long)a0;
    return t1;
}
