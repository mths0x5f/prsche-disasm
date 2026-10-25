/* 00537830: stores its argument at +0x4 and passes (0x28, argument) to 00540480. */
#define callee_00540480_00537830 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00540480)

struct Object_00537830 {
    unsigned char unknown_00[4];
    unsigned long value;
    unsigned long set(unsigned long a);
};

unsigned long Object_00537830::set(unsigned long a)
{
    value = a;
    return callee_00540480_00537830(0x28, a);
}
