/* 0058aa90: generated from the original by humanize-generate-430.py (straight-line code). */
U __cdecl function_0058aa90(U a0, U a1)
{
    *(unsigned long *)0x006b4a18u = (unsigned long)a0;
    U t1 = (a0 + a1 - 0x8u);
    *(unsigned long *)(a0 + 0x8u) = (unsigned long)a1;
    *(unsigned long *)(a0 + 0x4u) = (unsigned long)t1;
    U t2 = (a0 + 0x1bu);
    U t3 = t2 & 0xfffffffcu;
    U t4 = a1 - 0x3u;
    *(unsigned long *)a0 = (unsigned long)t3;
    U t5 = (t4 - 0x20u);
    *(unsigned long *)(a0 + 0xcu) = (unsigned long)t5;
    *(unsigned long *)(a0 + 0x10u) = (unsigned long)t4;
    return a0;
}
