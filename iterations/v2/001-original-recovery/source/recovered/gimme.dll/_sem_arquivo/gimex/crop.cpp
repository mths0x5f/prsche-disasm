// "Crop" filter 1.02 (Frank Barchard): filter 5, used by FaceInRace's CropToAspect.
// gimme.dll 3a43b0f6…, VA 10120260–10120941.  Parameters X, Y, Width, Height and Colour; only
// the first word of each 8-byte slot is read.  Pixels outside the source take Colour.

#include <string.h>

#include "gimexfilter.h"

// 10120260.  Filter 5 "Crop" 1.02.
GFILTERABOUT *CROP_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('C', 'R', 'O', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.02");
        strcpy(about->name, "Crop");
        strcpy(about->description, "Crop");
        about->values = 5;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = -32000;
        about->value[0].maximum.integer = 32000;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "X");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = -32000;
        about->value[1].maximum.integer = 32000;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Y");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x1;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = 32000;
        about->value[2].initial.integer = 0;
        strcpy(about->value[2].name, "Width");
        strcpy(about->value[2].help, "");
        about->value[3].type = 0x1;
        about->value[3].minimum.integer = 0;
        about->value[3].maximum.integer = 32000;
        about->value[3].initial.integer = 0;
        strcpy(about->value[3].name, "Height");
        strcpy(about->value[3].help, "");
        about->value[4].type = 0x1801;
        about->value[4].minimum.integer = 0;
        about->value[4].maximum.integer = -1;
        about->value[4].initial.integer = 0;
        strcpy(about->value[4].name, "Colour");
        strcpy(about->value[4].help, "");
    }
    return about;
}

// 1012053a.
int CROP_open(void **handle, int images, GIMAGE *image, int values, void *value)
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

// The parameters with their defaults, read the same way by info() and read().
struct CROPVALUES
{
    int x;
    int y;
    int width;
    int height;
    int colour;
};

static CROPVALUES CropValues(const GFILTERHANDLE *filter)
{
    CROPVALUES crop = { 0, 0, 1, 1, 0 };
    if (filter->value)
    {
        if (filter->values >= 1)
            crop.x = filter->value[0].integer;
        if (filter->values >= 2)
            crop.y = filter->value[1].integer;
        if (filter->values >= 3)
            crop.width = filter->value[2].integer;
        if (filter->values >= 4)
            crop.height = filter->value[3].integer;
        if (filter->values >= 5)
            crop.colour = filter->value[4].integer;
    }
    return crop;
}

// 101205af.  A copy of the source descriptor resized to the rectangle; the position moves by
// (x, y) and the centre and the shape points by (-x, -y).
GINFO *CROP_info(void *handle, int)
{
    GFILTERHANDLE *filter = (GFILTERHANDLE *)handle;
    CROPVALUES crop = CropValues(filter);
    const GINFO *source = filter->image->info;
    GINFO *info = (GINFO *)galloc(source->size);
    if (info)
    {
        memcpy(info, source, source->size);
        int dx = crop.x;
        int dy = crop.y;
        info->width = crop.width;
        info->height = crop.height;
        info->positionx += dx;
        info->positiony += dy;
        info->centrex -= dx;
        info->centrey -= dy;
        for (int i = 0; i < GINFO_pointcount(info); ++i)
        {
            GINFO_point(info, i)[0] -= dx;
            GINFO_point(info, i)[1] -= dy;
        }
    }
    return info;
}

// 10120764.  Copies the rectangle at the bit depth of the output descriptor: one byte per
// pixel at 8 bits, otherwise four.
int CROP_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    GFILTERHANDLE *filter = (GFILTERHANDLE *)handle;
    int bpp = info->bpp;
    CROPVALUES crop = CropValues(filter);
    unsigned char *row = (unsigned char *)pixels;
    for (int y = 0; y < info->height; ++y)
    {
        unsigned char *out = row;
        for (int x = 0; x < info->width; ++x)
        {
            int sx = crop.x + x;
            int sy = crop.y + y;
            const GIMAGE *source = filter->image;
            if (sx >= 0 && sx < source->info->width && sy >= 0 && sy < source->info->height)
            {
                const unsigned char *in = source->pixels + sy * source->rowbytes + sx * bpp / 8;
                if (bpp == 8)
                    *out++ = *in;
                else
                {
                    *(unsigned *)out = *(const unsigned *)in;
                    out += 4;
                }
            }
            else if (bpp == 8)
                *out++ = (unsigned char)crop.colour;
            else
            {
                *(int *)out = crop.colour;
                out += 4;
            }
        }
        row += rowbytes;
    }
    return 1;
}

// 10120934.
int CROP_close(void *handle)
{
    return gfree(handle);
}
