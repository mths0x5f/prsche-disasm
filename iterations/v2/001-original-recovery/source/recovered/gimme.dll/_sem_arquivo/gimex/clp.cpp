// "ClipBoard Gimex" module 1.03 (Kaz Okuda): GIMEX module 52.
// gimme.dll 3a43b0f6…, entry points about 100304e0, is 100306d2, open 100306de, info 10030784, read 10030865, close 100308b2,
// wopen 1002eac1, write 1002eb50, wclose 1002ed59.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100304e0.
GABOUT *CLP_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('C', 'L', 'I', 'P');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x77d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('C', 'L', 'I', 'P');
        strcpy(about->extension[0], ".clp");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.03");
        strcpy(about->shortname, "CLP");
        strcpy(about->longname, "ClipBoard");
        strcpy(about->name, "ClipBoard Gimex");
    }
    return about;
}

// 100306d2.
int GCALL CLP_is(GSTREAM *)
{
    return 100;
}

GIMEX_BOUNDARY_READ(CLP)
GIMEX_BOUNDARY_WRITE(CLP)
