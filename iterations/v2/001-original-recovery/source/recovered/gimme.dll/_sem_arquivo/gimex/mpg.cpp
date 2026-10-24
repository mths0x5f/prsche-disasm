// "MPEG" module 1.01 (Sasa Djolic): GIMEX module 59.
// gimme.dll 3a43b0f6…, entry points about 10018d00, is 10018f12, open 10018f79, info 1001903b, read 10019180, close 100191bf,
// wopen 10018ce0, write 10018ce9, wclose 10018cf2.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10018d00.
GABOUT *MPG_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('M', 'P', 'E', 'G');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xa705;
        about->unknown_14 = 0;
        about->unknown_18 = 90;
        about->mactype[0] = GTAG('M', 'P', 'E', 'G');
        strcpy(about->extension[0], ".mpg");
        strcpy(about->extension[1], ".mpeg");
        strcpy(about->author, "Sasa Djolic");
        strcpy(about->moduleversion, "1.01");
        strcpy(about->shortname, "MPG");
        strcpy(about->longname, "MPEG");
        strcpy(about->name, "MPEG");
    }
    return about;
}

// 10018f12.
int GCALL MPG_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char code[4];
    gseek(stream, 0);
    if (gread(stream, code, 4))
    {
        int start = ggetm(code, 4);
        if (start == 0x1b3 || start == 0x1ba || start == 0x1e0)
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(MPG)
GIMEX_BOUNDARY_WRITE(MPG)
