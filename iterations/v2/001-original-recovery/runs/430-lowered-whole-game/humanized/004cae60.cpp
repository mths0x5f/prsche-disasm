/* 004cae60: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7530_004cae60 {
    U call(void);
};

/* the original 004c7530 (thiscall) */
__declspec(naked) U Call_004c7530_004cae60::call(void)
{
    __asm mov eax, 0x004c7530
    __asm jmp eax
}

struct Call_00525620_004cae60 {
    U call(U);
};

/* the original 00525620 (thiscall) */
__declspec(naked) U Call_00525620_004cae60::call(U)
{
    __asm mov eax, 0x00525620
    __asm jmp eax
}

struct Call_00525600_004cae60 {
    U call(U);
};

/* the original 00525600 (thiscall) */
__declspec(naked) U Call_00525600_004cae60::call(U)
{
    __asm mov eax, 0x00525600
    __asm jmp eax
}

struct Object_004cae60 {
    U function_004cae60(void);
};

U Object_004cae60::function_004cae60(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7530_004cae60 *)self)->call();
    U t2 = ((Call_00525620_004cae60 *)self)->call(0x5d78ecu);
    U t3 = ((Call_00525600_004cae60 *)self)->call(t2);
    U t4 = ((U (__cdecl *)(U, U, U, U, U))0x005a134bu)(t3, 0x0u, 0x5d78f8u, 0x5d7910u, 0x0u);
    *(unsigned long *)(self + 0x140u) = (unsigned long)t4;
    return t4;
}
