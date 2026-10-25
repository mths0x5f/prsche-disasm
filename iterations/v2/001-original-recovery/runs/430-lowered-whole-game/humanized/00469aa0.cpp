/* 00469aa0: returns the dword at offset 0x88 of the object. */
struct Object_00469aa0 {
    char pad_00[136];
    unsigned long value;
    unsigned long fn_00469aa0();
};

unsigned long Object_00469aa0::fn_00469aa0()
{
    return value;
}
