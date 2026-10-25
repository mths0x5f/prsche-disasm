/* 00537850: stores its argument at +0x8 and passes (0x4, argument) to 00540480. */
#define callee_00540480_00537850 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00540480)

struct Object_00537850 {
    unsigned char unknown_00[8];
    unsigned long value;
    unsigned long set(unsigned long a);
};

unsigned long Object_00537850::set(unsigned long a)
{
    value = a;
    return callee_00540480_00537850(0x4, a);
}
