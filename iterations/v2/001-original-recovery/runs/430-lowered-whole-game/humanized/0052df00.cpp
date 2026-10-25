/* 0052df00: clears the first word of the object and returns the object. */
struct Object_0052df00 {
    unsigned long value;
    Object_0052df00 *fn_0052df00();
};

Object_0052df00 *Object_0052df00::fn_0052df00()
{
    value = 0;
    return this;
}
