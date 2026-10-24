// "Font Shape" module 1.11 (Gerry Shaw): GIMEX module 44.
// gimme.dll 3a43b0f6…, entry points about 10069100, is 100692b5, open 10069356, info 100693bf, read 10069d2a, close 1006a024,
// wopen 100690e0, write 100690e9, wclose 100690f2.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10069100.
GABOUT *FSHP_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 0, 0, 0);
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x2a041;
        about->unknown_10 = 0x10;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        strcpy(about->extension[0], ".sfs");
        strcpy(about->extension[1], ".pfs");
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->moduleversion, "1.11");
        strcpy(about->shortname, "FSHP");
        strcpy(about->longname, "FontShape");
        strcpy(about->name, "Font Shape");
    }
    return about;
}

// 100692b5.
int GCALL FSHP_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    int position = gtell(stream);
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'F'))
            score = 100;
        if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'P'))
            score = 100;
        if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'S'))
            score = 100;
    }
    gseek(stream, position);
    return score;
}

GIMEX_BOUNDARY_READ(FSHP)
GIMEX_BOUNDARY_WRITE(FSHP)
