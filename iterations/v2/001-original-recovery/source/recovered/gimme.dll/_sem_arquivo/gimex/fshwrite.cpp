// FSH Shape File module: wopen, write, wclose.
// gimme.dll 3a43b0f6…, VA 100f9a60–100fc154 and 10104aa8–10106e75 (the writer half of the shape
// library, see fsh.h; the 18fb block compressor 100fc155–10104a9f is in fshdxt.cpp).
// Function names are role names; the original VA of each function is cited above it.

#include <string.h>

#include "fsh.h"

// 100f9a60.  The table has room for `frames` entries; write() fills them in order.
int GCALL FSH_wopen(void **handle, GSTREAM *stream, const char *, int frames)
{
    int ok = 0;
    unsigned size = (frames * sizeof(FSHSHAPE) + 0x13) & ~0xfu;
    FSHTABLE *table = (FSHTABLE *)galloc(size);
    FSHHANDLE *fsh;
    if (table)
    {
        memset(table, 0, size);
        table->count = frames;
        fsh = (FSHHANDLE *)galloc(sizeof(FSHHANDLE));
        if (fsh)
        {
            memset(fsh, 0, sizeof(FSHHANDLE));
            fsh->count = frames;
            fsh->tag = GTAG('S', 'H', 'P', 'I');
            fsh->size = sizeof(FSHHANDLE);
            fsh->current = 0;
            fsh->stream = stream;
            fsh->table = table;
            *handle = fsh;
            ok = 1;
        }
    }
    return ok;
}

// ---------------------------------------------------------------------------------------------
// Helpers (static copies of the reader's 10107a2a, 101079c5, 10107986, 1010b5d6, 1010667c,
// 101089ad)

// 100fbc49.
static int BitsPerPixel(const unsigned char *block, int type)
{
    int bits;
    if (type == 3)
    {
        if (block[0] == 0x22)
            bits = 24;
        else if (block[0] == 0x24)
            bits = 24;
        else
            bits = 8;
    }
    else
    {
        switch (block[0] & 0x7f)
        {
        case 0x01: bits = 4; break;
        case 0x02: bits = 8; break;
        case 0x03: bits = 15; break;
        case 0x04: bits = 24; break;
        case 0x05: bits = 32; break;
        case 0x20: bits = 15; break;
        case 0x21: bits = 32; break;
        case 0x22: bits = 24; break;
        case 0x23: bits = 16; break;
        case 0x24: bits = 24; break;
        case 0x27: bits = 16; break;
        case 0x28: bits = 16; break;
        case 0x29: bits = 16; break;
        case 0x2a: bits = 32; break;
        case 0x2c: bits = 32; break;
        case 0x2d: bits = 16; break;
        case 0x2e: bits = 32; break;
        case 0x30: bits = 15; break;
        case 0x31: bits = 16; break;
        case 0x32: bits = 16; break;
        case 0x33: bits = 32; break;
        case 0x34: bits = 15; break;
        case 0x35: bits = 16; break;
        case 0x36: bits = 16; break;
        case 0x37: bits = 32; break;
        case 0x40: bits = 4; break;
        case 0x41: bits = 8; break;
        case 0x42: bits = 16; break;
        case 0x43: bits = 24; break;
        case 0x44: bits = 1; break;
        case 0x50: bits = 15; break;
        case 0x51: bits = 16; break;
        case 0x52: bits = 16; break;
        case 0x55: bits = 4; break;
        case 0x56: bits = 8; break;
        case 0x60: bits = 1; break;
        case 0x61: bits = 4; break;
        case 0x62: bits = 4; break;
        case 0x63: bits = 4; break;
        case 0x64: bits = 8; break;
        case 0x65: bits = 8; break;
        case 0x66: bits = 8; break;
        case 0x67: bits = 16; break;
        case 0x68: bits = 15; break;
        case 0x69: bits = 16; break;
        case 0x6a: bits = 32; break;
        case 0x6c: bits = 16; break;
        case 0x6d: bits = 16; break;
        case 0x78: bits = 16; break;
        case 0x79: bits = 1; break;
        case 0x7a: bits = 4; break;
        case 0x7b: bits = 8; break;
        case 0x7d: bits = 32; break;
        case 0x7e: bits = 15; break;
        case 0x7f: bits = 24; break;
        default: bits = 8; break;
        }
    }
    return bits;
}

// 100fa224.
static int RowBytes(int width, int bits, int type)
{
    int bytes;
    if (bits == 15)
        bits = 16;
    if (type < 2 || type > 5)
        bytes = ((width * bits + 15) & ~15) / 8;
    else
        bytes = ((width * bits + 7) & ~7) / 8;
    return bytes;
}

// 100fa1e5.
static int ImageBytes(int width, int height, int bits, int type)
{
    int bytes = RowBytes(width, bits, type);
    bytes = bytes * height;
    bytes = (bytes + 15) & ~15;
    return bytes;
}

// 100fc099.
static int SwizzleIndex(int x, int y, int width, int height)
{
    int linear = y * width + x;
    int sx = 0;
    int sy = 0;
    unsigned char xbit = 0;
    unsigned char ybit = 0;
    int bit;
    for (bit = 1; bit < width || bit < height; bit <<= 1)
    {
        if (bit < height)
        {
            sy |= (linear & 1) << ybit;
            ++ybit;
            linear >>= 1;
        }
        if (bit < width)
        {
            sx |= (linear & 1) << xbit;
            ++xbit;
            linear >>= 1;
        }
    }
    return sy * width + sx;
}

// 10104aa8.  Number of significant bits.  The swizzle test in BuildBitmap compares a size with
// 1 << BitCount(size), which never holds, so the writer always clears the swizzle attribute.
static int BitCount(unsigned value)
{
    int count = 0;
    for (; value; value >>= 1)
        ++count;
    return count;
}

// 1010667c.
static int IsRefPack(const unsigned char *data)
{
    if (ggetm(data, 2) != 0x10fb && ggetm(data, 2) != 0x11fb)
        return 0;
    return 100;
}

// 101066c1.  RefPack decoder (same as the reader's 101089ad).
static int RefUnpack(const unsigned char *source, int *used, unsigned char *destination)
{
    const unsigned char *s = source;
    unsigned char *d = destination;
    const unsigned char *reference;
    unsigned char first, second, third, fourth;
    unsigned run;
    unsigned header;
    int length = 0;
    if (s)
    {
        header = *s++;
        header = (header << 8) + *s++;
        if (header & 0x100)
            s += 3;
        length = *s++;
        length = (length << 8) + *s++;
        length = (length << 8) + *s++;
        for (;;)
        {
            first = *s++;
            if (!(first & 0x80))
            {
                second = *s++;
                run = first & 3;
                while (run--)
                    *d++ = *s++;
                reference = d - 1 - (((first & 0x60) << 3) + second);
                run = ((first & 0x1c) >> 2) + 3 - 1;
                do
                    *d++ = *reference++;
                while (run--);
                continue;
            }
            if (!(first & 0x40))
            {
                second = *s++;
                third = *s++;
                run = second >> 6;
                while (run--)
                    *d++ = *s++;
                reference = d - 1 - (((second & 0x3f) << 8) + third);
                run = (first & 0x3f) + 4 - 1;
                do
                    *d++ = *reference++;
                while (run--);
                continue;
            }
            if (!(first & 0x20))
            {
                second = *s++;
                third = *s++;
                fourth = *s++;
                run = first & 3;
                while (run--)
                    *d++ = *s++;
                reference = d - 1 - (((first & 0x10) >> 4 << 16) + (second << 8) + third);
                run = ((first & 0x0c) >> 2 << 8) + fourth + 5 - 1;
                do
                    *d++ = *reference++;
                while (run--);
                continue;
            }
            run = ((first & 0x1f) << 2) + 4;
            if (run <= 112)
            {
                while (run--)
                    *d++ = *s++;
                continue;
            }
            run = first & 3;
            while (run--)
                *d++ = *s++;
            break;
        }
    }
    if (used)
        *used = (int)(s - source);
    return length;
}

