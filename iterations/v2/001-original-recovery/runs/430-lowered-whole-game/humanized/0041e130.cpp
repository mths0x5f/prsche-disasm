/* 0041e130: Stores its argument into the dword at +0xac. */
struct Object_0041e130 {
    unsigned char unknown_00[172];
    unsigned long field_ac;
    void set_field_ac_0041e130(unsigned long value);
};

void Object_0041e130::set_field_ac_0041e130(unsigned long value)
{
    field_ac = value;
}
