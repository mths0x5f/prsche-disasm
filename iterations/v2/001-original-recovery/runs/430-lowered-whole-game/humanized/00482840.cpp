/* 00482840: Constructor step: runs the base initializer (00478040), clears +0x48, sets both flags and installs the vtable 005b47e0. */
struct Object_00482840 {
    unsigned long vtable;
    unsigned char flag_04;
    unsigned char flag_05;
    unsigned char unknown_06[0x42];
    unsigned long field_48;
    void base_init_00478040(unsigned long arg);
    Object_00482840 *init_00482840(unsigned long arg);
};

__declspec(naked) void Object_00482840::base_init_00478040(unsigned long arg)
{
    __asm mov eax, 0x00478040
    __asm jmp eax
}

Object_00482840 *Object_00482840::init_00482840(unsigned long arg)
{
    base_init_00478040(arg);
    field_48 = 0;
    flag_04 = 1;
    flag_05 = 1;
    vtable = 0x005b47e0;
    return this;
}
