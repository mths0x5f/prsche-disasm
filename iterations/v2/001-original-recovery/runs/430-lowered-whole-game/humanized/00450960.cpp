/* 00450960: the dword at +0 with its low two bytes forced to 0x2020 when bit 0 of the byte at +4 is set. */
struct Object_00450960 {
    unsigned long value;
    unsigned char flags;
    unsigned long get();
};

unsigned long Object_00450960::get()
{
    unsigned long v = value;
    if (flags & 1)
        v = (v & 0xffff2020) | 0x2020;
    return v;
}
