// FaceInRace: the driver-photo converter behind gimme.dll's only export, ConvertFile.
// gimme.dll 3a43b0f6…, VA 100010b0–1000315d, PDB D:\dev\FaceInRace\Debug\FaceInRace.pdb.
// The source file name is not attested; the function names here are role names except the
// export.  Porsche.exe calls ConvertFile from 004dbe36 (FUN_004dbba0).
//
// GIMEX_FIX_DESCRIPTOR_COPY selects the fixed variant: descriptor copies keep the source's
// own size, as the same-size branch of ConvertImage already does.  The faithful variant
// copies GINFO_SIZE_LEGACY bytes, which leaves a shape descriptor (0x2aa4) claiming a size
// larger than its block; see runs/432-gimme-dll/README.md.

#include <windows.h>
#include <string.h>
#include <stdlib.h>

#include "../../_sem_arquivo/gimex/gimex.h"

// The original fills debug stack memory with 0xcc; filter values it leaves unset keep that.
#define DEBUG_STACK_FILL ((int)0xcccccccc)

// 100010b0.
BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    return TRUE;
}

// Allocates the copy of a descriptor.  This is the defect: FaceInRace was built with the
// legacy GINFO, so sizeof(GINFO) was GINFO_SIZE_LEGACY, while the copied size field may say
// GINFO_SIZE_SHAPE.
static GINFO *CopyDescriptor(const GINFO *source)
{
#ifdef GIMEX_FIX_DESCRIPTOR_COPY
    GINFO *copy = (GINFO *)galloc(source->size);
    memcpy(copy, source, source->size);
#else
    GINFO *copy = (GINFO *)galloc(GINFO_SIZE_LEGACY);
    memcpy(copy, source, GINFO_SIZE_LEGACY);
#endif
    return copy;
}

static int RowBytes(const GINFO *info)
{
    return info->width * info->bpp / 8;
}

static void CopyPixels(GIMAGE *destination, const GIMAGE *source)
{
    destination->rowbytes = source->rowbytes;
    destination->pixels = (unsigned char *)galloc(destination->rowbytes * destination->info->height);
    memcpy(destination->pixels, source->pixels, destination->rowbytes * destination->info->height);
}

// 10002ba0.
static int IntPower(int base, int exponent)
{
    if (exponent == 0)
        return 1;
    return IntPower(base, exponent - 1) * base;
}

// 100030e0.
static void SeedRandom(unsigned seed)
{
    srand(seed);
}

// 10003130.
static int Random(void)
{
    return rand() >> 8;
}

// 10002fa0.  Replaces the bits below step with random ones.
static unsigned RandomLowBits(unsigned value, int step)
{
    return (value & ~(step - 1)) + (Random() & (step - 1));
}

// 10003000.  Random-threshold rounding to a multiple of step, clamped to 0..255.
static int DitherChannel(int value, int step)
{
    value -= step / 2;
    if ((unsigned)(Random() & (step - 1)) < (unsigned)(value & (step - 1)))
        value += step;
    if (value > 255)
        value = 255;
    if (value < 0)
        value = 0;
    return value;
}

// 10001c10.
static int GetChannelBits(const GINFO *info, unsigned char *bits)
{
    if (!info || !bits)
        return 0;
    bits[0] = (unsigned char)info->alphabits;
    bits[1] = (unsigned char)info->redbits;
    bits[2] = (unsigned char)info->greenbits;
    bits[3] = (unsigned char)info->bluebits;
    return 1;
}

static int MinEight(int bits)
{
    return bits < 9 ? bits : 8;
}

