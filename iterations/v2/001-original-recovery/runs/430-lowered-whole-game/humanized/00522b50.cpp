/* 00522b50: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bcf90_00522b50 {
    U call(void);
};

/* the original 004bcf90 (thiscall) */
__declspec(naked) U Call_004bcf90_00522b50::call(void)
{
    __asm mov eax, 0x004bcf90
    __asm jmp eax
}

struct Call_004c8b60_00522b50 {
    U call(U);
};

/* the original 004c8b60 (thiscall) */
__declspec(naked) U Call_004c8b60_00522b50::call(U)
{
    __asm mov eax, 0x004c8b60
    __asm jmp eax
}

struct Call_00528c90_00522b50 {
    U call(void);
};

/* the original 00528c90 (thiscall) */
__declspec(naked) U Call_00528c90_00522b50::call(void)
{
    __asm mov eax, 0x00528c90
    __asm jmp eax
}

struct Object_00522b50 {
    U function_00522b50(void);
};

U Object_00522b50::function_00522b50(void)
{
    U self = (U)this;
    U t1 = ((Call_004bcf90_00522b50 *)self)->call();
    U t2 = ((U (__stdcall *)(U))0x004c8b00u)(0x5d7c08u);
    *(unsigned long *)(self + 0x17cu) = (unsigned long)t2;
    U t3 = ((U (__stdcall *)(U))0x004c8b00u)(0x5dd978u);
    U t4 = (t3 & 0xffffff00u) | ((U)((t3 & t3) != 0u) & 0xffu);
    *(unsigned char *)(self + 0x180u) = (unsigned char)(t4 & 0xffu);
    U t5 = ((Call_004c8b60_00522b50 *)self)->call(0x5d78ecu);
    U t6 = ((U (__cdecl *)(U, U, U, U, U))0x005a134bu)(t5, 0x0u, 0x5d78f8u, 0x5d7a90u, 0x0u);
    *(unsigned long *)(self + 0x194u) = (unsigned long)t6;
    U t7 = ((Call_00528c90_00522b50 *)t6)->call();
    *(unsigned long *)(self + 0x190u) = (unsigned long)t7;
    return t7;
}
