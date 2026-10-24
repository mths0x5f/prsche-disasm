// "Adobe FilmStrip" module 1.02 (FrANK G. Barchard): GIMEX module 12.
// gimme.dll 3a43b0f6…, entry points about 100df440, is 100df650, open 100df70c, info 100df825, read 100df9f4, close 100dfc5e,
// wopen 100df010, write 100df076, wclose 100df2d2.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100df440.
GABOUT *FLM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'F', 'L', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x8703;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'F', 'L', 'M');
        strcpy(about->extension[0], ".flm");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.02");
        strcpy(about->shortname, "FLM");
        strcpy(about->longname, "FilmStrip");
        strcpy(about->name, "Adobe FilmStrip");
    }
    return about;
}

// 100df650.
// The FilmStrip trailer is the last 36 bytes of the file.
int GCALL FLM_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char trailer[36];
    int length = glen(stream);
    if (length > 0x24)
    {
        gseek(stream, length - 0x24);
        score = gread(stream, trailer, 0x24);
        if (score)
        {
            score = 0;
            int width = ggetm(trailer + 12, 2);
            int height = ggetm(trailer + 14, 2);
            if (ggetm(trailer, 4) == GTAG('R', 'a', 'n', 'd') && width > 0 && width <= 0x4000 && height > 0 &&
                height <= 0x4000)
                score = 100;
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(FLM)
GIMEX_BOUNDARY_WRITE(FLM)