// 10002870.  Derives alpha/red/green/blue widths from a depth; explicit bits win.
static void SetChannelBits(GIMAGE *image, int depth, const unsigned char *bits)
{
    GINFO *info = image->info;
    if (depth >= 9 && depth <= 24)
    {
        info->redbits = MinEight(depth / 3);
        info->greenbits = MinEight(depth - depth / 3 * 2);
        info->bluebits = MinEight(depth / 3);
        info->alphabits = 0;
    }
    else if (depth >= 25 && depth <= 32)
    {
        info->redbits = MinEight(depth / 3);
        info->greenbits = MinEight(depth / 3);
        info->bluebits = MinEight(depth / 3);
        info->alphabits = info->depth - MinEight(depth / 3) * 3;
    }
    else if (depth > 0 && depth < 9)
    {
        info->redbits = 8;
        info->greenbits = 8;
        info->bluebits = 8;
        info->alphabits = 8;
    }
    if (bits)
    {
        info->alphabits = bits[0];
        info->redbits = bits[1];
        info->greenbits = bits[2];
        info->bluebits = bits[3];
    }
}

// 10002c10.  Cuts every 32-bit channel down to its target width.  mode 0 truncates, 1 dithers,
// 2 randomises the dropped bits.  The loop runs x outside y, as in the original.
static void ReduceChannels(const GINFO *sourceinfo, const unsigned char *source, int sourcerow,
                           const GINFO *info, unsigned char *destination, int destinationrow, int mode)
{
    int alphastep = 1 << ((8 - info->alphabits) & 31);
    int redstep = 1 << ((8 - info->redbits) & 31);
    int greenstep = 1 << ((8 - info->greenbits) & 31);
    int bluestep = 1 << ((8 - info->bluebits) & 31);
    if (info->alphabits == 0)
        alphastep = 1;
    int width = info->width;
    int height = info->height;
    SeedRandom(0xfb123456);
    for (int x = 0; x < width; ++x)
    {
        for (int y = 0; y < height; ++y)
        {
            const unsigned char *in = source + x * 4 + y * sourcerow;
            unsigned char *out = destination + x * 4 + y * destinationrow;
            unsigned alpha = in[3];
            unsigned red = in[2];
            unsigned green = in[1];
            unsigned blue = in[0];
            if (mode == 0)
            {
                alpha &= ~(alphastep - 1);
                red &= ~(redstep - 1);
                green &= ~(greenstep - 1);
                blue &= ~(bluestep - 1);
            }
            else if (mode == 1)
            {
                alpha = DitherChannel(alpha, alphastep) & ~(alphastep - 1);
                red = DitherChannel(red, redstep) & ~(redstep - 1);
                green = DitherChannel(green, greenstep) & ~(greenstep - 1);
                blue = DitherChannel(blue, bluestep) & ~(bluestep - 1);
            }
            else if (mode == 2)
            {
                alpha = RandomLowBits(alpha, alphastep);
                red = RandomLowBits(red, redstep);
                green = RandomLowBits(green, greenstep);
                blue = RandomLowBits(blue, bluestep);
            }
            out[3] = (unsigned char)alpha;
            out[2] = (unsigned char)red;
            out[1] = (unsigned char)green;
            out[0] = (unsigned char)blue;
        }
    }
}

// 10001cb0.  Raises the depth: palette to true colour, or a wider palette/channel layout.
static GIMAGE *ExpandImage(const GIMAGE *source, int depth, const unsigned char *bits)
{
    GIMAGE *result = (GIMAGE *)galloc(sizeof(GIMAGE));
    const GINFO *in = source->info;
    if (in->depth < depth && depth < 33)
    {
        if (in->depth < 9 && depth > 8)
        {
            result->info = CopyDescriptor(in);
            SetChannelBits(result, depth, bits);
            result->info->numcolours = 0;
            result->info->bpp = 32;
            result->info->depth = depth;
            result->rowbytes = RowBytes(result->info);
            result->pixels = (unsigned char *)galloc(result->rowbytes * result->info->height);
            for (int y = 0; y < in->height; ++y)
            {
                const unsigned char *index = source->pixels + source->rowbytes * y;
                GCOLOUR *out = (GCOLOUR *)(result->pixels + result->rowbytes * y);
                for (int x = 0; x < in->width; ++x)
                    *out++ = in->colour[*index++];
            }
        }
        else if (in->depth < 9 || depth < 9)
        {
            if (in->depth < 9 && depth < 9)
            {
                int colours = IntPower(2, depth) - 1;
                result->info = CopyDescriptor(in);
                CopyPixels(result, source);
                SetChannelBits(result, depth, bits);
                result->info->depth = depth;
                result->info->bpp = 8;
                result->info->numcolours = result->info->alphabits == 0 ? colours : colours + 1;
            }
        }
        else
        {
            result->info = CopyDescriptor(in);
            CopyPixels(result, source);
            SetChannelBits(result, depth, bits);
            result->info->depth = depth;
        }
    }
    else
    {
        result->info = CopyDescriptor(in);
        CopyPixels(result, source);
    }
    return result;
}

