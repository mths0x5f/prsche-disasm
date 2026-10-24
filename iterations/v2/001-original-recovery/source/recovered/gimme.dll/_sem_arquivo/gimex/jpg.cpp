// "JPeg" module 1.10 (FrANK G. Barchard): GIMEX module 55.
// gimme.dll 3a43b0f6…, entry points about 100219d2, is 10021beb, open 10021cd3, info 10021d3c, read 100221e4, close 100226ad,
// wopen 10021462, write 100214b8, wclose 100217fd.  about(), is() and the reader (open, info, read,
// close and helpers 10021830, 10021cb2, 10022580, 100223f3, 10022680) are recovered on top of the
// unmodified IJG 6a library (jpeg/) and the GSTREAM source (jpgsource.cpp); the writer entry
// points are recovery boundaries (boundary.h).

#include <setjmp.h>
#include <stdlib.h>
#include <string.h>

#include "boundary.h"
#include "jpgsource.h"

// 100219d2.
GABOUT *JPG_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('J', 'P', 'E', 'G');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb3d7;
        about->unknown_14 = 0;
        about->unknown_18 = 70;
        about->mactype[0] = GTAG('J', 'P', 'E', 'G');
        strcpy(about->extension[0], ".jpg");
        strcpy(about->extension[1], ".jpeg");
        strcpy(about->extension[2], ".jfif");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.10");
        strcpy(about->shortname, "JPG");
        strcpy(about->longname, "JPeg");
        strcpy(about->name, "JPeg");
    }
    return about;
}

// ---------------------------------------------------------------------------------------------
// Reader.  Each entry point builds its own decompressor on the stack, as IJG's example.c does:
// an error manager extended with a jmp_buf (0x84 + 0x40 bytes) followed by the 0x1d0-byte
// jpeg_decompress_struct.  info() decodes the whole image only to finish cleanly.

struct JPGERROR
{
    jpeg_error_mgr pub;          // +0x00
    jmp_buf setjmpbuffer;        // +0x84
};

static_assert(sizeof(jpeg_error_mgr) == 0x84 && sizeof(JPGERROR) == 0xc4, "JPGERROR layout");
static_assert(sizeof(jpeg_decompress_struct) == 0x1d0, "IJG 6a decompressor layout");

// Handle returned by open() (0x18 bytes, cleared).
struct JPGHANDLE
{
    unsigned tag;                // +0x00 'JPEG'
    int size;                    // +0x04 sizeof(JPGHANDLE)
    int count;                   // +0x08 frames: always 1
    int unknown_0c;              // +0x0c
    GSTREAM *stream;             // +0x10
    int unknown_14;              // +0x14
};

static_assert(sizeof(JPGHANDLE) == 0x18, "JPGHANDLE layout");

// 10453054: set by the APP13 processor when the marker holds "GIMEXARGB".
static int jpgargbmarker;

// GINFO +0x287c: horizontal resolution as a float (see bmp.cpp, pcx.cpp).
static float *JpgResolution(GINFO *info)
{
    return (float *)((unsigned char *)info + 0x287c);
}

// 10021cb2.  error_exit: no message, straight back to the entry point's setjmp.
static void JpgErrorExit(j_common_ptr cinfo)
{
    JPGERROR *error = (JPGERROR *)cinfo->err;
    longjmp(error->setjmpbuffer, 1);
}

// 10021830.  APP13 processor (jdmarker.c INPUT_BYTE style).  A marker of at least 9 data bytes
// whose first 9 bytes are "GIMEXARGB" sets jpgargbmarker; the rest is skipped.  With fewer than
// 9 bytes nothing is read and the comparison looks at the uninitialised buffer.
static boolean JpgReadApp13(j_decompress_ptr cinfo)
{
    jpeg_source_mgr *datasrc = cinfo->src;
    const JOCTET *next = datasrc->next_input_byte;
    size_t bytes = datasrc->bytes_in_buffer;
    char name[9];
    int i;

    if (bytes == 0)
    {
        if (!(*datasrc->fill_input_buffer)(cinfo))
            return FALSE;
        next = datasrc->next_input_byte;
        bytes = datasrc->bytes_in_buffer;
    }
    bytes--;
    int length = (unsigned)*next++ << 8;
    if (bytes == 0)
    {
        if (!(*datasrc->fill_input_buffer)(cinfo))
            return FALSE;
        next = datasrc->next_input_byte;
        bytes = datasrc->bytes_in_buffer;
    }
    bytes--;
    length += *next++;
    length -= 2;
    if (length >= 9)
    {
        for (i = 0; i < 9; i++)
        {
            if (bytes == 0)
            {
                if (!(*datasrc->fill_input_buffer)(cinfo))
                    return FALSE;
                next = datasrc->next_input_byte;
                bytes = datasrc->bytes_in_buffer;
            }
            bytes--;
            name[i] = (char)*next++;
        }
        length -= 9;
    }
    if (strncmp(name, "GIMEXARGB", 9) == 0)
        jpgargbmarker = 1;
    datasrc->next_input_byte = next;
    datasrc->bytes_in_buffer = bytes;
    if (length > 0)
        (*cinfo->src->skip_input_data)(cinfo, (long)length);
    return TRUE;
}

