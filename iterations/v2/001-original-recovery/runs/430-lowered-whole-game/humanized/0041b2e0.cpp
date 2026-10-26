/* 0041b2e0: Stores its argument into the dword at +0xfc. */
struct Object_0041b2e0 {
    unsigned char unknown_00[252];
    unsigned long field_fc;
    void set_field_fc_0041b2e0(unsigned long value);
};

void Object_0041b2e0::set_field_fc_0041b2e0(unsigned long value)
{
    field_fc = value;
}
