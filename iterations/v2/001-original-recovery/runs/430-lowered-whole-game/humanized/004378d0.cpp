/* 004378d0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00523aa0_004378d0 {
    U call(void);
};

/* the original 00523aa0 (thiscall) */
__declspec(naked) U Call_00523aa0_004378d0::call(void)
{
    __asm mov eax, 0x00523aa0
    __asm jmp eax
}

struct Object_004378d0 {
    U function_004378d0(void);
};

U Object_004378d0::function_004378d0(void)
{
    U self = (U)this;
    U t1 = self + 0x4u;
    U t2 = ((Call_00523aa0_004378d0 *)t1)->call();
    U t3 = (t2 & 0xffffff00u) | (0x1u & 0xffu);
    return t3;
}
