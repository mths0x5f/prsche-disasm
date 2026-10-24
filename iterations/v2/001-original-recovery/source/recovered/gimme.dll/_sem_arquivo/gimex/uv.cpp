// "Movie Gimex" module 1.05 (Kaz Okuda): GIMEX module 68.
// gimme.dll 3a43b0f6…, entry points about 100089c0, is 10008bb6, open 10008ced, info 10009026, read 100093ff, close 1000afd9,
// wopen 10005a40, write 10005c4e, wclose 1000890e.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100089c0.
GABOUT *UV_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('0', '0', 'U', 'V');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xa717;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 't', 'g', 'q');
        strcpy(about->extension[0], ".uv");
        strcpy(about->extension[1], ".tgq");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.05");
        strcpy(about->shortname, "uV");
        strcpy(about->longname, "movie");
        strcpy(about->name, "Movie Gimex");
    }
    return about;
}

// 10008c93.
static int IsMovieChunk(const unsigned char *header)
{
    return ggeti(header, 4) == GTAG('T', 'G', 'Q', 'p') || ggeti(header, 4) == GTAG('p', 'Q', 'G', 'T') ||
           ggeti(header, 4) == GTAG('f', 'V', 'U', 'M');
}

// 10008bb6.
// Skips up to four chunks looking for a TGQ or "MUVf" chunk header.
int GCALL UV_is(GSTREAM *stream)
{
    int chunks = 0;
    int score = 0;
    unsigned char header[8];
    gseek(stream, 0);
    int got = gread(stream, header, 8);
    while (got == 8 && chunks <= 3)
    {
        int skip = ggeti(header + 4, 4) - 8;
        if (glen(stream) < gtell(stream) + skip && skip > 0)
            return 0;
        if (IsMovieChunk(header))
            return 100;
        ++chunks;
        gseek(stream, gtell(stream) + skip);
        got = gread(stream, header, 8);
    }
    return score;
}

GIMEX_BOUNDARY_READ(UV)
GIMEX_BOUNDARY_WRITE(UV)
