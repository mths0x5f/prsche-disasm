// "Gimex Images" module 2.14 (A.Brownsword): GIMEX module 23.
// gimme.dll 3a43b0f6…, entry points about 100cc850, is 100cca2e, open 100cca93, info 100ccd86, read 100cef4e, close 100cf1f2,
// wopen 100c9560, write 100c963a, wclose 100cc7cc.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100cc850.
GABOUT *GMX_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('G', 'I', 'M', 'X');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb7c3;
        about->unknown_14 = 255;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('G', 'I', 'M', 'X');
        strcpy(about->extension[0], ".gmx");
        strcpy(about->author, "A.Brownsword");
        strcpy(about->moduleversion, "2.14");
        strcpy(about->shortname, "GMX");
        strcpy(about->longname, "Gimex");
        strcpy(about->name, "Gimex Images");
    }
    return about;
}

// 100cca2e.
int GCALL GMX_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) != GTAG('G', 'M', 'X', 'p') && ggetm(magic, 4) != GTAG('G', 'M', 'X', 'h'))
            return score;
        score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(GMX)
GIMEX_BOUNDARY_WRITE(GMX)
