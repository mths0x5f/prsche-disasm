/* 004e2340: stores 0 at offset 0x44 of the object. */
struct Object_004e2340 {
    char pad_00[68];
    unsigned char value;
    void fn_004e2340();
};

void Object_004e2340::fn_004e2340()
{
    value = 0;
}
