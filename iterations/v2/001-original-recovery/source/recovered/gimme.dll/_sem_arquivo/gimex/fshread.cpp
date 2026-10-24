// FSH Shape File module: about, is, open, info, read, close.
// gimme.dll 3a43b0f6…, VA 10106e80–1010b839 (the reader half of the shape library, see fsh.h).
// Function names are role names; the original VA of each function is cited above it.

#include <string.h>

#include "fsh.h"

// 10106e80.  The flag bits are set one at a time in the original (bit fields); the result is
// 0xb7eb: bits 0, 1, 3, 5–10, 12, 13 and 15 (GABOUT_FLAG_DETECT_BY_CONTENT).
GABOUT *FSH_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', 'H', 'P', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->flags = (about->flags & ~0xcu) | 0x8;
        about->flags = (about->flags & ~0x30u) | 0x20;
        about->flags |= 0x40;
        about->flags |= 0x80;
        about->flags |= 0x100;
        about->flags |= 0x200;
        about->flags |= 0x400;
        about->flags &= ~0x800u;
        about->flags |= 0x1000;
        about->flags |= 0x2000;
        about->flags &= ~0x4000u;
        about->flags |= GABOUT_FLAG_DETECT_BY_CONTENT;
        about->unknown_14 = 4;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'f', 's', 'h');
        about->mactype[1] = 0;
        about->mactype[2] = 0;
        *(int *)(about->unknown_28 + 0) = 0;
        strcpy(about->extension[0], ".fsh");
        strcpy(about->extension[1], "");
        strcpy(about->extension[2], "");
        strcpy(about->extension[3], "");
        strcpy(about->author, "F Barchard");
        strcpy(about->moduleversion, "2.07");
        strcpy(about->shortname, "FSH");
        strcpy(about->longname, "FSH");
        strcpy(about->name, "FSH Shape File");
    }
    return about;
}

// 101070b1.
int GCALL FSH_is(GSTREAM *stream)
{
    unsigned char header[16];
    int score = 0;
    gseek(stream, 0);
    if (gread(stream, header, 16) == 16 && ggetm(header, 4) == (int)GTAG('S', 'H', 'P', 'I'))
        score = 100;
    return score;
}

// ---------------------------------------------------------------------------------------------
// Block helpers

// 10107a2a.  Bits per pixel of a bitmap or palette block from its type byte.
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

// 101079c5.  Bytes per row: 16-bit aligned, 8-bit aligned for shape types 2–5.
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

// 10107986.  Bytes of one image, 16-byte aligned.
static int ImageBytes(int width, int height, int bits, int type)
{
    int bytes = RowBytes(width, bits, type);
    bytes = bytes * height;
    bytes = (bytes + 15) & ~15;
    return bytes;
}

// 10107e7a.  Images in a bitmap block (bits 12–15 of the header word +0x0e: extra mip levels,
// 15 counts as none).  With levels != 0 the count is stored as levels - 1.
static int MipLevels(unsigned char *block, int levels, int)
{
    int value;
    int count;
    if (!block)
        return 0;
    value = ggeti(block + 0xe, 2);
    count = value >> 12;
    if (count == 0 || count == 15)
        count = 1;
    else
        count = count + 1;
    if (levels)
        gputi(block + 0xe, (value & 0xfff) + (levels - 1) * 0x1000, 2);
    return count;
}

// 10108449.  RefPack stream header.
static int IsRefPack(const unsigned char *data)
{
    if (ggetm(data, 2) != 0x10fb && ggetm(data, 2) != 0x11fb)
        return 0;
    return 100;
}

// 1010848e.  4x4 block compressed stream header.
static int IsBlockPacked(const unsigned char *data)
{
    int score = 0;
    if (ggetm(data, 2) == 0x18fb)
        score = 100;
    return score;
}

// 101084c6.  Block kind: 1 bitmap, 2 palette, 3 points (0x7c), 4 comment (0x6f), 5 records
// (0x6e), 6 tpage (0x6b), 0 unknown.
static int BlockKind(const unsigned char *block, int type)
{
    int kind;
    if (type == 3)
    {
        unsigned char code = block[0];
        if (code == 0x22)
            kind = 2;
        else if (code == 0x6f)
            kind = 4;
        else if (code == 0x7c)
            kind = 3;
        else
            kind = 1;
    }
    else
    {
        switch (block[0] & 0x7f)
        {
        case 0x01: case 0x02: case 0x03: case 0x04: case 0x05:
            kind = 1;
            break;
        case 0x20: case 0x21: case 0x22: case 0x23: case 0x24: case 0x27: case 0x28: case 0x29:
        case 0x2a: case 0x2c: case 0x2d: case 0x2e: case 0x30: case 0x31: case 0x32: case 0x33:
        case 0x34: case 0x35: case 0x36: case 0x37:
            kind = 2;
            break;
        case 0x40: case 0x41: case 0x42: case 0x43: case 0x44: case 0x50: case 0x51: case 0x52:
        case 0x55: case 0x56:
            kind = 1;
            break;
        case 0x60: case 0x61: case 0x62: case 0x63: case 0x64: case 0x65: case 0x66: case 0x67:
        case 0x68: case 0x69: case 0x6a:
            kind = 1;
            break;
        case 0x6b: kind = 6; break;
        case 0x6c: kind = 1; break;
        case 0x6d: kind = 1; break;
        case 0x6e: kind = 5; break;
        case 0x6f: kind = 4; break;
        case 0x78: case 0x79: case 0x7a: case 0x7b:
            kind = 1;
            break;
        case 0x7c: kind = 3; break;
        case 0x7d: case 0x7e: case 0x7f:
            kind = 1;
            break;
        default:
            kind = 0;
            break;
        }
    }
    return kind;
}

// 101088c5.  Signed 24-bit offset to the next block of the entry.
static int NextBlock(const unsigned char *block)
{
    return (ggeti(block + 1, 3) << 8) >> 8;
}

// 10108fe3.  Palette entries and first index; invalid ranges fall back to 1 << bits from 0.
static int PaletteRange(const unsigned char *palette, int *first, int bits, int type)
{
    int start = 0;
    int count;
    int width;
    int limit;
    if (type == 3 || type == 2 || type == 5 || type == 6 || type == 4)
    {
        start = ggeti(palette + 10, 2);
        if (start < 0 || start > 0xff)
            start = 0;
    }
    count = ggeti(palette + 8, 2);
    width = ggeti(palette + 4, 2) & 0xfff;
    limit = 0xff;
    if (bits > 0 && bits <= 8)
        limit = 1 << bits;
    if (count == 0)
        count = 1 << bits;
    if (count > 0x100)
        count = 0x100;
    if (count < 0 || count > limit || start < 0 || start > limit - 1 || start + count < 0 ||
        start + count > limit || (count != width && count * 3 != width))
    {
        start = 0;
        count = 1 << bits;
    }
    *first = start;
    return count;
}