// 10021beb.  100 when jpeg_read_header finds an image, 0 on any library error.
int GCALL JPG_is(GSTREAM *stream)
{
    int score = 0;
    JPGERROR error;
    jpeg_decompress_struct cinfo;

    gseek(stream, 0);
    cinfo.err = jpeg_std_error(&error.pub);
    error.pub.error_exit = JpgErrorExit;
    if (setjmp(error.setjmpbuffer))
    {
        jpeg_destroy_decompress(&cinfo);
    }
    else
    {
        jpeg_create_decompress(&cinfo);
        jpeg_gstream_src(&cinfo, stream);
        if (jpeg_read_header(&cinfo, TRUE) == JPEG_HEADER_OK)
            score = 100;
        jpeg_destroy_decompress(&cinfo);
    }
    return score;
}

// 10021cd3.
int GCALL JPG_open(void **handle, GSTREAM *stream, const char *, int)
{
    int ok = 0;
    JPGHANDLE *jpg = (JPGHANDLE *)galloc(sizeof(JPGHANDLE));
    if (jpg)
    {
        memset(jpg, 0, sizeof(JPGHANDLE));
        jpg->count = 1;
        jpg->tag = GTAG('J', 'P', 'E', 'G');
        jpg->size = sizeof(JPGHANDLE);
        jpg->stream = stream;
        *handle = jpg;
        ok = 1;
    }
    return ok;
}

