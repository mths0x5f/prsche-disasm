/* 005adb5b: Shifts a 96-bit number of the float formatter right by one bit. */
void __cdecl float_shift_right_005adb5b(unsigned long *value)
{
    value[0] = (value[0] >> 1) | (value[1] << 31);
    value[1] = (value[1] >> 1) | (value[2] << 31);
    value[2] >>= 1;
}
