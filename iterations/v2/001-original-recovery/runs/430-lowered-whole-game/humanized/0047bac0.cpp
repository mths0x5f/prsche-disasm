/* 0047bac0: returns the dword at offset 0x84 of the object. */
struct Object_0047bac0 {
    char pad_00[132];
    unsigned long value;
    unsigned long fn_0047bac0();
};

unsigned long Object_0047bac0::fn_0047bac0()
{
    return value;
}
