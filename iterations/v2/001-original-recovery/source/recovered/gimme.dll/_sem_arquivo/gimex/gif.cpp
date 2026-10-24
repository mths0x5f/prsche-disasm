// "Compuserve GIF" module 1.15 (FrANK G. Barchard): GIMEX module 28.
// gimme.dll 3a43b0f6…, entry points about 100a8b70, is 100a8d7c, open 100a8de5, info 100aa2c5, read 100aa5e2, close 100aa63d,
// wopen 100a86d8, write 100a8758, wclose 100a8b27.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100a8b70.
GABOUT *GIF_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'G', 'I', 'F');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x1b4d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('G', 'I', 'F', 'f');
        strcpy(about->extension[0], ".gif");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.15");
        strcpy(about->shortname, "GIF");
        strcpy(about->longname, "GIF");
        strcpy(about->name, "Compuserve GIF");
    }
    return about;
}

// 100a8d7c.
int GCALL GIF_is(GSTREAM *stream)
{
    int score = 0;
    char magic[8];
    gseek(stream, 0);
    if (gread(stream, magic, 6))
    {
        if (strncmp(magic, "GIF87a", 6) != 0 && strncmp(magic, "GIF89a", 6) != 0)
            return 0;
        score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(GIF)
GIMEX_BOUNDARY_WRITE(GIF)
