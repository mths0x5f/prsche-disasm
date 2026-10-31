/* 004cc400: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7480_004cc400 {
    U call(void);
};

/* the original 004c7480 (thiscall) */
__declspec(naked) U Call_004c7480_004cc400::call(void)
{
    __asm mov eax, 0x004c7480
    __asm jmp eax
}

struct Object_004cc400 {
    U function_004cc400(void);
};

U Object_004cc400::function_004cc400(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7480_004cc400 *)self)->call();
    *(unsigned long *)self = (unsigned long)0x5b60acu;
    *(unsigned long *)(self + 0x140u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x144u) = (unsigned long)0u;
    *(unsigned char *)(self + 0x148u) = (unsigned char)(0u & 0xffu);
    *(unsigned char *)(self + 0x156u) = (unsigned char)(0u & 0xffu);
    return self;
}
