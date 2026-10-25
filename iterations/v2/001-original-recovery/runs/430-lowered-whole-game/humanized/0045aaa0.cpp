/* 0045aaa0: stores the vtable 0x5b3e70 and its argument at +4; returns the object. */
struct Object_0045aaa0 {
    void *vtable;
    unsigned long value;
    Object_0045aaa0 *init(unsigned long a);
};

Object_0045aaa0 *Object_0045aaa0::init(unsigned long a)
{
    vtable = (void *)0x005b3e70;
    value = a;
    return this;
}
