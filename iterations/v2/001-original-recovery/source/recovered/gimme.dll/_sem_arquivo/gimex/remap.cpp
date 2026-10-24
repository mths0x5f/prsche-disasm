// "Remap" filter 1.04 (F.Barchard & G.Shaw): filter 6, used by FaceInRace's ReduceImage.
// gimme.dll 3a43b0f6…, VA 1011fd60–10120257.  Maps a 32-bit image to 8 bits through the
// GREMAP block whose address is the first word of the only parameter; the parameter count is
// not checked.

#include <string.h>

#include "gimexfilter.h"

// 1011fd60.  Filter 6 "Remap" 1.04.
GFILTERABOUT *REMAP_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('R', 'E', 'M', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 100;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "F.Barchard & G.Shaw");
        strcpy(about->filterversion, "1.04");
        strcpy(about->name, "Remap");
        strcpy(about->description, "Remap 32 to 8");
        about->values = 1;
        about->value[0].type = 0x403;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 0;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "Destination Palette");
        strcpy(about->value[0].help, "");
    }
    return about;
}

// 1011feb9.
int REMAP_open(void **handle, int images, GIMAGE *image, int values, void *value)
{
    int ok = 0;
    GFILTERHANDLE *filter = 0;
    filter = (GFILTERHANDLE *)galloc(sizeof(GFILTERHANDLE));
    if (filter)
    {
        memset(filter, 0, sizeof(GFILTERHANDLE));
        filter->unknown_00 = 1;
        filter->images = images;
        filter->image = image;
        filter->values = values;
        filter->value = (GFILTERNUMBER *)value;
        ok = 1;
    }
    *handle = filter;
    return ok;
}

static const GREMAP *RemapBlock(const GFILTERHANDLE *filter)
{
    return *(GREMAP *const *)&filter->value[0];
}

// 1011ff2e.  An 8-bit copy of the source descriptor whose palette is cleared and then holds
// the block's colours from index first.
GINFO *REMAP_info(void *handle, int)
{
    GFILTERHANDLE *filter = (GFILTERHANDLE *)handle;
    const GINFO *source = filter->image->info;
    GINFO *info = (GINFO *)galloc(source->size);
    if (info)
    {
        memcpy(info, source, source->size);
        info->bpp = 8;
        info->depth = 8;
        info->numcolours = 256;
        memset(info->colour, 0, sizeof(info->colour));
        const GREMAP *remap = RemapBlock(filter);
        memcpy(&info->colour[remap->first], remap->palette, remap->colours * sizeof(GCOLOUR));
    }
    return info;
}

// 101200da.  Palette index for one pixel: the inverse table when there is one, else the
// nearest colour with alpha weighted 16 times, the first one found winning ties.  With no
// colours the index is never set (as compiled; FaceInRace always passes at least one).
static int NearestColour(const unsigned char *pixel, const GREMAP *remap)
{
    int found;
    int a = pixel[3];
    int r = pixel[2];
    int g = pixel[1];
    int b = pixel[0];
    const unsigned char *inverse = remap->inverse;
    if (remap->inverse)
    {
        int index = ((r >> 2) << 6 << 6) + ((g >> 2) << 6) + (b >> 2);
        return inverse[index] + remap->first;
    }
    int best = 0x7fffffff;
    int colours = remap->colours;
    const GCOLOUR *colour = remap->palette;
    for (int i = 0; i < colours && best != 0; ++i, ++colour)
    {
        int ca = colour->a;
        int cr = colour->r;
        int cg = colour->g;
        int cb = colour->b;
        int distance = (a - ca) * 4 * ((a - ca) * 4) + (r - cr) * (r - cr) + (g - cg) * (g - cg) +
                       (b - cb) * (b - cb);
        if (distance < best)
        {
            best = distance;
            found = i;
        }
    }
    return found + remap->first;
}

// 1012002c.  Maps every 32-bit source pixel of the output rectangle.
static int RemapImage(const GIMAGE *source, const GIMAGE *destination, const GREMAP *remap)
{
    int width = destination->info->width;
    int height = destination->info->height;
    for (int y = 0; y < height; ++y)
    {
        const unsigned char *in = source->pixels + y * source->rowbytes;
        unsigned char *out = destination->pixels + y * destination->rowbytes;
        for (int x = 0; x < width; ++x)
        {
            *out++ = (unsigned char)NearestColour(in, remap);
            in += 4;
        }
    }
    return 1;
}

// 1011fff4.
int REMAP_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    GFILTERHANDLE *filter = (GFILTERHANDLE *)handle;
    GIMAGE destination;
    destination.info = info;
    destination.pixels = (unsigned char *)pixels;
    destination.rowbytes = rowbytes;
    return RemapImage(filter->image, &destination, RemapBlock(filter));
}

// 1012024a.
int REMAP_close(void *handle)
{
    return gfree(handle);
}
