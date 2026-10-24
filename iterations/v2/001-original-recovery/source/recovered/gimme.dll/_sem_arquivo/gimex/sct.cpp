// "Scitex SCT" module 1.02 (FrANK G. Barchard): GIMEX module 9.
// gimme.dll 3a43b0f6…, entry points about 100e5200, is 100e5406, open 100e54c1, info 100e552a, read 100e5765, close 100e59a5,
// wopen 100e4ef0, write 100e4f46, wclose 100e51da.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100e5200.
GABOUT *SCT_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'S', 'C', 'T');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9303;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'S', 'C', 'T');
        strcpy(about->extension[0], ".sct");
        strcpy(about->extension[1], ".sc");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.02");
        strcpy(about->shortname, "SCT");
        strcpy(about->longname, "SCT");
        strcpy(about->name, "Scitex SCT");
    }
    return about;
}

// 100e5406.
int GCALL SCT_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char word[4];
    if (glen(stream) > 0x800)
    {
        gseek(stream, 0x50);
        if (gread(stream, word, 4) && ggetm(word, 4) == GTAG('C', 'T', 0, 0))
        {
            score = 50;
            gseek(stream, 0x400);
            if (gread(stream, word, 4))
            {
                if (ggetm(word, 4) != 0x104000f && ggetm(word, 4) != 0x1030007)
                    return score;
                score = 100;
            }
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(SCT)
GIMEX_BOUNDARY_WRITE(SCT)
