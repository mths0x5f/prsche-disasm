// "Portable Network Graphics" module 1.06 (Kaz Okuda): GIMEX module 57.
// gimme.dll 3a43b0f6…, entry points about 1001c830, is 1001c9fb, open 1001ca69, info 1001cc34, read 1001d094, close 1001d42a,
// wopen 1001bf70, write 1001bfc6, wclose 1001c809.  about(), is() and the reader (open, info, read,
// close and helpers 1001cbcd, 1001cc13, 1001cc18, 1001cc26, 1001d1d3) are recovered on top of the
// unmodified libpng 1.0.3 (png/) and zlib 1.1.3 (zlib/); the writer entry points are recovery
// boundaries (boundary.h).

#include <setjmp.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

extern "C"
{
#include "png/png.h"
}

#include "boundary.h"

// 1001c830.
GABOUT *PNG_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 'P', 'N', 'G');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xa3d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG(0, 'P', 'N', 'G');
        strcpy(about->extension[0], ".png");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.06");
        strcpy(about->shortname, "PNG");
        strcpy(about->longname, "PNG");
        strcpy(about->name, "Portable Network Graphics");
    }
    return about;
}

// 1001c9fb.  100 for the 8-byte PNG signature, 50 when only its first 4 bytes match.
int GCALL PNG_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char signature[8];
    gseek(stream, 0);
    gread(stream, signature, 8);
    score = png_check_sig(signature, 8);
    if (score == 0)
    {
        score = png_check_sig(signature, 4);
        if (score)
            score = 50;
    }
    else
        score = 100;
    return score;
}

// ---------------------------------------------------------------------------------------------
// Reader on top of libpng 1.0.3.  The handle keeps the png_struct and png_info that open() used
// for png_read_info; read() builds a second pair of its own and decodes from the start.

struct PNGSTATE
{
    png_structp png;             // +0x00
    png_infop info;              // +0x04
};

// Handle returned by open() (0x18 bytes, cleared).
struct PNGHANDLE
{
    unsigned tag;                // +0x00 0x00504e47
    int size;                    // +0x04 sizeof(PNGHANDLE)
    int count;                   // +0x08 frames: always 1
    int unknown_0c;              // +0x0c
    GSTREAM *stream;             // +0x10
    PNGSTATE *state;             // +0x14
};

static_assert(sizeof(PNGHANDLE) == 0x18 && sizeof(PNGSTATE) == 8, "PNGHANDLE layout");
static_assert(offsetof(png_info, palette) == 0x10 && offsetof(png_info, num_palette) == 0x14 &&
                  offsetof(png_info, bit_depth) == 0x18 && offsetof(png_info, color_type) == 0x19,
              "libpng 1.0.3 png_info layout");
// png_create_struct_2 (10199663) allocates 0xb8 for png_info and 0x21c for png_struct: the sizes
// of this configuration (PNG_USER_MEM_SUPPORTED adds the three memory fields).
static_assert(sizeof(png_info) == 0xb8 && sizeof(png_struct) == 0x21c, "libpng 1.0.3 configuration");

// GINFO +0x287c: horizontal resolution as a float (see bmp.cpp, pcx.cpp).
static float *PngResolution(GINFO *info)
{
    return (float *)((unsigned char *)info + 0x287c);
}

// 1001cbcd.  png_rw_ptr over the GSTREAM given to png_set_read_fn.
static void PngReadData(png_structp png, png_bytep data, png_size_t length)
{
    GSTREAM *stream = (GSTREAM *)png_get_io_ptr(png);
    png_size_t count = gread(stream, data, length);
    if (count != length)
        png_error(png, "Read Error");
}

// 1001cc13.  Warnings are dropped; errors use libpng's default (message, then longjmp).
static void PngWarning(png_structp, png_const_charp)
{
}

// 1001cc18.
static png_voidp PngMalloc(png_structp, png_size_t size)
{
    return galloc(size);
}

// 1001cc26.  libpng 1.0.3 declares png_free_ptr's block argument as png_structp.
static void PngFree(png_structp, png_structp memory)
{
    gfree(memory);
}

