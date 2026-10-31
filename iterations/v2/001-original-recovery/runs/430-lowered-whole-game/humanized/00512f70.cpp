/* 00512f70: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00512390_00512f70 {
    U call(U);
};

/* the original 00512390 (thiscall) */
__declspec(naked) U Call_00512390_00512f70::call(U)
{
    __asm mov eax, 0x00512390
    __asm jmp eax
}

struct Call_005130e0_00512f70 {
    U call(U);
};

/* the original 005130e0 (thiscall) */
__declspec(naked) U Call_005130e0_00512f70::call(U)
{
    __asm mov eax, 0x005130e0
    __asm jmp eax
}

struct Object_00512f70 {
    U function_00512f70(U a0, U a1);
};

U Object_00512f70::function_00512f70(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_00512390_00512f70 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5ba0b4u;
    U t2 = ((Call_005130e0_00512f70 *)self)->call(a1);
    return self;
}
