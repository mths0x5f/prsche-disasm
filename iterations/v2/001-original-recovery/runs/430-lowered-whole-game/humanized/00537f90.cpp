/* 00537f90: Bits per pixel of a render descriptor format (table of 128 bytes). */
#define render_format_bits_005de890 ((const unsigned char *)0x005de890)

unsigned long __cdecl render_descriptor_bits_00537f90(const unsigned long *format)
{
    return render_format_bits_005de890[*format & 0x7f];
}
