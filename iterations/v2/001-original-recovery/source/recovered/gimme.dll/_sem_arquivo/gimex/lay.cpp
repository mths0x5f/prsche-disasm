// "Layout" module 1.09 (Gerry Shaw): GIMEX module 61.
// gimme.dll 3a43b0f6…, entry points about 10016ff2, is 100171c8, open 100172f9, info 1001760c, read 10017e81, close 100181e8,
// wopen 100165e0, write 100168d5, wclose 100169fb.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10016ff2.
GABOUT *LAY_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 0, 0, 0);
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xffd7;
        about->unknown_14 = 255;
        about->unknown_18 = 100;
        strcpy(about->extension[0], ".lay");
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->moduleversion, "1.09");
        strcpy(about->shortname, "LAY");
        strcpy(about->longname, "Layout");
        strcpy(about->name, "Layout");
    }
    return about;
}

// 100171c8.
int GCALL LAY_is(GSTREAM *stream)
{
    int score = 0;
    char text[256];
    gseek(stream, 0);
    memset(text, 0, sizeof(text));
    if (gread(stream, text, 0xff) > 15 && text[0] == ';')
    {
        if (ggetm(text, 4) == GTAG(';', 'L', 'A', 'Y'))
        {
            score = 100;
        }
        else
        {
            for (int i = 0; i < 0xf6; ++i)
            {
                if (score < 20 && strncmp(text + i, "filename:", 9) == 0)
                    score = 20;
                if (score < 80 && strncmp(text + i, "[screen]", 8) == 0)
                    score += 60;
            }
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(LAY)
GIMEX_BOUNDARY_WRITE(LAY)