// 101089ad.  RefPack decoder; returns the unpacked size from the stream header.
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

// 10108dc3.  Bytes of a block in memory (bitmaps: all mip levels, unpacked).
static int BlockSize(unsigned char *block, int type)
{
    int size = 0;
    int kind = BlockKind(block, type);
    int width, height, bits, levels, first, count;
    switch (kind)
    {
    case 1:
        width = ggeti(block + 4, 2) & 0xfff;
        height = ggeti(block + 6, 2) & 0xfff;
        if (kind != 1)
        {
            height = 1;
            if (type == 3)
                width = 0x100;
            else if (width > 0x100)
                width = 0x100;
        }
        bits = BitsPerPixel(block, type);
        levels = MipLevels(block, 0, type);
        size = 16;
        while (levels--)
        {
            if ((block[0] & 0x80) && IsBlockPacked(block + 0x10))
                size += 8 + width * height / 2;
            else
                size += ImageBytes(width, height, bits, type);
            if (width > 1)
                width >>= 1;
            if (height > 1)
                height >>= 1;
        }
        break;
    case 2:
        count = PaletteRange(block, &first, 8, type);
        bits = BitsPerPixel(block, type);
        size = RowBytes(count, bits, type);
        size = size + 16;
        break;
    case 3:
        size = ggeti(block + 4, 4) * 8 + 8;
        break;
    case 4:
        size = ggeti(block + 4, 4);
        size = size + 8;
        break;
    case 5:
        size = ggeti(block + 4, 4) * 4 + 8;
        break;
    case 6:
        size = 12;
        break;
    }
    return size;
}

// 101088f0.  Copies a block out of the file image; RefPack bitmaps are unpacked.
static unsigned char *CopyBlock(const unsigned char *block, int *size, int type)
{
    unsigned char *copy = 0;
    int bytes = BlockSize((unsigned char *)block, type);
    *size = bytes;
    if (bytes > 0 && (copy = (unsigned char *)galloc(bytes)) != 0)
    {
        if ((block[0] & 0x80) && IsRefPack(block + 0x10))
        {
            memcpy(copy, block, 16);
            RefUnpack(block + 0x10, 0, copy + 0x10);
            return copy;
        }
        memcpy(copy, block, bytes);
    }
    return copy;
}

// 10107f04.  Collects the blocks of one entry.  The chain is followed while the next block lies
// inside the file and is not another bitmap.  A missing palette uses the shared '!' palette; a
// missing bitmap gets a 256-entry ramp.  Returns 0 when the entry has no known block.
static int ShapeParse(unsigned char *entry, unsigned char *base, int length, unsigned char *sharedpalette,
                      FSHSHAPE *shape, int type)
{
    int blocksize = 0;
    int more = 0;
    unsigned char *block;
    unsigned char *copy;
    unsigned char *next;
    unsigned char *after;
    unsigned char *ramp;
    int offset, following, kind, i;
    shape->bitmap = 0;
    shape->palette = 0;
    shape->palettesize = 0;
    shape->points = 0;
    shape->comment = 0;
    shape->tpage = 0;
    shape->records = 0;
    shape->attributes = 0;
    shape->compression = 0;
    shape->size = 0;
    block = entry;
    do
    {
        copy = CopyBlock(block, &blocksize, type);
        if (copy)
        {
            shape->size += blocksize;
            switch (BlockKind(copy, type))
            {
            case 1:
                shape->bitmap = copy;
                if (IsRefPack(block + 0x10))
                    shape->compression = 2;
                else
                    shape->compression = IsBlockPacked(block + 0x10) ? 3 : 0;
                break;
            case 2:
                shape->palette = copy;
                shape->palettesize = blocksize;
                break;
            case 3:
                shape->points = copy;
                break;
            case 4:
                shape->comment = copy;
                break;
            case 5:
                shape->records = copy;
                break;
            case 6:
                shape->tpage = copy;
                break;
            default:
                gfree(copy);
                break;
            }
        }
        offset = NextBlock(block);
        next = block + offset;
        more = 0;
        if (offset != 0 && next > base && next < base + length && BlockKind(block, type) != 0 && type != 3 &&
            (kind = BlockKind(next, type)) != 0 && kind != 1)
        {
            following = NextBlock(next);
            after = next + following;
            if (following == 0 || (following != 0 && after > base && after < base + length))
            {
                more = 1;
                block = next;
            }
        }
    } while (more);
    if (type == 3 && shape->points == 0 && shape->bitmap != 0 && (copy = (unsigned char *)galloc(0x18)) != 0)
    {
        gputi(copy, 0x7d, 1);
        gputi(copy + 1, 0, 3);
        gputi(copy + 4, 2, 4);
        gputi(copy + 8, (signed char)entry[0], 4);
        gputi(copy + 0xc, (signed char)entry[1], 4);
        gputi(copy + 0x10, (signed char)entry[2], 4);
        gputi(copy + 0x14, (signed char)entry[3], 4);
        shape->points = copy;
    }
    if (!shape->bitmap && !shape->palette && !shape->points && !shape->tpage && !shape->records && !shape->comment)
    {
        more = 0;
    }
    else
    {
        if (!shape->palette)
        {
            shape->attributes |= 1;
            if (sharedpalette)
            {
                shape->palette = CopyBlock(sharedpalette, &blocksize, type);
                shape->palettesize = blocksize;
            }
        }
        if (!shape->bitmap)
        {
            shape->attributes |= 2;
            ramp = (unsigned char *)galloc(0x110);
            switch (type)
            {
            case 1: gputi(ramp, 0x41, 1); break;
            case 2: gputi(ramp, 0x7b, 1); break;
            case 3: gputi(ramp, 0x7b, 1); break;
            case 4: gputi(ramp, 0x66, 1); break;
            case 5: gputi(ramp, 0x56, 1); break;
            case 6: gputi(ramp, 0x02, 1); break;
            }
            gputi(ramp + 4, 0x100, 2);
            gputi(ramp + 6, 1, 2);
            gputi(ramp + 8, 0, 2);
            gputi(ramp + 10, 0, 2);
            gputi(ramp + 0xc, 0, 2);
            gputi(ramp + 0xe, 0, 2);
            for (i = 0; i < 0x100; ++i)
                ramp[0x10 + i] = (unsigned char)i;
            shape->bitmap = ramp;
        }
        if (!shape->tpage)
            shape->attributes |= 0x20;
        more = 1;
    }
    return more;
}

