/* 00515ca0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc610_00515ca0 {
    U call(void);
};

/* the original 004bc610 (thiscall) */
__declspec(naked) U Call_004bc610_00515ca0::call(void)
{
    __asm mov eax, 0x004bc610
    __asm jmp eax
}

struct Object_00515ca0 {
    U function_00515ca0(void);
};

U Object_00515ca0::function_00515ca0(void)
{
    U self = (U)this;
    U t1 = ((Call_004bc610_00515ca0 *)self)->call();
    U t2 = (t1 & 0xffffff00u) | (0u & 0xffu);
    *(unsigned char *)(self + 0x2cu) = (unsigned char)(t2 & 0xffu);
    *(unsigned char *)(self + 0x2du) = (unsigned char)(t2 & 0xffu);
    return t2;
}
