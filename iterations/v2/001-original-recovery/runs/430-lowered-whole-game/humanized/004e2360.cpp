/* 004e2360: stores 1 at offset 0x44 of the object. */
struct Object_004e2360 {
    char pad_00[68];
    unsigned char value;
    void fn_004e2360();
};

void Object_004e2360::fn_004e2360()
{
    value = 1;
}