// Runs one filter over an image and collects its output as a new image.
static void ReadFilterOutput(void *filter, GIMAGE *result)
{
    result->info = GFILTER_info(filter, 0);
    result->rowbytes = RowBytes(result->info);
    result->pixels = (unsigned char *)galloc(result->rowbytes * result->info->height);
    GFILTER_read(filter, result->info, result->pixels, result->rowbytes);
    GFILTER_close(filter);
}

// 10002340.  Lowers the depth: Wu quantizer plus Remap for palettes, channel truncation above.
static GIMAGE *ReduceImage(GIMAGE *source, int depth, const unsigned char *bits)
{
    GIMAGE *result = (GIMAGE *)galloc(sizeof(GIMAGE));
    if (depth < source->info->bpp && depth > 0)
    {
        if (depth > 8)
        {
            result->info = CopyDescriptor(source->info);
            result->info->numcolours = 0;
            result->info->bpp = 32;
            result->info->depth = depth;
            SetChannelBits(result, depth, bits);
            result->rowbytes = RowBytes(result->info);
            result->pixels = (unsigned char *)galloc(result->rowbytes * result->info->height);
            ReduceChannels(source->info, source->pixels, source->rowbytes, result->info, result->pixels,
                           result->rowbytes, 0);
        }
        else
        {
            int colours = IntPower(2, depth) - 1;
            int *remap = (int *)galloc(16);
            int used[256];
            for (int i = 0; i < 256; ++i)
                used[i] = 1;   // never read
            static const char quantizer[] = "Wu";
            if (strcmp(quantizer, "4D Wu") != 0)
                ++colours;
            GQUANT_find(quantizer);
            void *quant = GQUANT_open();
            GQUANT_add(quant, source->info, source->pixels, source->rowbytes);
            int exact;
            remap[2] = (int)GQUANT_make(quant, colours, &exact);
            // As compiled: an inexact palette stores exact + 0x100, which gfree later rejects.
            remap[3] = exact == 0 ? exact + 0x100 : 0;
            remap[1] = colours;
            remap[0] = 0;
            void *values[2] = { remap };
            void *filter = (void *)DEBUG_STACK_FILL;   // read even if GFILTER_open leaves it unset
            GFILTER_find("Remap");
            GFILTER_open(&filter, 1, source, 1, values);
            if (filter)
                ReadFilterOutput(filter, result);
            if (remap[3])
                gfree((void *)remap[3]);
            gfree((void *)remap[2]);
            gfree(remap);
            if (strcmp(quantizer, "4D Wu") == 0)
            {
                GCOLOUR *last = &result->info->colour[colours];
                last->b = last->g = last->r = last->a = 0;
            }
            result->info->numcolours = colours;
            result->info->bpp = 8;
            result->info->depth = depth;
            SetChannelBits(result, depth, bits);
        }
    }
    else
    {
        result->info = CopyDescriptor(source->info);
        CopyPixels(result, source);
    }
    return result;
}

