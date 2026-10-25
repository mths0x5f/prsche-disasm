/* 0046ee50: returns the word at offset 0xde of the object. */
struct Object_0046ee50 {
    char pad_00[222];
    unsigned short value;
    unsigned short fn_0046ee50();
};

unsigned short Object_0046ee50::fn_0046ee50()
{
    return value;
}
