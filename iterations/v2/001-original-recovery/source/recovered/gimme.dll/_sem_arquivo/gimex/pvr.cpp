// "PowerVR Texture" module 1.01 (Kaz Okuda): GIMEX module 67.
// gimme.dll 3a43b0f6…, entry points about 1000dd6f, is 1000df62, open 1000dfc7, info 1000e162, read 1000e6e8, close 1000eecb,
// wopen 1000c97c, write 1000c9e4, wclose 1000d30b.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1000dd6f.
GABOUT *PVR_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'P', 'V', 'R');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x83c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'P', 'V', 'R');
        strcpy(about->extension[0], ".pvr");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.01");
        strcpy(about->shortname, "PVR");
        strcpy(about->longname, "PowerVR");
        strcpy(about->name, "PowerVR Texture");
    }
    return about;
}

// 1000df62.
int GCALL PVR_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggeti(magic, 4) != GTAG('X', 'I', 'B', 'G') && ggeti(magic, 4) != GTAG('T', 'R', 'V', 'P'))
            return 0;
        score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(PVR)
GIMEX_BOUNDARY_WRITE(PVR)