// ---------------------------------------------------------------------------------------------
// RefPack encoder

// 100faeec.
static unsigned MatchLength(const unsigned char *a, const unsigned char *b, unsigned limit)
{
    unsigned length = 0;
    while (length < limit && *a++ == *b++)
        ++length;
    return length;
}

#define REFHASH(p) ((unsigned)(((p)[0] << 8) | (p)[2]) ^ ((unsigned)(p)[1] << 4))

// 100fa92e.  Hash-chained RefPack compressor (64K heads, 128K links); `maxback` is clamped and
// otherwise unused.  quick != 0 hashes only the first byte of each match.
static int RefCompress(const unsigned char *from, int length, unsigned char *dest, unsigned maxback, int quick)
{
    unsigned matchlength, cost, run, offset, bestoffset, bestlength, bestcost, limit;
    const unsigned char *candidate;
    const unsigned char *current;
    const unsigned char *literal;
    unsigned char *to;
    int hash, position, minposition, i;
    int *link;
    int *hashtable;
    to = dest;
    run = 0;
    current = from;
    literal = from;
    if (maxback > 0x1ffff)
        maxback = 0x1ffff;
    hashtable = (int *)galloc(0x10000 * sizeof(int));
    if (!hashtable)
        return 0;
    link = (int *)galloc(0x20000 * sizeof(int));
    if (!link)
        return 0;
    for (i = 0; i < 0x10000; ++i)
        hashtable[i] = -1;
    while (length > 0)
    {
        bestoffset = 0;
        bestlength = 2;
        bestcost = 2;
        limit = length < 0x404 ? length : 0x404;
        candidate = current - 1;
        hash = REFHASH(current);
        position = hashtable[hash];
        minposition = (int)(current - from) - 0x1ffff > 0 ? (int)(current - from) - 0x1ffff : 0;
        if (position >= minposition)
        {
            do
            {
                candidate = from + position;
                if (current[bestlength] == candidate[bestlength])
                {
                    matchlength = MatchLength(current, candidate, limit);
                    if (matchlength > bestlength)
                    {
                        offset = (unsigned)(current - 1 - candidate);
                        if (offset < 0x400 && matchlength <= 10)
                            cost = 2;
                        else if (offset < 0x4000 && matchlength <= 67)
                            cost = 3;
                        else
                            cost = 4;
                        if (matchlength - cost + 4 > bestlength - bestcost + 4)
                        {
                            bestlength = matchlength;
                            bestcost = cost;
                            bestoffset = offset;
                            if (bestlength >= 0x404)
                                break;
                        }
                    }
                }
            } while ((position = link[position & 0x1ffff]) >= minposition);
        }
        if (bestcost >= bestlength || length < 4)
        {
            position = (int)(current - from);
            link[position & 0x1ffff] = hashtable[hash];
            hashtable[hash] = position;
            ++run;
            ++current;
            --length;
        }
        else
        {
            while (run > 3)
            {
                matchlength = (run & ~3u) > 0x70 ? 0x70 : run & ~3u;
                run -= matchlength;
                *to++ = (unsigned char)(0xe0 + (matchlength >> 2) - 1);
                memcpy(to, literal, matchlength);
                literal += matchlength;
                to += matchlength;
            }
            if (bestcost == 2)
            {
                *to++ = (unsigned char)(((bestoffset >> 8) << 5) + ((bestlength - 3) << 2) + run);
                *to++ = (unsigned char)bestoffset;
            }
            else if (bestcost == 3)
            {
                *to++ = (unsigned char)(0x80 + (bestlength - 4));
                *to++ = (unsigned char)((run << 6) + (bestoffset >> 8));
                *to++ = (unsigned char)bestoffset;
            }
            else
            {
                *to++ = (unsigned char)(0xc0 + ((bestoffset >> 16) << 4) + (((bestlength - 5) >> 8) << 2) + run);
                *to++ = (unsigned char)(bestoffset >> 8);
                *to++ = (unsigned char)bestoffset;
                *to++ = (unsigned char)(bestlength - 5);
            }
            if (run)
            {
                memcpy(to, literal, run);
                to += run;
                run = 0;
            }
            if (quick)
            {
                position = (int)(current - from);
                link[position & 0x1ffff] = hashtable[hash];
                hashtable[hash] = position;
                current += bestlength;
            }
            else
            {
                for (i = 0; i < (int)bestlength; ++i)
                {
                    hash = REFHASH(current);
                    position = (int)(current - from);
                    link[position & 0x1ffff] = hashtable[hash];
                    hashtable[hash] = position;
                    ++current;
                }
            }
            literal = current;
            length -= bestlength;
        }
    }
    while (run > 3)
    {
        matchlength = (run & ~3u) > 0x70 ? 0x70 : run & ~3u;
        run -= matchlength;
        *to++ = (unsigned char)(0xe0 + (matchlength >> 2) - 1);
        memcpy(to, literal, matchlength);
        literal += matchlength;
        to += matchlength;
    }
    *to++ = (unsigned char)(0xfc + run);
    if (run)
    {
        memcpy(to, literal, run);
        to += run;
    }
    gfree(link);
    gfree(hashtable);
    return (int)(to - dest);
}

// 100fa8bb (stdcall in the original).  10fb header with the 3-byte unpacked size, then data.
static int GCALL RefPack(const unsigned char *source, int length, unsigned char *destination, int *)
{
    unsigned maxback = 0x20000;
    int quick = 0;
    int header;
    gputm(destination, 0x10fb, 2);
    gputm(destination + 2, length, 3);
    header = 5;
    return header + RefCompress(source, length, destination + header, maxback, quick);
}

// ---------------------------------------------------------------------------------------------
// Pixel conversion (GCOLOUR order b, g, r, a)

// 100fb84c.  1555 ARGB.
static unsigned short Pack1555(const unsigned char *colour)
{
    int a = colour[3] >> 7;
    int r = (colour[2] * 0x1f + 0x80) / 0xff;
    int g = (colour[1] * 0x1f + 0x80) / 0xff;
    int b = (colour[0] * 0x1f + 0x80) / 0xff;
    return (unsigned short)(a << 15 | r << 10 | g << 5 | b);
}

