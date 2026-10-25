/* 00525f40: returns the address of the member at offset 0x8. */
struct Object_00525f40 {
    char pad_00[8];
    unsigned long value;
    unsigned long fn_00525f40();
};

unsigned long Object_00525f40::fn_00525f40()
{
    return (unsigned long)&value;
}
