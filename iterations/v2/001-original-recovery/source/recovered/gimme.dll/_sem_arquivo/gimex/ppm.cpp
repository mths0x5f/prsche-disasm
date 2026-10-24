// "Portable Pixel Map" module 1.05 (FrANK G. Barchard): GIMEX module 17.
// gimme.dll 3a43b0f6…, entry points about 100d5f20, is 100d6162, open 100d61d3, info 100d623c, read 100d6664, close 100d68c6,
// wopen 100d5be0, write 100d5c36, wclose 100d5ef8.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100d5f20.
GABOUT *PPM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'P', 'P', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9303;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('P', 'P', 'M', ' ');
        strcpy(about->extension[0], ".ppm");
        strcpy(about->extension[1], ".pbm");
        strcpy(about->extension[2], ".pgm");
        strcpy(about->extension[3], ".pnm");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.05");
        strcpy(about->shortname, "PPM");
        strcpy(about->longname, "PPM");
        strcpy(about->name, "Portable Pixel Map");
    }
    return about;
}

// 100d6162.
int GCALL PPM_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && magic[0] == 'P' && magic[1] > '0' && magic[1] < '7' && magic[2] < 0x21)
        score = 80;
    return score;
}

GIMEX_BOUNDARY_READ(PPM)
GIMEX_BOUNDARY_WRITE(PPM)
