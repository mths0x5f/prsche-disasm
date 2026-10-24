// "Bank Mask" module 1.04 (FrANK G. Barchard): GIMEX module 46.
// gimme.dll 3a43b0f6…, entry points about 10057110, is 100572f2, open 100572fb, info 10057304, read 1005730d, close 10057316,
// wopen 10056c20, write 10056c7f, wclose 100570dc.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10057110.
GABOUT *BAM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'B', 'A', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9082;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'B', 'A', 'M');
        strcpy(about->extension[0], ".bam");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.04");
        strcpy(about->shortname, "BAM");
        strcpy(about->longname, "Bam");
        strcpy(about->name, "Bank Mask");
    }
    return about;
}

// 100572f2.
int GCALL BAM_is(GSTREAM *)
{
    return 0;
}

GIMEX_BOUNDARY_READ(BAM)
GIMEX_BOUNDARY_WRITE(BAM)
