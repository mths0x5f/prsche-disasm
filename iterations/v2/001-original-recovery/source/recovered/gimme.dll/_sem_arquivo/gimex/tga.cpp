// "Targa" module 1.37 (FrANK G. Barchard): GIMEX module 5.
// gimme.dll 3a43b0f6…, entry points about 100ea480, is 100ea6b0, open 100ea885, info 100ea8ee, read 100eb053, close 100ebad5,
// wopen 100e9700, write 100e9756, wclose 100ea44e.  about(), is() and the reader (open, info, read,
// close and their helpers 100eb216, 100eba09) are recovered; the writer entry points are recovery
// boundaries (boundary.h) until the module's writer is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100ea480.
GABOUT *TGA_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'T', 'G', 'A');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x93d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('T', 'P', 'I', 'C');
        strcpy(about->extension[0], ".tga");
        strcpy(about->extension[1], ".vda");
        strcpy(about->extension[2], ".icb");
        strcpy(about->extension[3], ".vst");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.37");
        strcpy(about->shortname, "TGA");
        strcpy(about->longname, "Targa");
        strcpy(about->name, "Targa");
    }
    return about;
}

// 100ea6b0.
// Targa has no signature: the 18-byte header must hold a plausible colour-map type, image type
// and depth (60), and then plausible sizes and origins (100).
int GCALL TGA_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[18];
    gseek(stream, 0);
    glen(stream);
    score = gread(stream, header, sizeof(header));
    if (score)
    {
        score = 0;
        int width = ggeti(header + 12, 2);
        int height = ggeti(header + 14, 2);
        int depth = ggeti(header + 16, 1);
        int imagetype = ggeti(header + 2, 1);
        int maptype = ggeti(header + 1, 1);
        int mapfirst = ggeti(header + 3, 2);
        int maplength = ggeti(header + 5, 2);
        int mapentrybits = ggeti(header + 7, 1);
        int xorigin = ggeti(header + 8, 2);
        int yorigin = ggeti(header + 10, 2);
        if (maptype >= 0 && maptype <= 1 &&
            ((imagetype >= 1 && imagetype <= 3) || (imagetype >= 9 && imagetype <= 11)) &&
            (depth == 8 || depth == 15 || depth == 16 || depth == 24 || depth == 32))
        {
            score = 60;
            if (width > 0 && width <= 0x800 && height > 0 && height <= 0x800 && mapfirst >= 0 &&
                mapfirst <= 0xff && maplength >= 0 && maplength <= 0x100 && mapentrybits >= 0 &&
                mapentrybits <= 0x20 && xorigin >= -0x400 && xorigin <= 0x400 && yorigin >= -0x400 &&
                yorigin <= 0x400)
                score = 100;
        }
    }
    return score;
}

// ---------------------------------------------------------------------------------------------
// Reader.  Every entry point rereads the 18-byte header from offset 0; the handle only keeps the
// stream.

// Handle returned by open() (0x18 bytes, cleared).
struct TGAHANDLE
{
    unsigned tag;                // +0x00 '.TGA'
    int size;                    // +0x04 sizeof(TGAHANDLE)
    int count;                   // +0x08 frames: always 1
    int unknown_0c;              // +0x0c
    GSTREAM *stream;             // +0x10
    int unknown_14;              // +0x14
};

static_assert(sizeof(TGAHANDLE) == 0x18, "TGAHANDLE layout");

// 100ea885.
int GCALL TGA_open(void **handle, GSTREAM *stream, const char *, int)
{
    int ok = 0;
    TGAHANDLE *tga = (TGAHANDLE *)galloc(sizeof(TGAHANDLE));
    if (tga)
    {
        memset(tga, 0, sizeof(TGAHANDLE));
        tga->count = 1;
        tga->tag = GTAG('.', 'T', 'G', 'A');
        tga->size = sizeof(TGAHANDLE);
        tga->stream = stream;
        *handle = tga;
        ok = 1;
    }
    return ok;
}

