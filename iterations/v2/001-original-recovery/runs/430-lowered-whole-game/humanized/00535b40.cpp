/* 00535b40: Sets the render mode flag byte (a global). */
#define render_mode_flag_0069dd1d (*(unsigned char *)0x0069dd1d)

void __cdecl render_mode_set_flag_00535b40(unsigned char flag)
{
    render_mode_flag_0069dd1d = flag;
}
