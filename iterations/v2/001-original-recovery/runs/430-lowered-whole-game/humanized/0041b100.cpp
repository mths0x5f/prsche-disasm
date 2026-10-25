/* 0041b100: writes half of the distance from two global extents to the object's origin into *out; returns out. */
#define extent_x_0041b100 (*(long *)0x00619784)
#define extent_y_0041b100 (*(long *)0x00619788)

struct Origin_0041b100 {
    unsigned char unknown_00[0x10];
    long x;
    long y;
    long *half_offset_0041b100(long *out);
};

long *Origin_0041b100::half_offset_0041b100(long *out)
{
    long dx = (extent_x_0041b100 - x) / 2;
    long dy = (extent_y_0041b100 - y) / 2;
    out[0] = dx;
    out[1] = dy;
    return out;
}
