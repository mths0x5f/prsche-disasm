// "Portable Network Graphics" module 1.06 (Kaz Okuda): GIMEX module 57.
// gimme.dll 3a43b0f6…, entry points about 1001c830, is 1001c9fb, open 1001ca69, info 1001cc34, read 1001d094, close 1001d42a,
// wopen 1001bf70, write 1001bfc6, wclose 1001c809.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1001c830.
GABOUT *PNG_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 'P', 'N', 'G');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xa3d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG(0, 'P', 'N', 'G');
        strcpy(about->extension[0], ".png");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.06");
        strcpy(about->shortname, "PNG");
        strcpy(about->longname, "PNG");
        strcpy(about->name, "Portable Network Graphics");
    }
    return about;
}

// 1001c9fb.  BOUNDARY: needs libpng 1.0.3 (png_check_sig).
int GCALL PNG_is(GSTREAM *)
{
    return gimexboundary("PNG_is");
}

GIMEX_BOUNDARY_READ(PNG)
GIMEX_BOUNDARY_WRITE(PNG)
