/* 0044af60: initialises four words to 0, 0, -1, -1 and returns the object. */
struct Object_0044af60 {
    unsigned long first;
    unsigned long second;
    long third;
    long fourth;
    Object_0044af60 *init();
};

Object_0044af60 *Object_0044af60::init()
{
    first = 0;
    second = 0;
    third = -1;
    fourth = -1;
    return this;
}
