// "Tiff" module 1.04 (FrANK G. Barchard): GIMEX module 60.
// gimme.dll 3a43b0f6…, entry points about 100185b0, is 100187b0, open 10018821, info 100188c7, read 10018b78, close 10018ca2,
// wopen 10018210, write 100182ab, wclose 1001856a.  about(), is() and the reader (open, info, read,
// close) are recovered on top of the unmodified libtiff 3.4 (tiff/) and the GSTREAM platform layer
// (tifgstream.cpp); the writer entry points are recovery boundaries (boundary.h).

#include <stdlib.h>
#include <string.h>

#include "boundary.h"
#include "tifgstream.h"

extern "C"
{
#include "tiff/tiffiop.h"
}

// 100185b0.
GABOUT *TIF_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 'T', 'G', 'A');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9317;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('T', 'I', 'F', 'F');
        strcpy(about->extension[0], ".tif");
        strcpy(about->extension[1], ".tiff");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.04");
        strcpy(about->shortname, "TIF");
        strcpy(about->longname, "Tiff");
        strcpy(about->name, "Tiff");
    }
    return about;
}

// 100187b0.
int GCALL TIF_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char order[4];
    gseek(stream, 0);
    if (gread(stream, order, 2) &&
        ((order[0] == 'M' && order[1] == 'M') || (order[0] == 'I' && order[1] == 'I')))
        score = 60;
    return score;
}

// ---------------------------------------------------------------------------------------------
// Reader on top of libtiff: TIFFReadRGBAImage does all decoding and colour conversion.

// Handle returned by open() (0x18 bytes, cleared).  Its tag repeats about()'s 0x00544741.
struct TIFHANDLE
{
    unsigned tag;                // +0x00
    int size;                    // +0x04 sizeof(TIFHANDLE)
    int count;                   // +0x08 frames: always 1
    int unknown_0c;              // +0x0c
    GSTREAM *stream;             // +0x10
    TIFF *tiff;                  // +0x14
};

static_assert(sizeof(TIFHANDLE) == 0x18, "TIFHANDLE layout");

// GINFO +0x287c: horizontal resolution as a float (see bmp.cpp, pcx.cpp).
static float *TifResolution(GINFO *info)
{
    return (float *)((unsigned char *)info + 0x287c);
}

// 10018821.
int GCALL TIF_open(void **handle, GSTREAM *stream, const char *name, int)
{
    int ok = 0;
    gseek(stream, 0);
    TIFHANDLE *tif = (TIFHANDLE *)galloc(sizeof(TIFHANDLE));
    if (tif)
    {
        memset(tif, 0, sizeof(TIFHANDLE));
        tif->count = 1;
        tif->tag = GTAG(0, 'T', 'G', 'A');
        tif->size = sizeof(TIFHANDLE);
        tif->stream = stream;
        TIFF *tiff = TIFFOpenGStream(name, stream, "r");
        if (tiff)
        {
            tif->tiff = tiff;
            *handle = tif;
            ok = 1;
        }
        else
            gfree(tif);
    }
    return ok;
}

