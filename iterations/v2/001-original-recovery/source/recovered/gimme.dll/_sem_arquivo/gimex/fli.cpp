// "FLIC Animation" module 1.06 (Frank Barchard): GIMEX module 22.
// gimme.dll 3a43b0f6…, entry points about 100cfc78, is 100cfe8f, open 100cff37, info 100d009a, read 100d0710, close 100d07af,
// wopen 100cf250, write 100cf2af, wclose 100cf6b7.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100cfc78.
GABOUT *FLI_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('F', 'L', 'I', 'C');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xa4c7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('F', 'L', 'I', 'C');
        strcpy(about->extension[0], ".fli");
        strcpy(about->extension[1], ".flc");
        strcpy(about->author, "Frank Barchard");
        strcpy(about->moduleversion, "1.06");
        strcpy(about->shortname, "FLI");
        strcpy(about->longname, "FLIC");
        strcpy(about->name, "FLIC Animation");
    }
    return about;
}

// 100cfe8f.
int GCALL FLI_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[0x80];
    gseek(stream, 0);
    int length = glen(stream);
    if (gread(stream, header, 0x80))
    {
        if (ggeti(header + 4, 2) != 0xaf11 && ggeti(header + 4, 2) != 0xaf12)
            return 0;
        score = 60;
        if (ggeti(header, 4) == length)
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(FLI)
GIMEX_BOUNDARY_WRITE(FLI)
