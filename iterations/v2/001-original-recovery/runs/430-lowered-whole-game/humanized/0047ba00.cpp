/* 0047ba00: clears the first word of the object and returns the object. */
struct Object_0047ba00 {
    unsigned long value;
    Object_0047ba00 *fn_0047ba00();
};

Object_0047ba00 *Object_0047ba00::fn_0047ba00()
{
    value = 0;
    return this;
}
