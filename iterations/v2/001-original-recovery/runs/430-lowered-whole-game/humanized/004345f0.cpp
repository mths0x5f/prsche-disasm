/* 004345f0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004345f0 {
    U function_004345f0(void);
};

U Object_004345f0::function_004345f0(void)
{
    U self = (U)this;
    U t1 = ((U (__cdecl *)(void))0x004204f0u)();
    *(unsigned long *)(self + 0x94u) = (unsigned long)t1;
    U t2 = t1 & 0xffffffu;
    U t3 = t2 | 0x3f000000u;
    *(unsigned long *)(self + 0x94u) = (unsigned long)t3;
    U t4 = ((U (__cdecl *)(void))0x004204f0u)();
    U t5 = t4 & 0xffffffu;
    U t6 = t5 | 0x3f000000u;
    *(unsigned long *)(self + 0x98u) = (unsigned long)t6;
    return t6;
}
