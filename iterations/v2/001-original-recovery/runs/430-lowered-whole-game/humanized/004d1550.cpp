/* 004d1550: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00473150_004d1550 {
    U call(void);
};

/* the original 00473150 (thiscall) */
__declspec(naked) U Call_00473150_004d1550::call(void)
{
    __asm mov eax, 0x00473150
    __asm jmp eax
}

struct Object_004d1550 {
    U function_004d1550(void);
};

U Object_004d1550::function_004d1550(void)
{
    U self = (U)this;
    U t1 = (self + 0x4u);
    U t2 = ((Call_00473150_004d1550 *)t1)->call();
    return self;
}
