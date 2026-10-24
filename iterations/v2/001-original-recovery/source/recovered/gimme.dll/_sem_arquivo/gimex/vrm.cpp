// "PSX VRAM Viewer" module 1.01 (FrANK G. Barchard): GIMEX module 43.
// gimme.dll 3a43b0f6…, entry points about 1006b580, is 1006b78b, open 1006b794, info 1006b79d, read 1006b7a6, close 1006b7af,
// wopen 1006adb4, write 1006af1c, wclose 1006b3f4.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1006b580.
GABOUT *VRM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('V', 'R', 'A', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb682;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('V', 'R', 'A', 'M');
        strcpy(about->extension[0], ".vrm");
        strcpy(about->extension[1], ".vram");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.01");
        strcpy(about->shortname, "VRM");
        strcpy(about->longname, "VRAM");
        strcpy(about->name, "PSX VRAM Viewer");
    }
    return about;
}

// 1006b78b.
int GCALL VRM_is(GSTREAM *)
{
    return 0;
}

GIMEX_BOUNDARY_READ(VRM)
GIMEX_BOUNDARY_WRITE(VRM)