// 1001ca69.  A failed allocation leaks what was allocated before it, as in the original.
int GCALL PNG_open(void **handle, GSTREAM *stream, const char *, int)
{
    int ok = 0;
    PNGHANDLE *png = (PNGHANDLE *)galloc(sizeof(PNGHANDLE));
    if (png)
    {
        memset(png, 0, sizeof(PNGHANDLE));
        png->state = (PNGSTATE *)galloc(sizeof(PNGSTATE));
        if (png->state)
        {
            PNGSTATE *state = png->state;
            state->png = png_create_read_struct_2(PNG_LIBPNG_VER_STRING, 0, 0, PngWarning, 0, PngMalloc, PngFree);
            if (state->png)
            {
                state->info = png_create_info_struct(state->png);
                if (state->info)
                {
                    png_set_read_fn(state->png, stream, PngReadData);
                    if (setjmp(state->png->jmpbuf) == 0)
                    {
                        gseek(stream, 0);
                        png_read_info(state->png, state->info);
                        png->count = 1;
                        png->unknown_0c = 0;
                        png->tag = GTAG(0, 'P', 'N', 'G');
                        png->size = sizeof(PNGHANDLE);
                        png->stream = stream;
                        *handle = png;
                        ok = png->count;
                    }
                    else
                        png_destroy_read_struct(&state->png, &state->info, 0);
                }
                else
                    png_destroy_read_struct(&state->png, 0, 0);
            }
        }
    }
    return ok;
}

// 1001cc34.  Colour type 0 and 3 below 8 bits stay 8-bit images (depth min(bit depth, 8)), with a
// grey ramp or the PLTE palette (tRNS as alpha); colour type 2 is 24-bit, types 4 and 6 are
// 32-bit, all three in 32-bit pixels.  Original behaviour kept: the tEXt pointer of
// png_get_text is stored over the first 4 bytes of GINFO.comment, and a palette image without
// PLTE entries yields no descriptor.
GINFO *GCALL PNG_info(void *handle, int)
{
    PNGHANDLE *png = (PNGHANDLE *)handle;
    GINFO *info = 0;
    int depth = 32;
    int ok = 1;
    int alpha = 0;
    int bits;
    int textcount;
    int i;

    PNGSTATE *state = png->state;
    info = (GINFO *)galloc(GINFO_SIZE_LEGACY);
    if (info)
    {
        memset(info, 0, GINFO_SIZE_LEGACY);
        switch (state->info->color_type)
        {
        case PNG_COLOR_TYPE_GRAY:
        case PNG_COLOR_TYPE_PALETTE:
            depth = state->info->bit_depth < 8 ? state->info->bit_depth : 8;
            break;
        case PNG_COLOR_TYPE_RGB:
            depth = 24;
            break;
        case PNG_COLOR_TYPE_GRAY_ALPHA:
        case PNG_COLOR_TYPE_RGB_ALPHA:
            depth = 32;
            break;
        }
        if (state->info->color_type == PNG_COLOR_TYPE_PALETTE)
            bits = 8;
        else
            bits = state->info->bit_depth;
        if (state->info->color_type & PNG_COLOR_MASK_ALPHA)
            alpha = 1;
        info->tag = GTAG(0, 'P', 'N', 'G');
        info->size = GINFO_SIZE_LEGACY;
        info->version = GINFO_VERSION;
        info->frames = 0;
        info->width = state->info->width;
        info->height = state->info->height;
        info->shapesize = 0;
        info->attributes = 0;
        info->compression = 0;
        info->unknown_430 = 100;
        info->alphabits = alpha ? bits : 0;
        info->redbits = bits;
        info->greenbits = bits;
        info->bluebits = bits;
        info->centrex = 0;
        info->centrey = 0;
        info->positionx = 0;
        info->positiony = 0;
        info->pointcount = 0;
        info->name[0] = 0;
        info->bpp = depth > 8 ? 32 : 8;
        info->depth = depth;
        info->numcolours = 0;
        png_get_text(state->png, state->info, (png_textp *)info->comment, &textcount);
        *PngResolution(info) =
            (float)(__int64)png_get_x_pixels_per_meter(state->png, state->info) * 0.03937008f;
        if (depth <= 8)
        {
            if (state->info->color_type == PNG_COLOR_TYPE_GRAY)
            {
                info->numcolours = 1 << depth;
                for (i = 0; i < info->numcolours; i++)
                {
                    unsigned char grey = (unsigned char)(i * 255 / (info->numcolours - 1));
                    info->colour[i].r = grey;
                    info->colour[i].g = grey;
                    info->colour[i].b = grey;
                    info->colour[i].a = 0xff;
                }
            }
            else
            {
                info->numcolours = state->info->num_palette;
                if (state->info->num_palette)
                {
                    png_bytep trans = 0;
                    png_color_16p transvalues = 0;
                    int transcount = 0;
                    if (png_get_tRNS(state->png, state->info, &trans, &transcount, &transvalues))
                        info->alphabits = 8;
                    else
                        trans = 0;
                    for (i = 0; i < info->numcolours; i++)
                    {
                        info->colour[i].r = state->info->palette[i].red;
                        info->colour[i].g = state->info->palette[i].green;
                        info->colour[i].b = state->info->palette[i].blue;
                        if (trans && i < transcount)
                            info->colour[i].a = trans[i];
                        else
                            info->colour[i].a = 0xff;
                    }
                }
                else
                    ok = 0;
            }
        }
        if (!ok)
        {
            gfree(info);
            info = 0;
        }
    }
    return info;
}

