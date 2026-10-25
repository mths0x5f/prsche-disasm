/* 0053e590: sets the global at 0x69eba8 to 1 and the one at 0x69ebac to 0. */
#define g_0069ebac_0053e590 (*(unsigned long *)0x0069ebac)
#define g_0069eba8_0053e590 (*(unsigned long *)0x0069eba8)

void set_0053e590()
{
    g_0069ebac_0053e590 = 0;
    g_0069eba8_0053e590 = 1;
}
