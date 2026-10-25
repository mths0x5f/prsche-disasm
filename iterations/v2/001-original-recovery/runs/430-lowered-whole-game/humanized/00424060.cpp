/* 00424060: copies a dword from the first argument and a byte from the second; returns the object. */
struct Value_00424060 {
    unsigned long first;
    unsigned char second;
    Value_00424060 *set(unsigned long *a, unsigned char *b);
};

Value_00424060 *Value_00424060::set(unsigned long *a, unsigned char *b)
{
    unsigned long f = *a;
    first = f;
    second = *b;
    return this;
}
