// "TGV Movie" module 1.39 (L.Ancessi & F.Barchard): GIMEX module 27.
// gimme.dll 3a43b0f6…, entry points about 100b0390, is 100b055b, open 100b082c, info 100b1ba4, read 100b1d6a, close 100b1e08,
// wopen 100aa670, write 100aa763, wclose 100b031d.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100b0390.
GABOUT *TGV_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('T', 'G', 'V', 'i');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb4d7;
        about->unknown_14 = 0;
        about->unknown_18 = 18;
        about->mactype[0] = GTAG('T', 'G', 'V', 'i');
        strcpy(about->extension[0], ".tgv");
        strcpy(about->author, "L.Ancessi & F.Barchard");
        strcpy(about->moduleversion, "1.39");
        strcpy(about->shortname, "TGV");
        strcpy(about->longname, "TGV");
        strcpy(about->name, "TGV Movie");
    }
    return about;
}

// 100b0680.  A chunk tag is four characters in ' '..'z'.
static int IsChunkTag(const unsigned char *tag)
{
    for (int i = 0; i < 4; ++i)
        if (tag[i] < 0x20 || tag[i] > 0x7a)
            return 0;
    return 1;
}

// 100b07dd.  Reads the chunk body, or skips it in mode 1.
static int ReadChunkBody(GSTREAM *stream, void *body, int size, int mode)
{
    if (mode == 1)
        return gseek(stream, gtell(stream) + size);
    return gread(stream, body, size);
}

// 100b06f4.  Loads one chunk (8-byte header: tag, little-endian size including the header)
// into a new block; *size receives the chunk size whenever the header is plausible.
static unsigned char *ReadChunk(GSTREAM *stream, int *size, int mode)
{
    int got = 0;
    unsigned char *chunk = 0;
    unsigned char header[8];
    int position = gtell(stream);
    int length = glen(stream);
    if (position < length)
        got = gread(stream, header, 8);
    if (got)
    {
        int chunksize = ggeti(header + 4, 4);
        if (IsChunkTag(header) && chunksize + position <= length)
        {
            chunk = (unsigned char *)galloc(chunksize);
            if (chunk)
            {
                memcpy(chunk, header, 8);
                if (!ReadChunkBody(stream, chunk + 8, chunksize - 8, mode))
                {
                    gfree(chunk);
                    chunk = 0;
                }
            }
            *size = chunksize;
        }
    }
    return chunk;
}

// 100b055b.
// "TGVk" at the start, or after one leading chunk.
int GCALL TGV_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[8];
    int size;
    gseek(stream, 0);
    if (gread(stream, header, 8))
    {
        if (ggeti(header, 4) == GTAG('T', 'G', 'V', 'k'))
        {
            score = 100;
        }
        else
        {
            int first = ggeti(header + 4, 4);
            if (first > 8 && first < 0x10000 && IsChunkTag(header))
            {
                gseek(stream, 0);
                unsigned char *chunk = ReadChunk(stream, &size, 0);
                if (chunk)
                {
                    if (gread(stream, header, 4) && ggeti(header, 4) == GTAG('T', 'G', 'V', 'k'))
                        score = 100;
                    gfree(chunk);
                }
            }
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(TGV)
GIMEX_BOUNDARY_WRITE(TGV)
