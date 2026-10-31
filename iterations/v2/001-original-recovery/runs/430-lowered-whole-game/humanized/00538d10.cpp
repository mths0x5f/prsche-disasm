/* 00538d10: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00539e50_00538d10 {
    U call(U);
};

/* the original 00539e50 (thiscall) */
__declspec(naked) U Call_00539e50_00538d10::call(U)
{
    __asm mov eax, 0x00539e50
    __asm jmp eax
}

struct Call_00539c90_00538d10 {
    U call(void);
};

/* the original 00539c90 (thiscall) */
__declspec(naked) U Call_00539c90_00538d10::call(void)
{
    __asm mov eax, 0x00539c90
    __asm jmp eax
}

struct Object_00538d10 {
    U function_00538d10(U a0);
};

U Object_00538d10::function_00538d10(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00539e50_00538d10 *)self)->call(0x28u);
    U t2 = (self + 0x5cu);
    U t3 = ((Call_00539e50_00538d10 *)t2)->call(0x28u);
    U t4 = (self + 0x108u);
    *(unsigned long *)(self + 0xb8u) = (unsigned long)0x3fu;
    U t5 = ((Call_00539c90_00538d10 *)t4)->call();
    U t6 = (self + 0x148u);
    U t7 = ((Call_00539c90_00538d10 *)t6)->call();
    U t8 = (self + 0x188u);
    U t9 = ((Call_00539c90_00538d10 *)t8)->call();
    *(unsigned long *)(self + 0x1d0u) = (unsigned long)0x0u;
    *(unsigned long *)(self + 0x1d4u) = (unsigned long)0xffffffffu;
    *(unsigned long *)(self + 0x1c8u) = (unsigned long)a0;
    *(unsigned long *)(a0 + 0x14u) = (unsigned long)self;
    return self;
}
