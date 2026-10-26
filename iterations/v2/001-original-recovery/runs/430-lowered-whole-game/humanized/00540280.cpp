/* 00540280: rebuilds the 256-entry ramp table (entry i = (i*step)>>8, as bytes) when the step changes. */
#define ramp_step_00540280 (*(long *)0x0069ecb8)
#define ramp_table_00540280 ((unsigned char *)0x0069ebb8)

void __cdecl ramp_set_step_00540280(long step)
{
    if (ramp_step_00540280 != step) {
        long i;
        long acc = 0;
        for (i = 0; i < 0x100; i++) {
            ramp_table_00540280[i] = (unsigned char)(acc >> 8);
            acc += step;
        }
        ramp_step_00540280 = step;
    }
}
