// "Size" filter 1.05 (Gerry Shaw): filter 31, used by FaceInRace's SizeImage.
// gimme.dll 3a43b0f6…, VA 10023740–1002542e.
//
// Dale Schumacher's "General Filtered Image Rescaling" (Graphics Gems III, filter functions
// and zoom()) on 32-bit ARGB pixels: a horizontal pass into a temporary image, then a
// vertical pass.  Changes against the published zoom(): the weights are normalised by their
// sum, a shrink's filter width is limited to the source size minus one, and with "Respect
// Alpha" chroma-key pixels are left out and a pixel whose weights sum below 0.3 becomes the
// key.  The X/Y sharpness parameters are read but overwritten with 1.0 and never used.
// Parameters Width and Height are read without checking the count; only the first word of
// the integer slots is read.  Pixels are always handled as 32 bits.

#include <math.h>
#include <string.h>

#include "gimexfilter.h"

#define M_PI 3.141592654   // as in the published source

typedef double (*SIZEFILTERFN)(double t);

// 10023740.  Filter 31 "Size" 1.05.
GFILTERABOUT *SIZE_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.05");
        strcpy(about->name, "Size");
        strcpy(about->description, "Image Size");
        about->values = 7;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 1;
        strcpy(about->value[0].name, "Width");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 1;
        strcpy(about->value[1].name, "Height");
        about->value[2].type = 0x201;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = 6;
        about->value[2].initial.integer = 0;
        strcpy(about->value[2].name, "Filter Function");
        strcpy(about->value[2].help, "Lanczos3,Mitchell,Cubic,Linear,Point,Bell,B-Spline");
        about->value[3].type = 0x1;
        about->value[3].minimum.integer = 0;
        about->value[3].maximum.integer = 1;
        about->value[3].initial.integer = 0;
        strcpy(about->value[3].name, "Respect Alpha");
        about->value[4].type = 0x801;
        about->value[4].minimum.integer = 0;
        about->value[4].maximum.integer = -1;
        about->value[4].initial.integer = 0;
        strcpy(about->value[4].name, "Chromakey Colour");
        about->value[5].type = 0x2;
        about->value[5].minimum.real = 0.0;
        about->value[5].maximum.real = 1.0;
        about->value[5].initial.real = 1.0;
        strcpy(about->value[5].name, "X Sharpness");
        about->value[6].type = 0x2;
        about->value[6].minimum.real = 0.0;
        about->value[6].maximum.real = 1.0;
        about->value[6].initial.real = 1.0;
        strcpy(about->value[6].name, "Y Sharpness");
    }
    return about;
}

// 10023ae1.
int SIZE_open(void **handle, int images, GIMAGE *image, int values, void *value)
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

// 10023b4f.  A copy of the source descriptor with the new size and frame number; the centre
// and the shape points are scaled and truncated.
GINFO *SIZE_info(void *handle, int frame)
{
    GFILTERHANDLE *filter = (GFILTERHANDLE *)handle;
    const GINFO *source = filter->image->info;
    GINFO *info = (GINFO *)galloc(source->size);
    if (info)
    {
        memcpy(info, source, source->size);
        info->frames = frame;
        info->width = filter->value[0].integer;
        info->height = filter->value[1].integer;
        double xscale = (double)info->width / source->width;
        double yscale = (double)info->height / source->height;
        for (int i = 0; i < GINFO_pointcount(info); ++i)
        {
            GINFO_point(info, i)[0] = (int)(GINFO_point(info, i)[0] * xscale);
            GINFO_point(info, i)[1] = (int)(GINFO_point(info, i)[1] * yscale);
        }
        info->centrex = (int)(info->centrex * xscale);
        info->centrey = (int)(info->centrey * yscale);
    }
    return info;
}

// ---------------------------------------------------------------------------------------------
// Filter functions (10023e83 … 10024171), as published.

// 10023e83.  f(t) = 2|t|^3 - 3|t|^2 + 1, -1 <= t <= 1 ("Cubic").
static double Filter(double t)
{
    if (t < 0.0)
        t = -t;
    if (t < 1.0)
        return (2.0 * t - 3.0) * t * t + 1.0;
    return 0.0;
}

// 10023ed3.  "Point".
static double BoxFilter(double t)
{
    if (t > -0.5 && t <= 0.5)
        return 1.0;
    return 0.0;
}

// 10023f06.  "Linear".
static double TriangleFilter(double t)
{
    if (t < 0.0)
        t = -t;
    if (t < 1.0)
        return 1.0 - t;
    return 0.0;
}

// 10023f44.  Box (*) box (*) box.
static double BellFilter(double t)
{
    if (t < 0)
        t = -t;
    if (t < .5)
        return .75 - (t * t);
    if (t < 1.5)
    {
        t = (t - 1.5);
        return .5 * (t * t);
    }
    return 0.0;
}

