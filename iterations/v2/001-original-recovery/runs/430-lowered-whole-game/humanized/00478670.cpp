/* 00478670: second word of entry n (8-byte entries) of the table at +0x38; zero for a negative index. */
struct Entry_00478670 {
    unsigned long unknown_00;
    unsigned long value;
};

struct Object_00478670 {
    unsigned char unknown_00[0x38];
    Entry_00478670 *entries;
    unsigned long get(long index);
};

unsigned long Object_00478670::get(long index)
{
    if (index < 0)
        return 0;
    return entries[index].value;
}
