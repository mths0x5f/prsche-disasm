/* 00469a80: returns the dword at offset 0x80 of the object. */
struct Object_00469a80 {
    char pad_00[128];
    unsigned long value;
    unsigned long fn_00469a80();
};

unsigned long Object_00469a80::fn_00469a80()
{
    return value;
}