// 100ea8ee.
// GINFO.shapesize receives the file length, GINFO.unknown_020 the first colour-map index and
// positionx/positiony the origin (y negated unless the image is stored top-down, x negated when
// it is stored right-to-left).  A colour map is stored from entry `mapfirst` for `maplength`
// entries; neither is checked against the 256 entries of GINFO.colour or of the read buffer.
// Without a colour map an 8-bit image gets a grey ramp.
GINFO *GCALL TGA_info(void *handle, int)
{
    TGAHANDLE *tga = (TGAHANDLE *)handle;
    GINFO *info = 0;
    int ok = 0;
    unsigned char header[18];
    unsigned char palette[0x400];
    int i;

    gseek(tga->stream, 0);
    int length = glen(tga->stream);
    ok = gread(tga->stream, header, 18);
    if (ok)
    {
        int width = ggeti(header + 12, 2);
        int height = ggeti(header + 14, 2);
        int depth = ggeti(header + 16, 1);
        int imagetype = ggeti(header + 2, 1);
        int rle = (imagetype & 8) != 0;
        int mapfirst = ggeti(header + 3, 2);
        int maplength = ggeti(header + 5, 2);
        int mapentrybits = ggeti(header + 7, 1);
        int idlength = ggeti(header, 1);
        int descriptor = ggeti(header + 17, 1);
        int xorigin = (short)ggeti(header + 8, 2);
        int yorigin = (short)ggeti(header + 10, 2);
        if ((descriptor & 0x20) == 0)
            yorigin = -yorigin;
        if (descriptor & 0x10)
            xorigin = -xorigin;
        int alphabits = depth - 24;
        if (depth == 15 || depth == 16 ||
            (depth == 8 && ggeti(header + 1, 1) && (mapentrybits == 15 || mapentrybits == 16)))
            alphabits = (descriptor & 0xf) == 1;
        if (alphabits <= 0)
            alphabits = 0;
        if (alphabits > 8)
            alphabits = 8;
        ok = gseek(tga->stream, idlength + 18);
        int colours = 0;
        if ((imagetype & 7) == 1)
            colours = maplength;
        else if ((imagetype & 7) == 3)
            colours = 256;

        info = (GINFO *)galloc(GINFO_SIZE_LEGACY);
        if (info)
        {
            memset(info, 0, GINFO_SIZE_LEGACY);
            info->tag = GTAG('.', 'T', 'G', 'A');
            info->size = GINFO_SIZE_LEGACY;
            info->version = GINFO_VERSION;
            info->frames = 0;
            info->width = width;
            info->height = height;
            info->shapesize = length;
            info->attributes = 0;
            info->compression = rle;
            info->unknown_430 = 100;
            info->alphabits = alphabits;
            info->redbits = 8;
            info->greenbits = 8;
            info->bluebits = 8;
            info->centrex = 0;
            info->centrey = 0;
            info->positionx = xorigin;
            info->positiony = yorigin;
            info->pointcount = 0;
            info->name[0] = 0;
            if (depth >= 15)
            {
                if (depth == 16)
                    depth = 15;
                info->bpp = 32;
                info->depth = depth;
                info->numcolours = 0;
                if (depth <= 16)
                {
                    info->bluebits = 5;
                    info->greenbits = 5;
                    info->redbits = 5;
                }
                if (depth < 32)
                    info->alphabits = 0;
            }
            else
            {
                if (depth == 0)
                    depth = 8;
                if (colours == 0)
                    colours = 1 << depth;
                if (colours > 256)
                    colours = 256;
                info->bpp = 8;
                info->depth = depth;
                info->numcolours = colours;
                info->unknown_020 = mapfirst;
                if (ggeti(header + 1, 1))
                {
                    switch (mapentrybits)
                    {
                    case 32:
                        info->alphabits = 8;
                        ok = gread(tga->stream, palette, colours * 4);
                        for (i = 0; i < maplength; ++i)
                        {
                            info->colour[mapfirst + i].a = palette[i * 4 + 3];
                            info->colour[mapfirst + i].r = palette[i * 4 + 2];
                            info->colour[mapfirst + i].g = palette[i * 4 + 1];
                            info->colour[mapfirst + i].b = palette[i * 4];
                        }
                        break;
                    case 24:
                        info->alphabits = 0;
                        ok = gread(tga->stream, palette, colours * 3);
                        for (i = 0; i < maplength; ++i)
                        {
                            info->colour[mapfirst + i].a = 0xff;
                            info->colour[mapfirst + i].r = palette[i * 3 + 2];
                            info->colour[mapfirst + i].g = palette[i * 3 + 1];
                            info->colour[mapfirst + i].b = palette[i * 3];
                        }
                        break;
                    case 15:
                    case 16:
                        info->bluebits = 5;
                        info->greenbits = 5;
                        info->redbits = 5;
                        info->alphabits = 0;
                        ok = gread(tga->stream, palette, colours * 2);
                        for (i = 0; i < maplength; ++i)
                        {
                            unsigned entry = ggeti(palette + i * 2, 2);
                            if (alphabits)
                                info->colour[mapfirst + i].a = (unsigned char)(((entry >> 15) & 1) * 255);
                            else
                                info->colour[mapfirst + i].a = 0xff;
                            info->colour[mapfirst + i].r = (unsigned char)(((entry >> 10) & 0x1f) * 255 / 31);
                            info->colour[mapfirst + i].g = (unsigned char)(((entry >> 5) & 0x1f) * 255 / 31);
                            info->colour[mapfirst + i].b = (unsigned char)((entry & 0x1f) * 255 / 31);
                        }
                        break;
                    }
                }
                else
                {
                    info->alphabits = 0;
                    for (i = 0; i < 256; ++i)
                    {
                        info->colour[i].a = 0xff;
                        info->colour[i].r = (unsigned char)i;
                        info->colour[i].g = (unsigned char)i;
                        info->colour[i].b = (unsigned char)i;
                    }
                }
            }
        }
        if (info && !ok)
        {
            gfree(info);
            info = 0;
        }
    }
    return info;
}

