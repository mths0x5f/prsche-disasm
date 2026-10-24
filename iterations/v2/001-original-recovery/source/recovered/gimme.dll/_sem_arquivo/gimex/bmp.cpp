// "Windows BMP" module 1.24 (FrANK G. Barchard): GIMEX module 2.
// gimme.dll 3a43b0f6…, entry points about 100f83d0, is 100f85d3, open 100f8629, info 100f8692, read 100f8e06, close 100f9a3a,
// wopen 100f7350, write 100f73a6, wclose 100f839b.  about(), is() and the reader (open, info, read,
// close and their helpers 100f8dbd, 100f91bd, 100f9a05) are recovered; the writer entry points are
// recovery boundaries (boundary.h) until the module's writer is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100f83d0.
GABOUT *BMP_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'B', 'M', 'P');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x93d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('B', 'I', 'N', 'A');
        about->mactype[1] = GTAG('.', 'B', 'M', 'P');
        strcpy(about->extension[0], ".bmp");
        strcpy(about->extension[1], ".rle");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.24");
        strcpy(about->shortname, "BMP");
        strcpy(about->longname, "BMP");
        strcpy(about->name, "Windows BMP");
    }
    return about;
}

// 100f85d3.
int GCALL BMP_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 2) && magic[0] == 'B' && magic[1] == 'M')
        score = 100;
    return score;
}

// ---------------------------------------------------------------------------------------------
// Reader.  Every entry point rereads the file header from offset 0; the handle only keeps the
// stream.

// Handle returned by open() (0x18 bytes, cleared).
struct BMPHANDLE
{
    unsigned tag;                // +0x00 '.BMP'
    int size;                    // +0x04 sizeof(BMPHANDLE)
    int count;                   // +0x08 frames: always 1
    int unknown_0c;              // +0x0c
    GSTREAM *stream;             // +0x10
    int unknown_14;              // +0x14
};

static_assert(sizeof(BMPHANDLE) == 0x18, "BMPHANDLE layout");

// Bitmap header generations as info() stores them in GINFO.attributes (read() dispatches on it).
enum
{
    BMP_HEADER_INFO = 0,         // BITMAPINFOHEADER (40 bytes) or any other size than below
    BMP_HEADER_CORE = 1,         // BITMAPCOREHEADER (12 bytes), RGB palette
    BMP_HEADER_V4 = 2,           // BITMAPV4HEADER (108 bytes), masks inside the header
    BMP_HEADER_INFO_MASKS = 3    // BITMAPINFOHEADER with BI_BITFIELDS, masks after the header
};

// GINFO +0x287c: info() stores the horizontal resolution here, pixels per metre / 39.37 as a
// float (pixels per inch).  gimex.h lays out this offset as point[0x400][0]; the field's own
// name is not known.
static float *BmpResolution(GINFO *info)
{
    return (float *)((unsigned char *)info + 0x287c);
}

// 100f8dbd.  Width of the lowest run of set bits of a colour mask.
static int MaskBits(unsigned mask)
{
    int bits = 0;
    if (mask)
    {
        while ((mask & 1) == 0)
            mask >>= 1;
        while (mask & 1)
        {
            mask >>= 1;
            ++bits;
        }
    }
    return bits;
}

// 100f9a05.  Position of the lowest set bit of a colour mask.
static int MaskShift(unsigned mask)
{
    int shift = 0;
    if (mask)
    {
        while ((mask & 1) == 0)
        {
            ++shift;
            mask >>= 1;
        }
    }
    return shift;
}

// 100f8629.
int GCALL BMP_open(void **handle, GSTREAM *stream, const char *, int)
{
    int ok = 0;
    BMPHANDLE *bmp = (BMPHANDLE *)galloc(sizeof(BMPHANDLE));
    if (bmp)
    {
        memset(bmp, 0, sizeof(BMPHANDLE));
        bmp->count = 1;
        bmp->tag = GTAG('.', 'B', 'M', 'P');
        bmp->size = sizeof(BMPHANDLE);
        bmp->stream = stream;
        *handle = bmp;
        ok = 1;
    }
    return ok;
}

