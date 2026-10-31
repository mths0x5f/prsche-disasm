/* 0041ca10: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004345f0_0041ca10 {
    U call(void);
};

/* the original 004345f0 (thiscall) */
__declspec(naked) U Call_004345f0_0041ca10::call(void)
{
    __asm mov eax, 0x004345f0
    __asm jmp eax
}

struct Object_0041ca10 {
    U function_0041ca10(void);
};

U Object_0041ca10::function_0041ca10(void)
{
    U self = (U)this;
    U t1 = ((Call_004345f0_0041ca10 *)self)->call();
    U t2 = ((U (__cdecl *)(void))0x004204f0u)();
    U t3 = *(unsigned long *)(self + 0xc8u);
    *(unsigned long *)(t3 + 0x24u) = (unsigned long)t2;
    U t4 = ((U (__cdecl *)(void))0x00420490u)();
    U t5 = *(unsigned long *)(self + 0xc8u);
    *(unsigned long *)(t5 + 0x28u) = (unsigned long)t4;
    U t6 = ((U (__cdecl *)(void))0x004204b0u)();
    U t7 = *(unsigned long *)(self + 0xc4u);
    *(unsigned long *)(t7 + 0x24u) = (unsigned long)t6;
    U t8 = ((U (__cdecl *)(void))0x00420490u)();
    U t9 = *(unsigned long *)(self + 0xc4u);
    *(unsigned long *)(t9 + 0x28u) = (unsigned long)t8;
    return t8;
}
