/* 004672a0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00539180_004672a0 {
    U call(void);
};

/* the original 00539180 (thiscall) */
__declspec(naked) U Call_00539180_004672a0::call(void)
{
    __asm mov eax, 0x00539180
    __asm jmp eax
}

struct Object_004672a0 {
    U function_004672a0(void);
};

U Object_004672a0::function_004672a0(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x10u);
    U t2 = *(unsigned long *)(t1 + 0xcu);
    U t3 = ((Call_00539180_004672a0 *)t2)->call();
    *(unsigned char *)(t1 + 0x134u) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)(self + 0x10u) = (unsigned long)0u;
    return 0u;
}
