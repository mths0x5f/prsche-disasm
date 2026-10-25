/* 0047b640: stores the argument at +0, clears +0x84 and +0x88 and returns the object. */
struct Object_0047b640 {
    unsigned long value;
    unsigned char unknown_04[0x80];
    unsigned long first;
    unsigned long second;
    Object_0047b640 *init(unsigned long v);
};

Object_0047b640 *Object_0047b640::init(unsigned long v)
{
    value = v;
    first = 0;
    second = 0;
    return this;
}
