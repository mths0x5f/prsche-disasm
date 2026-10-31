/* 004b81f0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004b81f0 {
    U function_004b81f0(void);
};

U Object_004b81f0::function_004b81f0(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x8u);
    U t2 = (0u & 0xffffff00u) | ((U)((t1 & t1) != 0u) & 0xffu);
    return t2;
}
