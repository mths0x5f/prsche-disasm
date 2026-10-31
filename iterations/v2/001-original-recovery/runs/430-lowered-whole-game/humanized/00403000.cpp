/* 00403000: generated from the original by humanize-generate-430.py (straight-line code). */
U __cdecl function_00403000(U a0)
{
    U t1 = *(unsigned long *)0x005d102cu;
    U t2 = *(unsigned long *)0x005d1028u;
    U t3 = (U)((long)t1 * (long)t2);
    *(unsigned long *)0x00655a0cu = (unsigned long)t3;
    U t4 = t3 & 0xffffu;
    *(unsigned long *)0x005d1028u = (unsigned long)t4;
    U t5 = t3 >> 0x8u;
    U t6 = *(unsigned long *)(a0 + 0xe38u);
    U t7 = t5 & 0x3u;
    U t8 = *(unsigned long *)(t6 + t7 * 4u + 0xcu);
    *(unsigned long *)(a0 + 0xec8u) = (unsigned long)t8;
    return t8;
}
