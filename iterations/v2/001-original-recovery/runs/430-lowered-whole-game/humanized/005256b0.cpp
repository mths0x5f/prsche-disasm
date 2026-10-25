/* 005256b0: element count (end - begin, in dwords) of the vector held at +0xdc. */
struct Span_005256b0 {
    unsigned long begin;
    unsigned long end;
};

struct Owner_005256b0 {
    unsigned char unknown_00[220];
    Span_005256b0 *span;
    long count();
};

long Owner_005256b0::count()
{
    return (long)(span->end - span->begin) >> 2;
}
