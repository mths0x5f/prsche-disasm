// "PSX Font File" module 2.30 (Gerry Shaw): GIMEX module 31.
// gimme.dll 3a43b0f6…, entry points about 1008fdb0, is 1008ffec, open 10090073, info 10090945, read 1009196b, close 10091f67,
// wopen 1008eb40, write 1008edb8, wclose 1008f28b.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1008fdb0.
GABOUT *PFN_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('F', 'N', 'T', 'P');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x2b4c3;
        about->unknown_10 = 0x10;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'p', 'f', 'n');
        strcpy(about->extension[0], ".pfn");
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->moduleversion, "2.30");
        strcpy(about->shortname, "PFN");
        strcpy(about->longname, "PFN");
        strcpy(about->name, "PSX Font File");
    }
    return about;
}

// 1008ffec.
int GCALL PFN_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    int position = gtell(stream);
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'P'))
            score = 100;
        else if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'p'))
            score = 90;
    }
    gseek(stream, position);
    return score;
}

GIMEX_BOUNDARY_READ(PFN)
GIMEX_BOUNDARY_WRITE(PFN)
