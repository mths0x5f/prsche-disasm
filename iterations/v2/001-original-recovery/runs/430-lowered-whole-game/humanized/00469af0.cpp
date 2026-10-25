/* 00469af0: returns the dword at offset 0x98 of the object. */
struct Object_00469af0 {
    char pad_00[152];
    unsigned long value;
    unsigned long fn_00469af0();
};

unsigned long Object_00469af0::fn_00469af0()
{
    return value;
}
