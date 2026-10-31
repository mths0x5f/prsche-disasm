/* 00482dd0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004892f0_00482dd0 {
    U call(U, U);
};

/* the original 004892f0 (thiscall) */
__declspec(naked) U Call_004892f0_00482dd0::call(U, U)
{
    __asm mov eax, 0x004892f0
    __asm jmp eax
}

struct Object_00482dd0 {
    U function_00482dd0(void);
};

U Object_00482dd0::function_00482dd0(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x18u);
    U t2 = *(unsigned long *)(self + 0x1cu);
    U t3 = ((Call_004892f0_00482dd0 *)self)->call(t2, t1);
    return t3;
}
