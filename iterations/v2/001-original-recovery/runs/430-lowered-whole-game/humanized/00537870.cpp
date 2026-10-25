/* 00537870: stores its argument at +0xc and passes (0x39, argument) to 00540480. */
#define callee_00540480_00537870 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00540480)

struct Object_00537870 {
    unsigned char unknown_00[12];
    unsigned long value;
    unsigned long set(unsigned long a);
};

unsigned long Object_00537870::set(unsigned long a)
{
    value = a;
    return callee_00540480_00537870(0x39, a);
}
