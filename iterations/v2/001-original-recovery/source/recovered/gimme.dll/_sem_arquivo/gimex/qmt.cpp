// "Quake Model Texture Gimex" module 1.00 (Julian Fong): GIMEX module 63.
// gimme.dll 3a43b0f6…, entry points about 10013440, is 10013616, open 10013673, info 1001379e, read 10013934, close 100139f3,
// wopen 10013420, write 10013429, wclose 10013432.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10013440.
GABOUT *QMT_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 'M', 'D', 'L');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x8041;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        strcpy(about->extension[0], ".mdl");
        strcpy(about->author, "Julian Fong");
        strcpy(about->moduleversion, "1.00");
        strcpy(about->shortname, "QMT");
        strcpy(about->longname, "Quake Model");
        strcpy(about->name, "Quake Model Texture Gimex");
    }
    return about;
}

// 10013616.
int GCALL QMT_is(GSTREAM *stream)
{
    int score = 0;
    char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && strncmp(magic, "IDPO", 4) == 0)
        score = 100;
    gseek(stream, 0);
    return score;
}

GIMEX_BOUNDARY_READ(QMT)
GIMEX_BOUNDARY_WRITE(QMT)
