/* 005255a0: element count (end - begin, in dwords) of the vector held at +0xd4. */
struct Span_005255a0 {
    unsigned long begin;
    unsigned long end;
};

struct Owner_005255a0 {
    unsigned char unknown_00[212];
    Span_005255a0 *span;
    long count();
};

long Owner_005255a0::count()
{
    return (long)(span->end - span->begin) >> 2;
}
