/* 0046edf0: returns the word at offset 0xd4 of the object. */
struct Object_0046edf0 {
    char pad_00[212];
    unsigned short value;
    unsigned short fn_0046edf0();
};

unsigned short Object_0046edf0::fn_0046edf0()
{
    return value;
}
