/* 00537960: stores the argument at +0x24 and passes it to 005404e0 with code 0x17. */
struct Object_00537960 {
    unsigned char unknown_00[0x24];
    unsigned long value;
    unsigned long set(unsigned long v);
};
#define call_005404e0_from_00537960 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x005404e0)

unsigned long Object_00537960::set(unsigned long v)
{
    value = v;
    return call_005404e0_from_00537960(0x17, v);
}