// Converts `count` 16-bit Targa pixels (x1555, little-endian) into b, g, r, a.  With `advance`
// the source moves on per pixel, otherwise one pixel is repeated (RLE packet).
// Part of 100eb216; the original repeats this expression in its three pixel loops.
static unsigned char *Convert16(unsigned char *destination, const unsigned char *source, int count, int alphabits,
                                int advance)
{
    for (int i = 0; i < count; ++i)
    {
        if (alphabits)
            destination[3] = (unsigned char)(((source[1] >> 7) & 1) * 255);
        else
            destination[3] = 0xff;
        destination[2] = (unsigned char)(((source[1] >> 2) & 0x1f) * 255 / 31);
        destination[1] = (unsigned char)(((((source[1] & 3) << 3) | ((source[0] >> 5) & 7)) * 255) / 31);
        destination[0] = (unsigned char)((source[0] & 0x1f) * 255 / 31);
        destination += 4;
        if (advance)
            source += 2;
    }
    return destination;
}

// Copies `count` stored pixels (8, 15/16, 24 or 32 bits) from `source` into `destination`
// (8-bit indices or 32-bit b, g, r, a).  Part of 100eb216 (raw rows and raw packets).
static unsigned char *ConvertPixels(unsigned char *destination, const unsigned char *source, int count, int depth,
                                    int alphabits)
{
    int i;
    switch (depth)
    {
    case 8:
        for (i = 0; i < count; ++i)
            *destination++ = *source++;
        break;
    case 15:
    case 16:
        destination = Convert16(destination, source, count, alphabits, 1);
        break;
    case 24:
        for (i = 0; i < count; ++i)
        {
            destination[3] = 0xff;
            destination[2] = source[2];
            destination[1] = source[1];
            destination[0] = source[0];
            destination += 4;
            source += 3;
        }
        break;
    case 32:
        for (i = 0; i < count; ++i)
        {
            destination[3] = source[3];
            destination[2] = source[2];
            destination[1] = source[1];
            destination[0] = source[0];
            destination += 4;
            source += 4;
        }
        break;
    }
    return destination;
}

