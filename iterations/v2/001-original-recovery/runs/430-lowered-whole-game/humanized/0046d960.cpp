/* 0046d960: element count (end - begin, in dwords) of the vector the global at 0x628178 points to. */
struct Span_0046d960 {
    unsigned long begin;
    unsigned long end;
};

#define g_00628178_0046d960 (*(Span_0046d960 **)0x00628178)

long count_0046d960()
{
    Span_0046d960 *span = g_00628178_0046d960;
    return (long)(span->end - span->begin) >> 2;
}
