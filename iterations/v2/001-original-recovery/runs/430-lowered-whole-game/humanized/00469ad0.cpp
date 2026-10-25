/* 00469ad0: returns the dword at offset 0x90 of the object. */
struct Object_00469ad0 {
    char pad_00[144];
    unsigned long value;
    unsigned long fn_00469ad0();
};

unsigned long Object_00469ad0::fn_00469ad0()
{
    return value;
}
