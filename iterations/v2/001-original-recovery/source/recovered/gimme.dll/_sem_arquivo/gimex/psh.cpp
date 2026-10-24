// "PSH Shape File" module 2.07 (F Barchard): GIMEX module 25.
// gimme.dll 3a43b0f6…, entry points about 100c17d0, is 100c1a01, open 100c1a52, info 100c3a62, read 100c5223, close 100c5fe2,
// wopen 100b43b0, write 100b4474, wclose 100c01ad.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100c17d0.
GABOUT *PSH_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', 'H', 'P', 'P');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb7eb;
        about->unknown_14 = 4;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'p', 's', 'h');
        strcpy(about->extension[0], ".psh");
        strcpy(about->author, "F Barchard");
        strcpy(about->moduleversion, "2.07");
        strcpy(about->shortname, "PSH");
        strcpy(about->longname, "PSH");
        strcpy(about->name, "PSH Shape File");
    }
    return about;
}

// 100c1a01.
int GCALL PSH_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[16];
    gseek(stream, 0);
    if (gread(stream, header, 16) == 16 && ggetm(header, 4) == GTAG('S', 'H', 'P', 'P'))
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(PSH)
GIMEX_BOUNDARY_WRITE(PSH)
