// "SGI RGB Image File" module 1.07 (FrANK G. Barchard): GIMEX module 14.
// gimme.dll 3a43b0f6…, entry points about 100dbb70, is 100dbd8a, open 100dbe61, info 100dbeca, read 100dc1ea, close 100dc96d,
// wopen 100db4d0, write 100db526, wclose 100dbb41.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100dbb70.
GABOUT *SGI_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'S', 'G', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9357;
        about->unknown_14 = 79;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'S', 'G', 'I');
        strcpy(about->extension[0], ".rgb");
        strcpy(about->extension[1], ".sgi");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.07");
        strcpy(about->shortname, "SGI");
        strcpy(about->longname, "SGI");
        strcpy(about->name, "SGI RGB Image File");
    }
    return about;
}

// 100dbd8a.
int GCALL SGI_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[0x200];
    gseek(stream, 0);
    if (gread(stream, header, 0x200) && ggetm(header, 2) == 0x1da && (unsigned)ggetm(header + 2, 1) < 2 &&
        ggetm(header + 3, 1) != 0 && (unsigned)ggetm(header + 3, 1) < 3 && ggetm(header + 4, 2) != 0 &&
        (unsigned)ggetm(header + 4, 2) < 4)
        score = 95;
    return score;
}

GIMEX_BOUNDARY_READ(SGI)
GIMEX_BOUNDARY_WRITE(SGI)
