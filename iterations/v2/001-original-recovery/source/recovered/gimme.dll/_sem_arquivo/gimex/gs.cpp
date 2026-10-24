// "Raw Grey Scale" module 1.03 (FrANK G. Barchard): GIMEX module 40.
// gimme.dll 3a43b0f6…, entry points about 1006f710, is 1006f924, open 1006f95f, info 1006f9c8, read 1006fb81, close 1006fbf0,
// wopen 1006f510, write 1006f566, wclose 1006f6e7.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1006f710.
GABOUT *GS_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'R', 'G', 'S');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x90c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'R', 'G', 'S');
        strcpy(about->extension[0], ".gs");
        strcpy(about->extension[1], ".rgs");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.03");
        strcpy(about->shortname, "GS");
        strcpy(about->longname, "RawGS");
        strcpy(about->name, "Raw Grey Scale");
    }
    return about;
}

// 1006f924.
// Raw grey scale is recognised by its length alone: 320Ã—200 or 512Ã—512.
int GCALL GS_is(GSTREAM *stream)
{
    int score = 0;
    int length = glen(stream);
    if (length == 64000 || length == 0x40000)
        score = 30;
    return score;
}

GIMEX_BOUNDARY_READ(GS)
GIMEX_BOUNDARY_WRITE(GS)
