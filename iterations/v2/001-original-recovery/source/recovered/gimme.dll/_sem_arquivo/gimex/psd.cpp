// "Adobe Photoshop 4.0" module 1.13 (Frank & Julian): GIMEX module 10.
// gimme.dll 3a43b0f6…, entry points about 100e31b0, is 100e33b7, open 100e3407, info 100e3eb9, read 100e4373, close 100e4e7d,
// wopen 100e1c7a, write 100e1d51, wclose 100e2307.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100e31b0.
GABOUT *PSD_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('8', 'B', 'P', 'S');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb757;
        about->unknown_14 = 32;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('8', 'B', 'P', 'S');
        strcpy(about->extension[0], ".psd");
        strcpy(about->extension[1], ".pdd");
        strcpy(about->author, "Frank & Julian");
        strcpy(about->moduleversion, "1.13");
        strcpy(about->shortname, "PSD");
        strcpy(about->longname, "Photoshop");
        strcpy(about->name, "Adobe Photoshop 4.0");
    }
    return about;
}

// 100e33b7.
int GCALL PSD_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && ggetm(magic, 4) == GTAG('8', 'B', 'P', 'S'))
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(PSD)
GIMEX_BOUNDARY_WRITE(PSD)
