/* 0048c840: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0048c840 {
    U function_0048c840(U a0, U a1);
};

U Object_0048c840::function_0048c840(U a0, U a1)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x40u) = (unsigned long)a1;
    U t1 = ((U (__cdecl *)(U, U, U))0x005a28a0u)(self, a0, 0x3fu);
    *(unsigned char *)(self + 0x3fu) = (unsigned char)0x0u;
    return self;
}
