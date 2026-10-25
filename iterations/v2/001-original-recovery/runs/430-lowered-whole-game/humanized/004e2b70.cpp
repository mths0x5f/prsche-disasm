/* 004e2b70: sums the 0x3c field of two linked records and one word of the argument. */
struct Record_004e2b70 {
    unsigned char unknown_00[0x3c];
    long value;
};

struct Pair_004e2b70 {
    Record_004e2b70 *first;
    Record_004e2b70 *second;
    long sum(const long *extra);
};

long Pair_004e2b70::sum(const long *extra)
{
    return second->value + first->value + extra[1];
}