// 10107609.  Splits every bitmap with mip levels into one entry per level ("mm1 ", "mm2 ", …);
// later levels get a copy of the palette and no other blocks.  Dereferences table even when it
// is null (open of a file whose header cannot be read).
static FSHTABLE *ExpandMipmaps(FSHTABLE *table, int type)
{
    FSHTABLE *expanded = 0;
    FSHSHAPE *shape, *level;
    unsigned char *bitmap, *pixels, *copy;
    int count = 0;
    int i, l, levels, width, height, bits, bytes;
    for (i = 0; i < table->count; ++i)
    {
        shape = &table->shape[i];
        count += MipLevels(shape->bitmap, 0, type);
    }
    if (count == table->count)
        return table;
    expanded = (FSHTABLE *)galloc(count * sizeof(FSHSHAPE) + 4);
    if (!expanded)
        return table;
    expanded->count = count;
    count = 0;
    for (i = 0; i < table->count; ++i)
    {
        shape = &table->shape[i];
        bitmap = shape->bitmap;
        pixels = bitmap + 0x10;
        width = ggeti(bitmap + 4, 2);
        height = ggeti(bitmap + 6, 2);
        bits = BitsPerPixel(bitmap, type);
        levels = MipLevels(bitmap, 0, type);
        for (l = 0; l < levels; ++l)
        {
            level = &expanded->shape[count];
            *level = *shape;
            if (l > 0)
            {
                level->name[0] = 'm';
                level->name[1] = 'm';
                if (l < 10)
                {
                    level->name[2] = (char)(l + '0');
                    level->name[3] = ' ';
                }
                else
                {
                    level->name[2] = (char)(l / 10 + '0');
                    level->name[3] = (char)(l % 10 + '0');
                }
                if (shape->palette && shape->palettesize)
                {
                    level->palette = (unsigned char *)galloc(shape->palettesize);
                    memcpy(level->palette, shape->palette, shape->palettesize);
                }
                level->points = 0;
                level->pointssize = 0;
                level->comment = 0;
                level->commentsize = 0;
                level->tpage = 0;
                level->tpagesize = 0;
                level->records = 0;
                level->recordssize = 0;
            }
            bytes = (ImageBytes(width, height, bits, type) + 15) & ~15;
            copy = (unsigned char *)galloc(bytes + 0x10);
            level->bitmap = copy;
            level->bitmapsize = bytes + 0x10;
            memcpy(copy, bitmap, 16);
            gputi(copy + 4, width, 2);
            gputi(copy + 6, height, 2);
            gputi(copy + 0xe, 0, 2);
            gputi(copy + 0xc, 0, 2);
            memcpy(copy + 0x10, pixels, bytes);
            pixels += bytes;
            if (width > 1)
                width >>= 1;
            if (height > 1)
                height >>= 1;
            ++count;
        }
        gfree(shape->bitmap);
    }
    gfree(table);
    return expanded;
}

// 1010719f.  Loads all entries of a shape file (directory != 0) or a single shape.  For shape
// type 3 the header is 6 bytes with separate name and offset arrays and the bitmap header words
// are rotated in place.
static int ShapeLoad(GSTREAM *stream, FSHTABLE **result, int directory, int type, unsigned tag)
{
    unsigned char *data = 0;
    FSHTABLE *table = 0;
    unsigned char *sharedpalette = 0;
    unsigned char *entry;
    unsigned char header[16];
    unsigned word0, word1, word2;
    unsigned name;
    FSHSHAPE shape;
    int ok = 0;
    int length, headersize, count, pass, i, n;
    gseek(stream, 0);
    if (directory)
    {
        if (type == 3)
        {
            ok = gread(stream, header, 6) == 6;
            headersize = 6;
            count = ggeti(header + 4, 2);
        }
        else
        {
            ok = gread(stream, header, 16) == 16;
            headersize = 16;
            count = ggeti(header + 8, 4);
        }
        if (ok)
        {
            ok = 0;
            length = glen(stream);
            data = (unsigned char *)galloc(length - headersize);
            if (data)
            {
                if (gread(stream, data, length - headersize) == length - headersize)
                {
                    table = (FSHTABLE *)galloc(count * sizeof(FSHSHAPE) + 4);
                    if (table)
                    {
                        table->count = 0;
                        for (pass = 0; pass < 2; ++pass)
                            for (i = 0; i < count; ++i)
                            {
                                if (type == 3)
                                {
                                    entry = data + ggeti(data + (i + count) * 4, 4) + count * 8 + 6 - headersize;
                                    name = ggetm(data + i * 4, 4);
                                    if (pass == 0)
                                    {
                                        word0 = ((unsigned *)entry)[0];
                                        word1 = ((unsigned *)entry)[1];
                                        word2 = ((unsigned *)entry)[2];
                                        ((unsigned *)entry)[0] = ((unsigned *)entry)[3];
                                        ((unsigned *)entry)[1] = word0;
                                        ((unsigned *)entry)[2] = word1;
                                        ((unsigned *)entry)[3] = word2;
                                    }
                                }
                                else
                                {
                                    entry = data + ggeti(data + i * 8 + 4, 4) - headersize;
                                    name = ggetm(data + i * 8, 4);
                                }
                                if ((name >> 24) == '!')
                                {
                                    sharedpalette = entry;
                                    if (name != GTAG('!', 'x', '0', '0') && name != GTAG('!', 'e', 'g', '0') &&
                                        name != GTAG('!', 'c', 'g', '0') && type == 3)
                                    {
                                        entry[0] = 0x22;
                                        entry[1] = 0;
                                        entry[2] = 0;
                                        entry[3] = 0;
                                    }
                                }
                                if (pass == 1 &&
                                    ShapeParse(entry, data - headersize, length, sharedpalette, &shape, type))
                                {
                                    n = table->count;
                                    table->shape[n] = shape;
                                    gputm(table->shape[n].name, name, 4);
                                    ++table->count;
                                }
                            }
                    }
                }
                gfree(data);
            }
        }
    }
    else
    {
        data = (unsigned char *)galloc(glen(stream));
        if (data)
        {
            length = glen(stream);
            if (gread(stream, data, length) == length)
            {
                table = (FSHTABLE *)galloc(sizeof(FSHSHAPE) + 4);
                if (table)
                {
                    table->count = 0;
                    entry = data;
                    if (ggetm(entry, 4) == (int)tag)
                        entry += ggeti(entry + 0x1c, 4);
                    if (ShapeParse(entry, data, length, 0, &shape, type))
                    {
                        n = 0;
                        table->shape[n] = shape;
                        gputm(table->shape[n].name, 0, 4);
                        ++table->count;
                    }
                }
            }
            gfree(data);
        }
    }
    table = ExpandMipmaps(table, type);
    *result = table;
    if (table)
        ok = 1;
    return ok;
}

