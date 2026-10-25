/* 005378c0: stores its argument at +0x2c and passes (0x3c, argument) to 00540480. */
#define callee_00540480_005378c0 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00540480)

struct Object_005378c0 {
    unsigned char unknown_00[44];
    unsigned long value;
    unsigned long set(unsigned long a);
};

unsigned long Object_005378c0::set(unsigned long a)
{
    value = a;
    return callee_00540480_005378c0(0x3c, a);
}
