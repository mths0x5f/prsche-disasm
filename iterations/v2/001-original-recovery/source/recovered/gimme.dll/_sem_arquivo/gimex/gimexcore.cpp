// GIMEX core: dispatch to the current format module, filter and quantizer, format detection
// and lookup.  gimme.dll 3a43b0f6…, VA 100049c0–10005a3f.  Built without /GZ, unlike the
// FaceInRace code before it, so it comes from a separately compiled library.  Function names
// are role names (functions.json).

#include <string.h>

#include "gimex.h"

static int currentmodule;     // 0x10449bb4
static int currentfilter;     // 0x10449bb8
static int currentquantizer;  // 0x10449bbc

// ---------------------------------------------------------------------------------------------
// Format modules

// 10004e96, 10004ea0.
int GCALL GIMEX_ok(void)
{
    return 1;
}

void GCALL GIMEX_end(void)
{
}

// 10005161.
int GCALL GIMEX_count(void)
{
    int count = 0;
    while (gimexmodules[count].about)
        ++count;
    return count;
}

// 10004fdf, 10005005.
void GCALL GIMEX_set(int module)
{
    if (module >= GIMEX_count() || module < 0)
        module = 0;
    currentmodule = module;
}

int GCALL GIMEX_get(void)
{
    return currentmodule;
}

// 10004ea5 … 10004fc5: the current module's entry points.
GABOUT *GCALL GIMEX_about(void)
{
    return gimexmodules[currentmodule].about();
}

int GCALL GIMEX_is(GSTREAM *stream)
{
    return gimexmodules[currentmodule].is(stream);
}

int GCALL GIMEX_open(void **handle, GSTREAM *stream, const char *name, int frame)
{
    return gimexmodules[currentmodule].open(handle, stream, name, frame);
}

// 10004ef8.
int GCALL GIMEX_open1(void **handle, GSTREAM *stream, const char *name)
{
    return gimexmodules[currentmodule].open(handle, stream, name, 1);
}

GINFO *GCALL GIMEX_info(void *handle, int frame)
{
    return gimexmodules[currentmodule].info(handle, frame);
}

int GCALL GIMEX_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    return gimexmodules[currentmodule].read(handle, info, pixels, rowbytes);
}

int GCALL GIMEX_close(void *handle)
{
    return gimexmodules[currentmodule].close(handle);
}

int GCALL GIMEX_wopen(void **handle, GSTREAM *stream, const char *name, int frames)
{
    return gimexmodules[currentmodule].wopen(handle, stream, name, frames);
}

int GCALL GIMEX_write(void *handle, const GINFO *info, const void *pixels, int rowbytes)
{
    return gimexmodules[currentmodule].write(handle, info, pixels, rowbytes);
}

int GCALL GIMEX_wclose(void *handle)
{
    return gimexmodules[currentmodule].wclose(handle);
}

// 10004b86.  ASCII case-insensitive compare; stops at the end of the first string.
static int CompareNoCase(const char *first, const char *second)
{
    unsigned a, b;
    for (;;)
    {
        unsigned char c = (unsigned char)*first;
        a = (c >= 'A' && c <= 'Z') ? c + 0x20 : c;
        c = (unsigned char)*second;
        b = (c >= 'A' && c <= 'Z') ? c + 0x20 : c;
        if (a != b || *first == 0)
            break;
        ++second;
        ++first;
    }
    return (int)(a - b);
}

