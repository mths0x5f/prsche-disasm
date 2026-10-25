/* 0052a570: returns the address of the member at offset 0x14. */
struct Object_0052a570 {
    char pad_00[20];
    unsigned long value;
    unsigned long fn_0052a570();
};

unsigned long Object_0052a570::fn_0052a570()
{
    return (unsigned long)&value;
}
