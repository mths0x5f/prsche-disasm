/* 0041c6e0: returns the byte at offset 0x170 of the object. */
struct Object_0041c6e0 {
    char pad_00[368];
    unsigned char value;
    unsigned char fn_0041c6e0();
};

unsigned char Object_0041c6e0::fn_0041c6e0()
{
    return value;
}
