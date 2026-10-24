// "JPeg" module 1.10 (FrANK G. Barchard): GIMEX module 55.
// gimme.dll 3a43b0f6…, entry points about 100219d2, is 10021beb, open 10021cd3, info 10021d3c, read 100221e4, close 100226ad,
// wopen 10021462, write 100214b8, wclose 100217fd.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100219d2.
GABOUT *JPG_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('J', 'P', 'E', 'G');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb3d7;
        about->unknown_14 = 0;
        about->unknown_18 = 70;
        about->mactype[0] = GTAG('J', 'P', 'E', 'G');
        strcpy(about->extension[0], ".jpg");
        strcpy(about->extension[1], ".jpeg");
        strcpy(about->extension[2], ".jfif");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.10");
        strcpy(about->shortname, "JPG");
        strcpy(about->longname, "JPeg");
        strcpy(about->name, "JPeg");
    }
    return about;
}

// 10021beb.  BOUNDARY: needs IJG libjpeg 6a (jpeg_read_header through a GSTREAM source).
int GCALL JPG_is(GSTREAM *)
{
    return gimexboundary("JPG_is");
}

GIMEX_BOUNDARY_READ(JPG)
GIMEX_BOUNDARY_WRITE(JPG)