// 10001930.  Crops the centre of the image to the aspect ratio width:height.
static GIMAGE *CropToAspect(GIMAGE *source, int width, int height)
{
    void *filter = 0;
    GIMAGE *result = (GIMAGE *)galloc(sizeof(GIMAGE));
    const GINFO *in = source->info;
    bool keepwidth = false;
    float aspect = (float)((double)width / height);
    float cropwidth = (float)((double)in->height * aspect);
    float cropheight = (float)in->height;
    if ((double)in->width < cropwidth || (double)in->height < cropheight)
    {
        cropwidth = (float)in->width;
        cropheight = (float)((double)in->width / aspect);
    }
    else
    {
        keepwidth = true;
    }
    int left, top;
    if (keepwidth)
    {
        left = (int)(((double)in->width - cropwidth) / 2.0f);
        top = 0;
    }
    else
    {
        left = 0;
        top = (int)(((double)in->height - cropheight) / 2.0f);
    }
    if (in->width == width && in->height == height)
    {
        result->info = CopyDescriptor(in);
        CopyPixels(result, source);
    }
    else
    {
        GFILTERVALUE values[5] = {
            { left, DEBUG_STACK_FILL }, { top, DEBUG_STACK_FILL }, { (int)cropwidth, DEBUG_STACK_FILL },
            { (int)cropheight, DEBUG_STACK_FILL }, { 0, DEBUG_STACK_FILL } };
        GFILTER_find("Crop");
        GFILTER_open(&filter, 1, source, 4, values);
        result->info = GFILTER_info(filter, 0);
        result->rowbytes = RowBytes(result->info);
        result->pixels = (unsigned char *)galloc(result->rowbytes * result->info->height);
        GFILTER_read(filter, result->info, result->pixels, result->rowbytes);
        GFILTER_close(filter);
    }
    return result;
}

// 10002160.  Rescales with the "Size" filter.
static GIMAGE *SizeImage(GIMAGE *source, int width, int height)
{
    void *filter = 0;
    GIMAGE *result = (GIMAGE *)galloc(sizeof(GIMAGE));
    if (source->info->width == width && source->info->height == height)
    {
        result->info = CopyDescriptor(source->info);
        CopyPixels(result, source);
    }
    else
    {
        GFILTERVALUE values[4] = {
            { width, DEBUG_STACK_FILL }, { height, DEBUG_STACK_FILL }, { 0, DEBUG_STACK_FILL },
            { 0, DEBUG_STACK_FILL } };
        GFILTER_find("Size");
        GFILTER_open(&filter, 1, source, 4, values);
        ReadFilterOutput(filter, result);
    }
    return result;
}

static void FreeImage(GIMAGE *image)
{
    gfree(image->info);
    gfree(image->pixels);
    gfree(image);
}

