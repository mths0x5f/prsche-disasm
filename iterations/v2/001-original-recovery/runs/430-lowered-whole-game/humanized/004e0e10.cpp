/* 004e0e10: Returns whether the field at +0x12c == 0. */
struct Object_004e0e10 {
    unsigned char unknown_00[300];
    unsigned long field_12c;
    unsigned long test_field_12c_004e0e10();
};

unsigned long Object_004e0e10::test_field_12c_004e0e10()
{
    return field_12c == 0;
}
