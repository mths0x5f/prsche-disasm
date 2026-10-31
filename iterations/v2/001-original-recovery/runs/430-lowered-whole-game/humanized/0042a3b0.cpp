/* 0042a3b0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0042a3b0 {
    U function_0042a3b0(void);
};

U Object_0042a3b0::function_0042a3b0(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0xcu);
    U t2 = (t1 & 0xffffff00u) | ((U)((t1 & t1) != 0u) & 0xffu);
    return t2;
}