// 10023fac.  Box (*) box (*) box (*) box.
static double BSplineFilter(double t)
{
    double tt;
    if (t < 0)
        t = -t;
    if (t < 1)
    {
        tt = t * t;
        return (.5 * tt * t) - tt + (2.0 / 3.0);
    }
    else if (t < 2)
    {
        t = 2 - t;
        return (1.0 / 6.0) * (t * t * t);
    }
    return 0.0;
}

// 10024095.
static double Sinc(double x)
{
    x *= M_PI;
    if (x != 0)
        return sin(x) / x;
    return 1.0;
}

// 1002402e.
static double Lanczos3Filter(double t)
{
    if (t < 0)
        t = -t;
    if (t < 3.0)
        return Sinc(t) * Sinc(t / 3.0);
    return 0.0;
}

#define B (1.0 / 3.0)
#define C (1.0 / 3.0)

// 100240c6.
static double MitchellFilter(double t)
{
    double tt;
    tt = t * t;
    if (t < 0)
        t = -t;
    if (t < 1.0)
    {
        t = (((12.0 - 9.0 * B - 6.0 * C) * (t * tt)) + ((-18.0 + 12.0 * B + 6.0 * C) * tt) + (6.0 - 2 * B));
        return t / 6.0;
    }
    else if (t < 2.0)
    {
        t = (((-1.0 * B - 6.0 * C) * (t * tt)) + ((6.0 * B + 30.0 * C) * tt) + ((-12.0 * B - 48.0 * C) * t) +
             (8.0 * B + 24 * C));
        return t / 6.0;
    }
    return 0.0;
}

#undef B
#undef C

// ---------------------------------------------------------------------------------------------
// Image helpers

// Read for a contribution outside the source row (x pass) and by GetPixel outside the image.
// 0x1045306c, uninitialised data; the indexed code only reads it.
static unsigned zoomoutside;

// 10024fbd.  A cleared image with its own descriptor (8 or 32 bits; channel bits at most 8).
static GIMAGE *NewImage(int width, int height, int depth)
{
    int bpp = depth <= 8 ? 8 : 32;
    int rowbytes = width * bpp / 8;
    GIMAGE *image = (GIMAGE *)galloc(sizeof(GIMAGE));
    memset(image, 0, sizeof(GIMAGE));
    image->info = (GINFO *)galloc(GINFO_SIZE_LEGACY);
    memset(image->info, 0, GINFO_SIZE_LEGACY);
    image->pixels = (unsigned char *)galloc(rowbytes * height);
    memset(image->pixels, 0, rowbytes * height);
    image->rowbytes = rowbytes;
    image->info->size = GINFO_SIZE_LEGACY;
    image->info->version = 200;
    image->info->bpp = bpp;
    image->info->depth = depth;
    image->info->numcolours = 256;
    image->info->width = width;
    image->info->height = height;
    image->info->redbits = bpp / 3 > 8 ? 8 : bpp / 3;
    image->info->greenbits = bpp / 3 > 8 ? 8 : bpp / 3;
    image->info->bluebits = bpp / 3 > 8 ? 8 : bpp / 3;
    image->info->alphabits = bpp - 3 * (bpp / 3 > 8 ? 8 : bpp / 3);
    return image;
}

// 1002518b.
static void FreeImage(GIMAGE *image)
{
    gfree(image->info);
    gfree(image->pixels);
    gfree(image);
}

// 100251b0.  Rounds to the nearest byte within [low, high].  The negated tests take the same
// branches as the original's x87 flag tests, also for a NaN (which gives high).
static unsigned char Clamp(double value, unsigned char low, unsigned char high)
{
    if (!(high >= value))
        return high;
    if (low > value)
        return low;
    return (unsigned char)(int)(value + 0.5);
}

// 10025203.  Copies source row y (32-bit pixels) into row.
static void GetRow(unsigned *row, const GIMAGE *image, int y)
{
    if (y < 0 || y >= image->info->height)
        return;
    memcpy(row, image->pixels + y * image->rowbytes, image->info->width * sizeof(unsigned));
}

// 1002524f.  Copies column x (32-bit pixels) into column.
static void GetColumn(unsigned *column, const GIMAGE *image, int x)
{
    if (x < 0 || x >= image->info->width)
        return;
    int count = image->info->height;
    const unsigned char *pixel = image->pixels + x * sizeof(unsigned);
    while (count > 0)
    {
        *column++ = *(const unsigned *)pixel;
        pixel += image->rowbytes;
        --count;
    }
}

// 100252b8.
static void PutPixel(GIMAGE *image, int x, int y, unsigned value)
{
    unsigned *row = 0;
    if (x < 0 || x >= image->info->width || y < 0 || y >= image->info->height)
        return;
    row = (unsigned *)(image->pixels + y * image->rowbytes);
    row[x] = value;
}

