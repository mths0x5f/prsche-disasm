/* 00570ed0: Snapshot of the cursor state: two 48-byte globals copied to `out`. */
#define cursor_state_a_005de620 ((const unsigned long *)0x005de620)
#define cursor_state_b_005de650 ((const unsigned long *)0x005de650)

void __cdecl cursor_state_save_00570ed0(unsigned long *out)
{
    long i;

    for (i = 0; i < 12; ++i)
        out[i] = cursor_state_a_005de620[i];
    for (i = 0; i < 12; ++i)
        out[12 + i] = cursor_state_b_005de650[i];
}
