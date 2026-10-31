/* 0047ba10: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0047ba10 {
    U function_0047ba10(U a0);
};

U Object_0047ba10::function_0047ba10(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)self;
    U t2 = *(unsigned long *)a0;
    U t3 = t2 ^ t1;
    U t4 = t3 & 0x3fffu;
    U t5 = t4 ^ t1;
    *(unsigned long *)self = (unsigned long)t5;
    U t6 = *(unsigned long *)a0;
    U t7 = t6 ^ t5;
    U t8 = t7 & 0xfffc000u;
    U t9 = t8 ^ t5;
    *(unsigned long *)self = (unsigned long)t9;
    U t10 = *(unsigned long *)a0;
    U t11 = t9 ^ t10;
    U t12 = t11 & 0xfffffffu;
    U t13 = t12 ^ t10;
    *(unsigned long *)self = (unsigned long)t13;
    return self;
}