// 100fb8d4.  565; alpha below 0x3f gives 0, an opaque black becomes 1.
static unsigned short Pack565(const unsigned char *colour)
{
    int a = colour[3];
    int r = (colour[2] * 0x1f + 0x80) / 0xff;
    int g = (colour[1] * 0x3f + 0x80) / 0xff;
    int b = (colour[0] * 0x1f + 0x80) / 0xff;
    int value;
    if (a < 0x3f)
    {
        value = 0;
    }
    else
    {
        value = r << 11 | g << 5 | b;
        if (value == 0)
            value = 1;
    }
    return (unsigned short)value;
}

// 100fb96d.  1555 ABGR (red low): alpha below 0x3f gives 0, below 0xbf sets bit 15, an opaque
// black becomes 0x400.
static unsigned short PackBgr1555(const unsigned char *colour)
{
    unsigned a = colour[3];
    int r = (colour[2] * 0x1f + 0x80) / 0xff;
    int g = (colour[1] * 0x1f + 0x80) / 0xff;
    int b = (colour[0] * 0x1f + 0x80) / 0xff;
    int value = b << 10 | g << 5 | r;
    if (a < 0x3f)
    {
        value = 0;
    }
    else if (a >= 0xbf)
    {
        if (value == 0)
            value = 0x400;
    }
    else
    {
        value |= 0x8000;
    }
    return (unsigned short)value;
}

// 100fba1a.  Luminance in the high byte, alpha in the low byte.
static unsigned short PackGreyAlpha(const unsigned char *colour)
{
    int value = (int)(colour[2] * 0.299 + colour[1] * 0.587 + colour[0] * 0.114) << 8;
    value |= colour[3];
    return (unsigned short)value;
}

// 100fba82.  5551 RGBA; alpha below 0x3f gives 0.
static unsigned short Pack5551(const unsigned char *colour)
{
    int a = colour[3];
    int r = (colour[2] * 0x1f + 0x80) / 0xff & 0x1f;
    int g = (colour[1] * 0x1f + 0x80) / 0xff & 0x1f;
    int b = (colour[0] * 0x1f + 0x80) / 0xff & 0x1f;
    int value;
    if (a < 0x3f)
        value = 0;
    else
        value = r << 11 | g << 6 | b << 1 | 1;
    return (unsigned short)value;
}

// 100fbb1e.  1555 ABGR with rounded alpha.
static unsigned short PackBgr1555Alpha(const unsigned char *colour)
{
    int a = (colour[3] + 0x80) / 0xff;
    int r = (colour[2] * 0x1f + 0x80) / 0xff;
    int g = (colour[1] * 0x1f + 0x80) / 0xff;
    int b = (colour[0] * 0x1f + 0x80) / 0xff;
    return (unsigned short)(a << 15 | b << 10 | g << 5 | r);
}

// 100fbbb2.  4444 ARGB.
static unsigned short Pack4444(const unsigned char *colour)
{
    int a = (colour[3] * 0xf + 0x80) / 0xff;
    int r = (colour[2] * 0xf + 0x80) / 0xff;
    int g = (colour[1] * 0xf + 0x80) / 0xff;
    int b = (colour[0] * 0xf + 0x80) / 0xff;
    return (unsigned short)(a << 12 | r << 8 | g << 4 | b);
}

// 100faf37.  1 when the palette is a strictly increasing grey ramp (or absent).
static int IsGreyRamp(const GCOLOUR *colour, int count, int)
{
    int previous = -1;
    int i;
    if (colour)
        for (i = 0; i < count; ++i)
        {
            if (colour[i].r != colour[i].g || colour[i].r != colour[i].b || colour[i].g != colour[i].b ||
                (int)colour[i].r <= previous)
                return 0;
            previous = colour[i].r;
        }
    return 1;
}

// 100fb002.  Packs the image rows into the format of the bitmap header's type byte.
static void PackPixels(const unsigned char *header, unsigned char *out, const GINFO *info, const unsigned char *pixels,
                       int rowbytes, int type)
{
    int bits = BitsPerPixel(header, type);
    int width = info->width;
    int height = info->height;
    int rowsize = RowBytes(width, bits, type);
    int pixelbytes = bits > 8 ? 4 : 1;
    int line = 0;
    int outline = 0;
    int x, y, at, o, index, shift;
    unsigned value;
    for (y = 0; y < height; ++y)
    {
        at = line;
        o = outline;
        memset(out + o, 0, rowsize);
        for (x = 0; x < width; ++x)
        {
            if (info->attributes & 0x2000)
            {
                index = SwizzleIndex(x, y, width, height);
                at = index / width * rowbytes + index % width * pixelbytes;
            }
            switch (header[0])
            {
            case 0x44: case 0x60: case 0x79:
                value = 0;
                for (shift = 7; shift >= 0 && x < width; --shift, ++x)
                {
                    value |= (pixels[at] & 1) << shift;
                    ++at;
                }
                out[o] = (unsigned char)value;
                ++o;
                --x;
                break;
            case 0x01: case 0x40: case 0x55: case 0x62: case 0x63: case 0x7a:
                if (header[0] == 0x01 || header[0] == 0x40 || header[0] == 0x7a || header[0] == 0x55)
                {
                    value = pixels[at] & 0xf;
                    ++at;
                    ++x;
                    if (x < width)
                    {
                        value |= (pixels[at] & 0xf) << 4;
                        ++at;
                    }
                }
                else
                {
                    value = pixels[at] << 4;
                    ++at;
                    ++x;
                    if (x < width)
                    {
                        value |= pixels[at] & 0xf;
                        ++at;
                    }
                }
                out[o] = (unsigned char)value;
                ++o;
                break;
            case 0x61:
                value = info->colour[ggetm(pixels + at++, 1)].r / 16;
                value <<= 4;
                ++x;
                if (x < width)
                    value |= (info->colour[ggetm(pixels + at++, 1)].r / 16) & 0xf;
                out[o] = (unsigned char)value;
                ++o;
                break;
            case 0x02: case 0x41: case 0x56: case 0x65: case 0x66:
                out[o] = pixels[at];
                ++o;
                ++at;
                break;
            case 0x64:
                value = pixels[at];
                ++at;
                out[o] = info->colour[value].r;
                ++o;
                break;
            case 0x7b:
                out[o] = pixels[at++];
                ++o;
                break;
            case 0x50: case 0x7e:
                gputi(out + o, Pack1555(pixels + at), 2);
                o += 2;
                at += 4;
                break;
            case 0x03:
                gputi(out + o, PackBgr1555Alpha(pixels + at), 2);
                o += 2;
                at += 4;
                break;
            case 0x68:
                gputi(out + o, Pack5551(pixels + at), 2);
                o += 2;
                at += 4;
                break;
            case 0x51: case 0x78:
                gputi(out + o, Pack565(pixels + at), 2);
                o += 2;
                at += 4;
                break;
            case 0x42:
                gputi(out + o, PackBgr1555(pixels + at), 2);
                o += 2;
                at += 4;
                break;
            case 0x67:
                gputi(out + o, PackGreyAlpha(pixels + at), 2);
                o += 2;
                at += 4;
                break;
            case 0x52: case 0x6d:
                gputi(out + o, Pack4444(pixels + at), 2);
                o += 2;
                at += 4;
                break;
            case 0x04: case 0x43:
                out[o] = pixels[at + 2];
                out[o + 1] = pixels[at + 1];
                out[o + 2] = pixels[at];
                o += 3;
                at += 4;
                break;
            case 0x7f:
                out[o] = pixels[at];
                out[o + 1] = pixels[at + 1];
                out[o + 2] = pixels[at + 2];
                o += 3;
                at += 4;
                break;
            case 0x7d:
                out[o] = pixels[at];
                out[o + 1] = pixels[at + 1];
                out[o + 2] = pixels[at + 2];
                out[o + 3] = pixels[at + 3];
                o += 4;
                at += 4;
                break;
            case 0x05:
                out[o] = pixels[at + 2];
                out[o + 1] = pixels[at + 1];
                out[o + 2] = pixels[at];
                out[o + 3] = pixels[at + 3];
                o += 4;
                at += 4;
                break;
            case 0x6a:
                out[o] = pixels[at + 2];
                out[o + 1] = pixels[at + 1];
                out[o + 2] = pixels[at];
                out[o + 3] = pixels[at + 3];
                o += 4;
                at += 4;
                break;
            }
        }
        outline += rowsize;
        line += rowbytes;
    }
}

