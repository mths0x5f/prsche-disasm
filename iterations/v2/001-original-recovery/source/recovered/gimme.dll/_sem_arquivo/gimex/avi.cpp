// "Audio Visual Interleave" module 1.10 (Kaz Okuda): GIMEX module 56.
// gimme.dll 3a43b0f6…, entry points about 1001f1d0, is 1001f399, open 1001f3fa, info 10020b38, read 10020d29, close 10021157,
// wopen 1001e64f, write 1001e723, wclose 1001ef27.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1001f1d0.
GABOUT *AVI_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'A', 'V', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xe7d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'A', 'V', 'I');
        strcpy(about->extension[0], ".avi");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.10");
        strcpy(about->shortname, "AVI");
        strcpy(about->longname, "AVI");
        strcpy(about->name, "Audio Visual Interleave");
    }
    return about;
}

// 1001f399.
int GCALL AVI_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[12];
    gseek(stream, 0);
    gread(stream, header, 12);
    if (ggetm(header, 4) == GTAG('R', 'I', 'F', 'F') && ggetm(header + 8, 4) == GTAG('A', 'V', 'I', ' '))
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(AVI)
GIMEX_BOUNDARY_WRITE(AVI)
