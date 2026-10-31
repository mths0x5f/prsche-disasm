/* 00436840: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00436840 {
    U function_00436840(U a0, U a1);
};

U Object_00436840::function_00436840(U a0, U a1)
{
    U self = (U)this;
    *(unsigned long *)(self + 0xcu) = (unsigned long)a0;
    *(unsigned long *)(self + 0x10u) = (unsigned long)a1;
    return a0;
}
