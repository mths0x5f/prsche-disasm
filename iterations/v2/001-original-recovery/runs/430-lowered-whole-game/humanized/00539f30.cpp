/* 00539f30: returns the dword at offset 0x4 of the object. */
struct Object_00539f30 {
    char pad_00[4];
    unsigned long value;
    unsigned long fn_00539f30();
};

unsigned long Object_00539f30::fn_00539f30()
{
    return value;
}
