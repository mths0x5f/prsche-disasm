/* 00423e90: copy-constructs a 5-byte value (dword + byte) from the argument; returns the object. */
struct Value_00423e90 {
    unsigned long first;
    unsigned char second;
    Value_00423e90 *copy(Value_00423e90 *src);
};

Value_00423e90 *Value_00423e90::copy(Value_00423e90 *src)
{
    unsigned long f = src->first;
    first = f;
    second = src->second;
    return this;
}
