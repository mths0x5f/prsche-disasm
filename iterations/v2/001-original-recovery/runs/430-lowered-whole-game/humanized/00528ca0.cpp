/* 00528ca0: Clears the dword at +0x120. */
struct Object_00528ca0 {
    unsigned char unknown_00[288];
    unsigned long field_120;
    void clear_field_120_00528ca0();
};

void Object_00528ca0::clear_field_120_00528ca0()
{
    field_120 = 0;
}
