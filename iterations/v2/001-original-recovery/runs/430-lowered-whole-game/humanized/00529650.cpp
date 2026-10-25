/* 00529650: returns the dword at offset 0x8 of the object. */
struct Object_00529650 {
    char pad_00[8];
    unsigned long value;
    unsigned long fn_00529650();
};

unsigned long Object_00529650::fn_00529650()
{
    return value;
}
