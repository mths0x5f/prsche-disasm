/* 004a5960: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004d56e0_004a5960 {
    U call(U);
};

/* the original 004d56e0 (thiscall) */
__declspec(naked) U Call_004d56e0_004a5960::call(U)
{
    __asm mov eax, 0x004d56e0
    __asm jmp eax
}

struct Object_004a5960 {
    U function_004a5960(void);
};

U Object_004a5960::function_004a5960(void)
{
    U self = (U)this;
    *(unsigned char *)(self + 0x1du) = (unsigned char)0x1u;
    U t1 = *(unsigned long *)0x0065b928u;
    U t2 = ((Call_004d56e0_004a5960 *)t1)->call(0x0u);
    U t3 = (t2 & 0xffffff00u) | (0x1u & 0xffu);
    return t3;
}
