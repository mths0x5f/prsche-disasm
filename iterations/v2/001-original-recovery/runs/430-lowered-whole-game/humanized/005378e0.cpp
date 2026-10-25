/* 005378e0: stores its argument at +0x14 and passes (0x9, argument) to 00540480. */
#define callee_00540480_005378e0 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00540480)

struct Object_005378e0 {
    unsigned char unknown_00[20];
    unsigned long value;
    unsigned long set(unsigned long a);
};

unsigned long Object_005378e0::set(unsigned long a)
{
    value = a;
    return callee_00540480_005378e0(0x9, a);
}
