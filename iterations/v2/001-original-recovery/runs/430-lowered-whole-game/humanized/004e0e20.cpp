/* 004e0e20: Returns whether the field at +0x12c == 2. */
struct Object_004e0e20 {
    unsigned char unknown_00[300];
    unsigned long field_12c;
    unsigned long test_field_12c_004e0e20();
};

unsigned long Object_004e0e20::test_field_12c_004e0e20()
{
    return field_12c == 2;
}
