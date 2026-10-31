/* 004f1a50: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004ef4c0_004f1a50 {
    U call(void);
};

/* the original 004ef4c0 (thiscall) */
__declspec(naked) U Call_004ef4c0_004f1a50::call(void)
{
    __asm mov eax, 0x004ef4c0
    __asm jmp eax
}

struct Call_004f1080_004f1a50 {
    U call(void);
};

/* the original 004f1080 (thiscall) */
__declspec(naked) U Call_004f1080_004f1a50::call(void)
{
    __asm mov eax, 0x004f1080
    __asm jmp eax
}

struct Object_004f1a50 {
    U function_004f1a50(void);
};

U Object_004f1a50::function_004f1a50(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x284u);
    U t2 = ((Call_004ef4c0_004f1a50 *)t1)->call();
    U t3 = ((Call_004f1080_004f1a50 *)self)->call();
    return t3;
}
