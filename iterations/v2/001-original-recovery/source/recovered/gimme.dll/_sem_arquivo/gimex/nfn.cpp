// "Nitendo64 Font File" module 2.30 (Gerry Shaw): GIMEX module 34.
// gimme.dll 3a43b0f6…, entry points about 10077610, is 10077837, open 100778bb, info 10078058, read 1007907b, close 100796a0,
// wopen 10076510, write 10076788, wclose 10076c5b.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10077610.
GABOUT *NFN_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('F', 'N', 'T', 'N');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x2b4c3;
        about->unknown_10 = 0x10;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'n', 'f', 'n');
        strcpy(about->extension[0], ".nfn");
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->moduleversion, "2.30");
        strcpy(about->shortname, "nfn");
        strcpy(about->longname, "NFN");
        strcpy(about->name, "Nitendo64 Font File");
    }
    return about;
}

// 10077837.
int GCALL NFN_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    int position = gtell(stream);
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) == GTAG('F', 'N', 'T', 'N'))
            score = 100;
        else if (ggetm(magic, 4) == 0)
            score = 90;
    }
    gseek(stream, position);
    return score;
}

GIMEX_BOUNDARY_READ(NFN)
GIMEX_BOUNDARY_WRITE(NFN)