// 100fa289.  Builds the bitmap block: chooses the type byte for the shape type and depth, writes
// the 16-byte header and the pixels, block-packs (compression 3, depth above 8) or RefPacks
// (compression 2) when that is smaller.  Clears GINFO.attributes bit 0x2000 (see BitCount).
static int BuildBitmap(unsigned char *block, GINFO *info, int bits, const void *pixels, int rowbytes, int, int type)
{
    int blockpacked = 0;
    int code;
    int width, height, positiony, size, packedsize;
    unsigned flags;
    unsigned char *packed;
    memset(block, 0, 16);
    if (info->compression == 3 && bits > 8)
    {
        blockpacked = 1;
        bits = 16;
    }
    if (type == 1)
    {
        switch (bits)
        {
        case 8: code = 0x41; break;
        case 15:
        case 16: code = 0x42; break;
        case 24: code = 0x43; break;
        default: code = 0x40; break;
        }
    }
    else if (type == 6)
    {
        switch (bits)
        {
        case 8: code = 0x02; break;
        case 15:
        case 16: code = 0x03; break;
        case 24: code = 0x04; break;
        case 32: code = 0x05; break;
        default: code = 0x01; break;
        }
    }
    else if (type == 5)
    {
        if (bits == 8)
            code = 0x56;
        else if (bits < 15 || bits > 16)
            code = 0x55;
        else if (info->alphabits < 4)
        {
            if (info->greenbits < 6)
                code = 0x50;
            else
                code = 0x51;
        }
        else
            code = 0x52;
    }
    else if (type == 4)
    {
        switch (bits)
        {
        case 4:
            if (IsGreyRamp(info->colour, 1 << bits, info->attributes & 1) == 0)
                code = 0x63;
            else
                code = 0x61;
            break;
        case 8:
            if (IsGreyRamp(info->colour, 1 << bits, info->attributes & 1) == 0)
                code = 0x66;
            else
                code = 0x64;
            break;
        case 15:
        case 16:
            if (info->alphabits == 8 && info->redbits == 8 && info->bluebits == 0 && info->greenbits == 0)
                code = 0x67;
            else
                code = 0x68;
            break;
        case 24:
        case 32:
            code = 0x6a;
            break;
        default:
            code = 0x60;
            break;
        }
    }
    else
    {
        switch (bits)
        {
        case 4: code = 0x7a; break;
        case 8: code = 0x7b; break;
        case 15:
        case 16:
            if (info->alphabits < 4)
            {
                if (info->greenbits < 6)
                    code = 0x7e;
                else
                    code = 0x78;
            }
            else
                code = 0x6d;
            break;
        case 24: code = 0x7f; break;
        case 32: code = 0x7d; break;
        default: code = 0x79; break;
        }
    }
    width = info->width;
    height = info->height;
    flags = info->positionx;
    positiony = info->positiony;
    if ((info->attributes & 0x2000) &&
        (width != 1 << BitCount(width) || height != 1 << BitCount(height)))
        info->attributes &= ~0x2000u;
    flags &= 0xfff;
    if (info->attributes & 0x800)
        flags |= 0x8000;
    if (info->attributes & 0x1000)
        flags |= 0x4000;
    if (info->attributes & 0x2000)
        flags |= 0x2000;
    gputi(block, code, 1);
    gputi(block + 4, width, 2);
    gputi(block + 6, height, 2);
    gputi(block + 8, info->centrex, 2);
    gputi(block + 10, info->centrey, 2);
    gputi(block + 0xc, flags, 2);
    gputi(block + 0xe, positiony, 2);
    if (blockpacked)
    {
        size = FSH_CompressBlocks(info, rowbytes, pixels, block + 0x10);
        block[0] |= 0x80;
    }
    else
    {
        PackPixels(block, block + 0x10, info, (const unsigned char *)pixels, rowbytes, type);
        size = ImageBytes(info->width, info->height, bits, type);
    }
    if (info->compression == 2 && (packed = (unsigned char *)galloc((int)(size * 3) / 2 + 0x400)) != 0)
    {
        packedsize = (RefPack(block + 0x10, size, packed, 0) + 15) & ~15;
        if (packedsize < size)
        {
            memcpy(block + 0x10, packed, packedsize);
            block[0] |= 0x80;
            size = packedsize;
        }
        gfree(packed);
    }
    return (size + 0x1f) & ~0xf;
}

// ---------------------------------------------------------------------------------------------
// Extra blocks

// 10105204.  Palette type for shape type 2 from the channel bits.
static int PaletteCode2(int alphabits, int redbits, int greenbits, int bluebits)
{
    int code;
    if (alphabits < 3 && redbits < 6 && greenbits < 6 && bluebits < 6)
        code = 0x2d;
    else if (alphabits < 3 && redbits < 6 && greenbits < 7 && bluebits < 6)
        code = 0x29;
    else if (alphabits < 3 && redbits < 7 && greenbits < 7 && bluebits < 7)
        code = 0x22;
    else if (alphabits < 3 && redbits < 9 && greenbits < 9 && bluebits < 9)
        code = 0x24;
    else if (redbits < 6 && greenbits < 6 && bluebits < 6)
        code = 0x2e;
    else if (redbits < 6 && greenbits < 7 && bluebits < 6)
        code = 0x2c;
    else
        code = 0x2a;
    return code;
}

// 101052da.  Palette type for shape type 5.
static int PaletteCode5(int alphabits, int redbits, int greenbits, int bluebits)
{
    int code;
    if (alphabits < 3 && redbits < 6 && greenbits < 6 && bluebits < 6)
        code = 0x30;
    else if (alphabits < 3 && redbits < 6 && greenbits < 7 && bluebits < 6)
        code = 0x31;
    else if (alphabits < 5 && redbits < 5 && greenbits < 5 && bluebits < 5)
        code = 0x32;
    else
        code = 0x33;
    return code;
}

