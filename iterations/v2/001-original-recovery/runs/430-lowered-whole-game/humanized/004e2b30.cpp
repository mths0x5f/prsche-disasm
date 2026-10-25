/* 004e2b30: sums the 0x38 field of two linked records and one word of the argument. */
struct Record_004e2b30 {
    unsigned char unknown_00[0x38];
    long value;
};

struct Pair_004e2b30 {
    Record_004e2b30 *first;
    Record_004e2b30 *second;
    long sum(const long *extra);
};

long Pair_004e2b30::sum(const long *extra)
{
    return second->value + first->value + extra[0];
}
