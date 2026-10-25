/* 00537920: stores the argument at +0x1c and passes it to 005404e0 with code 0xe. */
struct Object_00537920 {
    unsigned char unknown_00[0x1c];
    unsigned long value;
    unsigned long set(unsigned long v);
};
#define call_005404e0_from_00537920 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x005404e0)

unsigned long Object_00537920::set(unsigned long v)
{
    value = v;
    return call_005404e0_from_00537920(0xe, v);
}
