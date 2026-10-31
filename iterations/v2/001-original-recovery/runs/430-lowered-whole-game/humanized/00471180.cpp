/* 00471180: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00539cd0_00471180 {
    U call(U, U);
};

/* the original 00539cd0 (thiscall) */
__declspec(naked) U Call_00539cd0_00471180::call(U, U)
{
    __asm mov eax, 0x00539cd0
    __asm jmp eax
}

struct Call_0053a540_00471180 {
    U call(void);
};

/* the original 0053a540 (thiscall) */
__declspec(naked) U Call_0053a540_00471180::call(void)
{
    __asm mov eax, 0x0053a540
    __asm jmp eax
}

struct Object_00471180 {
    U function_00471180(U a0);
};

U Object_00471180::function_00471180(U a0)
{
    U self = (U)this;
    *(unsigned char *)(self + 0x4u) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)(self + 0xcu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x54u) = (unsigned long)0u;
    *(unsigned long *)self = (unsigned long)0x5b45bcu;
    *(unsigned long *)(self + 0x10u) = (unsigned long)a0;
    U t1 = *(unsigned long *)0x005bb2b0u;
    U t2 = (self + 0x58u);
    U t3 = (self + 0x14u);
    *(unsigned long *)t2 = (unsigned long)t1;
    U t4 = *(unsigned long *)0x005bb2b4u;
    *(unsigned long *)(t2 + 0x4u) = (unsigned long)t4;
    U t5 = *(unsigned long *)0x005bb2b8u;
    *(unsigned long *)self = (unsigned long)0x5b45e4u;
    *(unsigned long *)(t2 + 0x8u) = (unsigned long)t5;
    U t6 = (a0 + 0x28u);
    U t7 = a0 + 0x34u;
    U t8 = ((Call_00539cd0_00471180 *)t3)->call(t7, t6);
    U t9 = ((Call_0053a540_00471180 *)t3)->call();
    return self;
}
