/* 00483260: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00482ea0_00483260 {
    U call(U, U, U);
};

/* the original 00482ea0 (thiscall) */
__declspec(naked) U Call_00482ea0_00483260::call(U, U, U)
{
    __asm mov eax, 0x00482ea0
    __asm jmp eax
}

struct Object_00483260 {
    U function_00483260(U a0, U a1, U a2);
};

U Object_00483260::function_00483260(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = *(unsigned long *)self;
    U t2 = ((Call_00482ea0_00483260 *)t1)->call(a0, a1, a2);
    U t3 = *(unsigned long *)(self + 0xcu);
    U t4 = (t3 + 0x1u);
    *(unsigned long *)(self + 0xcu) = (unsigned long)t4;
    return t3;
}
