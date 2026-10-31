/* 0052a020: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0052a000_0052a020 {
    U call(U);
};

/* the original 0052a000 (thiscall) */
__declspec(naked) U Call_0052a000_0052a020::call(U)
{
    __asm mov eax, 0x0052a000
    __asm jmp eax
}

struct Call_00525620_0052a020 {
    U call(U);
};

/* the original 00525620 (thiscall) */
__declspec(naked) U Call_00525620_0052a020::call(U)
{
    __asm mov eax, 0x00525620
    __asm jmp eax
}

struct Call_00525600_0052a020 {
    U call(U);
};

/* the original 00525600 (thiscall) */
__declspec(naked) U Call_00525600_0052a020::call(U)
{
    __asm mov eax, 0x00525600
    __asm jmp eax
}

struct Object_0052a020 {
    U function_0052a020(U a0);
};

U Object_0052a020::function_0052a020(U a0)
{
    U self = (U)this;
    U t1 = ((Call_0052a000_0052a020 *)self)->call(a0);
    U t2 = *(unsigned long *)t1;
    U t3 = *(unsigned long *)self;
    U t4 = ((Call_00525620_0052a020 *)t3)->call(t2);
    U t5 = *(unsigned long *)self;
    U t6 = ((Call_00525600_0052a020 *)t5)->call(t4);
    return t6;
}
