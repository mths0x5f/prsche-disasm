// "Windows BMP" module 1.24 (FrANK G. Barchard): GIMEX module 2.
// gimme.dll 3a43b0f6…, entry points about 100f83d0, is 100f85d3, open 100f8629, info 100f8692, read 100f8e06, close 100f9a3a,
// wopen 100f7350, write 100f73a6, wclose 100f839b.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100f83d0.
GABOUT *BMP_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'B', 'M', 'P');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x93d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('B', 'I', 'N', 'A');
        about->mactype[1] = GTAG('.', 'B', 'M', 'P');
        strcpy(about->extension[0], ".bmp");
        strcpy(about->extension[1], ".rle");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.24");
        strcpy(about->shortname, "BMP");
        strcpy(about->longname, "BMP");
        strcpy(about->name, "Windows BMP");
    }
    return about;
}

// 100f85d3.
int GCALL BMP_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 2) && magic[0] == 'B' && magic[1] == 'M')
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(BMP)
GIMEX_BOUNDARY_WRITE(BMP)
