/* 00455250: returns the dword at offset 0x0 of the object. */
struct Object_00455250 {
    unsigned long value;
    unsigned long fn_00455250();
};

unsigned long Object_00455250::fn_00455250()
{
    return value;
}
