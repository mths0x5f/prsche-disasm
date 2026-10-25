/* 0045d3a0: returns the dword at offset 0x70 of the object. */
struct Object_0045d3a0 {
    char pad_00[112];
    unsigned long value;
    unsigned long fn_0045d3a0();
};

unsigned long Object_0045d3a0::fn_0045d3a0()
{
    return value;
}
