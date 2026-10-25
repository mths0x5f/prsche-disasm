/* 00525580: calls 005271f0 on the object held at +0xf4 with its argument. */
struct Target_00525580 {
    unsigned long fn_005271f0(unsigned long a);
};

__declspec(naked) unsigned long Target_00525580::fn_005271f0(unsigned long a)
{
    __asm mov eax, 0x005271f0
    __asm jmp eax
}

struct Object_00525580 {
    unsigned char unknown_00[244];
    Target_00525580 *target;
    unsigned long forward(unsigned long a);
};

unsigned long Object_00525580::forward(unsigned long a)
{
    return target->fn_005271f0(a);
}
