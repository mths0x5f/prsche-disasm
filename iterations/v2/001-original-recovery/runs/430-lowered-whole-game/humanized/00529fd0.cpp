/* 00529fd0: returns the address of the member at offset 0x4. */
struct Object_00529fd0 {
    char pad_00[4];
    unsigned long value;
    unsigned long fn_00529fd0();
};

unsigned long Object_00529fd0::fn_00529fd0()
{
    return (unsigned long)&value;
}