// 100f8692.
// The bitmap header is read whole into a 0x7a-byte buffer (file header, then up to 108 bytes);
// a larger header size (BITMAPV5HEADER, 124) overruns the buffer in the original as well.  The
// masks are taken from header bytes 0x36… for every non-core header: zero for a plain 40-byte
// header, because the buffer is cleared first.  The palette follows the header directly.
GINFO *GCALL BMP_info(void *handle, int)
{
    BMPHANDLE *bmp = (BMPHANDLE *)handle;
    GINFO *info = 0;
    int xpelspermeter = 0;
    int ok = 0;
    unsigned char header[0x7a];
    unsigned char palette[0x400];
    int headersize, maskbytes, kind;
    int width, height, depth, colours, compression;
    unsigned redmask, greenmask, bluemask, alphamask;

    gseek(bmp->stream, 0);
    memset(header, 0, sizeof(header));
    ok = gread(bmp->stream, header, 18);
    if (ok)
    {
        headersize = ggeti(header + 14, 4);
        maskbytes = 0;
        ok = gread(bmp->stream, header + 18, headersize - 4);
        if (headersize == 12)
        {
            kind = BMP_HEADER_CORE;
            width = ggeti(header + 18, 2);
            height = ggeti(header + 20, 2);
            depth = ggeti(header + 24, 2);
            colours = 1 << depth;
            compression = 0;
        }
        else
        {
            kind = BMP_HEADER_INFO;
            width = ggeti(header + 18, 4);
            height = ggeti(header + 22, 4);
            depth = ggeti(header + 28, 2);
            colours = ggeti(header + 46, 4);
            compression = ggeti(header + 30, 4);
            xpelspermeter = ggeti(header + 38, 4);
            if (compression == 3 && headersize == 40)
            {
                kind = BMP_HEADER_INFO_MASKS;
                maskbytes = 12;
                ok = gread(bmp->stream, header + 14 + headersize, maskbytes);
            }
            if (headersize == 108)
                kind = BMP_HEADER_V4;
            redmask = ggeti(header + 54, 4);
            greenmask = ggeti(header + 58, 4);
            bluemask = ggeti(header + 62, 4);
            alphamask = ggeti(header + 66, 4);
        }
    }
    if (height < 0)
        height = -height;

    if (ok)
    {
        info = (GINFO *)galloc(GINFO_SIZE_LEGACY);
        if (info)
        {
            memset(info, 0, GINFO_SIZE_LEGACY);
            info->tag = GTAG('.', 'B', 'M', 'P');
            info->size = GINFO_SIZE_LEGACY;
            info->version = GINFO_VERSION;
            info->frames = 0;
            info->width = width;
            info->height = height;
            info->attributes = kind;
            info->compression = (compression == 1 || compression == 2) ? 1 : 0;   // BI_RLE8, BI_RLE4
            info->unknown_430 = 100;
            info->alphabits = 0;
            info->redbits = 8;
            info->greenbits = 8;
            info->bluebits = 8;
            info->centrex = 0;
            info->centrey = 0;
            info->positionx = 0;
            info->positiony = 0;
            info->pointcount = 0;
            *BmpResolution(info) = xpelspermeter / 39.3700787f;
            info->name[0] = 0;
            if (depth > 8)
            {
                info->bpp = 32;
                info->depth = depth;
                info->numcolours = 0;
                if (compression != 3)
                {
                    if (depth == 16)
                    {
                        info->depth = 15;
                        info->bluebits = 5;
                        info->greenbits = 5;
                        info->redbits = 5;
                    }
                }
                else
                {
                    if (depth == 32 && kind == BMP_HEADER_V4)
                        info->alphabits = MaskBits(alphamask);
                    else
                        info->alphabits = 0;
                    info->redbits = MaskBits(redmask);
                    info->greenbits = MaskBits(greenmask);
                    info->bluebits = MaskBits(bluemask);
                }
            }
            else
            {
                if (depth == 0)
                    depth = 8;
                if (colours == 0)
                    colours = 1 << depth;
                if (colours > 256)
                    colours = 256;
                if (colours != 0)
                {
                    if (kind == BMP_HEADER_CORE)
                    {
                        if (ok)
                            ok = gread(bmp->stream, palette, colours * 3);
                        for (int i = 0; i < colours; ++i)
                        {
                            info->colour[i].a = 0xff;
                            info->colour[i].r = palette[i * 3 + 2];
                            info->colour[i].g = palette[i * 3 + 1];
                            info->colour[i].b = palette[i * 3];
                        }
                    }
                    else
                    {
                        int withalpha = 0;
                        if (ok)
                            ok = gread(bmp->stream, palette, colours * 4);
                        for (int i = 0; i < colours; ++i)
                        {
                            info->colour[i].a = palette[i * 4 + 3];
                            info->colour[i].r = palette[i * 4 + 2];
                            info->colour[i].g = palette[i * 4 + 1];
                            info->colour[i].b = palette[i * 4];
                            if (info->colour[i].a)
                                ++withalpha;
                        }
                        if (withalpha)
                            info->alphabits = 8;
                        else
                        {
                            info->alphabits = 0;
                            for (int i = 0; i < colours; ++i)
                                info->colour[i].a = 0xff;
                        }
                    }
                }
                info->bpp = 8;
                info->depth = depth;
                info->numcolours = colours;
            }
        }
    }
    if (info && !ok)
    {
        gfree(info);
        info = 0;
    }
    return info;
}