// 10105356.  Palette type for shape type 6.
static int PaletteCode6(int alphabits, int redbits, int greenbits, int bluebits)
{
    int code;
    if (alphabits < 3 && redbits < 6 && greenbits < 6 && bluebits < 6)
        code = 0x20;
    else
        code = 0x21;
    return code;
}

// 10104ad3.  Palette block.  The CLUT position of the header is taken from the shape extension
// only for 'SHPP' descriptors of GINFO_SIZE_SHAPE.
static void BuildPalette(const GINFO *info, int count, const GCOLOUR *colour, unsigned char **result, int *resultsize,
                         int skip, int type)
{
    unsigned size = 0;
    unsigned char *block = 0;
    const unsigned char *c = (const unsigned char *)colour;
    int code, x, y, i;
    if (count > 0 && skip == 0)
    {
        size = count;
        switch (type)
        {
        case 1:
            code = 0x23;
            size = count << 1;
            break;
        case 2:
            code = PaletteCode2(info->alphabits, info->redbits, info->greenbits, info->bluebits);
            if (code == 0x29 || code == 0x2d)
                size = count << 1;
            else if (code == 0x22 || code == 0x24)
                size = count * 3;
            else
                size = count << 2;
            break;
        case 3:
            code = 0x22;
            size = count * 3;
            break;
        case 4:
            code = 0x27;
            if (IsGreyRamp(colour, count, info->attributes & 1) == 0)
                size = count << 1;
            else
                size = 0;
            break;
        case 5:
            code = PaletteCode5(info->alphabits, info->redbits, info->greenbits, info->bluebits);
            if (code == 0x33)
                size = count << 2;
            else
                size = count << 1;
            break;
        case 6:
            code = PaletteCode6(info->alphabits, info->redbits, info->greenbits, info->bluebits);
            if (code == 0x20)
                size = count << 1;
            else
                size = count << 2;
            break;
        }
        if (size != 0)
        {
            size = (size + 0x1f) & ~0xfu;
            block = (unsigned char *)galloc(size);
        }
        if (block)
        {
            x = 0;
            y = 0;
            if (type == 1)
                y = 0xf0;
            if (info->tag == GTAG('S', 'H', 'P', 'P') && info->size == GINFO_SIZE_SHAPE)
            {
                x = info->clutx;
                y = info->cluty;
            }
            memset(block, 0, size);
            gputi(block, code, 1);
            gputi(block + 4, count, 2);
            gputi(block + 6, 1, 2);
            gputi(block + 8, count, 2);
            gputi(block + 10, 0, 2);
            gputi(block + 0xc, x, 2);
            gputi(block + 0xe, y, 2);
            for (i = 0; i < count; ++i)
            {
                switch (type)
                {
                case 1:
                    gputi(block + i * 2 + 0x10, PackBgr1555(c + i * 4), 2);
                    break;
                case 2:
                case 5:
                case 6:
                    switch (code)
                    {
                    case 0x20:
                        gputi(block + i * 2 + 0x10, PackBgr1555Alpha(c + i * 4), 2);
                        break;
                    case 0x2d:
                    case 0x30:
                        gputi(block + i * 2 + 0x10, Pack1555(c + i * 4), 2);
                        break;
                    case 0x29:
                    case 0x31:
                        gputi(block + i * 2 + 0x10, Pack565(c + i * 4), 2);
                        break;
                    case 0x32:
                        gputi(block + i * 2 + 0x10, Pack4444(c + i * 4), 2);
                        break;
                    case 0x22:
                        block[i * 3 + 0x10] = (unsigned char)(c[i * 4 + 2] >> 2);
                        block[i * 3 + 0x11] = (unsigned char)(c[i * 4 + 1] >> 2);
                        block[i * 3 + 0x12] = (unsigned char)(c[i * 4] >> 2);
                        break;
                    case 0x24:
                        block[i * 3 + 0x10] = c[i * 4 + 2];
                        block[i * 3 + 0x11] = c[i * 4 + 1];
                        block[i * 3 + 0x12] = c[i * 4];
                        break;
                    case 0x2e:
                        gputi(block + i * 4 + 0x10, Pack1555(c + i * 4), 2);
                        block[i * 4 + 0x12] = 0;
                        block[i * 4 + 0x13] = c[i * 4 + 3];
                        break;
                    case 0x2c:
                        gputi(block + i * 4 + 0x10, Pack565(c + i * 4), 2);
                        block[i * 4 + 0x12] = 0;
                        block[i * 4 + 0x13] = c[i * 4 + 3];
                        break;
                    case 0x2a:
                    case 0x33:
                        block[i * 4 + 0x10] = c[i * 4];
                        block[i * 4 + 0x11] = c[i * 4 + 1];
                        block[i * 4 + 0x12] = c[i * 4 + 2];
                        block[i * 4 + 0x13] = c[i * 4 + 3];
                        break;
                    case 0x21:
                        block[i * 4 + 0x10] = c[i * 4 + 2];
                        block[i * 4 + 0x11] = c[i * 4 + 1];
                        block[i * 4 + 0x12] = c[i * 4];
                        block[i * 4 + 0x13] = c[i * 4 + 3];
                        break;
                    }
                    break;
                case 3:
                    block[i * 3 + 0x10] = (unsigned char)(c[i * 4 + 2] >> 2);
                    block[i * 3 + 0x11] = (unsigned char)(c[i * 4 + 1] >> 2);
                    block[i * 3 + 0x12] = (unsigned char)(c[i * 4] >> 2);
                    break;
                case 4:
                    gputi(block + i * 2 + 0x10, Pack5551(c + i * 4), 2);
                    break;
                }
            }
        }
    }
    *resultsize = size;
    *result = block;
}

// 10105390.  0x7c block from GINFO.point.
static void BuildPoints(const GINFO *info, unsigned char **result, int *resultsize, int skip)
{
    unsigned char *block = 0;
    unsigned size = 0;
    int i;
    if (info->pointcount > 0 && skip == 0)
    {
        size = info->pointcount * 8 + 8;
        block = (unsigned char *)galloc(size);
        if (block)
        {
            memset(block, 0, size);
            block[0] = 0x7c;
            gputi(block + 4, info->pointcount, 4);
            for (i = 0; i < info->pointcount; ++i)
            {
                gputi(block + i * 8 + 8, info->point[i][0], 4);
                gputi(block + i * 8 + 0xc, info->point[i][1], 4);
            }
        }
    }
    *resultsize = size;
    *result = block;
}

