/* 00460c70: Returns the dword at +8 + index*4. */
struct Object_00460c70 {
    unsigned long unknown_00[2];
    unsigned long items[1];
    unsigned long get_00460c70(unsigned long index);
};

unsigned long Object_00460c70::get_00460c70(unsigned long index)
{
    return items[index];
}
