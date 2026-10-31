/* 00519a70: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004f0980_00519a70 {
    U call(U, U, U);
};

/* the original 004f0980 (thiscall) */
__declspec(naked) U Call_004f0980_00519a70::call(U, U, U)
{
    __asm mov eax, 0x004f0980
    __asm jmp eax
}

struct Object_00519a70 {
    U function_00519a70(U a0, U a1, U a2);
};

U Object_00519a70::function_00519a70(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_004f0980_00519a70 *)self)->call(a0, a1, a2);
    *(unsigned long *)self = (unsigned long)0x5ba8acu;
    return self;
}
