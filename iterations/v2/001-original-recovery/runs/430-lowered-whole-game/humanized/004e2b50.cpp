/* 004e2b50: [[this]+0x3c] + the dword at +4 of the argument. */
struct Table_004e2b50 {
    unsigned char unknown_00[60];
    unsigned long value;
};

struct Arg_004e2b50 {
    unsigned long unknown_00;
    unsigned long offset;
};

struct Object_004e2b50 {
    Table_004e2b50 *table;
    unsigned long sum(Arg_004e2b50 *arg);
};

unsigned long Object_004e2b50::sum(Arg_004e2b50 *arg)
{
    unsigned long base = table->value;
    return base + arg->offset;
}
