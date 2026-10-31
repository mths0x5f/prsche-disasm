/* 004c8b60: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00525620_004c8b60 {
    U call(U);
};

/* the original 00525620 (thiscall) */
__declspec(naked) U Call_00525620_004c8b60::call(U)
{
    __asm mov eax, 0x00525620
    __asm jmp eax
}

struct Call_00525600_004c8b60 {
    U call(U);
};

/* the original 00525600 (thiscall) */
__declspec(naked) U Call_00525600_004c8b60::call(U)
{
    __asm mov eax, 0x00525600
    __asm jmp eax
}

struct Object_004c8b60 {
    U function_004c8b60(U a0);
};

U Object_004c8b60::function_004c8b60(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00525620_004c8b60 *)self)->call(a0);
    U t2 = ((Call_00525600_004c8b60 *)self)->call(t1);
    return t2;
}
