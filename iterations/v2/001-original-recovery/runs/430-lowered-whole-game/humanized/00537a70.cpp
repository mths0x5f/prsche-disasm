/* 00537a70: Stores its argument at +0x14 and +0x18. */
struct Object_00537a70 {
    unsigned char unknown_00[20];
    unsigned long field_14;
    unsigned long field_18;
    void set_00537a70(unsigned long value);
};

void Object_00537a70::set_00537a70(unsigned long value)
{
    field_14 = value;
    field_18 = value;
}