// 1001d1d3.  32-bit descriptors decode into a temporary buffer (height x 3 x rowbytes bytes) and
// convert RGB and RGBA rows to B, G, R, A; anything else decodes straight into the pixels.
// Sets its own longjmp target; a libpng error returns 0.
static int PngReadImage(GINFO *ginfo, png_infop info, png_structp png, unsigned char *pixels, int rowbytes)
{
    int y, x;
    if (setjmp(png->jmpbuf))
        return 0;
    png_bytep *rows = (png_bytep *)galloc(ginfo->height * 4);
    if (rows)
    {
        if (ginfo->bpp == 32)
        {
            png_bytep buffer = (png_bytep)galloc(ginfo->height * 3 * info->rowbytes);
            if (buffer)
            {
                for (y = 0; y < ginfo->height; y++)
                    rows[y] = buffer + info->rowbytes * y;
                png_read_image(png, rows);
                for (y = 0; y < ginfo->height; y++)
                {
                    png_bytep s = rows[y];
                    unsigned char *d = pixels + rowbytes * y;
                    if (info->color_type == PNG_COLOR_TYPE_RGB)
                    {
                        for (x = 0; x < ginfo->width; x++)
                        {
                            d[2] = *s++;
                            d[1] = *s++;
                            d[0] = *s++;
                            d[3] = 0xff;
                            d += 4;
                        }
                    }
                    else if (info->color_type == PNG_COLOR_TYPE_RGB_ALPHA)
                    {
                        for (x = 0; x < ginfo->width; x++)
                        {
                            d[2] = *s++;
                            d[1] = *s++;
                            d[0] = *s++;
                            d[3] = *s++;
                            d += 4;
                        }
                    }
                }
                gfree(buffer);
            }
        }
        else
        {
            for (y = 0; y < ginfo->height; y++)
                rows[y] = pixels + rowbytes * y;
            png_read_image(png, rows);
        }
        gfree(rows);
    }
    return 1;
}

// 1001d094.  16-bit samples are stripped to 8, sub-byte samples unpacked to bytes, grey+alpha
// expanded to RGBA; palettes stay indices.
int GCALL PNG_read(void *handle, GINFO *ginfo, void *pixels, int rowbytes)
{
    PNGHANDLE *handlepng = (PNGHANDLE *)handle;
    int ok = 0;
    png_structp png = png_create_read_struct_2(PNG_LIBPNG_VER_STRING, 0, 0, PngWarning, 0, PngMalloc, PngFree);
    if (png)
    {
        png_infop info = png_create_info_struct(png);
        if (info)
        {
            png_set_read_fn(png, handlepng->stream, PngReadData);
            if (setjmp(png->jmpbuf) == 0)
            {
                gseek(handlepng->stream, 0);
                png_read_info(png, info);
                if (info->bit_depth == 16)
                    png_set_strip_16(png);
                if (info->bit_depth < 8)
                    png_set_packing(png);
                if (info->color_type == PNG_COLOR_TYPE_GRAY_ALPHA)
                    png_set_gray_to_rgb(png);
                png_read_update_info(png, info);
                ok = PngReadImage(ginfo, info, png, (unsigned char *)pixels, rowbytes);
            }
            else
                ok = 0;
            png_destroy_read_struct(&png, &info, 0);
        }
    }
    return ok;
}

// 1001d42a.
int GCALL PNG_close(void *handle)
{
    PNGHANDLE *png = (PNGHANDLE *)handle;
    int result = 0;
    if (png)
    {
        if (png->state)
        {
            PNGSTATE *state = png->state;
            png_destroy_read_struct(&state->png, &state->info, 0);
            gfree(png->state);
        }
        result = gfree(png);
    }
    return result;
}

GIMEX_BOUNDARY_WRITE(PNG)
