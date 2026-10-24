// "ATI VQ Texture" module 1.02 (FrANK G. Barchard): GIMEX module 29.
// gimme.dll 3a43b0f6…, entry points about 100a6f90, is 100a718a, open 100a71fa, info 100a7263, read 100a7467, close 100a76ef,
// wopen 100a5fc0, write 100a6016, wclose 100a6f65.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100a6f90.
GABOUT *VQT_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'V', 'Q', 'T');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9317;
        about->unknown_14 = 0;
        about->unknown_18 = 70;
        about->mactype[0] = GTAG('.', 'V', 'Q', 'T');
        strcpy(about->extension[0], ".vqt");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.02");
        strcpy(about->shortname, "VQT");
        strcpy(about->longname, "VQT");
        strcpy(about->name, "ATI VQ Texture");
    }
    return about;
}

// 100a718a.
int GCALL VQT_is(GSTREAM *stream)
{
    int score = 0;
    char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (strncmp(magic, "0tqv", 4) == 0)
            score = 100;
        if (strncmp(magic, "vqt0", 4) == 0)
            score = 90;
    }
    return score;
}

GIMEX_BOUNDARY_READ(VQT)
GIMEX_BOUNDARY_WRITE(VQT)
