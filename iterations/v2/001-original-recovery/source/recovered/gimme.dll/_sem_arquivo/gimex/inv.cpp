// "Inverse Table" module 1.02 (FrANK G. Barchard): GIMEX module 41.
// gimme.dll 3a43b0f6…, entry points about 1006efc3, is 1006f1a0, open 1006f207, info 1006f270, read 1006f4b0, close 1006f4e9,
// wopen 1006eac4, write 1006eb1a, wclose 1006ecbf.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1006efc3.
GABOUT *INV_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'I', 'N', 'V');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x90c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        strcpy(about->extension[0], ".inv");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.02");
        strcpy(about->shortname, "INV");
        strcpy(about->longname, "INV");
        strcpy(about->name, "Inverse Table");
    }
    return about;
}

// 1006f1a0.
int GCALL INV_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    int length = glen(stream);
    if (length > 0x10)
    {
        gseek(stream, length - 0x10);
        if (gread(stream, magic, 4) && ggetm(magic, 4) == GTAG('I', 'N', 'V', 't'))
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(INV)
GIMEX_BOUNDARY_WRITE(INV)
