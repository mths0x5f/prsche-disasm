/* 005a6abf: Resets the CRT locale tables: 257 bytes at 006c0400 and five words. */
#define locale_table_006c0400 ((unsigned char *)0x006c0400)
#define locale_words_006c02f0 ((unsigned long *)0x006c02f0)
#define locale_code_006c02ec (*(unsigned long *)0x006c02ec)
#define locale_flag_006c02fc (*(unsigned long *)0x006c02fc)
#define locale_mode_006c0504 (*(unsigned long *)0x006c0504)

void __cdecl locale_reset_005a6abf(void)
{
    long i;

    for (i = 0; i < 0x101; ++i)
        locale_table_006c0400[i] = 0;
    locale_code_006c02ec = 0;
    locale_flag_006c02fc = 0;
    locale_mode_006c0504 = 0;
    locale_words_006c02f0[0] = 0;
    locale_words_006c02f0[1] = 0;
    locale_words_006c02f0[2] = 0;
}
