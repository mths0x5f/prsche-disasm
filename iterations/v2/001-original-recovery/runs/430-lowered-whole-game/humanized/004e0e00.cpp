/* 004e0e00: returns the dword at offset 0x12c of the object. */
struct Object_004e0e00 {
    char pad_00[300];
    unsigned long value;
    unsigned long fn_004e0e00();
};

unsigned long Object_004e0e00::fn_004e0e00()
{
    return value;
}
