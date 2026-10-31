/* 0050cbf0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004d23f0_0050cbf0 {
    U call(U);
};

/* the original 004d23f0 (thiscall) */
__declspec(naked) U Call_004d23f0_0050cbf0::call(U)
{
    __asm mov eax, 0x004d23f0
    __asm jmp eax
}

U __cdecl function_0050cbf0(void)
{
    U t1 = *(unsigned long *)0x0065b928u;
    U t2 = ((Call_004d23f0_0050cbf0 *)t1)->call(0x0u);
    return t2;
}
