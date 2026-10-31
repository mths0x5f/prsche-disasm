/* 0058ff50: generated from the original by humanize-generate-430.py (straight-line code). */
U __cdecl function_0058ff50(U a0)
{
    U t1 = *(unsigned char *)0x006b49a1u;
    U t2 = (U)(long)(signed char)t1;
    *(unsigned long *)(t2 * 4u + 0x6b49c8u) = (unsigned long)a0;
    U t3 = *(unsigned char *)0x006b49a1u;
    U t4 = (t2 & 0xffffff00u) | (t3 & 0xffu);
    U t5 = (t4 & 0xffffff00u) | (((t4 & 0xffu) + 1u) & 0xffu & 0xffu);
    *(unsigned char *)0x006b49a1u = (unsigned char)(t5 & 0xffu);
    return t5;
}
