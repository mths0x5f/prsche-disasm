/* 0046ee00: Stores its 16-bit argument at +0xd8. */
struct Object_0046ee00 {
    unsigned char unknown_00[216];
    unsigned short field_d8;
    void set_word_d8_0046ee00(unsigned short value);
};

void Object_0046ee00::set_word_d8_0046ee00(unsigned short value)
{
    field_d8 = value;
}
