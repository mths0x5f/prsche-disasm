/* 004dab00: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004da5f0_004dab00 {
    U call(void);
};

/* the original 004da5f0 (thiscall) */
__declspec(naked) U Call_004da5f0_004dab00::call(void)
{
    __asm mov eax, 0x004da5f0
    __asm jmp eax
}

struct Call_00537830_004dab00 {
    U call(U);
};

/* the original 00537830 (thiscall) */
__declspec(naked) U Call_00537830_004dab00::call(U)
{
    __asm mov eax, 0x00537830
    __asm jmp eax
}

struct Object_004dab00 {
    U function_004dab00(void);
};

U Object_004dab00::function_004dab00(void)
{
    U self = (U)this;
    *(unsigned char *)0x0065b990u = (unsigned char)0x0u;
    U t1 = ((Call_004da5f0_004dab00 *)self)->call();
    U t2 = *(unsigned long *)0x00628130u;
    U t3 = *(unsigned long *)0x0065b944u;
    U t4 = *(unsigned long *)(t2 + 0x70u);
    U t5 = *(unsigned long *)(t4 + 0x4u);
    U t6 = ((Call_00537830_004dab00 *)t5)->call(t3);
    U t7 = *(unsigned long *)0x0065b988u;
    *(unsigned char *)0x0065b984u = (unsigned char)0x0u;
    *(unsigned long *)0x0065b954u = (unsigned long)t7;
    return t7;
}
