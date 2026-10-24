// "Sony2 Font File" module 2.30 (Gerry Shaw): GIMEX module 33.
// gimme.dll 3a43b0f6…, entry points about 1007aa30, is 1007ac6a, open 1007acf1, info 1007b5ab, read 1007c5d1, close 1007cbcd,
// wopen 100797d0, write 10079a48, wclose 10079f1b.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1007aa30.
GABOUT *SFN_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('F', 'N', 'T', 'S');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x2b4c3;
        about->unknown_10 = 0x10;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 's', 'f', 'n');
        strcpy(about->extension[0], ".sfn");
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->moduleversion, "2.30");
        strcpy(about->shortname, "SFN");
        strcpy(about->longname, "SFN");
        strcpy(about->name, "Sony2 Font File");
    }
    return about;
}

// 1007ac6a.
int GCALL SFN_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    int position = gtell(stream);
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'S'))
            score = 100;
        else if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 's'))
            score = 90;
    }
    gseek(stream, position);
    return score;
}

GIMEX_BOUNDARY_READ(SFN)
GIMEX_BOUNDARY_WRITE(SFN)
