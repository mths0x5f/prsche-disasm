/* 004e35e0: Returns whether the global byte at 0x006197aa is zero. */
#define global_006197aa (*(unsigned char *)0x006197aa)

unsigned long __cdecl global_byte_is_zero_6197aa_004e35e0(void)
{
    return global_006197aa == 0;
}
