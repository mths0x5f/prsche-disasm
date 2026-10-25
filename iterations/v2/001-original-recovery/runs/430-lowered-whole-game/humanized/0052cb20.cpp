/* 0052cb20: element count of a vector of 28-byte elements held by a global. */
struct Elem_0052cb20 {
    unsigned char bytes[28];
};

struct Vector_0052cb20 {
    Elem_0052cb20 *begin;
    Elem_0052cb20 *end;
};

#define vector_0069caf4 (*(Vector_0052cb20 **)0x0069caf4)

long vector_size_0052cb20(void)
{
    return vector_0069caf4->end - vector_0069caf4->begin;
}
