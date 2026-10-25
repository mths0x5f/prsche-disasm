/* 005255e0: element count (end - begin, in dwords) of the vector held at +0xd8. */
struct Span_005255e0 {
    unsigned long begin;
    unsigned long end;
};

struct Owner_005255e0 {
    unsigned char unknown_00[216];
    Span_005255e0 *span;
    long count();
};

long Owner_005255e0::count()
{
    return (long)(span->end - span->begin) >> 2;
}
