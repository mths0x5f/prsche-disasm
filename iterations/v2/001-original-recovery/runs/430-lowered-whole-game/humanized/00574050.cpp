/* 00574050: Address of pixel (x, y): base + y * pitch + x * bits / 8 (three globals). */
#define pixel_bits_005de62e (*(const unsigned char *)0x005de62e)
#define pixel_pitch_005de644 (*(const long *)0x005de644)
#define pixel_base_005de64c (*(const long *)0x005de64c)

long __cdecl pixel_address_00574050(long x, long y)
{
    return pixel_base_005de64c + (((long)pixel_bits_005de62e * x) >> 3) + pixel_pitch_005de644 * y;
}