// 100f91bd.  Reads one stored row into `row` and converts it into `destination` (8-bit indices
// or 32-bit b, g, r, a).  RLE rows are decoded code by code: an escape below 3 (end of line, end
// of bitmap, delta) ends the row unless nothing was decoded yet, so delta offsets are read as
// codes.  Every row is then padded to a multiple of 4 consumed bytes, RLE rows included, and the
// padding is read to the current source position.  A 16-bit row is read four bytes per pixel.
static int ReadRow(GSTREAM *stream, unsigned char *destination, unsigned char *row, int depth, const GINFO *info,
                   unsigned alphamask, unsigned redmask, unsigned greenmask, unsigned bluemask)
{
    int ok = 0;
    int x = 0;
    int consumed = 0;
    unsigned char *source = row;
    int width = info->width;
    int compression = info->compression;
    int bits = depth;
    int count, bytes, i;
    if (bits == 15)
        bits = 16;

    if (compression == 0)
    {
        count = width;
        bytes = ((count * bits + 31) & ~31) >> 3;
        ok = gread(stream, source, bytes);
        consumed += bytes;
        switch (depth)
        {
        case 1:
            for (i = 0; i < count; ++i)
            {
                *destination++ = (*source >> (7 - (i & 7))) & 1;
                if ((i & 7) == 7)
                    ++source;
            }
            break;
        case 4:
            for (i = 0; i < count; ++i)
            {
                if (i & 1)
                {
                    *destination++ = *source & 0xf;
                    ++source;
                }
                else
                    *destination++ = *source >> 4;
            }
            break;
        case 8:
            for (i = 0; i < count; ++i)
                *destination++ = *source++;
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
        case 15:
        case 16:
        case 32:
        {
            int alphascale = 1 << info->alphabits;
            int redscale = 1 << info->redbits;
            int greenscale = 1 << info->greenbits;
            int bluescale = 1 << info->bluebits;
            int step;
            if (depth <= 16)
                step = 2;
            else
                step = 4;
            int alphashift = MaskShift(alphamask);
            int redshift = MaskShift(redmask);
            int greenshift = MaskShift(greenmask);
            int blueshift = MaskShift(bluemask);
            for (i = 0; i < count; ++i)
            {
                if (alphamask)
                {
                    if (alphascale != 1)
                        destination[3] = (unsigned char)((((*(unsigned *)source & alphamask) >> alphashift) * 255 +
                                                          (alphascale >> 1)) / (alphascale - 1));
                    else
                        destination[3] = (unsigned char)(((*(unsigned *)source & alphamask) >> alphashift) * 255);
                }
                else
                    destination[3] = 0xff;
                destination[2] = (unsigned char)((((*(unsigned *)source & redmask) >> redshift) * 255 + (redscale >> 1)) /
                                                 (redscale - 1));
                destination[1] = (unsigned char)((((*(unsigned *)source & greenmask) >> greenshift) * 255 +
                                                  (greenscale >> 1)) / (greenscale - 1));
                destination[0] = (unsigned char)((((*(unsigned *)source & bluemask) >> blueshift) * 255 +
                                                  (bluescale >> 1)) / (bluescale - 1));
                destination += 4;
                source += step;
            }
            break;
        }
        }
    }
    else
    {
        do
        {
            ok = gread(stream, source, 1);
            ++consumed;
            count = *source;
            source = row;
            if (count != 0)
            {
                // Encoded run: count pixels of one value.
                x += count;
                ok = gread(stream, source, 1);
                ++consumed;
                int value = *source;
                switch (depth)
                {
                case 1:
                    for (i = 0; i < count; ++i)
                        *destination++ = ((value & 0xff) >> (7 - (i & 7))) & 1;
                    break;
                case 4:
                    for (i = 0; i < count; ++i)
                    {
                        if (i & 1)
                            *destination++ = (value & 0xff) & 0xf;
                        else
                            *destination++ = (value & 0xff) >> 4;
                    }
                    break;
                case 8:
                    for (i = 0; i < count; ++i)
                        *destination++ = (unsigned char)value;
                    break;
                case 24:
                    ok = gread(stream, source + 1, 2);
                    consumed += 2;
                    value = ggeti(source, 3) | 0xff000000;
                    for (i = 0; i < count; ++i)
                    {
                        *(int *)destination = value;
                        destination += 4;
                    }
                    break;
                }
            }
            else
            {
                ok = gread(stream, source, 1);
                ++consumed;
                count = *source;
                if (count < 3)
                {
                    if (x != 0)
                    {
                        x = width;
                        break;
                    }
                }
                else
                {
                    // Absolute run: count pixels stored as they are, padded to 16 bits.
                    x += count;
                    bytes = ((count * depth + 15) & ~15) >> 3;
                    ok = gread(stream, source, bytes);
                    consumed += bytes;
                    switch (depth)
                    {
                    case 1:
                        for (i = 0; i < count; ++i)
                        {
                            *destination++ = (*source >> (7 - (i & 7))) & 1;
                            if ((i & 7) == 7)
                                ++source;
                        }
                        break;
                    case 4:
                        for (i = 0; i < count; ++i)
                        {
                            if (i & 1)
                            {
                                *destination++ = *source & 0xf;
                                ++source;
                            }
                            else
                                *destination++ = *source >> 4;
                        }
                        break;
                    case 8:
                        for (i = 0; i < count; ++i)
                            *destination++ = *source++;
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
                    }
                }
            }
        } while (x < width);
    }
    if (consumed & 3)
        gread(stream, source, -consumed & 3);
    return ok;
}

