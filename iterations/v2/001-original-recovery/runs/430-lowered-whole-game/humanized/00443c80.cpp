/* 00443c80: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00447af0_00443c80 {
    U call(void);
};

/* the original 00447af0 (thiscall) */
__declspec(naked) U Call_00447af0_00443c80::call(void)
{
    __asm mov eax, 0x00447af0
    __asm jmp eax
}

struct Object_00443c80 {
    U function_00443c80(U a0);
};

U Object_00443c80::function_00443c80(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x78u);
    U t2 = (a0 + a0 * 2u);
    U t3 = (a0 + t2 * 4u);
    U t4 = (t1 + t3 * 4u);
    U t5 = ((Call_00447af0_00443c80 *)t4)->call();
    return t5;
}