// 101054a0.  0x6e block from the shape extension ('MBLI' or 'SHP?' of GINFO_SIZE_SHAPE only).
static void BuildRecords(const GINFO *info, unsigned char **result, int *resultsize, int skip)
{
    unsigned size = 0;
    unsigned char *block = 0;
    int i;
    if ((info->tag == GTAG('M', 'B', 'L', 'I') || (info->tag & 0xffffff00) == GTAG('S', 'H', 'P', 0)) &&
        info->size == GINFO_SIZE_SHAPE && info->shaperecordcount > 0 && skip == 0)
    {
        size = info->shaperecordcount * 8 + 8;
        block = (unsigned char *)galloc(size);
        if (block)
        {
            memset(block, 0, size);
            block[0] = 0x6e;
            gputi(block + 4, info->shaperecordcount, 4);
            for (i = 0; i < info->shaperecordcount; ++i)
            {
                block[i * 4 + 8] = (unsigned char)info->shaperecord[i].a;
                block[i * 4 + 9] = (unsigned char)info->shaperecord[i].b;
                block[i * 4 + 10] = (unsigned char)info->shaperecord[i].c;
                block[i * 4 + 0xb] = (unsigned char)info->shaperecord[i].d;
            }
        }
    }
    *resultsize = size;
    *result = block;
}

// 10105606.  0x6b block from the shape extension; `code` is the bitmap type byte.
static void BuildTpage(const GINFO *info, unsigned char **result, int *resultsize, int skip, unsigned char code)
{
    int size = 0;
    unsigned char *block = 0;
    const GINFO *shape = info;
    if ((info->tag == GTAG('M', 'B', 'L', 'I') || (info->tag & 0xffffff00) == GTAG('S', 'H', 'P', 0)) &&
        info->size == GINFO_SIZE_SHAPE && skip == 0 && (shape->tpage != 0 || shape->tpageextra != 0))
    {
        size = 0xc;
        block = (unsigned char *)galloc(size);
        if (block)
        {
            memset(block, 0, size);
            block[0] = 0x6b;
            gputi(block + 8, shape->tpageextra, 2);
            gputi(block + 6, shape->cluty << 6 | ((shape->clutx >> 4) & 0x3f), 2);
            gputi(block + 4,
                  (code & 3) << 7 | (shape->tpage & 0x60) | (info->positiony & 0x100) >> 4 |
                      (info->positionx & 0x3ff) >> 6 | (info->positiony & 0x200) << 2,
                  2);
        }
    }
    *resultsize = size;
    *result = block;
}

// 1010577b.  0x6f block from GINFO.comment, size rounded to 16 with room for the terminator.
static void BuildComment(const GINFO *info, unsigned char **result, int *resultsize, int skip)
{
    unsigned char *block = 0;
    unsigned size = 0;
    if (info->comment[0] != 0 && skip == 0)
    {
        size = (strlen(info->comment) + 1 + 0x17) & ~0xfu;
        block = (unsigned char *)galloc(size);
        if (block)
        {
            memset(block, 0, size);
            block[0] = 0x6f;
            gputi(block + 4, size - 8, 4);
            strcpy((char *)block + 8, info->comment);
        }
    }
    *resultsize = size;
    *result = block;
}

// ---------------------------------------------------------------------------------------------
// write()

// 100f9b76.  Converts one image into entry `index`: bitmap, palette and extra blocks, the name
// (GINFO.name or the four-digit index) and the palette name ('!' + name[1..3], or name[4..7]).
static int WriteShape(FSHTABLE *table, GINFO *info, const void *pixels, int rowbytes, int index, int type)
{
    unsigned char *bitmap = 0;
    unsigned char *palette = 0;
    unsigned char *points = 0;
    unsigned char *records = 0;
    unsigned char *comment = 0;
    unsigned char *tpage = 0;
    int bitmapsize, palettesize, pointssize, recordssize, commentsize, tpagesize;
    int bits, ok, i;
    char name[8];
    char palettename[8];
    FSHSHAPE *shape;
    switch (type)
    {
    case 1:
        bits = 4;
        if (info->depth > 4)
            bits = 8;
        if (info->depth > 8)
            bits = 16;
        if (info->depth > 16)
            bits = 24;
        break;
    case 2:
        bits = 1;
        if (info->depth > 1)
            bits = 4;
        if (info->depth > 4)
            bits = 8;
        if (info->depth > 8)
            bits = 15;
        if (info->depth > 15)
            bits = 16;
        if (info->depth > 16)
            bits = 24;
        if (info->depth > 24)
            bits = 32;
        break;
    case 3:
        bits = 8;
        break;
    case 4:
        bits = 1;
        if (info->depth > 1)
            bits = 4;
        if (info->depth > 4)
            bits = 8;
        if (info->depth > 8)
            bits = 15;
        if (info->depth > 15)
            bits = 16;
        if (info->depth > 16)
            bits = 32;
        if (info->alphabits == 8 && info->redbits == 8 && info->greenbits == 0 && info->bluebits == 0)
            bits = 16;
        break;
    case 5:
        bits = 4;
        if (info->depth > 4)
            bits = 8;
        if (info->depth > 8)
            bits = 15;
        if (info->depth > 15)
            bits = 16;
        break;
    case 6:
        bits = 4;
        if (info->depth > 4)
            bits = 8;
        if (info->depth > 8)
            bits = 15;
        if (info->depth > 16)
            bits = 24;
        if (info->depth > 24)
            bits = 32;
        break;
    }
    ok = 1;
    if ((info->attributes & 2) == 0)
    {
        bitmapsize = (ImageBytes(info->width, info->height, bits, type) + 0x1f) & ~0xf;
        bitmap = (unsigned char *)galloc(bitmapsize);
        if (!bitmap)
        {
            ok = 0;
        }
        else
        {
            memset(bitmap, 0, bitmapsize);
            bitmapsize = BuildBitmap(bitmap, info, bits, pixels, rowbytes, info->attributes & 2, type);
            bitmapsize = (bitmapsize + 0xf) & ~0xf;
        }
    }
    else
    {
        bitmap = 0;
        bitmapsize = 0;
    }
    BuildPalette(info, info->numcolours, info->colour, &palette, &palettesize, info->attributes & 1, type);
    BuildPoints(info, &points, &pointssize, info->attributes & 4);
    BuildRecords(info, &records, &recordssize, info->attributes & 0x10);
    BuildComment(info, &comment, &commentsize, info->attributes & 8);
    if (bitmap)
        BuildTpage(info, &tpage, &tpagesize, info->attributes & 0x20, bitmap[0]);
    if (info->name[0] == 0)
    {
        name[0] = (char)(index / 1000 % 10 + '0');
        name[1] = (char)(index / 100 % 10 + '0');
        name[2] = (char)(index / 10 % 10 + '0');
        name[3] = (char)(index % 10 + '0');
    }
    else
    {
        for (i = 0; i < 4 && info->name[i] != 0; ++i)
            name[i] = info->name[i];
        for (; i < 4; ++i)
            name[i] = ' ';
    }
    palettename[0] = '!';
    for (i = 1; i < 4; ++i)
        palettename[i] = name[i];
    for (i = 0; i < 4 && info->name[i] != 0; ++i)
        ;
    if (info->name[i] != 0)
    {
        for (i = 0; i < 4 && info->name[4 + i] != 0; ++i)
            palettename[i] = info->name[4 + i];
        for (; i < 4; ++i)
            palettename[i] = ' ';
    }
    shape = &table->shape[index];
    gputm(shape->name, ggetm(name, 4), 4);
    gputm(shape->palettename, ggetm(palettename, 4), 4);
    shape->bitmap = bitmap;
    shape->bitmapsize = bitmapsize;
    shape->palette = palette;
    shape->palettesize = palettesize;
    shape->points = points;
    shape->pointssize = pointssize;
    shape->records = records;
    shape->recordssize = recordssize;
    shape->comment = comment;
    shape->commentsize = commentsize;
    shape->tpage = tpage;
    shape->tpagesize = tpagesize;
    shape->attributes = info->attributes;
    return ok;
}