// 10021d3c.  Grey images (one output component) become 8-bit with a grey ramp, everything else
// 24-bit in a 32-bit pixel.  attributes = "GIMEXARGB" marker seen, compression = 1,
// resolution = X_density when density_unit is set (no unit conversion).
GINFO *GCALL JPG_info(void *handle, int)
{
    JPGHANDLE *jpg = (JPGHANDLE *)handle;
    GINFO *info = 0;
    int ok = 1;
    int argb = 0;
    JPGERROR error;
    jpeg_decompress_struct cinfo;
    int i;

    cinfo.err = jpeg_std_error(&error.pub);
    error.pub.error_exit = JpgErrorExit;
    if (setjmp(error.setjmpbuffer))
    {
        jpeg_destroy_decompress(&cinfo);
        return 0;
    }
    jpeg_create_decompress(&cinfo);
    jpeg_set_marker_processor(&cinfo, JPEG_APP0 + 13, JpgReadApp13);
    gseek(jpg->stream, 0);
    jpeg_gstream_src(&cinfo, jpg->stream);
    jpgargbmarker = 0;
    jpeg_read_header(&cinfo, TRUE);
    argb = jpgargbmarker;
    jpeg_start_decompress(&cinfo);
    int rowbytes = cinfo.output_width * cinfo.output_components;
    int width = cinfo.output_width;
    int height = cinfo.output_height;
    int resolution = 0;
    if (cinfo.density_unit)
        resolution = cinfo.X_density;
    int components = cinfo.output_components;
    JSAMPARRAY row = (*cinfo.mem->alloc_sarray)((j_common_ptr)&cinfo, JPOOL_IMAGE, rowbytes, 1);
    while (cinfo.output_scanline < cinfo.output_height)
        jpeg_read_scanlines(&cinfo, row, 1);
    jpeg_finish_decompress(&cinfo);
    jpeg_destroy_decompress(&cinfo);

    if (ok)
    {
        int depth, alphabits;
        switch (components)
        {
        case 1:
            depth = 8;
            alphabits = 0;
            break;
        case 4:
            depth = 24;
            alphabits = 0;
            break;
        default:
            depth = 24;
            alphabits = 0;
            break;
        }
        info = (GINFO *)galloc(GINFO_SIZE_LEGACY);
        if (info)
        {
            memset(info, 0, GINFO_SIZE_LEGACY);
            info->tag = GTAG('J', 'P', 'E', 'G');
            info->size = GINFO_SIZE_LEGACY;
            info->version = GINFO_VERSION;
            info->frames = 0;
            info->width = width;
            info->height = height;
            info->attributes = argb != 0;
            info->compression = 1;
            info->unknown_430 = 70;
            info->alphabits = alphabits;
            info->redbits = 8;
            info->greenbits = 8;
            info->bluebits = 8;
            info->centrex = 0;
            info->centrey = 0;
            info->positionx = 0;
            info->positiony = 0;
            info->pointcount = 0;
            *JpgResolution(info) = (float)resolution;
            info->name[0] = 0;
            if (depth >= 15)
            {
                info->bpp = 32;
                info->depth = depth;
                info->numcolours = 0;
            }
            else
            {
                info->bpp = 8;
                info->depth = 8;
                info->numcolours = 256;
                for (i = 0; i < 256; i++)
                {
                    info->colour[i].a = 0xff;
                    info->colour[i].r = (unsigned char)i;
                    info->colour[i].g = (unsigned char)i;
                    info->colour[i].b = (unsigned char)i;
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

// 10022680.  Explicit output colour spaces; they equal the library's defaults.
static void JpgSetColourSpace(j_decompress_ptr cinfo)
{
    if (cinfo->jpeg_color_space == JCS_YCbCr)
        cinfo->out_color_space = JCS_RGB;
    else if (cinfo->jpeg_color_space == JCS_YCCK)
        cinfo->out_color_space = JCS_CMYK;
}

#define JPG_MIN(a, b) ((a) < (b) ? (a) : (b))

// 10022580.  Plain inversion with black added: 255 - min(c + k, 255).
static void JpgCmykToRgb(const unsigned char *cmyk, unsigned char *rgb)
{
    unsigned char c = (unsigned char)JPG_MIN(cmyk[0] + cmyk[3], 0xff);
    unsigned char m = (unsigned char)JPG_MIN(cmyk[1] + cmyk[3], 0xff);
    unsigned char y = (unsigned char)JPG_MIN(cmyk[2] + cmyk[3], 0xff);
    rgb[0] = (unsigned char)(0xff - c);
    rgb[1] = (unsigned char)(0xff - m);
    rgb[2] = (unsigned char)(0xff - y);
}

// 100223f3.  One decoded row to GIMEX pixels (B, G, R, A in memory).  With the "GIMEXARGB"
// marker the four components are A, R, G, B; otherwise grey rows are copied as they are.
static void JpgCopyRow(const unsigned char *source, unsigned char *destination, int width, int,
                       int colourspace, int argb)
{
    const unsigned char *s = source;
    unsigned char *d = destination;
    int i;
    unsigned char rgb[3];

    if (argb)
    {
        for (i = 0; i < width; i++)
        {
            d[i * 4 + 3] = s[i * 4];
            d[i * 4 + 2] = s[i * 4 + 1];
            d[i * 4 + 1] = s[i * 4 + 2];
            d[i * 4] = s[i * 4 + 3];
        }
        return;
    }
    switch (colourspace)
    {
    case JCS_GRAYSCALE:
        memcpy(destination, source, width);
        break;
    case JCS_CMYK:
        for (i = 0; i < width; i++)
        {
            JpgCmykToRgb(s + i * 4, rgb);
            d[i * 4 + 3] = 0xff;
            d[i * 4 + 2] = rgb[0];
            d[i * 4 + 1] = rgb[1];
            d[i * 4] = rgb[2];
        }
        break;
    default:
        for (i = 0; i < width; i++)
        {
            d[i * 4 + 3] = 0xff;
            d[i * 4 + 2] = s[i * 3];
            d[i * 4 + 1] = s[i * 3 + 1];
            d[i * 4] = s[i * 3 + 2];
        }
        break;
    }
}

// 100221e4.  Decodes again from the start; rows past info->height are decoded and dropped.
int GCALL JPG_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    JPGHANDLE *jpg = (JPGHANDLE *)handle;
    int ok = 1;
    int argb = 0;
    JPGERROR error;
    jpeg_decompress_struct cinfo;
    unsigned char *destination = (unsigned char *)pixels;

    cinfo.err = jpeg_std_error(&error.pub);
    error.pub.error_exit = JpgErrorExit;
    if (setjmp(error.setjmpbuffer))
    {
        jpeg_destroy_decompress(&cinfo);
        return 0;
    }
    jpeg_create_decompress(&cinfo);
    jpeg_set_marker_processor(&cinfo, JPEG_APP0 + 13, JpgReadApp13);
    gseek(jpg->stream, 0);
    jpeg_gstream_src(&cinfo, jpg->stream);
    jpgargbmarker = 0;
    jpeg_read_header(&cinfo, TRUE);
    argb = jpgargbmarker;
    JpgSetColourSpace(&cinfo);
    jpeg_start_decompress(&cinfo);
    int samples = cinfo.output_width * cinfo.output_components;
    int width = cinfo.output_width;
    int height = cinfo.output_height;
    int components = cinfo.output_components;
    (void)height;
    JSAMPARRAY row = (*cinfo.mem->alloc_sarray)((j_common_ptr)&cinfo, JPOOL_IMAGE, samples, 1);
    for (JDIMENSION y = 0; y < cinfo.output_height; y++)
    {
        jpeg_read_scanlines(&cinfo, row, 1);
        if ((int)y < info->height)
        {
            JpgCopyRow(row[0], destination, width, components, cinfo.out_color_space, argb);
            destination += rowbytes;
        }
    }
    jpeg_finish_decompress(&cinfo);
    jpeg_destroy_decompress(&cinfo);
    return ok;
}

// 100226ad.  The decompressor lives only inside info() and read(); the handle is all there is.
int GCALL JPG_close(void *handle)
{
    int result = 0;
    if (handle)
        result = gfree(handle);
    return result;
}

GIMEX_BOUNDARY_WRITE(JPG)
