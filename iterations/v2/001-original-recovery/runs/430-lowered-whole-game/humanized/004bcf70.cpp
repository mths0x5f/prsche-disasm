/* 004bcf70: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7480_004bcf70 {
    U call(void);
};

/* the original 004c7480 (thiscall) */
__declspec(naked) U Call_004c7480_004bcf70::call(void)
{
    __asm mov eax, 0x004c7480
    __asm jmp eax
}

struct Object_004bcf70 {
    U function_004bcf70(void);
};

U Object_004bcf70::function_004bcf70(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7480_004bcf70 *)self)->call();
    *(unsigned long *)self = (unsigned long)0x5b5484u;
    return self;
}
