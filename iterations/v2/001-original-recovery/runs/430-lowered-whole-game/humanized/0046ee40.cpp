/* 0046ee40: Stores its 16-bit argument at +0xde. */
struct Object_0046ee40 {
    unsigned char unknown_00[222];
    unsigned short field_de;
    void set_word_de_0046ee40(unsigned short value);
};

void Object_0046ee40::set_word_de_0046ee40(unsigned short value)
{
    field_de = value;
}
