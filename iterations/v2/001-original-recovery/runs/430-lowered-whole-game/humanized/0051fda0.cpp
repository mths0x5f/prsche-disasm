/* 0051fda0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0051fda0 {
    U function_0051fda0(U a0, U a1, U a2, U a3);
};

U Object_0051fda0::function_0051fda0(U a0, U a1, U a2, U a3)
{
    U self = (U)this;
    *(unsigned long *)self = (unsigned long)a1;
    *(unsigned long *)(self + 0x4u) = (unsigned long)a2;
    *(unsigned long *)(self + 0x8u) = (unsigned long)a3;
    *(unsigned long *)(self + 0xcu) = (unsigned long)a0;
    *(unsigned char *)(self + 0x10u) = (unsigned char)0x0u;
    U t1 = ((U (__cdecl *)(void))0x0053c2e0u)();
    *(unsigned long *)(self + 0x14u) = (unsigned long)t1;
    *(unsigned long *)(self + 0x18u) = (unsigned long)0x0u;
    return self;
}
