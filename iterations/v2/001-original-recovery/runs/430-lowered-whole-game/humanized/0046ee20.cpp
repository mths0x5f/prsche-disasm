/* 0046ee20: Stores its 16-bit argument at +0xdc. */
struct Object_0046ee20 {
    unsigned char unknown_00[220];
    unsigned short field_dc;
    void set_word_dc_0046ee20(unsigned short value);
};

void Object_0046ee20::set_word_dc_0046ee20(unsigned short value)
{
    field_dc = value;
}
