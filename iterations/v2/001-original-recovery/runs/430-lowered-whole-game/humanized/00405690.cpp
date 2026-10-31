/* 00405690: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00405d70_00405690 {
    U call(void);
};

/* the original 00405d70 (thiscall) */
__declspec(naked) U Call_00405d70_00405690::call(void)
{
    __asm mov eax, 0x00405d70
    __asm jmp eax
}

struct Call_0040b4d0_00405690 {
    U call(void);
};

/* the original 0040b4d0 (thiscall) */
__declspec(naked) U Call_0040b4d0_00405690::call(void)
{
    __asm mov eax, 0x0040b4d0
    __asm jmp eax
}

struct Object_00405690 {
    U function_00405690(void);
};

U Object_00405690::function_00405690(void)
{
    U self = (U)this;
    U t1 = ((Call_00405d70_00405690 *)self)->call();
    U t2 = *(unsigned long *)(self + 0x8u);
    U t3 = ((Call_0040b4d0_00405690 *)t2)->call();
    return t3;
}
