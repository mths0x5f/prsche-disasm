/* 0046af50: returns the dword at offset 0x7c of the object. */
struct Object_0046af50 {
    char pad_00[124];
    unsigned long value;
    unsigned long fn_0046af50();
};

unsigned long Object_0046af50::fn_0046af50()
{
    return value;
}
