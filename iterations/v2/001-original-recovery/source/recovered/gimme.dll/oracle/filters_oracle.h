// Differential cases for the recovered Crop, Remap and Size filters and the Wu quantizer
// (included by gimme_oracle.cpp after Side, LoadOriginal and ApplyHeapMode).
//
//   gimme_oracle filters <original.dll> [--pad|--guard] [--only crop|size|remap|wu|reduce]
//
// Each side builds the same synthetic images with its own galloc, runs its own table entry
// (original 0x10432428 / 0x10432720 by index, recovered gimexfilters[] / gimexquantizers[]) and
// the results are compared: open/read results, the whole output descriptor (over its size) and
// the output pixels; for Wu the palette and the inverse table (except its never-written bytes
// 0xc..0xf).

#include <math.h>

#include "../_sem_arquivo/gimex/gimexfilter.h"

namespace filteroracle
{

struct Random
{
    unsigned state;
    unsigned Next()
    {
        state = state * 1103515245u + 12345u;
        return state >> 8;
    }
    int Range(int low, int high)   // inclusive
    {
        return low + (int)(Next() % (unsigned)(high - low + 1));
    }
};

// Description of one synthetic source image.
struct ImageSpec
{
    int width, height, bpp;
    unsigned seed;
    int content;      // 0 random, 1 few colours, 2 random with transparent pixels, 3 gradient
    int points;       // shape points at GINFO +0x458
};

static GIMAGE *BuildImage(const Side &side, const ImageSpec &spec)
{
    GIMAGE *image = (GIMAGE *)side.alloc(sizeof(GIMAGE));
    GINFO *info = (GINFO *)side.alloc(GINFO_SIZE_LEGACY);
    memset(info, 0, GINFO_SIZE_LEGACY);
    Random random = { spec.seed };
    info->tag = GTAG('S', 'H', 'P', 'I');
    info->size = GINFO_SIZE_LEGACY;
    info->version = GINFO_VERSION;
    info->frames = 1;
    info->width = spec.width;
    info->height = spec.height;
    info->bpp = spec.bpp;
    info->depth = spec.bpp;
    info->numcolours = spec.bpp == 8 ? 256 : 0;
    for (int i = 0; i < 256; ++i)
        *(unsigned *)&info->colour[i] = random.Next() ^ (random.Next() << 16);
    info->alphabits = info->redbits = info->greenbits = info->bluebits = 8;
    info->centrex = random.Range(-50, 50);
    info->centrey = random.Range(-50, 50);
    info->positionx = random.Range(-50, 50);
    info->positiony = random.Range(-50, 50);
    GINFO_pointcount(info) = spec.points;
    for (int p = 0; p < spec.points; ++p)
    {
        GINFO_point(info, p)[0] = random.Range(-100, 100);
        GINFO_point(info, p)[1] = random.Range(-100, 100);
    }
    image->info = info;
    image->rowbytes = spec.width * spec.bpp / 8;
    int bytes = image->rowbytes * spec.height;
    image->pixels = (unsigned char *)side.alloc(bytes > 0 ? bytes : 1);
    unsigned few[5];
    for (int i = 0; i < 5; ++i)
        few[i] = random.Next() ^ (random.Next() << 16);
    for (int y = 0; y < spec.height; ++y)
        for (int x = 0; x < spec.width; ++x)
        {
            unsigned value;
            if (spec.content == 1)
                value = few[random.Range(0, 4)];
            else if (spec.content == 3)
                value = 0xff000000u | (unsigned)(x * 255 / (spec.width > 1 ? spec.width - 1 : 1)) << 16 |
                        (unsigned)(y * 255 / (spec.height > 1 ? spec.height - 1 : 1)) << 8 | ((x + y) & 0xff);
            else
            {
                value = random.Next() ^ (random.Next() << 16);
                if (spec.content == 2 && random.Range(0, 3) == 0)
                    value &= 0x00ffffff;
            }
            unsigned char *pixel = image->pixels + y * image->rowbytes + x * spec.bpp / 8;
            if (spec.bpp == 8)
                *pixel = (unsigned char)value;
            else
                *(unsigned *)pixel = value;
        }
    return image;
}

static void FreeImage(const Side &side, GIMAGE *image)
{
    side.free(image->info);
    side.free(image->pixels);
    side.free(image);
}

struct FilterResult
{
    int opened, read;
    GINFO *info;
    unsigned char *pixels;
    int rowbytes;
};

static FilterResult RunFilter(const Side &side, const GFILTER &filter, GIMAGE *image, int values, void *value)
{
    FilterResult result = { 0, 0, 0, 0, 0 };
    void *handle = (void *)0xcccccccc;
    result.opened = filter.open(&handle, 1, image, values, value);
    if (result.opened)
    {
        result.info = filter.info(handle, 0);
        if (result.info)
        {
            result.rowbytes = result.info->width * result.info->bpp / 8;
            int bytes = result.rowbytes * result.info->height;
            result.pixels = (unsigned char *)side.alloc(bytes > 0 ? bytes : 1);
            if (bytes > 0)
                memset(result.pixels, 0x5a, bytes);
            result.read = filter.read(handle, result.info, result.pixels, result.rowbytes);
        }
        filter.close(handle);
    }
    return result;
}

static int CompareFilter(const char *label, FilterResult *r, int verbose)
{
    const char *what = 0;
    if (r[0].opened != r[1].opened || r[0].read != r[1].read || !r[0].info != !r[1].info)
        what = "results";
    else if (r[0].info && (r[0].info->size != r[1].info->size || memcmp(r[0].info, r[1].info, r[0].info->size)))
        what = "descriptor";
    else if (r[0].info && memcmp(r[0].pixels, r[1].pixels, r[0].rowbytes * r[0].info->height))
        what = "pixels";
    if (what || verbose)
        printf("%s: %s\n", label, what ? what : "MATCH");
    if (what && !strcmp(what, "pixels"))
        for (int i = 0; i < r[0].rowbytes * r[0].info->height; ++i)
            if (r[0].pixels[i] != r[1].pixels[i])
            {
                printf("  first pixel byte difference at %d: %02x/%02x\n", i, r[0].pixels[i], r[1].pixels[i]);
                break;
            }
    if (what && !strcmp(what, "descriptor"))
        for (int i = 0; i < r[0].info->size; ++i)
            if (((unsigned char *)r[0].info)[i] != ((unsigned char *)r[1].info)[i])
            {
                printf("  descriptor differs first at +%#x\n", i);
                break;
            }
    return what != 0;
}

static void FreeResult(const Side &side, FilterResult &r)
{
    if (r.info)
        side.free(r.info);
    if (r.pixels)
        side.free(r.pixels);
}

// Runs filter `index` on the image of `spec` with the same parameter slots on both sides.
static int FilterCase(int index, const ImageSpec &spec, int values, const GFILTERNUMBER *value, const char *label,
                      int *cases)
{
    Side sides[2] = { OriginalSide(), RecoveredSide() };
    const GFILTER *tables[2] = { (const GFILTER *)0x10432428, gimexfilters };
    FilterResult result[2];
    GIMAGE *image[2];
    GFILTERNUMBER slots[2][16];
    for (int s = 0; s < 2; ++s)
    {
        memcpy(slots[s], value, sizeof(slots[s]));
        image[s] = BuildImage(sides[s], spec);
        result[s] = RunFilter(sides[s], tables[s][index], image[s], values, slots[s]);
    }
    char text[200];
    sprintf(text, "%s %dx%dx%d seed %u values %d", label, spec.width, spec.height, spec.bpp, spec.seed, values);
    int failed = CompareFilter(text, result, 0);
    for (int s = 0; s < 2; ++s)
    {
        FreeResult(sides[s], result[s]);
        FreeImage(sides[s], image[s]);
    }
    ++*cases;
    return failed;
}

static void FillSlots(GFILTERNUMBER *slots)
{
    for (int i = 0; i < 16; ++i)
    {
        slots[i].integer = 0;
        ((int *)&slots[i])[1] = (int)0xcccccccc;
    }
}

static int CropCases(int *cases)
{
    int failures = 0;
    Random random = { 5 };
    for (int n = 0; n < 400; ++n)
    {
        ImageSpec spec = { random.Range(1, 40), random.Range(1, 40), random.Range(0, 1) ? 32 : 8, random.Next(),
                           random.Range(0, 3), random.Range(0, 3) };
        GFILTERNUMBER slots[16];
        FillSlots(slots);
        int values = n < 40 ? random.Range(0, 5) : random.Range(4, 5);
        slots[0].integer = random.Range(-10, spec.width + 5);
        slots[1].integer = random.Range(-10, spec.height + 5);
        slots[2].integer = random.Range(1, 50);
        slots[3].integer = random.Range(1, 50);
        slots[4].integer = (int)random.Next();
        failures += FilterCase(5, spec, values, slots, "crop", cases);
    }
    // FaceInRace CropToAspect: centred, 4 values, second words 0xcccccccc.
    static const int sizes[][4] = { { 256, 128, 64, 64 }, { 300, 200, 64, 32 }, { 64, 64, 128, 64 },
                                    { 100, 37, 16, 16 }, { 17, 99, 32, 64 } };
    for (int i = 0; i < 5; ++i)
    {
        ImageSpec spec = { sizes[i][0], sizes[i][1], 32, 1000u + i, 0, 1 };
        float aspect = (float)((double)sizes[i][2] / sizes[i][3]);
        float cropwidth = (float)((double)spec.height * aspect), cropheight = (float)spec.height;
        int left = 0, top = 0;
        if ((double)spec.width < cropwidth || (double)spec.height < cropheight)
        {
            cropwidth = (float)spec.width;
            cropheight = (float)((double)spec.width / aspect);
            top = (int)(((double)spec.height - cropheight) / 2.0f);
        }
        else
            left = (int)(((double)spec.width - cropwidth) / 2.0f);
        GFILTERNUMBER slots[16];
        FillSlots(slots);
        slots[0].integer = left;
        slots[1].integer = top;
        slots[2].integer = (int)cropwidth;
        slots[3].integer = (int)cropheight;
        failures += FilterCase(5, spec, 4, slots, "crop faceinrace", cases);
    }
    return failures;
}

static int SizeCases(int *cases, int tiny)
{
    int failures = 0;
    Random random = { 31 };
    int run = 0;
    for (int n = 0; n < 600; ++n)
    {
        ImageSpec spec = { random.Range(1, 48), random.Range(1, 48), 32, random.Next(), random.Range(0, 3),
                           random.Range(0, 3) };
        GFILTERNUMBER slots[16];
        FillSlots(slots);
        slots[0].integer = random.Range(1, 64);
        slots[1].integer = random.Range(1, 64);
        int values = random.Range(2, 7);
        slots[2].integer = random.Range(0, 8);
        slots[3].integer = random.Range(0, 2) == 0;
        slots[4].integer = random.Range(0, 1) ? 0 : (int)random.Next();
        slots[5].real = random.Range(0, 10) / 10.0;
        slots[6].real = random.Range(0, 10) / 10.0;
        // A source side under twice the support reflects contributions past both edges: the
        // original then reads outside the row buffer (heap data), so such cases are separate.
        int narrow = spec.width < 7 || spec.height < 7;
        if (narrow != tiny)
            continue;
        ++run;
        failures += FilterCase(31, spec, values, slots, tiny ? "size tiny" : "size", cases);
    }
    if (!tiny)
    {
        // FaceInRace SizeImage: {width, height, 0, 0}, Lanczos3, second words 0xcccccccc.
        static const int sizes[][4] = { { 128, 128, 64, 64 }, { 64, 32, 128, 64 }, { 200, 100, 64, 32 },
                                        { 33, 77, 16, 32 }, { 256, 256, 32, 32 }, { 40, 40, 41, 39 } };
        for (int i = 0; i < 6; ++i)
        {
            ImageSpec spec = { sizes[i][0], sizes[i][1], 32, 2000u + i, i % 4, 2 };
            GFILTERNUMBER slots[16];
            FillSlots(slots);
            slots[0].integer = sizes[i][2];
            slots[1].integer = sizes[i][3];
            failures += FilterCase(31, spec, 4, slots, "size faceinrace", cases);
        }
    }
    return failures;
}

static int RemapCases(int *cases)
{
    int failures = 0;
    Random random = { 6 };
    for (int n = 0; n < 200; ++n)
    {
        ImageSpec spec = { random.Range(1, 40), random.Range(1, 40), 32, random.Next(), random.Range(0, 3), 0 };
        int colours = random.Range(1, 256);
        int first = random.Range(0, 256 - colours);
        int inverse = n % 4 == 3;
        Side sides[2] = { OriginalSide(), RecoveredSide() };
        const GFILTER *tables[2] = { (const GFILTER *)0x10432428, gimexfilters };
        FilterResult result[2];
        GIMAGE *image[2];
        GREMAP *remap[2];
        unsigned seed = random.Next();
        for (int s = 0; s < 2; ++s)
        {
            Random palette = { seed };
            remap[s] = (GREMAP *)sides[s].alloc(sizeof(GREMAP));
            remap[s]->first = first;
            remap[s]->colours = colours;
            remap[s]->palette = (GCOLOUR *)sides[s].alloc(colours * sizeof(GCOLOUR));
            for (int c = 0; c < colours; ++c)
                *(unsigned *)&remap[s]->palette[c] = palette.Next() ^ (palette.Next() << 16);
            remap[s]->inverse = 0;
            if (inverse)
            {
                remap[s]->inverse = (unsigned char *)sides[s].alloc(64 * 64 * 64);
                for (int c = 0; c < 64 * 64 * 64; ++c)
                    remap[s]->inverse[c] = (unsigned char)palette.Next();
            }
            GFILTERNUMBER slots[16];
            FillSlots(slots);
            slots[0].integer = (int)remap[s];
            image[s] = BuildImage(sides[s], spec);
            result[s] = RunFilter(sides[s], tables[s][6], image[s], 1, slots);
        }
        char text[200];
        sprintf(text, "remap %dx%d colours %d first %d inverse %d", spec.width, spec.height, colours, first, inverse);
        failures += CompareFilter(text, result, 0);
        for (int s = 0; s < 2; ++s)
        {
            FreeResult(sides[s], result[s]);
            FreeImage(sides[s], image[s]);
            if (remap[s]->inverse)
                sides[s].free(remap[s]->inverse);
            sides[s].free(remap[s]->palette);
            sides[s].free(remap[s]);
        }
        ++*cases;
    }
    return failures;
}

// Wu over one or two images; with `reduce`, the palette then goes through Remap as in
// FaceInRace's ReduceImage (block {0, colours, palette, 0}).
static int WuCase(const ImageSpec *spec, int images, int colours, int wantinverse, int reduce, int *cases)
{
    Side sides[2] = { OriginalSide(), RecoveredSide() };
    const GQUANT *quant[2] = { (const GQUANT *)0x10432720, gimexquantizers };
    const GFILTER *tables[2] = { (const GFILTER *)0x10432428, gimexfilters };
    GIMAGE *image[2][2];
    int added[2][2];
    GCOLOUR *palette[2];
    unsigned char *inverse[2];
    FilterResult result[2];
    for (int s = 0; s < 2; ++s)
    {
        void *handle = quant[s][1].open();
        for (int i = 0; i < images; ++i)
        {
            image[s][i] = BuildImage(sides[s], spec[i]);
            added[s][i] = quant[s][1].add(handle, image[s][i]->info, image[s][i]->pixels, image[s][i]->rowbytes);
        }
        int exact = 0x77777777;
        palette[s] = quant[s][1].make(handle, colours, wantinverse ? &exact : 0);
        inverse[s] = wantinverse ? (unsigned char *)exact : 0;
        if (reduce)
        {
            GREMAP *remap = (GREMAP *)sides[s].alloc(sizeof(GREMAP));
            remap->first = 0;
            remap->colours = colours;
            remap->palette = palette[s];
            remap->inverse = 0;
            GFILTERNUMBER slots[16];
            FillSlots(slots);
            slots[0].integer = (int)remap;
            result[s] = RunFilter(sides[s], tables[s][6], image[s][0], 1, slots);
            sides[s].free(remap);
        }
    }
    const char *what = 0;
    for (int i = 0; i < images; ++i)
        if (added[0][i] != added[1][i])
            what = "add result";
    if (!what && memcmp(palette[0], palette[1], colours * sizeof(GCOLOUR)))
        what = "palette";
    if (!what && wantinverse &&
        (memcmp(inverse[0], inverse[1], 12) || memcmp(inverse[0] + 16, inverse[1] + 16, 0x40000)))
        what = "inverse";
    char text[200];
    sprintf(text, "wu %dx%dx%d content %d images %d colours %d inverse %d", spec[0].width, spec[0].height, spec[0].bpp,
            spec[0].content, images, colours, wantinverse);
    if (what)
        printf("%s: %s\n", text, what);
    if (what && !strcmp(what, "palette"))
        for (int c = 0; c < colours; ++c)
            if (memcmp(&palette[0][c], &palette[1][c], 4))
            {
                printf("  first palette difference at %d: %08x/%08x\n", c, *(unsigned *)&palette[0][c],
                       *(unsigned *)&palette[1][c]);
                break;
            }
    int failed = what != 0;
    if (reduce)
    {
        strcat(text, " reduce");
        failed |= CompareFilter(text, result, 0);
    }
    for (int s = 0; s < 2; ++s)
    {
        if (reduce)
            FreeResult(sides[s], result[s]);
        for (int i = 0; i < images; ++i)
            FreeImage(sides[s], image[s][i]);
        if (palette[s])
            sides[s].free(palette[s]);
        if (inverse[s])
            sides[s].free(inverse[s]);
    }
    ++*cases;
    return failed;
}

static int WuCases(int *cases, int reduce)
{
    int failures = 0;
    Random random = { 1 };
    static const int counts[] = { 1, 2, 3, 16, 64, 255, 256 };
    for (int n = 0; n < (reduce ? 40 : 120); ++n)
    {
        ImageSpec spec[2];
        int images = !reduce && random.Range(0, 3) == 0 ? 2 : 1;
        for (int i = 0; i < 2; ++i)
        {
            ImageSpec one = { random.Range(1, 64), random.Range(1, 64), 32, random.Next(), random.Range(0, 3), 0 };
            spec[i] = one;
        }
        if (n % 17 == 5 && !reduce)
            spec[0].bpp = 8;   // rejected by add(); Remap would read it as 32 bits
        int colours = n < 14 ? counts[n % 7] : random.Range(1, 256);
        failures += WuCase(spec, images, colours, n % 3 != 2, reduce, cases);
    }
    return failures;
}

static int Filters(int argc, char **argv)
{
    if (argc < 3)
        return 2;
    HMODULE original = LoadOriginal(argv[2]);
    ApplyHeapMode(original, argc, argv, 3);
    const char *only = 0;
    for (int i = 3; i + 1 < argc; ++i)
        if (!strcmp(argv[i], "--only"))
            only = argv[i + 1];
    for (int i = 3; i < argc; ++i)
        if (!strcmp(argv[i], "--x87math"))
            _set_SSE2_enable(0);   // CRT sin() on the x87 path (fsin), as the original's CRT
    struct
    {
        const char *name;
        int failures, cases;
    } sets[] = { { "crop", 0, 0 }, { "remap", 0, 0 }, { "size", 0, 0 }, { "sizetiny", 0, 0 }, { "wu", 0, 0 },
                 { "reduce", 0, 0 } };
    int total = 0;
    for (int i = 0; i < 6; ++i)
    {
        if (only ? strcmp(only, sets[i].name) != 0 : i == 3)
            continue;   // the tiny-source Size cases only on request
        switch (i)
        {
        case 0: sets[i].failures = CropCases(&sets[i].cases); break;
        case 1: sets[i].failures = RemapCases(&sets[i].cases); break;
        case 2: sets[i].failures = SizeCases(&sets[i].cases, 0); break;
        case 3: sets[i].failures = SizeCases(&sets[i].cases, 1); break;
        case 4: sets[i].failures = WuCases(&sets[i].cases, 0); break;
        case 5: sets[i].failures = WuCases(&sets[i].cases, 1); break;
        }
        printf("%-8s %4d cases, %d differ\n", sets[i].name, sets[i].cases, sets[i].failures);
        total += sets[i].failures;
    }
    printf("%s\n", total ? "FAIL" : "PASS");
    return total != 0;
}

} // namespace filteroracle
