/* 0048d370: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0048c870_0048d370 {
    U call(U, U, U, U, U);
};

/* the original 0048c870 (thiscall) */
__declspec(naked) U Call_0048c870_0048d370::call(U, U, U, U, U)
{
    __asm mov eax, 0x0048c870
    __asm jmp eax
}

U __cdecl function_0048d370(void)
{
    U t1 = *(unsigned long *)0x00628c70u;
    U t2 = *(unsigned long *)(t1 + 0xcu);
    U t3 = ((Call_0048c870_0048d370 *)t2)->call(0xb3u, 0x80000000u, 0x80000000u, 0x0u, 0x0u);
    return t3;
}