// 100188c7.  The descriptor is always 32 bits per pixel (TIFFReadRGBAImage output); depth is
// samples x bits (24 for one sample), alphabits 8 above three samples.  Original defects kept:
//   - bits per sample are taken only if TIFFFieldSet(tif, TIFFTAG_BITSPERSAMPLE) is true, i.e.
//     the tag number 258 used as a field bit: that tests bit 2 of word 8 of td_fieldsset, which
//     is td_tiledepth; normally clear, so bits per sample stay 8.
//   - an inch or absent unit is replaced by "unit = RESUNIT_INCH" (assignment, not a test), so
//     the resolution is XResolution as stored; centimetres are converted to inches.  Without an
//     XResolution tag the resolution is whatever the stack held.
GINFO *GCALL TIF_info(void *handle, int)
{
    TIFHANDLE *tif = (TIFHANDLE *)handle;
    uint16 unit = 0;             // an int cleared to 0 in the original; TIFFGetField writes 16 bits
    float resolution = 0;
    int ok = 0;
    int samples = 3;
    int bits = 8;
    GINFO *info = 0;
    uint32 width, height;
    float xresolution;           // not initialised in the original either

    TIFF *tiff = tif->tiff;
    if (tiff)
    {
        TIFFDirectory *td = &tiff->tif_dir;
        TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, &width);
        TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, &height);
        TIFFGetField(tiff, TIFFTAG_RESOLUTIONUNIT, &unit);
        TIFFGetField(tiff, TIFFTAG_XRESOLUTION, &xresolution);
        if (unit == RESUNIT_CENTIMETER)
            resolution = (float)(xresolution * 100.0 * 0.039370079);
        else if ((unit = RESUNIT_INCH) != RESUNIT_NONE)
            resolution = xresolution;
        else if (unit != RESUNIT_INCH)
            resolution = 0;
        TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, &xresolution);
        if (TIFFFieldSet(tiff, TIFFTAG_BITSPERSAMPLE))
            bits = td->td_bitspersample;
        if (TIFFFieldSet(tiff, FIELD_SAMPLESPERPIXEL))
            samples = td->td_samplesperpixel;
        int depth = samples * bits;
        info = (GINFO *)galloc(GINFO_SIZE_LEGACY);
        if (info)
        {
            memset(info, 0, GINFO_SIZE_LEGACY);
            info->tag = GTAG('T', 'I', 'F', 'F');
            info->size = GINFO_SIZE_LEGACY;
            info->version = GINFO_VERSION;
            info->frames = 0;
            info->width = width;
            info->height = height;
            info->shapesize = 0;
            info->attributes = 0;
            info->compression = 0;
            info->unknown_430 = 100;
            info->alphabits = samples > 3 ? 8 : 0;
            info->redbits = bits;
            info->greenbits = bits;
            info->bluebits = bits;
            info->centrex = 0;
            info->centrey = 0;
            info->positionx = 0;
            info->positiony = 0;
            info->pointcount = 0;
            info->name[0] = 0;
            info->bpp = 32;
            *TifResolution(info) = resolution;
            info->depth = samples == 1 ? 24 : depth;
            info->numcolours = 0;
            ok = 1;
        }
        if (info && !ok)
        {
            gfree(info);
            info = 0;
        }
    }
    return info;
}

// 10018b78.  TIFFReadRGBAImage fills a bottom-up R, G, B, A raster; rows are flipped and the
// samples reordered to B, G, R, A.
int GCALL TIF_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    TIFHANDLE *tif = (TIFHANDLE *)handle;
    int ok = 0;
    TIFF *tiff = tif->tiff;
    int width = info->width;
    int height = info->height;
    int bytes = width * 4 * height;
    uint32 *raster = (uint32 *)galloc(bytes);
    if (raster)
    {
        if (TIFFReadRGBAImage(tiff, width, height, raster, 0))
        {
            for (int y = 0; y < height; y++)
            {
                unsigned char *s = (unsigned char *)(raster + (height - 1 - y) * width);
                unsigned char *d = (unsigned char *)pixels + y * rowbytes;
                for (int x = 0; x < width; x++)
                {
                    d[3] = s[3];
                    d[2] = s[0];
                    d[1] = s[1];
                    d[0] = s[2];
                    d += 4;
                    s += 4;
                }
            }
            ok = 1;
        }
        gfree(raster);
    }
    return ok;
}

// 10018ca2.
int GCALL TIF_close(void *handle)
{
    TIFHANDLE *tif = (TIFHANDLE *)handle;
    int result = 0;
    if (tif)
    {
        if (tif->tiff)
            TIFFClose(tif->tiff);
        result = gfree(tif);
    }
    return result;
}

GIMEX_BOUNDARY_WRITE(TIF)
