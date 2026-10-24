// "HSI Raw" module 1.07 (FrANK G. Barchard): GIMEX module 8.
// gimme.dll 3a43b0f6…, entry points about 100e5d10, is 100e5f12, open 100e5f9f, info 100e6111, read 100e6319, close 100e64b4,
// wopen 100e59d0, write 100e5a26, wclose 100e5cdb.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100e5d10.
GABOUT *HSI_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'H', 'S', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x187c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'H', 'S', 'I');
        strcpy(about->extension[0], ".hsi");
        strcpy(about->extension[1], ".raw");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.07");
        strcpy(about->shortname, "HSI");
        strcpy(about->longname, "HSI");
        strcpy(about->name, "HSI Raw");
    }
    return about;
}

// 100e5f12.
int GCALL HSI_is(GSTREAM *stream)
{
    int score = 0;
    char header[32];
    gseek(stream, 0);
    if (gread(stream, header, 32) && header[0] == 'm' && header[1] == 'h' && header[2] == 'w' &&
        header[3] == 'a' && header[4] == 'n' && header[5] == 'h')
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(HSI)
GIMEX_BOUNDARY_WRITE(HSI)