// 100eb216.  Reads one row into `destination`.  RLE packets are decoded until at least the row
// width is reached; a packet that runs past the end of the row is written out whole (the next
// row in memory receives the excess).  An unknown depth stores nothing.
static int ReadRow(GSTREAM *stream, unsigned char *destination, unsigned char *row, const GINFO *info)
{
    int ok = 0;
    int x = 0;
    int consumed = 0;
    unsigned char *source = row;
    int width = info->width;
    int depth = info->depth;
    int rle = info->compression;
    int alphabits = info->alphabits;
    int count, bytes, i;

    if (rle == 0)
    {
        count = width;
        bytes = (count * ((depth + 7) & ~7)) >> 3;
        ok = gread(stream, source, bytes);
        consumed += bytes;
        ConvertPixels(destination, source, count, depth, alphabits);
    }
    else
    {
        do
        {
            ok = gread(stream, source, 1);
            ++consumed;
            count = *source;
            source = row;
            if (count & 0x80)
            {
                // Run packet: one stored pixel repeated.
                count = (count & 0x7f) + 1;
                x += count;
                switch (depth)
                {
                case 8:
                    ok = gread(stream, source, 1);
                    ++consumed;
                    for (i = 0; i < count; ++i)
                        *destination++ = *source;
                    break;
                case 15:
                case 16:
                    ok = gread(stream, source, 2);
                    consumed += 2;
                    destination = Convert16(destination, source, count, alphabits, 0);
                    break;
                case 24:
                    ok = gread(stream, source, 3);
                    consumed += 3;
                    for (i = 0; i < count; ++i)
                    {
                        destination[3] = 0xff;
                        destination[2] = source[2];
                        destination[1] = source[1];
                        destination[0] = source[0];
                        destination += 4;
                    }
                    break;
                case 32:
                    ok = gread(stream, source, 4);
                    consumed += 4;
                    for (i = 0; i < count; ++i)
                    {
                        destination[3] = source[3];
                        destination[2] = source[2];
                        destination[1] = source[1];
                        destination[0] = source[0];
                        destination += 4;
                    }
                    break;
                }
            }
            else
            {
                // Raw packet: count stored pixels.
                count = (count & 0x7f) + 1;
                x += count;
                bytes = (count * ((depth + 7) & ~7)) >> 3;
                ok = gread(stream, source, bytes);
                consumed += bytes;
                destination = ConvertPixels(destination, source, count, depth, alphabits);
            }
        } while (x < width);
    }
    (void)consumed;
    return ok;
}

// 100eba09.  Reverses a row left to right (32-bit or 8-bit pixels).
static void MirrorRow(unsigned char *row, int width, int bpp)
{
    int i;
    if (bpp == 32)
    {
        unsigned *left = (unsigned *)row;
        unsigned *right = (unsigned *)row + width - 1;
        for (i = 0; i < width >> 1; ++i)
        {
            unsigned pixel = *left;
            *left++ = *right;
            *right-- = pixel;
        }
    }
    else
    {
        unsigned char *left = row;
        unsigned char *right = row + width - 1;
        for (i = 0; i < width >> 1; ++i)
        {
            unsigned char pixel = *left;
            *left++ = *right;
            *right-- = pixel;
        }
    }
}

// 100eb053.
// The image data starts after the identification field and the colour map, whatever the image
// type.  Rows are stored bottom-up unless descriptor bit 5 is set; bit 4 mirrors each row.
// Reading stops at the first row whose last read returned 0.
int GCALL TGA_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    TGAHANDLE *tga = (TGAHANDLE *)handle;
    unsigned char header[18];
    unsigned char *destination;
    int step;
    int ok;

    gseek(tga->stream, 0);
    ok = gread(tga->stream, header, 18);
    if (ok)
    {
        int width = info->width;
        int height = info->height;
        int depth = info->depth;
        int colours = info->numcolours;
        int rle = info->compression;
        (void)colours;
        (void)rle;
        int maplength = ggeti(header + 5, 2);
        int mapentrybits = ggeti(header + 7, 1);
        int idlength = ggeti(header, 1);
        int descriptor = ggeti(header + 17, 1);
        int dataoffset = idlength + 18;
        if (ggeti(header + 1, 1))
            dataoffset += maplength * ((mapentrybits + 7) / 8);
        ok = gseek(tga->stream, dataoffset);
        if (descriptor & 0x20)
        {
            destination = (unsigned char *)pixels;
            step = rowbytes;
        }
        else
        {
            destination = (unsigned char *)pixels + rowbytes * (height - 1);
            step = -rowbytes;
        }
        unsigned char *row = (unsigned char *)galloc((width * ((depth + 7) & ~7)) >> 3);
        if (row)
        {
            for (int y = 0; y < height && ok; ++y)
            {
                ok = ReadRow(tga->stream, destination, row, info);
                if (descriptor & 0x10)
                    MirrorRow(destination, width, info->bpp);
                destination += step;
            }
            gfree(row);
        }
    }
    return ok;
}

// 100ebad5.
int GCALL TGA_close(void *handle)
{
    int ok = 0;
    if (handle)
        ok = gfree(handle);
    return ok;
}

GIMEX_BOUNDARY_WRITE(TGA)
