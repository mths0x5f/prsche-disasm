// "Stareo 3D" module 1.04 (FrANK G. Barchard): GIMEX module 42.
// gimme.dll 3a43b0f6…, entry points about 1006e6d0, is 1006e8dc, open 1006e8e5, info 1006e8ee, read 1006e8f7, close 1006e900,
// wopen 1006c534, write 1006c5a6, wclose 1006e6a7.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1006e6d0.
GABOUT *S3D_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', 'T', '3', 'D');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb282;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('S', 'T', '3', 'D');
        strcpy(about->extension[0], ".s3d");
        strcpy(about->extension[1], ".tga");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.04");
        strcpy(about->shortname, "S3D");
        strcpy(about->longname, "Stareo3D");
        strcpy(about->name, "Stareo 3D");
    }
    return about;
}

// 1006e8dc.
int GCALL S3D_is(GSTREAM *)
{
    return 0;
}

GIMEX_BOUNDARY_READ(S3D)
GIMEX_BOUNDARY_WRITE(S3D)