// 100049c0.  Scores every module and selects the best one.  Modules that cannot detect by
// content match the file name against their names (50, 80, 95); the others score is() and
// lose 10 points when the extension is not theirs.  A score of 100 stops the search.
int GCALL GIMEX_detect(const char *name, GSTREAM *stream)
{
    int best = 0;
    int bestmodule = 0;
    for (int module = 0; module < GIMEX_count() && best < 100; ++module)
    {
        GABOUT *about = gimexmodules[module].about();
        if (!about)
            continue;
        int score = 0;
        if (!(about->flags & GABOUT_FLAG_DETECT_BY_CONTENT))
        {
            if (CompareNoCase(name, about->shortname) == 0)
                score = 50;
            if (CompareNoCase(name, about->longname) == 0)
                score = 80;
            if (CompareNoCase(name, about->name) == 0)
                score = 95;
        }
        else
        {
            if (stream)
                score = (int)((unsigned)gimexmodules[module].is(stream) * 100u) / 100;
            if (score > 10)
            {
                bool ownextension = false;
                const char *extension = strrchr(name, '.');
                if (extension)
                    for (int i = 0; i < 8; ++i)
                        if (CompareNoCase(about->extension[i], extension) == 0)
                            ownextension = true;
                if (!ownextension)
                    score -= 10;
            }
        }
        if (best < score)
        {
            best = score;
            bestmodule = module;
        }
        gfree(about);
    }
    if (best == 0)
        bestmodule = 0;
    GIMEX_set(bestmodule);
    return bestmodule;
}

// 10004c2d.  Opens name, or else name plus each extension of the modules that detect by
// content, and selects the module for it.  foundname receives the name that was opened.
GSTREAM *GCALL GIMEX_openfile(const char *name, char *foundname)
{
    char tryname[512];
    strcpy(tryname, name);
    GSTREAM *stream = gopen(tryname);
    bool found = true;
    if (!stream)
    {
        found = false;
        for (int module = 0; module < GIMEX_count() && !found; ++module)
        {
            GABOUT *about = gimexmodules[module].about();
            if (!about)
                continue;
            if ((about->flags & GABOUT_FLAG_DETECT_BY_CONTENT) && foundname)
            {
                for (int i = 0; i < 8; ++i)
                {
                    if (!about->extension[i][0])
                        continue;
                    strcpy(tryname, name);
                    strcat(tryname, about->extension[i]);
                    stream = gopen(tryname);
                    if (stream)
                    {
                        if (gimexmodules[module].is(stream))
                        {
                            found = true;
                            break;
                        }
                        gclose(stream);
                        stream = 0;
                    }
                }
            }
            gfree(about);
        }
    }
    int module = 0;
    if (found)
    {
        module = GIMEX_detect(name, stream);
        if (module == 0)
        {
            tryname[0] = '\0';
            if (stream)
                gclose(stream);
            stream = 0;
        }
    }
    GIMEX_set(module);
    if (foundname)
        strcpy(foundname, tryname);
    return stream;
}

// 1000500f.  Selects the first module (after module 0) listing the extension; one leading
// '-', '+' or '.' is skipped and the extension ends at a blank or '?'.
int GCALL GIMEX_find(const char *extension, int *extensionindex)
{
    int found = 0;
    const char *text = extension;
    if (*text == '-' || *text == '+' || *text == '.')
        ++text;
    char dotted[80];
    char *out = dotted;
    *out++ = '.';
    if ((unsigned char)*text > ' ')
    {
        while ((unsigned char)*text > ' ' && *text != '?')
            *out++ = *text++;
        *out++ = '\0';
        for (int i = 0; i < 8 && !found; ++i)
        {
            for (int module = 1; module < GIMEX_count() && !found; ++module)
            {
                GIMEX_set(module);
                GABOUT *about = GIMEX_about();
                if (!about)
                    continue;
                if (_stricmp(dotted, about->extension[i]) == 0)
                {
                    found = module;
                    if (extensionindex)
                        *extensionindex = i;
                }
                gfree(about);
            }
        }
    }
    GIMEX_set(found);
    return found;
}

// 1000518d.  Frees a GIMAGE; one built by GFILTER_apply holds its descriptor inline.
void GCALL GIMEX_freeimage(GIMAGE *image)
{
    if (!image)
        return;
    if ((void *)image->info != (void *)(image + 1))
    {
        if (image->pixels)
            gfree(image->pixels);
        if (image->info)
            gfree(image->info);
    }
    gfree(image);
}