// 10025398.
static unsigned GetPixel(const GIMAGE *image, int x, int y)
{
    unsigned *row = 0;
    if (x < 0 || x >= image->info->width || y < 0 || y >= image->info->height)
        return zoomoutside;
    row = (unsigned *)(image->pixels + y * image->rowbytes);
    return row[x];
}

// 10025310.  The first fully transparent pixel, in row order; 0x0000ffff if there is none.
static unsigned FindKey(const GIMAGE *image)
{
    for (int y = 0; y < image->info->height; ++y)
        for (int x = 0; x < image->info->width; ++x)
        {
            unsigned pixel = GetPixel(image, x, y);
            if ((pixel >> 24) == 0)
                return pixel;
        }
    return 0x0000ffff;
}

// 100253f2.  Is the pixel the key: equal to key, or fully transparent when key is 0.
static int IsKey(unsigned pixel, unsigned key)
{
    int match = (pixel >> 24) == 0;
    if (key)
        match = pixel == key;
    return match;
}

// ---------------------------------------------------------------------------------------------
// Rescaling

struct CONTRIB
{
    int pixel;
    double weight;
};

struct CLIST
{
    int n;                       // number of contributors
    CONTRIB *p;                  // pointer to list of contributions
};

static_assert(sizeof(CONTRIB) == 0x10, "CONTRIB layout");

static CLIST *contrib;          // 0x105df5ec

// The contributions to `count` output samples along one axis of `size` source samples
// (published zoom(), in both passes).  `mirror` is the sample count used to reflect indices
// past the far edge.
static void Contributions(int count, int size, int mirror, double scale, SIZEFILTERFN filterf, double fwidth,
                          bool horizontal)
{
    double center, left, right;
    double width, fscale, weight;
    int i, j, k, n;
    if (scale < 1.0)
    {
        width = fwidth / scale < size - 1 ? fwidth / scale : size - 1;
        fscale = width / fwidth;
        for (i = 0; i < count; ++i)
        {
            contrib[i].n = 0;
            contrib[i].p = (CONTRIB *)galloc((int)(width * 2 + 1) * sizeof(CONTRIB));
            center = (double)i / scale;
            left = ceil(center - width);
            right = floor(center + width);
            for (j = (int)left; j <= right; ++j)
            {
                weight = center - (double)j;
                weight = (*filterf)(weight / fscale) / fscale;
                if (j < 0)
                    n = -j;
                else if (j >= mirror)
                    n = horizontal ? mirror - 1 - (j - mirror) : (mirror - j) + mirror - 1;
                else
                    n = j;
                k = contrib[i].n++;
                contrib[i].p[k].pixel = n;
                contrib[i].p[k].weight = weight;
            }
        }
    }
    else
    {
        for (i = 0; i < count; ++i)
        {
            contrib[i].n = 0;
            contrib[i].p = (CONTRIB *)galloc((int)(fwidth * 2 + 1) * sizeof(CONTRIB));
            center = (double)i / scale;
            left = ceil(center - fwidth);
            right = floor(center + fwidth);
            for (j = (int)left; j <= right; ++j)
            {
                weight = center - (double)j;
                weight = (*filterf)(weight);
                if (j < 0)
                    n = -j;
                else if (j >= mirror)
                    n = horizontal ? mirror - 1 - (j - mirror) : (mirror - j) + mirror - 1;
                else
                    n = j;
                k = contrib[i].n++;
                contrib[i].p[k].pixel = n;
                contrib[i].p[k].weight = weight;
            }
        }
    }
}

// One output pixel from the weighted contributions: the sums are divided by the weight sum.
static unsigned Resample(const CLIST *list, const unsigned *raster, bool horizontal, int limit, int alpha,
                         unsigned key)
{
    double a = 0.0, r = 0.0, b = 0.0, g = 0.0, total = 0.0;
    unsigned result;
    for (int j = 0; j < list->n; ++j)
    {
        double weight;
        unsigned pixel;
        if (horizontal)
        {
            weight = list->p[j].weight;
            pixel = list->p[j].pixel < limit ? raster[list->p[j].pixel] : zoomoutside;
        }
        else
        {
            pixel = raster[list->p[j].pixel];   // the vertical pass does not check the index
            weight = list->p[j].weight;
        }
        if (!alpha || (alpha && !IsKey(pixel, key)))
        {
            a += (int)(pixel >> 24 & 0xff) * weight;
            r += (int)(pixel >> 16 & 0xff) * weight;
            g += (int)(pixel >> 8 & 0xff) * weight;
            b += (int)(pixel & 0xff) * weight;
            total += weight;
        }
    }
    if (alpha && !(total >= 0.3))   // also a NaN, as the original's flag test
        result = key;
    else
    {
        unsigned char ca = Clamp(a / total, 0, 255);
        unsigned char cr = Clamp(r / total, 0, 255);
        unsigned char cg = Clamp(g / total, 0, 255);
        unsigned char cb = Clamp(b / total, 0, 255);
        result = (unsigned)ca << 24 | (unsigned)cr << 16 | (unsigned)cg << 8 | cb;
    }
    return result;
}

