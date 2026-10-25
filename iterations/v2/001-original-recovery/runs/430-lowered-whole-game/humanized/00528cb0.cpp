/* 00528cb0: replaces the dword at +0x120 with its argument; returns the old value. */
struct Object_00528cb0 {
    unsigned char unknown_00[0x120];
    unsigned long value;
    unsigned long exchange(unsigned long a);
};

unsigned long Object_00528cb0::exchange(unsigned long a)
{
    unsigned long old = value;
    value = a;
    return old;
}