// 100051ef.  Loads one frame of a file into a new GIMAGE (null on failure).
GIMAGE *GCALL GIMEX_load(const char *name, int frame)
{
    GSTREAM *stream = 0;
    void *handle = 0;
    GABOUT *about = 0;
    GINFO *info = 0;
    unsigned char *pixels = 0;
    GIMAGE *image = 0;
    int ok = 0;
    int previous = GIMEX_get();
    stream = GIMEX_openfile(name, 0);
    if (stream)
    {
        ok = GIMEX_open(&handle, stream, name, 0);
        if (ok)
        {
            about = GIMEX_about();
            if (about)
            {
                info = GIMEX_info(handle, frame);
                if (info)
                {
                    pixels = (unsigned char *)galloc(info->width * info->height * info->bpp / 8);
                    if (pixels)
                    {
                        ok = GIMEX_read(handle, info, pixels, info->width * info->bpp / 8);
                        if (ok)
                        {
                            ok = 0;
                            image = (GIMAGE *)galloc(sizeof(GIMAGE));
                            if (image)
                            {
                                ok = 1;
                                image->info = info;
                                image->pixels = pixels;
                                image->rowbytes = info->width * info->bpp / 8;
                            }
                        }
                    }
                }
            }
        }
    }
    if (about)
        gfree(about);
    if (handle)
        GIMEX_close(handle);
    if (stream)
        gclose(stream);
    if (!ok)
    {
        GIMEX_freeimage(image);
        image = 0;
    }
    GIMEX_set(previous);
    return image;
}

// ---------------------------------------------------------------------------------------------
// Filters (entry points may be null; the dispatchers then return 0)

// 10005390, 1000539a.
int GCALL GFILTER_ok(void)
{
    return 1;
}

void GCALL GFILTER_end(void)
{
}

// 100055ba.
int GCALL GFILTER_count(void)
{
    int count = 0;
    while (gimexfilters[count].about)
        ++count;
    return count;
}

// 1000558a, 100055b0.
void GCALL GFILTER_set(int filter)
{
    if (filter >= GFILTER_count() || filter < 0)
        filter = 0;
    currentfilter = filter;
}

int GCALL GFILTER_get(void)
{
    return currentfilter;
}

// 1000539f … 1000547c.
GFILTERABOUT *GCALL GFILTER_about(void)
{
    if (!gimexfilters[currentfilter].about)
        return 0;
    return gimexfilters[currentfilter].about();
}

int GCALL GFILTER_open(void **handle, int images, GIMAGE *image, int values, void *value)
{
    if (!gimexfilters[currentfilter].open)
        return 0;
    return gimexfilters[currentfilter].open(handle, images, image, values, value);
}

GINFO *GCALL GFILTER_info(void *handle, int frame)
{
    if (!gimexfilters[currentfilter].info)
        return 0;
    return gimexfilters[currentfilter].info(handle, frame);
}

int GCALL GFILTER_read(void *handle, GINFO *info, void *pixels, int rowbytes)
{
    if (!gimexfilters[currentfilter].read)
        return 0;
    return gimexfilters[currentfilter].read(handle, info, pixels, rowbytes);
}

int GCALL GFILTER_close(void *handle)
{
    if (!gimexfilters[currentfilter].close)
        return 0;
    return gimexfilters[currentfilter].close(handle);
}

// 100054ae.  Selects the filter whose about name matches exactly (no null check on about).
int GCALL GFILTER_find(const char *name)
{
    int found = 0;
    bool matched = false;
    for (int filter = 0; filter < GFILTER_count() && !matched; ++filter)
    {
        GFILTER_set(filter);
        char *about = (char *)GFILTER_about();
        if (strcmp(about + 0x48, name) == 0)
        {
            found = filter;
            matched = true;
        }
        gfree(about);
    }
    GFILTER_set(found);
    return found;
}

