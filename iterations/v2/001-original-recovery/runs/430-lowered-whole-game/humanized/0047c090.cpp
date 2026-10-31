/* 0047c090: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0047c090 {
    U function_0047c090(U a0, U a1);
};

U Object_0047c090::function_0047c090(U a0, U a1)
{
    U self = (U)this;
    U t1 = *(unsigned long *)self;
    U t2 = t1 >> 0x1cu;
    U t3 = t2 + 1u;
    U t4 = 0xdu - t3;
    U t5 = a1 & 0x2u;
    U t6 = t5 << ((t4 & 0xffu) & 31u);
    U t7 = a1 & 0x1u;
    U t8 = t3 << 0xeu;
    U t9 = t6 & 0x3fffu;
    U t10 = t9 | t8;
    U t11 = 0xeu - t3;
    U t12 = t7 << ((t11 & 0xffu) & 31u);
    U t13 = t10 << 0xeu;
    U t14 = t12 | t1;
    U t15 = t1 & 0xfffc000u;
    U t16 = t14 & 0x3fffu;
    U t17 = t13 | t16;
    U t18 = *(unsigned long *)a0;
    U t19 = t17 | t15;
    U t20 = t18 ^ t19;
    U t21 = t20 & 0x3fffu;
    U t22 = t21 ^ t18;
    U t23 = t22 ^ t19;
    U t24 = t23 & 0x3fffu;
    U t25 = t24 ^ t19;
    *(unsigned long *)a0 = (unsigned long)t25;
    return a0;
}
