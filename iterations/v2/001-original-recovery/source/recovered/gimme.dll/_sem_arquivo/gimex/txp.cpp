// "Latenight Text Palette" module 1.03 (FrANK G. Barchard): GIMEX module 36.
// gimme.dll 3a43b0f6…, entry points about 10071fa0, is 1007219a, open 100721a3, info 100721ac, read 100721b5, close 100721be,
// wopen 10071b40, write 10071b9f, wclose 10071f6d.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10071fa0.
GABOUT *TXP_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('T', 'P', 'A', 'L');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9082;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('M', 'P', 'S', ' ');
        strcpy(about->extension[0], ".txt");
        strcpy(about->extension[1], ".txp");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.03");
        strcpy(about->shortname, "TXP");
        strcpy(about->longname, "TextPal");
        strcpy(about->name, "Latenight Text Palette");
    }
    return about;
}

// 1007219a.
int GCALL TXP_is(GSTREAM *)
{
    return 0;
}

GIMEX_BOUNDARY_READ(TXP)
GIMEX_BOUNDARY_WRITE(TXP)
