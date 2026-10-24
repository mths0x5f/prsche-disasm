// "Open Media Framework" module 1.01 (Kaz Okuda): GIMEX module 54.
// gimme.dll 3a43b0f6…, entry points about 10022700, is 100228d4, open 1002293b, info 10022e51, read 10023495, close 100236ab,
// wopen 100226e0, write 100226e9, wclose 100226f2.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10022700.
GABOUT *OMF_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('O', 'M', 'F', 'i');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb7d7;
        about->unknown_14 = 0;
        about->unknown_18 = 70;
        about->mactype[0] = GTAG('O', 'M', 'F', 'i');
        strcpy(about->extension[0], ".omf");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.01");
        strcpy(about->shortname, "OMF");
        strcpy(about->longname, "OMFi");
        strcpy(about->name, "Open Media Framework");
    }
    return about;
}

// 100228d4.
int GCALL OMF_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    int length = glen(stream);
    if (length > 0x28)
    {
        gseek(stream, length - 0x24);
        if (gread(stream, magic, 4) && ggetm(magic, 4) == GTAG('M', 'D', 'F', 'L'))
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(OMF)
GIMEX_BOUNDARY_WRITE(OMF)
