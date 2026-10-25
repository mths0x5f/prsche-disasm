/* 0052a000: first element pointer of the vector at +0x10 plus index * 12. */
struct Vector_0052a000 {
    unsigned long begin;
};

struct Object_0052a000 {
    unsigned char unknown_00[0x10];
    Vector_0052a000 *vector;
    unsigned long element(unsigned long index);
};

unsigned long Object_0052a000::element(unsigned long index)
{
    return vector->begin + index * 12;
}
