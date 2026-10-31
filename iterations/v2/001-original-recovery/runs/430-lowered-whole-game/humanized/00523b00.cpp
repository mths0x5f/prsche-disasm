/* 00523b00: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00523ad0_00523b00 {
    U call(U, U);
};

/* the original 00523ad0 (thiscall) */
__declspec(naked) U Call_00523ad0_00523b00::call(U, U)
{
    __asm mov eax, 0x00523ad0
    __asm jmp eax
}

struct Object_00523b00 {
    U function_00523b00(U a0, U a1);
};

U Object_00523b00::function_00523b00(U a0, U a1)
{
    U self = (U)this;
    U t1 = a1 & 0xffu;
    U t2 = ((Call_00523ad0_00523b00 *)self)->call(a0, t1);
    U t3 = 0u - t2;
    U t4 = (U)(0u - (U)(t2 != 0u));
    U t5 = 0u - t4;
    return t5;
}
