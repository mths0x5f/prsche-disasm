/* 004e2370: Returns whether the field at +0x44 == 0. */
struct Object_004e2370 {
    unsigned char unknown_00[68];
    unsigned char field_44;
    unsigned long test_field_44_004e2370();
};

unsigned long Object_004e2370::test_field_44_004e2370()
{
    return field_44 == 0;
}
