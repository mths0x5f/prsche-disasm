/* 00443660: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00443660 {
    U function_00443660(U a0);
};

U Object_00443660::function_00443660(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x2d4u);
    U t2 = *(unsigned char *)(t1 + a0);
    U t3 = (t1 & 0xffffff00u) | (t2 & 0xffu);
    return t3;
}
