// "3Dfx Texture" module 1.05 (FrANK G. Barchard): GIMEX module 66.
// gimme.dll 3a43b0f6…, entry points about 10010020, is 1001023c, open 100102a1, info 100104f3, read 10010af0, close 10010b92,
// wopen 1000f693, write 1000f70b, wclose 1000ff5a.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10010020.
GABOUT *FX_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('3', 'D', 'F', 'X');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x897c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('3', 'D', 'F', 'X');
        strcpy(about->extension[0], ".3df");
        strcpy(about->extension[1], ".txs");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.05");
        strcpy(about->shortname, "FX");
        strcpy(about->longname, "3DF");
        strcpy(about->name, "3Dfx Texture");
    }
    return about;
}

// 1001023c.
int GCALL FX_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) != GTAG('3', 'd', 'f', ' ') && ggetm(magic, 4) != GTAG('T', 'X', 'S', 'F'))
            return 0;
        score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(FX)
GIMEX_BOUNDARY_WRITE(FX)
