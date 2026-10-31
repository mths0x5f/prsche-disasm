/* 004994f0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00474440_004994f0 {
    U call(U);
};

/* the original 00474440 (thiscall) */
__declspec(naked) U Call_00474440_004994f0::call(U)
{
    __asm mov eax, 0x00474440
    __asm jmp eax
}

struct Call_00474060_004994f0 {
    U call(U, U);
};

/* the original 00474060 (thiscall) */
__declspec(naked) U Call_00474060_004994f0::call(U, U)
{
    __asm mov eax, 0x00474060
    __asm jmp eax
}

U __cdecl function_004994f0(U a0)
{
    U t1 = (a0 + 0x330u);
    U t2 = (a0 + 0x8u);
    U t3 = ((Call_00474440_004994f0 *)t2)->call(t1);
    U t4 = ((Call_00474060_004994f0 *)t2)->call(t1, 0x1u);
    return t4;
}
