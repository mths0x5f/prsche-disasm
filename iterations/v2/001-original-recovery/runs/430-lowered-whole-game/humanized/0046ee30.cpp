/* 0046ee30: returns the word at offset 0xdc of the object. */
struct Object_0046ee30 {
    char pad_00[220];
    unsigned short value;
    unsigned short fn_0046ee30();
};

unsigned short Object_0046ee30::fn_0046ee30()
{
    return value;
}
