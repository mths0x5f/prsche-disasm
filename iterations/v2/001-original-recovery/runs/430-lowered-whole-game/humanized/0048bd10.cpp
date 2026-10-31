/* 0048bd10: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_0048bd10 {
    U function_0048bd10(U a0, U a1, U a2);
};

U Object_0048bd10::function_0048bd10(U a0, U a1, U a2)
{
    U self = (U)this;
    *(unsigned char *)(self + 0x3u) = (unsigned char)(a1 & 0xffu);
    U t1 = (self + 0x4u);
    U t2 = (U)((long)a1 >> 0x10u);
    U t3 = (U)((long)a1 >> 0x8u);
    *(unsigned char *)self = (unsigned char)0xb4u;
    *(unsigned char *)(self + 0x1u) = (unsigned char)(t2 & 0xffu);
    *(unsigned char *)(self + 0x2u) = (unsigned char)(t3 & 0xffu);
    U t4 = ((U (__cdecl *)(void))0x0053c290u)();
    U t5 = (self + 0x18u);
    U t6 = ((U (__cdecl *)(void))0x005323e0u)();
    U t7 = a2 >> 0x18u;
    *(unsigned char *)(self + 0x4fu) = (unsigned char)(t7 & 0xffu);
    U t8 = (U)((long)a2 >> 0x10u);
    U t9 = (U)((long)a2 >> 0x8u);
    *(unsigned char *)(self + 0x4cu) = (unsigned char)(a2 & 0xffu);
    *(unsigned char *)(self + 0x4eu) = (unsigned char)(t8 & 0xffu);
    *(unsigned char *)(self + 0x4du) = (unsigned char)(t9 & 0xffu);
    return self;
}
