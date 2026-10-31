/* 004d6490: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004d6490 {
    U function_004d6490(void);
};

U Object_004d6490::function_004d6490(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x178u);
    U t2 = (0u & 0xffffff00u) | ((U)(t1 == 0x1u) & 0xffu);
    return t2;
}
