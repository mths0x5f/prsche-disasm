// "SoftImage PIC" module 1.08 (FrANK G. Barchard): GIMEX module 26.
// gimme.dll 3a43b0f6…, entry points about 100b3d47, is 100b3f63, open 100b3fb3, info 100b401c, read 100b42b0, close 100b4388,
// wopen 100b2e2d, write 100b2e79, wclose 100b3135.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100b3d47.
GABOUT *SIM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'S', 'I', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9303;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('U', 'N', 'K', 'N');
        strcpy(about->extension[0], ".pic");
        strcpy(about->extension[1], ".sim");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.08");
        strcpy(about->shortname, "Sim");
        strcpy(about->longname, "SoftImage");
        strcpy(about->name, "SoftImage PIC");
    }
    return about;
}

// 100b3f63.
int GCALL SIM_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && ggetm(magic, 4) == 0x5380f634)
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(SIM)
GIMEX_BOUNDARY_WRITE(SIM)
