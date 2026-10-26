/* 00537a30: stores its argument at offset 0x0 of the object. */
struct Object_00537a30 {
    unsigned long value;
    void fn_00537a30(unsigned long v);
};

void Object_00537a30::fn_00537a30(unsigned long v)
{
    value = v;
}
