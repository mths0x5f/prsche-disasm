// "Abobe Illustrator" module 1.01 (Kaz Okuda): GIMEX module 53.
// gimme.dll 3a43b0f6…, entry points about 1002bbdc, is 1002bde3, open 1002be4c, info 1002cfa8, read 1002d134, close 1002d918,
// wopen 10023720, write 10023729, wclose 10023732.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1002bbdc.
GABOUT *AI_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 0, 'A', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x10a501;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'A', 'I', ' ');
        strcpy(about->extension[0], ".ai");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.01");
        strcpy(about->shortname, "AI");
        strcpy(about->longname, "Illustrator");
        strcpy(about->name, "Abobe Illustrator");
    }
    return about;
}

// 1002bde3.
int GCALL AI_is(GSTREAM *stream)
{
    int score = 0;
    char header[200];
    gseek(stream, 0);
    if (gread(stream, header, 199))
    {
        header[199] = '\0';
        if (strstr(header, "Illustrator"))
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(AI)
GIMEX_BOUNDARY_WRITE(AI)
