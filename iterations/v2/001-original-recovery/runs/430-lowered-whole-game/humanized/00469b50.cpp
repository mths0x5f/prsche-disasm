/* 00469b50: returns the dword at offset 0xc0 of the object. */
struct Object_00469b50 {
    char pad_00[192];
    unsigned long value;
    unsigned long fn_00469b50();
};

unsigned long Object_00469b50::fn_00469b50()
{
    return value;
}
