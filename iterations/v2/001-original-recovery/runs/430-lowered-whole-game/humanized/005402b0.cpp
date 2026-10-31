/* 005402b0: generated from the original by humanize-generate-430.py (straight-line code). */
U __cdecl function_005402b0(U a0, U a1, U a2)
{
    U t1 = *(unsigned char *)a1;
    U t2 = (0u & 0xffffff00u) | (t1 & 0xffu);
    U t3 = (U)((long)t2 * (long)a2);
    U t4 = (U)((long)t3 >> 0x8u);
    *(unsigned char *)a0 = (unsigned char)(t4 & 0xffu);
    U t5 = *(unsigned char *)(a1 + 0x1u);
    U t6 = (0u & 0xffffff00u) | (t5 & 0xffu);
    U t7 = (U)((long)t6 * (long)a2);
    U t8 = (U)((long)t7 >> 0x8u);
    *(unsigned char *)(a0 + 0x1u) = (unsigned char)(t8 & 0xffu);
    U t9 = *(unsigned char *)(a1 + 0x2u);
    U t10 = (0u & 0xffffff00u) | (t9 & 0xffu);
    U t11 = (U)((long)t10 * (long)a2);
    U t12 = (U)((long)t11 >> 0x8u);
    *(unsigned char *)(a0 + 0x2u) = (unsigned char)(t12 & 0xffu);
    U t13 = *(unsigned char *)(a1 + 0x3u);
    U t14 = (0u & 0xffffff00u) | (t13 & 0xffu);
    U t15 = (U)((long)t14 * (long)a2);
    U t16 = (U)((long)t15 >> 0x8u);
    *(unsigned char *)(a0 + 0x3u) = (unsigned char)(t16 & 0xffu);
    return a1;
}
