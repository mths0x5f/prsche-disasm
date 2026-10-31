/* 004930f0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_004930f0 {
    U function_004930f0(U a0, U a1);
};

U Object_004930f0::function_004930f0(U a0, U a1)
{
    U self = (U)this;
    U t1 = *(unsigned long *)self;
    U t2 = *(unsigned long *)t1;
    *(unsigned long *)self = (unsigned long)t2;
    *(unsigned long *)a0 = (unsigned long)t1;
    return a0;
}
