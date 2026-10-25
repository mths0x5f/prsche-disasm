/* 00514960: calls 00514ab0 on the object held at +0xfc with its argument. */
struct Target_00514960 {
    unsigned long fn_00514ab0(unsigned long a);
};

__declspec(naked) unsigned long Target_00514960::fn_00514ab0(unsigned long a)
{
    __asm mov eax, 0x00514ab0
    __asm jmp eax
}

struct Object_00514960 {
    unsigned char unknown_00[252];
    Target_00514960 *target;
    unsigned long forward(unsigned long a);
};

unsigned long Object_00514960::forward(unsigned long a)
{
    return target->fn_00514ab0(a);
}
