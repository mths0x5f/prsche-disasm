/* 0041c6f0: returns the byte at offset 0x171 of the object. */
struct Object_0041c6f0 {
    char pad_00[369];
    unsigned char value;
    unsigned char fn_0041c6f0();
};

unsigned char Object_0041c6f0::fn_0041c6f0()
{
    return value;
}
