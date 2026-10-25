/* 00537980: stores its argument at +0x28 and passes (0xf, argument) to 00540480. */
#define callee_00540480_00537980 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00540480)

struct Object_00537980 {
    unsigned char unknown_00[40];
    unsigned long value;
    unsigned long set(unsigned long a);
};

unsigned long Object_00537980::set(unsigned long a)
{
    value = a;
    return callee_00540480_00537980(0xf, a);
}
