extern int DAT_00690848;
extern int DAT_00656864;
extern int DAT_00656ac0;
extern int DAT_006a6450;
extern int DAT_00699c84;
extern unsigned int DAT_00699fe0;
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
    void* cells[6] = {&DAT_00690848, &DAT_00656864, &DAT_00656ac0,
        &DAT_006a6450, &DAT_00699c84, &DAT_00699fe0};
    const unsigned int patterns[6] = {0, 1, 0x7fffffffu, 0x80000000u, 0x80000001u, 0xffffffffu};
    for (unsigned int i = 0; i != 6; ++i) {
        if (raw_word(cells[i]) != 0) ExitProcess(1);
        for (unsigned int j = i + 1; j != 6; ++j)
            if (cells[i] == cells[j]) ExitProcess(2);
    }
    for (unsigned int i = 0; i != 6; ++i) {
        for (unsigned int p = 0; p != 6; ++p) {
            store_word(cells[i], patterns[p]);
            if (raw_word(cells[i]) != patterns[p]) ExitProcess(3);
            for (unsigned int j = 0; j != 6; ++j)
                if (j != i && raw_word(cells[j]) != 0) ExitProcess(4);
        }
        store_word(cells[i], 0);
    }
    for (unsigned int i = 0; i != 6; ++i)
        if (raw_word(cells[i]) != 0) ExitProcess(5);
    ExitProcess(0);
}