// 100f8e06.
// The file header and the start of the bitmap header are read again: 26 bytes, or 70 for the
// V4 and masked headers.  The compression word lies past the 26 bytes, so for core and plain
// info headers it is tested on whatever the uncleared stack buffer holds (as in the original;
// it only selects the mask source).  A zero data offset is replaced by the header and palette
// size.  Rows are stored bottom-up unless header bytes 0x16… are negative; for a core header
// those bytes are its planes and bit count, never negative.
int GCALL BMP_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    BMPHANDLE *bmp = (BMPHANDLE *)handle;
    int dataoffset = 0;
    int fileheadersize = 14;
    int colours = info->numcolours;
    int kind = info->attributes;
    int compression = info->compression;
    int width = info->width;
    int height = info->height;
    unsigned char header[0x7c];
    unsigned redmask, greenmask, bluemask, alphamask;
    int ok;
    (void)compression;

    gseek(bmp->stream, 0);
    if (kind >= BMP_HEADER_V4)
        ok = gread(bmp->stream, header, fileheadersize + 0x38);
    else
        ok = gread(bmp->stream, header, fileheadersize + 12);
    if (ok)
    {
        int depth = info->depth;
        if (ggeti(header + 30, 4) == 3)
        {
            redmask = ggeti(header + 54, 4);
            greenmask = ggeti(header + 58, 4);
            bluemask = ggeti(header + 62, 4);
            if (depth == 32 && kind == BMP_HEADER_V4)
                alphamask = ggeti(header + 66, 4);
            else
                alphamask = 0;
        }
        else if (depth == 15)
        {
            redmask = 0x7c00;
            greenmask = 0x3e0;
            bluemask = 0x1f;
            alphamask = 0;
        }
        else if (depth == 32)
        {
            redmask = 0xff0000;
            greenmask = 0xff00;
            bluemask = 0xff;
            alphamask = 0;
        }
        if (fileheadersize > 6)
            dataoffset = ggeti(header + 10, 4);
        if (dataoffset == 0)
        {
            if (kind == BMP_HEADER_CORE)
            {
                dataoffset = fileheadersize + 12;
                if (depth <= 8)
                    dataoffset += colours * 3;
            }
            else if (kind == BMP_HEADER_V4)
                dataoffset = fileheadersize + 108;
            else if (kind == BMP_HEADER_INFO_MASKS)
                dataoffset = fileheadersize + 52;
            else
            {
                dataoffset = fileheadersize + 40;
                if (depth <= 8)
                    dataoffset += colours * 4;
            }
        }
        ok = gseek(bmp->stream, dataoffset);
        int bits = depth;
        if (bits == 15)
            bits = 16;
        unsigned char *row = (unsigned char *)galloc(((width * bits + 31) & ~31) >> 3);
        if (row)
        {
            unsigned char *destination;
            int y;
            if (ggeti(header + 22, 4) >= 0)
            {
                destination = (unsigned char *)pixels + rowbytes * (height - 1);
                for (y = 0; y < height; ++y)
                {
                    if (ok)
                        ok = ReadRow(bmp->stream, destination, row, depth, info, alphamask, redmask, greenmask,
                                     bluemask);
                    destination -= rowbytes;
                }
            }
            else
            {
                destination = (unsigned char *)pixels;
                for (y = height; y > 0; --y)
                {
                    if (ok)
                        ok = ReadRow(bmp->stream, destination, row, depth, info, alphamask, redmask, greenmask,
                                     bluemask);
                    destination += rowbytes;
                }
            }
            gfree(row);
        }
    }
    return ok;
}

// 100f9a3a.
int GCALL BMP_close(void *handle)
{
    int ok = 0;
    if (handle)
        ok = gfree(handle);
    return ok;
}

GIMEX_BOUNDARY_WRITE(BMP)
