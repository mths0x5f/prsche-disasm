/* 00590d80: generated from the original by humanize-generate-430.py (straight-line code). */
U __cdecl function_00590d80(U a0, U a1)
{
    U t1 = a0 & 0xffffu;
    U t2 = a0 >> 0x10u;
    U t3 = a1 >> 0x10u;
    U t4 = a1 & 0xffffu;
    U t5 = (U)((long)t3 * (long)t1);
    U t6 = (U)((long)t4 * (long)t2);
    U t7 = (U)((long)t4 * (long)t1);
    U t8 = (t6 + t5);
    U t9 = t8 << 0x10u;
    U t10 = (U)((long)t3 * (long)t2);
    U t11 = t9 + t7;
    U t12 = t6 & 0xffffu;
    U t13 = t7 >> 0x10u;
    U t14 = t12 + t13;
    U t15 = t5 & 0xffffu;
    U t16 = t14 + t15;
    U t17 = t16 >> 0x10u;
    U t18 = t17 + t10;
    U t19 = t6 >> 0x10u;
    U t20 = t18 + t19;
    U t21 = t5 >> 0x10u;
    U t22 = t20 + t21;
    return t11;
}
