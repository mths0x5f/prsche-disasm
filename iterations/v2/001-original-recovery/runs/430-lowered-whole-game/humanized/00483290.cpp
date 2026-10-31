/* 00483290: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00482f70_00483290 {
    U call(U, U, U);
};

/* the original 00482f70 (thiscall) */
__declspec(naked) U Call_00482f70_00483290::call(U, U, U)
{
    __asm mov eax, 0x00482f70
    __asm jmp eax
}

struct Object_00483290 {
    U function_00483290(U a0, U a1, U a2);
};

U Object_00483290::function_00483290(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = *(unsigned long *)self;
    U t2 = ((Call_00482f70_00483290 *)t1)->call(a0, a1, a2);
    return t2;
}
