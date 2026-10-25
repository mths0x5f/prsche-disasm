/* 00539890: calls 005398b0 with this and the two arguments. */
#define call_005398b0_from_00539890 ((unsigned long (__cdecl *)(void *, unsigned long, unsigned long))0x005398b0)

struct Object_00539890 {
    unsigned long unknown_00;
    unsigned long call(unsigned long a, unsigned long b);
};

unsigned long Object_00539890::call(unsigned long a, unsigned long b)
{
    return call_005398b0_from_00539890(this, a, b);
}
