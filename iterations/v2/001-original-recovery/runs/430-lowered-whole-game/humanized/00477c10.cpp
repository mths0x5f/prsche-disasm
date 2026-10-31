/* 00477c10: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004891b0_00477c10 {
    U call(void);
};

/* the original 004891b0 (thiscall) */
__declspec(naked) U Call_004891b0_00477c10::call(void)
{
    __asm mov eax, 0x004891b0
    __asm jmp eax
}

struct Object_00477c10 {
    U function_00477c10(void);
};

U Object_00477c10::function_00477c10(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x30u);
    *(unsigned long *)self = (unsigned long)0x5b46e8u;
    U t2 = ((U (__cdecl *)(U))0x0059ecd0u)(t1);
    U t3 = ((Call_004891b0_00477c10 *)self)->call();
    return t3;
}
