/* 00529020: returns the dword at offset 0x11c of the object. */
struct Object_00529020 {
    char pad_00[284];
    unsigned long value;
    unsigned long fn_00529020();
};

unsigned long Object_00529020::fn_00529020()
{
    return value;
}
