/* 0041b2f0: stores 1 at offset 0x102 of the object. */
struct Object_0041b2f0 {
    char pad_00[258];
    unsigned char value;
    void fn_0041b2f0();
};

void Object_0041b2f0::fn_0041b2f0()
{
    value = 1;
}
