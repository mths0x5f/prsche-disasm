// "DPaint ANM" module 1.12 (D. Gyles & F. Barchard): GIMEX module 11.
// gimme.dll 3a43b0f6…, entry points about 100e0dc0, is 100e0d70, open 100e0fb0, info 100e1233, read 100e13b3, close 100e1991,
// wopen 100e04cd, write 100e0820, wclose 100e0aec.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100e0dc0.
GABOUT *ANM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'A', 'N', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x1a4d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'A', 'N', 'M');
        strcpy(about->extension[0], ".anm");
        strcpy(about->author, "D. Gyles & F. Barchard");
        strcpy(about->moduleversion, "1.12");
        strcpy(about->shortname, "ANM");
        strcpy(about->longname, "Anim");
        strcpy(about->name, "DPaint ANM");
    }
    return about;
}

// 100e0d70.
int GCALL ANM_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && ggetm(magic, 4) == GTAG('L', 'P', 'F', ' '))
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(ANM)
GIMEX_BOUNDARY_WRITE(ANM)