// 100055e6.  Applies the named filter to one image; the result is a single block holding the
// GIMAGE, a copy of the output descriptor and the pixels.
GIMAGE *GCALL GFILTER_apply(const char *name, GIMAGE *image, int values, void *value)
{
    GIMAGE *result = 0;
    int previous = GFILTER_get();
    GFILTER_find(name);
    gfree(GFILTER_about());
    void *handle;
    if (GFILTER_open(&handle, 1, image, values, value))
    {
        GINFO *info = GFILTER_info(handle, 0);
        if (info)
        {
            int rowbytes = info->width * info->bpp / 8;
            result = (GIMAGE *)galloc(info->size + sizeof(GIMAGE) + rowbytes * info->height);
            if (result)
            {
                result->rowbytes = rowbytes;
                result->info = (GINFO *)(result + 1);
                result->pixels = (unsigned char *)result + info->size + sizeof(GIMAGE);
                memcpy(result->info, info, info->size);
                if (!GFILTER_read(handle, info, result->pixels, rowbytes))
                {
                    gfree(result);
                    result = 0;
                }
            }
            gfree(info);
        }
        GFILTER_close(handle);
    }
    GFILTER_set(previous);
    return result;
}

// 1000571f.  Runs the current filter and returns a separately allocated GIMAGE.
GIMAGE *GCALL GFILTER_run(int images, GIMAGE *image, int values, void *value)
{
    unsigned char *pixels = 0;
    GINFO *info = 0;
    GIMAGE *result = 0;
    GFILTERABOUT *about = GFILTER_about();
    if (about)
    {
        void *handle;
        if (GFILTER_open(&handle, images, image, values, value))
        {
            info = GFILTER_info(handle, 0);
            if (info)
            {
                int rowbytes = info->width * info->bpp / 8;
                pixels = (unsigned char *)galloc(info->height * rowbytes);
                if (pixels)
                {
                    result = (GIMAGE *)galloc(sizeof(GIMAGE));
                    if (result)
                    {
                        result->info = info;
                        result->pixels = pixels;
                        result->rowbytes = rowbytes;
                        if (!GFILTER_read(handle, info, pixels, rowbytes))
                        {
                            gfree(result);
                            result = 0;
                        }
                    }
                }
            }
            GFILTER_close(handle);
        }
        gfree(about);
    }
    if (!result && pixels)
        gfree(pixels);
    if (!result && info)
        gfree(info);
    return result;
}

// 10005859.
void GCALL GFILTER_freeimage(GIMAGE *image)
{
    gfree(image->info);
    gfree(image->pixels);
    gfree(image);
}

// ---------------------------------------------------------------------------------------------
// Quantizers

// 10005880, 1000588a.
int GCALL GQUANT_ok(void)
{
    return 1;
}

void GCALL GQUANT_end(void)
{
}

// 1000592c.
int GCALL GQUANT_count(void)
{
    int count = 0;
    while (gimexquantizers[count].about)
        ++count;
    return count;
}

// 100058fc, 10005922.
void GCALL GQUANT_set(int quantizer)
{
    if (quantizer >= GQUANT_count() || quantizer < 0)
        quantizer = 0;
    currentquantizer = quantizer;
}

int GCALL GQUANT_get(void)
{
    return currentquantizer;
}

// 1000588f … 100058db.
GQUANTABOUT *GCALL GQUANT_about(void)
{
    return gimexquantizers[currentquantizer].about();
}

void *GCALL GQUANT_open(void)
{
    return gimexquantizers[currentquantizer].open();
}

int GCALL GQUANT_add(void *handle, const GINFO *info, const void *pixels, int rowbytes)
{
    return gimexquantizers[currentquantizer].add(handle, info, pixels, rowbytes);
}

GCOLOUR *GCALL GQUANT_make(void *handle, int colours, int *exact)
{
    return gimexquantizers[currentquantizer].make(handle, colours, exact);
}

// 10005958.  Selects the quantizer whose about name (+0x38) matches exactly.
int GCALL GQUANT_find(const char *name)
{
    int found = 0;
    bool matched = false;
    for (int quantizer = 0; quantizer < GQUANT_count() && !matched; ++quantizer)
    {
        GQUANT_set(quantizer);
        char *about = (char *)GQUANT_about();
        if (strcmp(about + 0x38, name) == 0)
        {
            found = quantizer;
            matched = true;
        }
        gfree(about);
    }
    GQUANT_set(found);
    return found;
}
