/* 0052a3d0: Returns the element count of the pointer range held in the object at +4 (end - begin, in dwords). */
struct Range_0052a3d0 {
    long *begin;
    long *end;
};

struct Object_0052a3d0 {
    unsigned long unknown_00;
    Range_0052a3d0 *range;
    long count_0052a3d0();
};

long Object_0052a3d0::count_0052a3d0()
{
    return ((char *)range->end - (char *)range->begin) >> 2;
}
