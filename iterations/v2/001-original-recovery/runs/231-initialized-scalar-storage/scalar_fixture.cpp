extern int DAT_005ccb34;
extern int DAT_005d0608;
extern int DAT_005e5f4c;
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned int);

static unsigned int raw_word(const void* p) {
    const unsigned char* b = static_cast<const unsigned char*>(p);
    return b[0] | (static_cast<unsigned int>(b[1]) << 8) |
        (static_cast<unsigned int>(b[2]) << 16) | (static_cast<unsigned int>(b[3]) << 24);
}
static void store_word(void* p, unsigned int value) {
    unsigned char* b = static_cast<unsigned char*>(p);
    for (unsigned int i = 0; i != 4; ++i) b[i] = static_cast<unsigned char>(value >> (i * 8));
}
extern "C" void __cdecl entry() {
    int* cells[3] = {&DAT_005ccb34, &DAT_005d0608, &DAT_005e5f4c};
    const unsigned int initials[3] = {128, 1, 10};
    const unsigned int patterns[6] = {0, 1, 0x7fffffffu, 0x80000000u, 0x80000001u, 0xffffffffu};
    if (cells[0] == cells[1] || cells[0] == cells[2] || cells[1] == cells[2]) ExitProcess(1);
    for (unsigned int c = 0; c != 3; ++c) {
        if (raw_word(cells[c]) != initials[c]) ExitProcess(2);
        for (unsigned int p = 0; p != 6; ++p) {
            store_word(cells[c], patterns[p]);
            if (raw_word(cells[c]) != patterns[p]) ExitProcess(3);
            for (unsigned int other = 0; other != 3; ++other)
                if (other != c && raw_word(cells[other]) != initials[other]) ExitProcess(4);
        }
        store_word(cells[c], initials[c]);
    }
    if (DAT_005ccb34 != 128 || DAT_005d0608 != 1 || DAT_005e5f4c != 10) ExitProcess(5);
    ExitProcess(0);
}
