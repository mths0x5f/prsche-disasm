/* 00528c90: returns the dword at offset 0x120 of the object. */
struct Object_00528c90 {
    char pad_00[288];
    unsigned long value;
    unsigned long fn_00528c90();
};

unsigned long Object_00528c90::fn_00528c90()
{
    return value;
}