// 100f9b24.  The GWRITEFN descriptor is const, but the writer changes GINFO.attributes.
int GCALL FSH_write(void *handle, const GINFO *info, const void *pixels, int rowbytes)
{
    FSHHANDLE *fsh = (FSHHANDLE *)handle;
    int ok = WriteShape(fsh->table, (GINFO *)info, pixels, rowbytes, fsh->current, SHAPE_FSH);
    ++fsh->current;
    return ok;
}

// ---------------------------------------------------------------------------------------------
// wclose()

// 10106ad7.
static void SetMipLevels(unsigned char *bitmap, int levels)
{
    unsigned value;
    if (bitmap && levels > 1)
    {
        value = ggeti(bitmap + 0xe, 2);
        gputi(bitmap + 0xe, (value & 0xfff) + (levels - 1) * 0x1000, 2);
    }
}

// 1010613c.  Merges entries named "mm0 ".."mm9…" into the bitmap of the entry before them as
// extra mip levels, RefPacking the result again when the first level was packed, then drops the
// emptied entries.
static void MergeMipmaps(FSHTABLE *table, int type)
{
    int levels = 0;
    unsigned char *merged = 0;
    int size = 0;
    int base = 0;
    int i, width, height, basewidth, baseheight, bits, bytes;
    FSHSHAPE *first, *shape;
    unsigned char *firstbitmap, *bitmap, *packed;
    for (i = 1; i < table->count; ++i)
    {
        first = &table->shape[base];
        shape = &table->shape[i];
        bitmap = shape->bitmap;
        firstbitmap = first->bitmap;
        if (shape->name[0] == 'm' && shape->name[1] == 'm' && (unsigned char)shape->name[2] >= '0' &&
            (unsigned char)shape->name[2] <= '9')
        {
            width = ggeti(bitmap + 4, 2);
            height = ggeti(bitmap + 6, 2);
            bits = BitsPerPixel(bitmap, type);
            if (levels == 0)
            {
                basewidth = ggeti(firstbitmap + 4, 2);
                baseheight = ggeti(firstbitmap + 6, 2);
                bytes = (ImageBytes(basewidth, baseheight, bits, type) + 0xf) & ~0xf;
                size = bytes + 0x10;
                while (basewidth > 1 || baseheight > 1)
                {
                    if (basewidth > 1)
                        basewidth >>= 1;
                    if (baseheight > 1)
                        baseheight >>= 1;
                    size += ImageBytes(basewidth, baseheight, bits, type);
                }
                merged = (unsigned char *)galloc(size);
                memcpy(merged, firstbitmap, 16);
                size = 0x10;
                if ((firstbitmap[0] & 0x80) && IsRefPack(firstbitmap + 0x10))
                    RefUnpack(firstbitmap + 0x10, 0, merged + size);
                else
                    memcpy(merged + size, firstbitmap + 0x10, bytes);
                size += bytes;
                levels = 1;
            }
            bytes = (ImageBytes(width, height, bits, type) + 0xf) & ~0xf;
            if ((bitmap[0] & 0x80) && IsRefPack(bitmap + 0x10))
                RefUnpack(bitmap + 0x10, 0, merged + size);
            else
                memcpy(merged + size, bitmap + 0x10, bytes);
            if (shape->bitmap)
                gfree(shape->bitmap);
            if (shape->palette)
                gfree(shape->palette);
            if (shape->points)
                gfree(shape->points);
            if (shape->comment)
                gfree(shape->comment);
            if (shape->records)
                gfree(shape->records);
            shape->bitmapsize = 0;
            shape->palettesize = 0;
            shape->pointssize = 0;
            shape->commentsize = 0;
            shape->recordssize = 0;
            size += bytes;
            ++levels;
        }
        if (i == table->count - 1 || shape->name[0] != 'm' || shape->name[1] != 'm' ||
            (unsigned char)shape->name[2] < '0' || (unsigned char)shape->name[2] > '9')
        {
            if (merged)
            {
                if ((firstbitmap[0] & 0x80) && IsRefPack(firstbitmap + 0x10))
                {
                    packed = (unsigned char *)galloc(size * 3 / 2 + 0x400);
                    memcpy(packed, merged, 16);
                    size = (RefPack(merged + 0x10, size - 0x10, packed + 0x10, 0) + 0xf) & ~0xf;
                    size = size + 0x10;
                    gfree(merged);
                    merged = packed;
                }
                gfree(first->bitmap);
                first->bitmap = merged;
                first->bitmapsize = size;
                firstbitmap = merged;
                SetMipLevels(firstbitmap, levels);
            }
            base = i;
            levels = 0;
            merged = 0;
            size = 0;
        }
    }
    base = 0;
    for (i = 0; i < table->count; ++i)
    {
        shape = &table->shape[i];
        if (shape->bitmapsize != 0 || shape->palettesize != 0 || shape->pointssize != 0 || shape->recordssize != 0 ||
            shape->commentsize != 0)
        {
            if (i != base)
                table->shape[base] = *shape;
            ++base;
        }
    }
    table->count = base;
}

// 10106d1f.  Appends a block to the entry's chain: the previous block gets the offset to it.
static void LinkBlock(unsigned char **last, int *lastsize, unsigned char *block, int size)
{
    if (block)
    {
        if (*last)
            gputi(*last + 1, *lastsize, 3);
        gputi(block + 1, 0, 3);
        *last = block;
        *lastsize = size;
    }
}

// 10106b24.  Chains each entry's blocks in file order; shape type 3 rotates the first block's
// header words back.
static void LinkBlocks(FSHTABLE *table, int type)
{
    unsigned char *last;
    int lastsize;
    unsigned word;
    unsigned *header;
    int i;
    for (i = 0; i < table->count; ++i)
    {
        last = 0;
        lastsize = 0;
        LinkBlock(&last, &lastsize, table->shape[i].bitmap, table->shape[i].bitmapsize);
        LinkBlock(&last, &lastsize, table->shape[i].palette, table->shape[i].palettesize);
        LinkBlock(&last, &lastsize, table->shape[i].points, table->shape[i].pointssize);
        LinkBlock(&last, &lastsize, table->shape[i].records, table->shape[i].recordssize);
        LinkBlock(&last, &lastsize, table->shape[i].comment, table->shape[i].commentsize);
        LinkBlock(&last, &lastsize, table->shape[i].tpage, table->shape[i].tpagesize);
        if (type == 3)
        {
            header = (unsigned *)table->shape[i].bitmap;
            if (header == 0)
            {
                header = (unsigned *)table->shape[i].palette;
                if (header)
                {
                    word = ggetm(header, 4);
                    header[0] = header[1];
                    header[1] = header[2];
                    header[2] = header[3];
                    gputm(header + 3, word, 4);
                }
            }
            else
            {
                word = ggetm(header, 4);
                header[0] = header[1];
                header[1] = header[2];
                header[2] = header[3];
                gputm(header + 3, word, 4);
            }
        }
    }
}

