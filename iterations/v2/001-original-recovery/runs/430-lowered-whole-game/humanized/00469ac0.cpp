/* 00469ac0: returns the dword at offset 0x78 of the object. */
struct Object_00469ac0 {
    char pad_00[120];
    unsigned long value;
    unsigned long fn_00469ac0();
};

unsigned long Object_00469ac0::fn_00469ac0()
{
    return value;
}
