/* 0046af40: returns the sign-extended word at offset 0x78 of the object. */
struct Object_0046af40 {
    char pad_00[120];
    short value;
    long fn_0046af40();
};

long Object_0046af40::fn_0046af40()
{
    return value;
}
