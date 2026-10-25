/* 005379f0: initialises a six-dword record (1, 2, 0, 0, 0, -1) and returns it. */
struct Init_005379f0 {
    unsigned long unknown_00;
    unsigned long unknown_04;
    unsigned long unknown_08;
    unsigned long unknown_0c;
    unsigned long unknown_10;
    long unknown_14;
    Init_005379f0 *init();
};

Init_005379f0 *Init_005379f0::init()
{
    unknown_00 = 1;
    unknown_04 = 2;
    unknown_08 = 0;
    unknown_0c = 0;
    unknown_10 = 0;
    unknown_14 = -1;
    return this;
}