// 10001450.  Brings an image to width×height (0 keeps the aspect ratio) and depth bits
// (0 keeps bpp, at most 32).  A size change crops to the target aspect first.
static GIMAGE *ConvertImage(GIMAGE *source, int width, int height, int depth)
{
    GIMAGE *result;
    const GINFO *in = source->info;
    if (width < 0)
        width = 0;
    if (height < 0)
        height = 0;
    int targetwidth, targetheight;
    if (width == 0 && height != 0)
    {
        targetwidth = (int)((double)in->width * height / in->height + 0.5);
        targetheight = height;
    }
    else if (width != 0 && height == 0)
    {
        targetwidth = width;
        targetheight = (int)((double)in->height * width / in->width + 0.5);
    }
    else if (width != 0 && height != 0)
    {
        targetwidth = width;
        targetheight = height;
    }
    else
    {
        targetwidth = in->width;
        targetheight = in->height;
    }
    if (depth > 32)
        depth = 32;
    if (depth < 0)
        depth = 0;
    int targetdepth = depth ? depth : in->bpp;

    if (targetdepth == in->depth && in->height == targetheight && in->width == targetwidth)
    {
        result = (GIMAGE *)galloc(sizeof(GIMAGE));
        result->info = (GINFO *)galloc(in->size);
        memcpy(result->info, in, in->size);
        result->pixels = (unsigned char *)galloc(source->rowbytes * in->height);
        memcpy(result->pixels, source->pixels, source->rowbytes * in->height);
        result->rowbytes = source->rowbytes;
        return result;
    }

    unsigned char bits[4];
    GetChannelBits(in, bits);
    const unsigned char *keepbits = targetdepth < 9 ? bits : 0;
    if (in->height == targetheight && in->width == targetwidth && in->depth > 8)
    {
        if (in->depth > targetdepth)
            result = ReduceImage(source, targetdepth, keepbits);
        else
            result = ExpandImage(source, targetdepth, keepbits);
        return result;
    }

    GIMAGE *sized;
    int truecolourdepth = bits[0] + bits[1] + bits[2] + bits[3];
    if (in->depth <= 8)
    {
        GIMAGE *expanded = ExpandImage(source, truecolourdepth, bits);
        GIMAGE *cropped = CropToAspect(expanded, targetwidth, targetheight);
        sized = SizeImage(cropped, targetwidth, targetheight);
        FreeImage(expanded);
    }
    else
    {
        GIMAGE *cropped = CropToAspect(source, targetwidth, targetheight);
        sized = SizeImage(cropped, targetwidth, targetheight);
    }
    // The cropped intermediates are never freed in the original.
    if (sized->info->depth > targetdepth)
        result = ReduceImage(sized, targetdepth, keepbits);
    else
        result = ExpandImage(sized, targetdepth, keepbits);
    FreeImage(sized);
    return result;
}

// 100010e0, exported as ConvertFile.  Reads image 'frame' of source, converts it to the
// 54×64, 16-bit driver portrait and writes it with the module chosen by destination's
// extension (FSH when there is none or it is unknown).  Always returns 1.
extern "C" __declspec(dllexport) char __cdecl ConvertFile(const char *source, const char *destination, int frame)
{
    char foundname[256] = "";
    int depth = 16;
    if (GIMEX_ok())
    {
        GSTREAM *stream = GIMEX_openfile(source, foundname);
        if (stream && GIMEX_is(stream))
        {
            GABOUT *about = GIMEX_about();
            if (about)
                GIMEX_get();
            gfree(about);

            void *handle;
            GIMEX_open(&handle, stream, source, frame);
            GINFO *info = GIMEX_info(handle, frame);
            unsigned char *pixels = (unsigned char *)galloc(info->width * info->height * info->bpp / 8);
            GIMEX_read(handle, info, pixels, info->width * info->bpp / 8);
            GIMEX_close(handle);
            gclose(stream);

            GIMAGE image;
            image.info = info;
            image.rowbytes = info->width * info->bpp / 8;
            image.pixels = pixels;
            GIMAGE *portrait = ConvertImage(&image, 54, 64, depth);
            GINFO *portraitinfo = portrait->info;
            unsigned char *portraitpixels = portrait->pixels;
            portraitinfo->centrex = 0;
            portraitinfo->centrey = 0;
            portraitinfo->positionx = 0;
            portraitinfo->positiony = 0;

            if (strstr(destination, "."))
            {
                if (!GIMEX_find(strstr(destination, ".") + 1, 0))
                    GIMEX_find("fsh", 0);
            }
            else
            {
                GIMEX_find("fsh", 0);
            }
            gfree(GIMEX_about());

            GSTREAM *output = gwopen(destination);
            if (output)
            {
                GIMEX_wopen(&handle, output, destination, 1);
                GIMEX_write(handle, portraitinfo, portraitpixels, portraitinfo->width * portraitinfo->bpp / 8);
                GIMEX_wclose(handle);
                gclose(output);
            }
            gfree(pixels);
            gfree(info);
        }
        GIMEX_end();
    }
    return 1;
}
