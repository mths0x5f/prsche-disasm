// "PC Font File" module 2.30 (Gerry Shaw): GIMEX module 24.
// gimme.dll 3a43b0f6…, entry points about 100c7380, is 100c75ba, open 100c7641, info 100c7ddb, read 100c8e01, close 100c9426,
// wopen 100c6190, write 100c6408, wclose 100c68db.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100c7380.
GABOUT *FFN_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('F', 'N', 'T', 'F');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x2b4c3;
        about->unknown_10 = 0x10;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'f', 'f', 'n');
        strcpy(about->extension[0], ".ffn");
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->moduleversion, "2.30");
        strcpy(about->shortname, "FFN");
        strcpy(about->longname, "FFN");
        strcpy(about->name, "PC Font File");
    }
    return about;
}

// 100c75ba.
int GCALL FFN_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    int position = gtell(stream);
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'F'))
            score = 100;
        else if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'I'))
            score = 90;
    }
    gseek(stream, position);
    return score;
}

GIMEX_BOUNDARY_READ(FFN)
GIMEX_BOUNDARY_WRITE(FFN)
