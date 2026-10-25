/* 00469ab0: returns the dword at offset 0x8c of the object. */
struct Object_00469ab0 {
    char pad_00[140];
    unsigned long value;
    unsigned long fn_00469ab0();
};

unsigned long Object_00469ab0::fn_00469ab0()
{
    return value;
}
