/* 00423d60: Stores its byte argument at +0xed. */
struct Object_00423d60 {
    unsigned char unknown_00[237];
    unsigned char field_ed;
    void set_byte_ed_00423d60(unsigned char value);
};

void Object_00423d60::set_byte_ed_00423d60(unsigned char value)
{
    field_ed = value;
}
