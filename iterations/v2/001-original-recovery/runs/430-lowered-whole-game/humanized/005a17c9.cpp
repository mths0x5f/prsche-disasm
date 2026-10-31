/* 005a17c9: generated from the original by humanize-generate-430.py (straight-line code). */
U __cdecl _rand_005a17c9(void)
{
    U t1 = ((U (__cdecl *)(void))0x005a545cu)();
    U t2 = *(unsigned long *)(t1 + 0x14u);
    U t3 = (U)((long)t2 * (long)0x343fdu);
    U t4 = t3 + 0x269ec3u;
    *(unsigned long *)(t1 + 0x14u) = (unsigned long)t4;
    U t5 = t4 >> 0x10u;
    U t6 = t5 & 0x7fffu;
    return t6;
}
