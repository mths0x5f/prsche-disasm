/* 00537900: stores its argument at +0x18 and passes (0x15, argument) to 00540480. */
#define callee_00540480_00537900 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00540480)

struct Object_00537900 {
    unsigned char unknown_00[24];
    unsigned long value;
    unsigned long set(unsigned long a);
};

unsigned long Object_00537900::set(unsigned long a)
{
    value = a;
    return callee_00540480_00537900(0x15, a);
}
