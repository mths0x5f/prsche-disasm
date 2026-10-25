/* 00533b70: clamps the first argument between the second and third (low bound applied first). */
long __cdecl clamp_00533b70(long value, long low, long high)
{
    if (value < low)
        value = low;
    if (value > high)
        value = high;
    return value;
}
