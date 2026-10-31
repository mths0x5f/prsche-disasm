/* 004ccb50: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7ef0_004ccb50 {
    U call(void);
};

/* the original 004c7ef0 (thiscall) */
__declspec(naked) U Call_004c7ef0_004ccb50::call(void)
{
    __asm mov eax, 0x004c7ef0
    __asm jmp eax
}

struct Call_004cc5c0_004ccb50 {
    U call(void);
};

/* the original 004cc5c0 (thiscall) */
__declspec(naked) U Call_004cc5c0_004ccb50::call(void)
{
    __asm mov eax, 0x004cc5c0
    __asm jmp eax
}

struct Object_004ccb50 {
    U function_004ccb50(void);
};

U Object_004ccb50::function_004ccb50(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7ef0_004ccb50 *)self)->call();
    U t2 = ((Call_004cc5c0_004ccb50 *)self)->call();
    return t2;
}
