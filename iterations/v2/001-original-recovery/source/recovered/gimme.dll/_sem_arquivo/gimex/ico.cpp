// "Windows Icon" module 1.00 (FrANK G. Barchard): GIMEX module 3.
// gimme.dll 3a43b0f6…, entry points about 100f5ea0, is 100f60b0, open 100f6135, info 100f619e, read 100f6804, close 100f731d,
// wopen 100f5290, write 100f52e6, wclose 100f5e6c.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100f5ea0.
GABOUT *ICO_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('I', 'C', 'O', 'N');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9041;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'I', 'C', 'O');
        about->mactype[1] = GTAG('.', 'C', 'U', 'R');
        strcpy(about->extension[0], ".ico");
        strcpy(about->extension[1], ".cur");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.00");
        strcpy(about->shortname, "ICO");
        strcpy(about->longname, "Icon");
        strcpy(about->name, "Windows Icon");
    }
    return about;
}

// 100f60b0.
int GCALL ICO_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[6];
    gseek(stream, 0);
    if (gread(stream, header, 6) && ggeti(header, 2) == 0 && ggeti(header + 2, 2) == 1 &&
        ggeti(header + 4, 2) != 0 && (unsigned)ggeti(header + 4, 2) < 10)
        score = 80;
    return score;
}

GIMEX_BOUNDARY_READ(ICO)
GIMEX_BOUNDARY_WRITE(ICO)
