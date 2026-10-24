// "Tiff" module 1.04 (FrANK G. Barchard): GIMEX module 60.
// gimme.dll 3a43b0f6…, entry points about 100185b0, is 100187b0, open 10018821, info 100188c7, read 10018b78, close 10018ca2,
// wopen 10018210, write 100182ab, wclose 1001856a.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100185b0.
GABOUT *TIF_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 'T', 'G', 'A');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9317;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('T', 'I', 'F', 'F');
        strcpy(about->extension[0], ".tif");
        strcpy(about->extension[1], ".tiff");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.04");
        strcpy(about->shortname, "TIF");
        strcpy(about->longname, "Tiff");
        strcpy(about->name, "Tiff");
    }
    return about;
}

// 100187b0.
int GCALL TIF_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char order[4];
    gseek(stream, 0);
    if (gread(stream, order, 2) &&
        ((order[0] == 'M' && order[1] == 'M') || (order[0] == 'I' && order[1] == 'I')))
        score = 60;
    return score;
}

GIMEX_BOUNDARY_READ(TIF)
GIMEX_BOUNDARY_WRITE(TIF)
