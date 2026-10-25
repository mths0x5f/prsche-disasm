/* 00474ac0: stores the vtable 0x5b465c and its argument at +4; returns the object. */
struct Object_00474ac0 {
    void *vtable;
    unsigned long value;
    Object_00474ac0 *init(unsigned long a);
};

Object_00474ac0 *Object_00474ac0::init(unsigned long a)
{
    vtable = (void *)0x005b465c;
    value = a;
    return this;
}
