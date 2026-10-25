/* 00538c90: returns the dword at offset 0xc of the object. */
struct Object_00538c90 {
    char pad_00[12];
    unsigned long value;
    unsigned long fn_00538c90();
};

unsigned long Object_00538c90::fn_00538c90()
{
    return value;
}
