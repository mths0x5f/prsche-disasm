// "DSH Shape File" module 2.07 (F Barchard): GIMEX module 48.
// gimme.dll 3a43b0f6…, entry points about 10050c90, is 10050ec1, open 10050f12, info 10052f22, read 100546e3, close 100554a2,
// wopen 10043870, write 10043934, wclose 1004f66d.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10050c90.
GABOUT *DSH_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', 'H', 'P', 'D');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb7eb;
        about->unknown_14 = 4;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'd', 's', 'h');
        strcpy(about->extension[0], ".dsh");
        strcpy(about->author, "F Barchard");
        strcpy(about->moduleversion, "2.07");
        strcpy(about->shortname, "DSH");
        strcpy(about->longname, "DSH");
        strcpy(about->name, "DSH Shape File");
    }
    return about;
}

// 10050ec1.
int GCALL DSH_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[16];
    gseek(stream, 0);
    if (gread(stream, header, 16) == 16 && ggetm(header, 4) == GTAG('S', 'H', 'P', 'D'))
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(DSH)
GIMEX_BOUNDARY_WRITE(DSH)
