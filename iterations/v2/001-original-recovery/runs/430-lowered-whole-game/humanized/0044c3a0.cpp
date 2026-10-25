/* 0044c3a0: stores its two arguments at +0 and +4; returns the object. */
struct Object_0044c3a0 {
    unsigned long first;
    unsigned long second;
    Object_0044c3a0 *set(unsigned long a, unsigned long b);
};

Object_0044c3a0 *Object_0044c3a0::set(unsigned long a, unsigned long b)
{
    first = a;
    second = b;
    return this;
}
