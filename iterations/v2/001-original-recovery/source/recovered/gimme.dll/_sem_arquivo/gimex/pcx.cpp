// "ZSoft PCX" module 1.05 (FrANK G. Barchard): GIMEX module 16.
// gimme.dll 3a43b0f6…, entry points about 100d7060, is 100d727b, open 100d72fd, info 100d743e, read 100d78fa, close 100d7fb1,
// wopen 100d68f0, write 100d69e9, wclose 100d6fb6.  about(), is() and the reader (open, info, read,
// close and the row decoder 100d7a37) are recovered; the writer entry points are recovery
// boundaries (boundary.h) until the module's writer is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100d7060.
GABOUT *PCX_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'P', 'C', 'X');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x97d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('P', 'C', 'X', ' ');
        about->mactype[1] = GTAG('B', 'I', 'N', 'A');
        strcpy(about->extension[0], ".pcx");
        strcpy(about->extension[1], ".dcx");
        strcpy(about->extension[2], ".pcc");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.05");
        strcpy(about->shortname, "PCX");
        strcpy(about->longname, "PCX");
        strcpy(about->name, "ZSoft PCX");
    }
    return about;
}

// 100d727b.
int GCALL PCX_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[8];
    gseek(stream, 0);
    if (gread(stream, header, 8))
    {
        if (header[0] == 10 && header[1] < 6 && header[2] < 2)
            score = 95;
        else if (ggeti(header, 4) == 0x3ade68b1)   // DCX page table
            score = 100;
    }
    return score;
}

// ---------------------------------------------------------------------------------------------
// Reader.  A DCX file is a page table (magic 0x3ade68b1, then page offsets up to a zero entry)
// in front of PCX pages; open() keeps the table, or the first 12 bytes of a plain PCX file.

#define PCX_DCX_MAGIC 0x3ade68b1

// Handle returned by open() (0x18 bytes, cleared).
struct PCXHANDLE
{
    unsigned tag;                // +0x00 '.PCX'
    int size;                    // +0x04 sizeof(PCXHANDLE)
    int count;                   // +0x08 pages: 1, or the DCX table entries before the zero entry
    int unknown_0c;              // +0x0c
    GSTREAM *stream;             // +0x10
    unsigned char *table;        // +0x14 count * 4 + 8 bytes from offset 0 (magic, offsets, 0)
};

static_assert(sizeof(PCXHANDLE) == 0x18, "PCXHANDLE layout");

// GINFO +0x287c: info() stores the horizontal resolution (header word 0x0c, dots per inch) here
// as a float.  gimex.h lays out this offset as point[0x400][0]; the BMP reader stores its
// resolution at the same place.  The field's own name is not known.
static float *PcxResolution(GINFO *info)
{
    return (float *)((unsigned char *)info + 0x287c);
}

// 100d72fd.  Returns the page count (also 0 for a DCX table without pages) once the handle
// exists, whether or not the table could be read.
int GCALL PCX_open(void **handle, GSTREAM *stream, const char *, int)
{
    int count = 1;
    int ok = 0;
    unsigned char word[4];
    PCXHANDLE *pcx = (PCXHANDLE *)galloc(sizeof(PCXHANDLE));
    if (pcx)
    {
        memset(pcx, 0, sizeof(PCXHANDLE));
        pcx->count = count;
        pcx->tag = GTAG('.', 'P', 'C', 'X');
        pcx->size = sizeof(PCXHANDLE);
        pcx->stream = stream;
        gseek(stream, 0);
        if (gread(stream, word, 4))
        {
            ok = 1;
            if (ggeti(word, 4) == PCX_DCX_MAGIC)
            {
                count = -1;
                do
                {
                    ++count;
                    ok = gread(stream, word, 4);
                } while (ok && ggeti(word, 4) != 0);
            }
            unsigned char *table = (unsigned char *)galloc(count * 4 + 8);
            if (table)
            {
                pcx->table = table;
                gseek(pcx->stream, 0);
                ok = gread(pcx->stream, table, count * 4 + 8);
            }
        }
        pcx->count = count;
        ok = count;
        *handle = pcx;
    }
    return ok;
}