// 10107102.  Returns the number of entries (0 on failure).
int GCALL FSH_open(void **handle, GSTREAM *stream, const char *, int)
{
    FSHTABLE *table = 0;
    FSHHANDLE *fsh;
    int count = 0;
    if (ShapeLoad(stream, &table, 1, SHAPE_FSH, GTAG('S', 'H', 'P', 'I')))
    {
        fsh = (FSHHANDLE *)galloc(sizeof(FSHHANDLE));
        if (fsh)
        {
            count = table->count;
            memset(fsh, 0, sizeof(FSHHANDLE));
            fsh->count = count;
            fsh->tag = GTAG('S', 'H', 'P', 'I');
            fsh->size = sizeof(FSHHANDLE);
            fsh->stream = stream;
            fsh->table = table;
        }
        *handle = fsh;
    }
    return count;
}

// ---------------------------------------------------------------------------------------------
// Colour conversion (GCOLOUR is b, g, r, a)

// 1010a277.  1555 ARGB.
static GCOLOUR Colour1555(unsigned value)
{
    GCOLOUR colour;
    if (value)
    {
        colour.a = (unsigned char)(((value >> 15) & 1) * 0xff);
        colour.r = (unsigned char)((((value >> 10) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.g = (unsigned char)((((value >> 5) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.b = (unsigned char)(((value & 0x1f) * 0xff + 0x10) / 0x1f);
    }
    else
    {
        colour.a = 0;
        colour.b = colour.a;
        colour.g = colour.b;
        colour.r = colour.g;
    }
    return colour;
}

// 1010a309.  565 RGB, opaque.
static GCOLOUR Colour565(unsigned value)
{
    GCOLOUR colour;
    if (value)
    {
        colour.a = 0xff;
        colour.r = (unsigned char)((((value >> 11) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.g = (unsigned char)((((value >> 5) & 0x3f) * 0xff + 0x20) / 0x3f);
        colour.b = (unsigned char)(((value & 0x1f) * 0xff + 0x10) / 0x1f);
    }
    else
    {
        colour.a = 0;
        colour.b = colour.a;
        colour.g = colour.b;
        colour.r = colour.g;
    }
    return colour;
}

// 1010a38d.  1555 ABGR (red in the low bits); bit 15 gives alpha 0x80, else 0xff (0 for 0).
static GCOLOUR ColourBgr1555(unsigned value)
{
    GCOLOUR colour;
    if (value & 0x8000)
    {
        colour.b = (unsigned char)((((value >> 10) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.g = (unsigned char)((((value >> 5) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.r = (unsigned char)(((value & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.a = 0x80;
    }
    else if (value)
    {
        colour.b = (unsigned char)((((value >> 10) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.g = (unsigned char)((((value >> 5) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.r = (unsigned char)(((value & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.a = 0xff;
    }
    else
    {
        colour.a = 0;
        colour.b = colour.a;
        colour.g = colour.b;
        colour.r = colour.g;
    }
    return colour;
}

// 1010a47a.  1555 ABGR; entries without bit 15 are transparent black.
static GCOLOUR ColourBgr1555Masked(unsigned value)
{
    GCOLOUR colour;
    if (value & 0x8000)
    {
        colour.a = 0xff;
        colour.r = (unsigned char)(((value & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.g = (unsigned char)((((value >> 5) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour.b = (unsigned char)((((value >> 10) & 0x1f) * 0xff + 0x10) / 0x1f);
    }
    else
    {
        colour.a = 0;
        colour.b = colour.a;
        colour.g = colour.b;
        colour.r = colour.g;
    }
    return colour;
}

// 1010a504.  4444 ARGB.
static GCOLOUR Colour4444(unsigned value)
{
    GCOLOUR colour;
    if (value)
    {
        colour.a = (unsigned char)((((value >> 12) & 0xf) * 0xff + 8) / 0xf);
        colour.r = (unsigned char)((((value >> 8) & 0xf) * 0xff + 8) / 0xf);
        colour.g = (unsigned char)((((value >> 4) & 0xf) * 0xff + 8) / 0xf);
        colour.b = (unsigned char)(((value & 0xf) * 0xff + 8) / 0xf);
    }
    else
    {
        colour.a = 0;
        colour.b = colour.a;
        colour.g = colour.b;
        colour.r = colour.g;
    }
    return colour;
}

// 1010a5a2.  5551 RGBA (alpha in bit 0).
static GCOLOUR Colour5551(unsigned value)
{
    GCOLOUR colour;
    colour.r = (unsigned char)((((value >> 11) & 0x1f) * 0xff + 0x10) / 0x1f);
    colour.g = (unsigned char)((((value >> 6) & 0x1f) * 0xff + 0x10) / 0x1f);
    colour.b = (unsigned char)((((value >> 1) & 0x1f) * 0xff + 0x10) / 0x1f);
    if (value & 1)
        colour.a = 0xff;
    else
        colour.a = 0;
    return colour;
}

// 1010a61a.  8-bit grey in the high byte, alpha in the low byte.
static GCOLOUR ColourGreyAlpha(unsigned value)
{
    GCOLOUR colour;
    colour.b = (unsigned char)(value >> 8);
    colour.g = colour.b;
    colour.r = colour.g;
    colour.a = (unsigned char)(value & 0xff);
    return colour;
}

// ---------------------------------------------------------------------------------------------
// info()

// 1010a645.  0x7c block: count, then (x, y) pairs; no bound on the count.
static void ReadPoints(FSHTABLE *table, int frame, GINFO *info)
{
    unsigned char *block;
    int i;
    info->pointcount = 0;
    block = table->shape[frame].points;
    if (block)
    {
        info->pointcount = ggeti(block + 4, 4);
        for (i = 0; i < info->pointcount; ++i)
        {
            info->point[i][0] = ggeti(block + 8 + i * 8, 4);
            info->point[i][1] = ggeti(block + 0xc + i * 8, 4);
        }
    }
}

// 1010a6fa.  0x6e block: count (at most 32, compared unsigned), then 4-byte records.
static void ReadRecords(FSHTABLE *table, int frame, GINFO *info)
{
    unsigned char *block;
    int i;
    info->shaperecordcount = 0;
    block = table->shape[frame].records;
    if (block)
    {
        info->shaperecordcount = (unsigned)ggeti(block + 4, 4) > 32 ? 32 : ggeti(block + 4, 4);
        for (i = 0; i < info->shaperecordcount; ++i)
        {
            info->shaperecord[i].a = (signed char)block[8 + i * 4];
            info->shaperecord[i].b = (signed char)block[9 + i * 4];
            info->shaperecord[i].c = block[10 + i * 4];
            info->shaperecord[i].d = block[0xb + i * 4];
        }
    }
}

// 1010a805.  0x6f block: text at +8.
static void ReadComment(FSHTABLE *table, int frame, GINFO *info)
{
    unsigned char *block;
    info->comment[0] = 0;
    block = table->shape[frame].comment;
    if (block)
        strcpy(info->comment, (const char *)block + 8);
}

// 1010a85f.  0x6b block.
static void ReadTpage(FSHTABLE *table, int frame, GINFO *info)
{
    unsigned char *block = table->shape[frame].tpage;
    if (block)
    {
        info->tpage = ggeti(block + 4, 2);
        info->tpageclut = (unsigned char)ggeti(block + 6, 2);
        info->tpageextra = (unsigned char)ggeti(block + 8, 2);
    }
}

// 10109112.  Builds a GINFO_SIZE_SHAPE descriptor for entry `frame` (not checked against the
// entry count).  Palettes are converted to GCOLOUR; true-colour formats only set channel bits.
GINFO *GCALL FSH_info(void *handle, int frame)
{
    int type = SHAPE_FSH;
    GINFO *info = 0;
    FSHTABLE *table = ((FSHHANDLE *)handle)->table;
    FSHSHAPE *shape = &table->shape[frame];
    unsigned char *bitmap = shape->bitmap;
    unsigned char *palette;
    unsigned flags;
    int width, height, centrex, centrey, positionx, positiony;
    int bits, alphabits, colourbits, colours, first, count, clutx, cluty, i, channel;
    if (bitmap)
    {
        flags = ggeti(bitmap + 0xc, 2);
        width = ggeti(bitmap + 4, 2) & 0xfff;
        height = ggeti(bitmap + 6, 2) & 0xfff;
        centrex = (short)ggeti(bitmap + 8, 2);
        centrey = (short)ggeti(bitmap + 10, 2);
        positionx = (short)(ggeti(bitmap + 0xc, 2) << 4) >> 4;
        positiony = (short)(ggeti(bitmap + 0xe, 2) << 4) >> 4;
        if (flags & 0x8000)
            shape->attributes |= 0x800;
        if (flags & 0x4000)
            shape->attributes |= 0x1000;
        if (flags & 0x2000)
            shape->attributes |= 0x2000;
        bits = BitsPerPixel(bitmap, type);
        if (bits > 8)
            shape->attributes &= ~1u;
        switch (type)
        {
        case 1:
            alphabits = 1;
            colourbits = 5;
            if (bits == 24)
                colourbits = 8;
            break;
        case 4:
            alphabits = 1;
            colourbits = 8;
            if (bits == 16)
                colourbits = 5;
            break;
        case 5:
        case 6:
            alphabits = 1;
            colourbits = 5;
            break;
        default:
            alphabits = 1;
            colourbits = 8;
            break;
        }
        info = (GINFO *)galloc(sizeof(GINFO));
        if (info)
        {
            memset(info, 0, sizeof(GINFO));
            info->tag = GTAG('S', 'H', 'P', 'I');
            info->size = sizeof(GINFO);
            info->version = GINFO_VERSION;
            info->frames = frame;
            info->width = width;
            info->height = height;
            info->attributes = shape->attributes;
            info->compression = shape->compression;
            info->shapesize = shape->size;
            info->unknown_430 = 100;
            info->alphabits = alphabits;
            info->redbits = colourbits;
            info->greenbits = colourbits;
            info->bluebits = colourbits;
            info->centrex = centrex;
            info->centrey = centrey;
            info->positionx = positionx;
            info->positiony = positiony;
            info->pointcount = 0;
            gputm(info->name, ggetm(table->shape[frame].name, 4), 4);
            for (i = 3; i >= 0 && info->name[i] == ' '; --i)
                info->name[i] = 0;
            ReadPoints(table, frame, info);
            ReadComment(table, frame, info);
            ReadRecords(table, frame, info);
            ReadTpage(table, frame, info);
            if (bits < 9)
            {
                if (bits == 0)
                    bits = 8;
                info->bpp = 8;
                info->depth = bits;
                palette = table->shape[frame].palette;
                colours = 1 << bits;
                if (!palette)
                {
                    if (bitmap[0] == 'b')
                    {
                        info->alphabits = 1;
                        info->redbits = 3;
                        info->greenbits = 3;
                        info->bluebits = 3;
                        info->numcolours = colours;
                        for (i = 0; i < colours; ++i)
                        {
                            info->colour[i].a = (unsigned char)((i & 1) * 0xff);
                            info->colour[i].r = (unsigned char)(((i >> 1) * 0xff) / ((colours >> 1) - 1));
                            info->colour[i].g = (unsigned char)(((i >> 1) * 0xff) / ((colours >> 1) - 1));
                            info->colour[i].b = (unsigned char)(((i >> 1) * 0xff) / ((colours >> 1) - 1));
                        }
                    }
                    else if (bitmap[0] == 'e')
                    {
                        info->alphabits = 4;
                        info->redbits = 4;
                        info->greenbits = 4;
                        info->bluebits = 4;
                        info->numcolours = colours;
                        for (i = 0; i < colours; ++i)
                        {
                            info->colour[i].a = (unsigned char)(((i & 0xf) * 0xff) / 0xf);
                            info->colour[i].r = (unsigned char)(((i >> 4) * 0xff) / ((colours >> 4) - 1));
                            info->colour[i].g = (unsigned char)(((i >> 4) * 0xff) / ((colours >> 4) - 1));
                            info->colour[i].b = (unsigned char)(((i >> 4) * 0xff) / ((colours >> 4) - 1));
                        }
                    }
                    else
                    {
                        info->numcolours = colours;
                        info->alphabits = 0;
                        if (colours > 1)
                            for (i = 0; i < colours; ++i)
                            {
                                info->colour[i].a = 0xff;
                                info->colour[i].r = (unsigned char)((i * 0xff) / (colours - 1));
                                info->colour[i].g = (unsigned char)((i * 0xff) / (colours - 1));
                                info->colour[i].b = (unsigned char)((i * 0xff) / (colours - 1));
                            }
                    }
                }
                else
                {
                    cluty = 0;
                    clutx = 0;
                    if (type == 1)
                    {
                        clutx = ggeti(palette + 0xc, 2);
                        cluty = ggeti(palette + 0xe, 2);
                    }
                    count = PaletteRange(palette, &first, bits, type);
                    info->numcolours = count + first;
                    info->clutx = clutx;
                    info->cluty = cluty;
                    switch (palette[0])
                    {
                    case 0x20:
                        info->alphabits = 1;
                        info->redbits = 5;
                        info->greenbits = 5;
                        info->bluebits = 5;
                        for (i = 0; i < count; ++i)
                            info->colour[first + i] = ColourBgr1555Masked(ggeti(palette + i * 2 + 0x10, 2));
                        break;
                    case 0x21:
                        info->alphabits = 8;
                        info->bluebits = 8;
                        info->greenbits = 8;
                        info->redbits = 8;
                        for (i = 0; i < count; ++i)
                        {
                            info->colour[first + i].r = palette[i * 4 + 0x10];
                            info->colour[first + i].g = palette[i * 4 + 0x11];
                            info->colour[first + i].b = palette[i * 4 + 0x12];
                            info->colour[first + i].a = palette[i * 4 + 0x13];
                        }
                        break;
                    case 0x22:
                        info->alphabits = 0;
                        info->redbits = 6;
                        info->greenbits = 6;
                        info->bluebits = 6;
                        for (i = 0; i < count; ++i)
                        {
                            info->colour[first + i].a = i != 0xff ? 0xff : 0;
                            info->colour[first + i].r = (unsigned char)((palette[i * 3 + 0x10] * 0xff + 0x20) / 0x3f);
                            info->colour[first + i].g = (unsigned char)((palette[i * 3 + 0x11] * 0xff + 0x20) / 0x3f);
                            info->colour[first + i].b = (unsigned char)((palette[i * 3 + 0x12] * 0xff + 0x20) / 0x3f);
                        }
                        break;
                    case 0x23:
                        info->alphabits = 1;
                        info->redbits = 5;
                        info->greenbits = 5;
                        info->bluebits = 5;
                        for (i = 0; i < count; ++i)
                            info->colour[first + i] = ColourBgr1555(ggeti(palette + i * 2 + 0x10, 2));
                        break;
                    case 0x24:
                        info->bluebits = 8;
                        info->greenbits = 8;
                        info->redbits = 8;
                        info->alphabits = 0;
                        for (i = 0; i < count; ++i)
                        {
                            info->colour[first + i].a = i != 0xff ? 0xff : 0;
                            info->colour[first + i].r = palette[i * 3 + 0x10];
                            info->colour[first + i].g = palette[i * 3 + 0x11];
                            info->colour[first + i].b = palette[i * 3 + 0x12];
                        }
                        break;
                    case 0x27:
                        info->alphabits = 1;
                        info->redbits = 5;
                        info->greenbits = 5;
                        info->bluebits = 5;
                        for (i = 0; i < count; ++i)
                            info->colour[first + i] = Colour5551(ggeti(palette + i * 2 + 0x10, 2));
                        break;
                    case 0x28:
                        info->alphabits = 8;
                        info->redbits = 8;
                        info->greenbits = 8;
                        info->bluebits = 8;
                        for (i = 0; i < count; ++i)
                            info->colour[first + i] = ColourGreyAlpha(ggeti(palette + i * 2 + 0x10, 2));
                        break;
                    case 0x29:
                    case 0x31:
                        info->alphabits = 0;
                        info->redbits = 5;
                        info->greenbits = 6;
                        info->bluebits = 5;
                        for (i = 0; i < count; ++i)
                            info->colour[first + i] = Colour565(ggeti(palette + i * 2 + 0x10, 2));
                        break;
                    case 0x2a:
                    case 0x33:
                        info->alphabits = 8;
                        info->redbits = 8;
                        info->greenbits = 8;
                        info->bluebits = 8;
                        for (i = 0; i < count; ++i)
                        {
                            info->colour[first + i].b = palette[i * 4 + 0x10];
                            info->colour[first + i].g = palette[i * 4 + 0x11];
                            info->colour[first + i].r = palette[i * 4 + 0x12];
                            info->colour[first + i].a = palette[i * 4 + 0x13];
                        }
                        break;
                    case 0x2c:
                        info->alphabits = 8;
                        info->redbits = 5;
                        info->greenbits = 6;
                        info->bluebits = 5;
                        for (i = 0; i < count; ++i)
                        {
                            info->colour[first + i] = Colour565(ggeti(palette + i * 4 + 0x10, 2));
                            info->colour[first + i].a = palette[i * 4 + 0x13];
                        }
                        break;
                    case 0x2d:
                    case 0x30:
                        info->alphabits = 1;
                        info->redbits = 5;
                        info->greenbits = 5;
                        info->bluebits = 5;
                        for (i = 0; i < count; ++i)
                            info->colour[first + i] = Colour1555(ggeti(palette + i * 2 + 0x10, 2));
                        break;
                    case 0x2e:
                        info->alphabits = 8;
                        info->redbits = 5;
                        info->greenbits = 5;
                        info->bluebits = 5;
                        for (i = 0; i < count; ++i)
                        {
                            info->colour[first + i] = Colour1555(ggeti(palette + i * 4 + 0x10, 2));
                            info->colour[first + i].a = palette[i * 4 + 0x13];
                        }
                        break;
                    case 0x32:
                        info->alphabits = 4;
                        info->redbits = 4;
                        info->greenbits = 4;
                        info->bluebits = 4;
                        for (i = 0; i < count; ++i)
                            info->colour[first + i] = Colour4444(ggeti(palette + i * 2 + 0x10, 2));
                        break;
                    }
                }
            }
            else
            {
                info->bpp = 32;
                info->depth = bits;
                info->numcolours = 0;
                if (bits < 16)
                {
                    info->bluebits = 5;
                    info->greenbits = 5;
                    info->redbits = 5;
                    info->alphabits = 1;
                }
                if (bits == 16)
                {
                    if (type == 4)
                    {
                        info->bluebits = 8;
                        info->greenbits = 8;
                        info->redbits = 8;
                        info->alphabits = 8;
                    }
                    else if (type == 2)
                    {
                        if (bitmap[0] == 'm')
                        {
                            info->alphabits = 4;
                            info->greenbits = 4;
                            info->bluebits = 4;
                            info->redbits = 4;
                        }
                        else
                        {
                            info->bluebits = 5;
                            info->redbits = 5;
                            info->greenbits = 6;
                            info->alphabits = 0;
                        }
                    }
                    else if (type == 5)
                    {
                        if (bitmap[0] == 'R')
                        {
                            info->alphabits = 4;
                            info->greenbits = 4;
                            info->bluebits = 4;
                            info->redbits = 4;
                        }
                        else
                        {
                            info->bluebits = 5;
                            info->redbits = 5;
                            info->greenbits = 6;
                            info->alphabits = 0;
                        }
                    }
                }
                if (bits > 16)
                {
                    if (bits / 3 > 8)
                        channel = 8;
                    else
                        channel = bits / 3;
                    info->bluebits = channel;
                    info->greenbits = channel;
                    info->redbits = channel;
                    info->alphabits = bits - channel * 3;
                }
            }
        }
    }
    return info;
}

// ---------------------------------------------------------------------------------------------
// read()

// 1010b5d6.  Linear index of pixel (x, y) in a swizzled (bit-interleaved) image.
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

// 1010b173.  One 8-byte colour block into 4x4 GCOLOUR (rows `stride` bytes apart).
static void UnpackBlock(GCOLOUR *destination, int stride, const unsigned char *block)
{
    GCOLOUR colour[4];
    unsigned colour0 = ggeti(block, 2);
    unsigned colour1 = ggeti(block + 2, 2);
    int row;
    if (colour0 > colour1)
    {
        colour[0].a = 0xff;
        colour[0].r = (unsigned char)((((colour0 >> 11) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[0].g = (unsigned char)((((colour0 >> 5) & 0x3f) * 0xff + 0x20) / 0x3f);
        colour[0].b = (unsigned char)(((colour0 & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[1].a = 0xff;
        colour[1].r = (unsigned char)((((colour1 >> 11) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[1].g = (unsigned char)((((colour1 >> 5) & 0x3f) * 0xff + 0x20) / 0x3f);
        colour[1].b = (unsigned char)(((colour1 & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[2].a = 0xff;
        colour[2].r = (unsigned char)((colour[0].r * 2 + colour[1].r) / 3);
        colour[2].g = (unsigned char)((colour[0].g * 2 + colour[1].g) / 3);
        colour[2].b = (unsigned char)((colour[0].b * 2 + colour[1].b) / 3);
        colour[3].a = 0xff;
        colour[3].r = (unsigned char)((colour[0].r + colour[1].r * 2) / 3);
        colour[3].g = (unsigned char)((colour[0].g + colour[1].g * 2) / 3);
        colour[3].b = (unsigned char)((colour[0].b + colour[1].b * 2) / 3);
    }
    else
    {
        colour[0].a = 0xff;
        colour[0].r = (unsigned char)((((colour0 >> 11) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[0].g = (unsigned char)((((colour0 >> 5) & 0x3f) * 0xff + 0x20) / 0x3f);
        colour[0].b = (unsigned char)(((colour0 & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[1].a = 0xff;
        colour[1].r = (unsigned char)((((colour1 >> 11) & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[1].g = (unsigned char)((((colour1 >> 5) & 0x3f) * 0xff + 0x20) / 0x3f);
        colour[1].b = (unsigned char)(((colour1 & 0x1f) * 0xff + 0x10) / 0x1f);
        colour[2].a = 0xff;
        colour[2].r = (unsigned char)((colour[0].r + colour[1].r) / 2);
        colour[2].g = (unsigned char)((colour[0].g + colour[1].g) / 2);
        colour[2].b = (unsigned char)((colour[0].b + colour[1].b) / 2);
        colour[3].b = 0;
        colour[3].g = colour[3].b;
        colour[3].r = colour[3].g;
        colour[3].a = colour[3].r;
    }
    for (row = 0; row < 4; ++row)
    {
        destination[0] = colour[block[row + 4] & 3];
        destination[1] = colour[(block[row + 4] >> 2) & 3];
        destination[2] = colour[(block[row + 4] >> 4) & 3];
        destination[3] = colour[block[row + 4] >> 6];
        destination = (GCOLOUR *)((unsigned char *)destination + stride);
    }
}

// 1010b0e4 (stdcall in the original).  The 18fb stream: 3-byte big-endian output size at +2,
// colour blocks from +8; each block becomes 64 bytes of 4x4 GCOLOUR.
static int GCALL UnpackBlocks(const unsigned char *source, int *blocks, unsigned char *destination)
{
    int size = ggetm(source + 2, 3);
    int done;
    if (blocks)
        *blocks = size / 8;
    source += 8;
    for (done = 0; done < size; done += 0x40)
    {
        UnpackBlock((GCOLOUR *)destination, 0x10, source);
        destination += 0x40;
        source += 8;
    }
    return size;
}

// 1010b4da.  4x4 blocks into rows.  The source advances only for the rows that are copied,
// so partial blocks at the bottom edge shift the blocks after them.
static void PlaceBlocks(int width, int height, int rowbytes, const unsigned char *source, unsigned char *destination)
{
    int y, x, row, rows, columns;
    unsigned char *line;
    for (y = 0; y < height; y += 4)
    {
        if (height - y < 5)
            rows = height - y;
        else
            rows = 4;
        line = destination + y * rowbytes;
        for (x = 0; x < width; x += 4)
        {
            if (width - x < 5)
                columns = width - x;
            else
                columns = 4;
            for (row = 0; row < rows; ++row)
            {
                memcpy(line + row * rowbytes, source, columns * 4);
                source += 16;
            }
            line += 0x10;
        }
    }
}

// 1010a937.  Decodes the first image of a bitmap block into 8-bit indices or 32-bit GCOLOUR.
static int ReadBitmap(unsigned char *bitmap, unsigned char *pixels, int rowbytes, int type)
{
    int swizzled = 0;
    int bits = BitsPerPixel(bitmap, type);
    int width = ggeti(bitmap + 4, 2) & 0xfff;
    int height = ggeti(bitmap + 6, 2) & 0xfff;
    int code = ggeti(bitmap, 1);
    unsigned char *data = bitmap + 0x10;
    int sourcerow = RowBytes(width, bits, type);
    int flags, pixelbytes, line, sourceline, y, x, at, source, index;
    unsigned value;
    unsigned char *buffer;
    unsigned paddedwidth, paddedheight;
    if ((bitmap[0] & 0x80) && IsBlockPacked(data))
    {
        paddedwidth = (width + 3) & ~3u;
        paddedheight = (height + 3) & ~3u;
        buffer = (unsigned char *)galloc(paddedwidth * paddedheight * 4);
        if (buffer)
        {
            gputm(data + 2, paddedwidth * paddedheight * 4, 3);
            UnpackBlocks(data, 0, buffer);
            PlaceBlocks(width, height, rowbytes, buffer, pixels);
            gfree(buffer);
        }
        return 1;
    }
    flags = ggeti(bitmap + 0xc, 2);
    if ((flags & 0x2000) && !(flags & 0x1000) && (width & (width - 1)) == 0 && (height & (height - 1)) == 0)
        swizzled = 1;
    pixelbytes = bits > 8 ? 4 : 1;
    line = 0;
    sourceline = 0;
    for (y = 0; y < height; ++y)
    {
        at = line;
        source = sourceline;
        for (x = 0; x < width; ++x)
        {
            if (swizzled)
            {
                index = SwizzleIndex(x, y, width, height);
                at = index / width * rowbytes + index % width * pixelbytes;
            }
            switch (code & 0x7f)
            {
            case 0x01: case 0x40: case 0x55: case 0x61: case 0x62: case 0x63: case 0x7a:
                if (bitmap[0] == 0x40 || bitmap[0] == 0x01 || bitmap[0] == 0x7a || bitmap[0] == 0x55)
                {
                    value = data[source];
                    if (x & 1)
                    {
                        value >>= 4;
                        ++source;
                    }
                }
                else
                {
                    value = data[source];
                    if (x & 1)
                        ++source;
                    else
                        value >>= 4;
                }
                pixels[at] = (unsigned char)(value & 0xf);
                ++at;
                break;
            case 0x02: case 0x41: case 0x56: case 0x64: case 0x65: case 0x66: case 0x7b:
                pixels[at] = data[source];
                ++at;
                ++source;
                break;
            case 0x03:
                *(GCOLOUR *)(pixels + at) = ColourBgr1555Masked(ggeti(data + source, 2));
                source += 2;
                at += 4;
                break;
            case 0x04: case 0x43:
                pixels[at + 3] = 0xff;
                pixels[at + 2] = data[source];
                pixels[at + 1] = data[source + 1];
                pixels[at] = data[source + 2];
                source += 3;
                at += 4;
                break;
            case 0x05:
                pixels[at + 2] = data[source];
                pixels[at + 1] = data[source + 1];
                pixels[at] = data[source + 2];
                pixels[at + 3] = data[source + 3];
                source += 4;
                at += 4;
                break;
            case 0x42:
                *(GCOLOUR *)(pixels + at) = ColourBgr1555(ggeti(data + source, 2));
                source += 2;
                at += 4;
                break;
            case 0x44: case 0x60: case 0x79:
                value = data[source];
                if ((x & 7) == 7)
                    ++source;
                else
                    value >>= 7 - (x & 7);
                pixels[at] = (unsigned char)(value & 1);
                ++at;
                break;
            case 0x50: case 0x7e:
                *(GCOLOUR *)(pixels + at) = Colour1555(ggeti(data + source, 2));
                source += 2;
                at += 4;
                break;
            case 0x51: case 0x78:
                *(GCOLOUR *)(pixels + at) = Colour565(ggeti(data + source, 2));
                source += 2;
                at += 4;
                break;
            case 0x52: case 0x6d:
                *(GCOLOUR *)(pixels + at) = Colour4444(ggeti(data + source, 2));
                source += 2;
                at += 4;
                break;
            case 0x67:
                *(GCOLOUR *)(pixels + at) = ColourGreyAlpha(ggeti(data + source, 2));
                source += 2;
                at += 4;
                break;
            case 0x68:
                *(GCOLOUR *)(pixels + at) = Colour5551(ggeti(data + source, 2));
                source += 2;
                at += 4;
                break;
            case 0x6a:
                pixels[at + 2] = data[source];
                pixels[at + 1] = data[source + 1];
                pixels[at] = data[source + 2];
                pixels[at + 3] = data[source + 3];
                source += 4;
                at += 4;
                break;
            case 0x7d:
                pixels[at + 3] = data[source + 3];
                pixels[at + 2] = data[source + 2];
                pixels[at + 1] = data[source + 1];
                pixels[at] = data[source];
                source += 4;
                at += 4;
                break;
            case 0x7f:
                pixels[at + 3] = 0xff;
                pixels[at + 2] = data[source + 2];
                pixels[at + 1] = data[source + 1];
                pixels[at] = data[source];
                source += 3;
                at += 4;
                break;
            }
        }
        sourceline += sourcerow;
        line += rowbytes;
    }
    return 1;
}

// 1010a8d3.
int GCALL FSH_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    int ok = 0;
    unsigned char *bitmap;
    if (info->frames != -1 &&
        (bitmap = ((FSHHANDLE *)handle)->table->shape[info->frames].bitmap) != 0)
        ok = ReadBitmap(bitmap, (unsigned char *)pixels, rowbytes, SHAPE_FSH);
    return ok;
}

// 1010b6cc.
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
        if (table->shape[i].tpage)
            gfree(table->shape[i].tpage);
        if (table->shape[i].comment)
            gfree(table->shape[i].comment);
        if (table->shape[i].records)
            gfree(table->shape[i].records);
        table->shape[i].bitmap = 0;
        table->shape[i].palette = 0;
        table->shape[i].points = 0;
        table->shape[i].tpage = 0;
        table->shape[i].comment = 0;
        table->shape[i].records = 0;
    }
    gfree(table);
}

// 1010b692.
int GCALL FSH_close(void *handle)
{
    if (handle)
    {
        FreeTable(((FSHHANDLE *)handle)->table);
        gfree(handle);
    }
    return 1;
}