// 101058c8.  Writes the file: header placeholder, directory placeholder, "Buy ERTS" padding to
// 16 bytes, the blocks of every entry, then the real header and directory.  With attribute 0x100
// of the first entry (types 2 and 3) every entry also gets a directory slot for its palette.
static int WriteFile(GSTREAM *stream, FSHTABLE *table, int type, int directory, unsigned tag)
{
    unsigned char header[16];        // written once uninitialised as a placeholder, then rewritten
    unsigned char shortheader[8];
    unsigned char *entries = 0;
    unsigned char *padding;
    int slots = 1;
    int doubled = 0;
    int ok, size, count, i, j, position, paletteposition;
    int a, b;
    unsigned offseta, offsetb;
    FSHSHAPE *shape;
    if (table->count > 0 && (table->shape[0].attributes & 0x200))
        MergeMipmaps(table, type);
    LinkBlocks(table, type);
    if (directory == 0)
    {
        ok = 1;
    }
    else
    {
        size = type != 3 ? 16 : 6;
        ok = gwrite(stream, header, size) == size;
    }
    if (ok)
    {
        if (directory)
        {
            count = table->count;
            if ((table->shape[0].attributes & 0x100) && (type == 2 || type == 3))
            {
                slots = 2;
                count <<= 1;
                doubled = 1;
            }
            size = count << 3;
            ok = 1;
            if (size != 0)
            {
                entries = (unsigned char *)galloc(size);
                if (!entries)
                    ok = 0;
                if (ok)
                    ok = gwrite(stream, entries, size) == size;
            }
            size = ((gtell(stream) + 0xf) & ~0xf) - gtell(stream);
            if (size != 0)
            {
                padding = (unsigned char *)galloc(size);
                memset(padding, 0, size);
                if (size >= 8)
                    memcpy(padding, "Buy ERTS", 8);
                ok = gwrite(stream, padding, size) == size;
                gfree(padding);
            }
        }
        if (ok)
        {
            for (i = 0; i < table->count; ++i)
            {
                shape = &table->shape[i];
                position = glen(stream);
                paletteposition = position + shape->bitmapsize;
                if (type == 3)
                {
                    position -= count * 8 + 6;
                    paletteposition -= count * 8 + 6;
                    if (doubled == 0)
                    {
                        gputm(entries + i * 4 * slots, ggetm(shape->name, 4), 4);
                        gputi(entries + count * 4 + i * 4 * slots, position, 4);
                    }
                    else
                    {
                        gputm(entries + i * 4 * slots, ggetm(shape->palettename, 4), 4);
                        gputi(entries + count * 4 + i * 4 * slots, paletteposition, 4);
                        gputm(entries + 4 + i * 4 * slots, ggetm(shape->name, 4), 4);
                        gputi(entries + count * 4 + 4 + i * 4 * slots, position, 4);
                    }
                }
                else if (doubled == 0)
                {
                    gputm(entries + i * 8, ggetm(shape->name, 4), 4);
                    gputi(entries + 4 + i * 8, position, 4);
                }
                else
                {
                    gputm(entries + i * slots * 8, ggetm(shape->palettename, 4), 4);
                    gputi(entries + 4 + i * slots * 8, paletteposition, 4);
                    gputm(entries + 8 + i * slots * 8, ggetm(shape->name, 4), 4);
                    gputi(entries + 0xc + i * slots * 8, position, 4);
                }
                if (ok && shape->bitmap)
                    ok = gwrite(stream, shape->bitmap, shape->bitmapsize) == shape->bitmapsize;
                if (ok && shape->palette)
                    ok = gwrite(stream, shape->palette, shape->palettesize) == shape->palettesize;
                if (ok && shape->points)
                    ok = gwrite(stream, shape->points, shape->pointssize) == shape->pointssize;
                if (ok && shape->records)
                    ok = gwrite(stream, shape->records, shape->recordssize) == shape->recordssize;
                if (ok && shape->comment)
                    ok = gwrite(stream, shape->comment, shape->commentsize) == shape->commentsize;
                if (ok && shape->tpage)
                    ok = gwrite(stream, shape->tpage, shape->tpagesize) == shape->tpagesize;
            }
            if (ok && type == 3 && (table->shape[0].attributes & 0x400) == 0)
                for (i = 0; i < count; ++i)
                    for (j = 0; j < count - 1; ++j)
                    {
                        a = ggetm(entries + j * 4, 4);
                        b = ggetm(entries + 4 + j * 4, 4);
                        offseta = ggeti(entries + (count + j) * 4, 4);
                        offsetb = ggeti(entries + 4 + (count + j) * 4, 4);
                        if (b < a)
                        {
                            gputm(entries + j * 4, b, 4);
                            gputm(entries + 4 + j * 4, a, 4);
                            gputi(entries + (count + j) * 4, offsetb, 4);
                            gputi(entries + 4 + (count + j) * 4, offseta, 4);
                        }
                    }
            if (ok && directory)
            {
                gseek(stream, 0);
                if (type == 3)
                {
                    gputi(shortheader, glen(stream), 4);
                    gputi(shortheader + 4, count, 2);
                    ok = gwrite(stream, shortheader, 6) == 6;
                }
                else
                {
                    gputm(header, tag, 4);
                    gputi(header + 4, glen(stream), 4);
                    gputi(header + 8, count, 4);
                    gputm(header + 12, GTAG('G', 'I', 'M', 'X'), 4);
                    ok = gwrite(stream, header, 16) == 16;
                }
                size = count << 3;
                ok = gwrite(stream, entries, size) == size;
            }
        }
    }
    if (entries)
        gfree(entries);
    return ok;
}

// 10106d6e.
static void FreeTable(FSHTABLE *table)
{
    int i;
    for (i = 0; i < table->count; ++i)
    {
        if (table->shape[i].bitmap)
            gfree(table->shape[i].bitmap);
        if (table->shape[i].palette)
            gfree(table->shape[i].palette);
        if (table->shape[i].points)
            gfree(table->shape[i].points);
        if (table->shape[i].records)
            gfree(table->shape[i].records);
        if (table->shape[i].comment)
            gfree(table->shape[i].comment);
        if (table->shape[i].tpage)
            gfree(table->shape[i].tpage);
    }
    gfree(table);
}

// 1010585d.  The written entry count becomes the table count.
int GCALL FSH_wclose(void *handle)
{
    FSHHANDLE *fsh = (FSHHANDLE *)handle;
    FSHTABLE *table;
    int ok = 0;
    if (fsh)
    {
        table = fsh->table;
        table->count = fsh->current;
        ok = WriteFile(fsh->stream, table, SHAPE_FSH, 1, GTAG('S', 'H', 'P', 'I'));
        FreeTable(table);
        gfree(fsh);
    }
    return ok;
}
