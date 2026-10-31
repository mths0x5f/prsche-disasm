/* 0045e640: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0045e640 {
    U function_0045e640(U a0, U a1);
};

U Object_0045e640::function_0045e640(U a0, U a1)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x4u) = (unsigned long)a0;
    *(unsigned long *)(self + 0xcu) = (unsigned long)a1;
    U t1 = a1 + 0x10u;
    *(unsigned long *)self = (unsigned long)0x5b3ef4u;
    *(unsigned long *)(self + 0x8u) = (unsigned long)t1;
    return self;
}