// 10024172.  Rescales src into dst; dst->info gives the size.
static void Zoom(const GIMAGE *src, GIMAGE *dst, SIZEFILTERFN filterf, double fwidth, int alpha, unsigned key,
                 double xsharpness, double ysharpness)
{
    unsigned keycolour = key;
    if (alpha && !key)
        keycolour = FindKey(src);
    xsharpness = 1.0;
    ysharpness = 1.0;
    GIMAGE *tmp = NewImage(dst->info->width, src->info->height, 32);
    double xscale = (double)dst->info->width / src->info->width;
    double yscale = (double)dst->info->height / src->info->height;

    // pre-calculate filter contributions for a row
    contrib = (CLIST *)galloc(dst->info->width * sizeof(CLIST));
    Contributions(dst->info->width, src->info->width, src->info->width, xscale, filterf, fwidth, true);

    // apply filter to zoom horizontally from src to tmp
    unsigned *raster = (unsigned *)galloc(src->info->width * sizeof(unsigned));
    for (int k = 0; k < tmp->info->height; ++k)
    {
        GetRow(raster, src, k);
        for (int i = 0; i < tmp->info->width; ++i)
            PutPixel(tmp, i, k, Resample(&contrib[i], raster, true, src->info->width, alpha, keycolour));
    }
    gfree(raster);

    // free the memory allocated for horizontal filter weights
    for (int i = 0; i < tmp->info->width; ++i)
        gfree(contrib[i].p);
    gfree(contrib);

    // pre-calculate filter contributions for a column
    contrib = (CLIST *)galloc(dst->info->height * sizeof(CLIST));
    Contributions(dst->info->height, src->info->height, tmp->info->height, yscale, filterf, fwidth, false);

    // apply filter to zoom vertically from tmp to dst
    raster = (unsigned *)galloc(tmp->info->height * sizeof(unsigned));
    for (int k = 0; k < dst->info->width; ++k)
    {
        GetColumn(raster, tmp, k);
        for (int i = 0; i < dst->info->height; ++i)
            PutPixel(dst, k, i, Resample(&contrib[i], raster, false, 0, alpha, keycolour));
    }
    gfree(raster);

    // free the memory allocated for vertical filter weights
    for (int i = 0; i < dst->info->height; ++i)
        gfree(contrib[i].p);
    gfree(contrib);
    FreeImage(tmp);
}

// 10023c8a.  Parameter 2 selects the filter: Lanczos3 (default, also for unknown values),
// Mitchell, Cubic, Linear, Point, Bell, B-Spline.
int SIZE_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    GFILTERHANDLE *filter = (GFILTERHANDLE *)handle;
    int function = 0;
    int alpha = 0;
    int key = 0;
    double xsharpness = 1.0;
    double ysharpness = 1.0;
    SIZEFILTERFN filterf;
    double support;
    if (filter->value)
    {
        if (filter->values >= 3)
            function = filter->value[2].integer;
        if (filter->values >= 4)
            alpha = filter->value[3].integer;
        if (filter->values >= 5)
            key = filter->value[4].integer;
        if (filter->values >= 6)
            xsharpness = filter->value[5].real;
        if (filter->values >= 7)
            ysharpness = filter->value[6].real;
    }
    switch (function)
    {
    case 0:
        filterf = Lanczos3Filter;
        support = 3.0;
        break;
    case 1:
        filterf = MitchellFilter;
        support = 2.0;
        break;
    case 2:
        filterf = Filter;
        support = 1.0;
        break;
    case 3:
        filterf = TriangleFilter;
        support = 1.0;
        break;
    case 4:
        filterf = BoxFilter;
        support = 0.5;
        break;
    case 5:
        filterf = BellFilter;
        support = 1.5;
        break;
    case 6:
        filterf = BSplineFilter;
        support = 2.0;
        break;
    default:
        filterf = Lanczos3Filter;
        support = 3.0;
        break;
    }
    GIMAGE destination;
    destination.info = info;
    destination.pixels = (unsigned char *)pixels;
    destination.rowbytes = rowbytes;
    Zoom(filter->image, &destination, filterf, support, alpha, key, xsharpness, ysharpness);
    return 1;
}

// 10025421.
int SIZE_close(void *handle)
{
    return gfree(handle);
}
