/* 005aba53: Clears a 12-byte number of the float parser. */
void __cdecl float_parse_clear_005aba53(unsigned long *value)
{
    value[0] = 0;
    value[1] = 0;
    value[2] = 0;
}
