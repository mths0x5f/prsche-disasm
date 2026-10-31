/* 004bc460: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004bc460 {
    U function_004bc460(U a0);
};

U Object_004bc460::function_004bc460(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x18u);
    U t2 = *(unsigned long *)a0;
    *(unsigned long *)t2 = (unsigned long)t1;
    U t3 = *(unsigned long *)a0;
    U t4 = t3 + 0x4u;
    *(unsigned long *)a0 = (unsigned long)t4;
    return a0;
}
