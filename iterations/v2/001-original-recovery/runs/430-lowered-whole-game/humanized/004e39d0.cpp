/* 004e39d0: initialises three words to 0, 1, 0 and returns the object. */
struct Object_004e39d0 {
    unsigned long first;
    unsigned long second;
    unsigned long third;
    Object_004e39d0 *init();
};

Object_004e39d0 *Object_004e39d0::init()
{
    first = 0;
    second = 1;
    third = 0;
    return this;
}
