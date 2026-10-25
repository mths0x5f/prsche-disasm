/* 0044de20: copies a 16-byte record (does nothing for a null destination); returns the destination. */
struct Quad_0044de20 {
    unsigned long a;
    unsigned long b;
    unsigned long c;
    unsigned long d;
};

Quad_0044de20 *__cdecl copy_quad_0044de20(Quad_0044de20 *dest, Quad_0044de20 *src)
{
    if (dest != 0) {
        dest->a = src->a;
        dest->b = src->b;
        dest->c = src->c;
        dest->d = src->d;
    }
    return dest;
}