// 100d743e.
// The header is 128 bytes at the page offset.  depth = bits per pixel * planes; above 8 the
// image is returned as 32-bit.  Up to 16 colours come from the header palette, more from the
// 3 * colours bytes before the next page (or the end of the file); the 0x0c marker before them
// is not checked.  Depth 1, and depth 3 in one plane, get black and white instead.
GINFO *GCALL PCX_info(void *handle, int frame)
{
    PCXHANDLE *pcx = (PCXHANDLE *)handle;
    GINFO *info = 0;
    int ok = 0;
    int offset = 0;
    unsigned char header[0x80];
    unsigned char palette[0x300];
    unsigned char *table = pcx->table;

    if (ggeti(table, 4) == PCX_DCX_MAGIC)
        offset = ggeti(table + frame * 4 + 4, 4);
    gseek(pcx->stream, offset);
    ok = gread(pcx->stream, header, 0x80);
    if (ok)
    {
        int width = ggeti(header + 8, 2) - ggeti(header + 4, 2) + 1;
        int height = ggeti(header + 10, 2) - ggeti(header + 6, 2) + 1;
        int xmin = ggeti(header + 4, 2);
        int ymin = ggeti(header + 6, 2);
        int depth = ggeti(header + 3, 1);
        int planes = ggeti(header + 0x41, 1);
        int encoding = ggeti(header + 2, 1);
        int version = ggeti(header + 1, 1);
        int resolution = ggeti(header + 12, 2);
        (void)version;
        if (planes == 0)
            planes = 1;
        if (depth == 0)
            depth = 8;

        info = (GINFO *)galloc(GINFO_SIZE_LEGACY);
        if (info)
        {
            memset(info, 0, GINFO_SIZE_LEGACY);
            info->tag = GTAG('.', 'P', 'C', 'X');
            info->size = GINFO_SIZE_LEGACY;
            info->version = GINFO_VERSION;
            info->frames = frame;
            info->width = width;
            info->height = height;
            info->attributes = 0;
            info->compression = encoding;
            info->unknown_430 = 100;
            info->alphabits = 0;
            info->redbits = 8;
            info->greenbits = 8;
            info->bluebits = 8;
            info->centrex = 0;
            info->centrey = 0;
            info->positionx = xmin;
            info->positiony = ymin;
            info->pointcount = 0;
            info->name[0] = 0;
            *PcxResolution(info) = (float)resolution;
            depth *= planes;
            if (depth > 8)
            {
                info->bpp = 32;
                info->depth = depth;
                info->numcolours = 0;
            }
            else
            {
                int colours = 1 << depth;
                int vga = 0;
                if (colours > 16)
                    vga = 1;
                if (vga)
                {
                    int end;
                    if (frame < pcx->count - 1)
                        end = ggeti(table + frame * 4 + 8, 4);
                    else
                        end = glen(pcx->stream);
                    gseek(pcx->stream, end - colours * 3);
                    ok = gread(pcx->stream, palette, colours * 3);
                }
                else
                    memcpy(palette, header + 0x10, colours * 3);
                if (ok)
                {
                    if (depth == 1 || (depth == 3 && planes == 1))
                    {
                        info->colour[0].a = 0xff;
                        info->colour[0].r = 0;
                        info->colour[0].g = 0;
                        info->colour[0].b = 0;
                        info->colour[1].a = 0xff;
                        info->colour[1].r = 0xff;
                        info->colour[1].g = 0xff;
                        info->colour[1].b = 0xff;
                    }
                    else
                    {
                        for (int i = 0; i < colours; ++i)
                        {
                            info->colour[i].a = 0xff;
                            info->colour[i].r = palette[i * 3];
                            info->colour[i].g = palette[i * 3 + 1];
                            info->colour[i].b = palette[i * 3 + 2];
                        }
                    }
                }
                info->bpp = 8;
                info->depth = depth;
                info->numcolours = colours;
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

// 100d7a37.  Reads one stored line (bytesperline per plane; three planes counted above 8 bits,
// whatever the plane count) into `row`, RLE-decoded or raw (an odd raw line reads one byte
// more), then converts it into `destination`.  The planes of a planar line are taken
// width / 8 (1-bit planes) or width (8-bit planes) bytes apart, not bytesperline.  4-bit lines are
// planar unless GINFO.attributes is 1, which info() never sets.  Depths other than 1, 2, 3, 4,
// 8 and 24 store nothing.
static int ReadRow(GSTREAM *stream, unsigned char *destination, unsigned char *row, const GINFO *info,
                   int bytesperline)
{
    int ok = 0;
    int x = 0;
    unsigned char *source = row;
    int width = info->width;
    int depth = info->depth;
    int encoding = info->compression;
    int count = width;
    int packed = info->attributes;
    int total = bytesperline;
    int i;
    if (depth > 8)
        total *= 3;

    source = row;
    if (encoding)
    {
        for (x = 0; x < total; x += count)
        {
            ok = gread(stream, source, 1);
            count = *source;
            if ((count & 0xc0) == 0xc0)
            {
                count &= 0x3f;
                if (count >= total - x)
                    count = total - x;
                ok = gread(stream, source, 1);
                int value = *source;
                for (i = 0; i < count; ++i)
                    *source++ = (unsigned char)value;
            }
            else
            {
                count = 1;
                ++source;
            }
        }
    }
    else
    {
        ok = gread(stream, source, total);
        if (total & 1)
            ok = gread(stream, source + total, 1);
    }

    source = row;
    count = width;
    if (ok)
    {
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
        case 2:
            for (i = 0; i < count; ++i)
            {
                *destination++ = (*source >> (6 - (i & 3) * 2)) & 3;
                if ((i & 3) == 3)
                    ++source;
            }
            break;
        case 3:
            for (i = 0; i < count; ++i)
            {
                int bit0 = (source[0] >> (7 - (i & 7))) & 1;
                int bit1 = (source[count / 8] >> (7 - (i & 7))) & 1;
                int bit2 = (source[count / 8 * 2] >> (7 - (i & 7))) & 1;
                *destination++ = (unsigned char)(bit0 | (bit1 << 1) | (bit2 << 2));
                if ((i & 7) == 7)
                    ++source;
            }
            break;
        case 4:
            if (packed == 1)
            {
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
            }
            else
            {
                for (i = 0; i < count; ++i)
                {
                    int bit0 = (source[0] >> (7 - (i & 7))) & 1;
                    int bit1 = (source[count / 8] >> (7 - (i & 7))) & 1;
                    int bit2 = (source[count / 8 * 2] >> (7 - (i & 7))) & 1;
                    int bit3 = (source[count / 8 * 3] >> (7 - (i & 7))) & 1;
                    *destination++ = (unsigned char)(bit0 | (bit1 << 1) | (bit2 << 2) | (bit3 << 3));
                    if ((i & 7) == 7)
                        ++source;
                }
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
                destination[2] = source[0];
                destination[1] = source[count];
                destination[0] = source[count * 2];
                destination += 4;
                ++source;
            }
            break;
        }
    }
    return ok;
}

// 100d78fa.  Rows are stored top-down; a zero bytes-per-line word is replaced by the packed size.
int GCALL PCX_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    PCXHANDLE *pcx = (PCXHANDLE *)handle;
    int offset = 0;
    unsigned char header[0x80];
    unsigned char *table = pcx->table;
    int ok;

    if (ggeti(table, 4) == PCX_DCX_MAGIC)
        offset = ggeti(table + info->frames * 4 + 4, 4);
    gseek(pcx->stream, offset);
    ok = gread(pcx->stream, header, 0x80);
    if (ok)
    {
        int width = info->width;
        int height = info->height;
        int depth = info->depth;
        int bytesperline = ggeti(header + 0x42, 2);
        if (bytesperline == 0)
            bytesperline = ((width * depth + 15) & ~15) >> 3;
        unsigned char *destination = (unsigned char *)pixels;
        unsigned char *row = (unsigned char *)galloc(bytesperline * 4);
        if (row)
        {
            for (int y = 0; y < height; ++y)
            {
                if (ok)
                    ok = ReadRow(pcx->stream, destination, row, info, bytesperline);
                destination += rowbytes;
            }
            gfree(row);
        }
    }
    return ok;
}

// 100d7fb1.  Returns the result of freeing the table (0 without one).
int GCALL PCX_close(void *handle)
{
    int ok = 0;
    PCXHANDLE *pcx = (PCXHANDLE *)handle;
    if (pcx)
    {
        if (pcx->table)
            ok = gfree(pcx->table);
        gfree(pcx);
    }
    return ok;
}

GIMEX_BOUNDARY_WRITE(PCX)
