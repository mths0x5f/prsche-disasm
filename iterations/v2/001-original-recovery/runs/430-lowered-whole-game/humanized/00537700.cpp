/* 00537700: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00537760_00537700 {
    U call(void);
};

/* the original 00537760 (thiscall) */
__declspec(naked) U Call_00537760_00537700::call(void)
{
    __asm mov eax, 0x00537760
    __asm jmp eax
}

struct Object_00537700 {
    U function_00537700(void);
};

U Object_00537700::function_00537700(void)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x28u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x10u) = (unsigned long)0x1u;
    *(unsigned long *)(self + 0x8u) = (unsigned long)0x1u;
    *(unsigned long *)(self + 0xcu) = (unsigned long)0x1u;
    *(unsigned long *)self = (unsigned long)0u;
    *(unsigned long *)(self + 0x4u) = (unsigned long)0x3u;
    *(unsigned long *)(self + 0x14u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x18u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x1cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x20u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x24u) = (unsigned long)0x3f7fff00u;
    *(unsigned long *)(self + 0x28u) = (unsigned long)0xffffffffu;
    *(unsigned long *)(self + 0x2cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x30u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x34u) = (unsigned long)0x3f800000u;
    U t1 = ((Call_00537760_00537700 *)self)->call();
    U t2 = ((U (__cdecl *)(void))0x00535b00u)();
    return self;
}
