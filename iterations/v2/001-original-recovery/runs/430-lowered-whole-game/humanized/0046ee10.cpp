/* 0046ee10: returns the word at offset 0xd8 of the object. */
struct Object_0046ee10 {
    char pad_00[216];
    unsigned short value;
    unsigned short fn_0046ee10();
};

unsigned short Object_0046ee10::fn_0046ee10()
{
    return value;
}
