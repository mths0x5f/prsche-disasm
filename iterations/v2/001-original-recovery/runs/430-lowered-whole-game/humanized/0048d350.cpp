/* 0048d350: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0048c870_0048d350 {
    U call(U, U, U, U, U);
};

/* the original 0048c870 (thiscall) */
__declspec(naked) U Call_0048c870_0048d350::call(U, U, U, U, U)
{
    __asm mov eax, 0x0048c870
    __asm jmp eax
}

struct Object_0048d350 {
    U function_0048d350(U a0, U a1, U a2, U a3);
};

U Object_0048d350::function_0048d350(U a0, U a1, U a2, U a3)
{
    U self = (U)this;
    U t1 = ((Call_0048c870_0048d350 *)self)->call(a0, a1, a2, 0x0u, a3);
    return t1;
}
