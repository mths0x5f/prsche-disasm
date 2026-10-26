/* 0044f220: increments the global at 00657d70, wrapping from 4 to 0. */
#define counter_00657d70 (*(unsigned long *)0x00657d70)

void __cdecl advance_counter_0044f220(void)
{
    unsigned long next = counter_00657d70 + 1;
    counter_00657d70 = next;
    if (next == 4)
        counter_00657d70 = 0;
}
