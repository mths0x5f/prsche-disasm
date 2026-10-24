// "Encapsulated Postscript" module 1.05 (FrANK G. Barchard): GIMEX module 38.
// gimme.dll 3a43b0f6…, entry points about 10070ae0, is 10070cec, open 10070d5d, info 10070d66, read 10070d6f, close 10070d78,
// wopen 10070330, write 10070386, wclose 10070ab5.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10070ae0.
GABOUT *EPS_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'E', 'P', 'S');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9282;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('E', 'P', 'S', 'F');
        about->mactype[1] = GTAG('E', 'P', 'S', 'I');
        strcpy(about->extension[0], ".eps");
        strcpy(about->extension[1], ".epsf");
        strcpy(about->extension[2], ".ps");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.05");
        strcpy(about->shortname, "EPS");
        strcpy(about->longname, "EPSF");
        strcpy(about->name, "Encapsulated Postscript");
    }
    return about;
}

// 10070cec.
int GCALL EPS_is(GSTREAM *stream)
{
    int score = 0;
    char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && magic[0] == '%' && magic[1] == '!' && magic[2] == 'P' && magic[3] == 'S')
        score = 80;
    return score;
}

GIMEX_BOUNDARY_READ(EPS)
GIMEX_BOUNDARY_WRITE(EPS)
