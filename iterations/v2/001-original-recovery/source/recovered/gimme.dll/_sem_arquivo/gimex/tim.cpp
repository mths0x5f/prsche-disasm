// "TIM PSX Texture Image" module 1.05 (FrANK G. Barchard): GIMEX module 7.
// gimme.dll 3a43b0f6…, entry points about 100e6b80, is 100e6d57, open 100e6da5, info 100e6e0e, read 100e7349, close 100e7690,
// wopen 100e64f0, write 100e6546, wclose 100e6b4f.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100e6b80.
GABOUT *TIM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'T', 'I', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x93c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'T', 'I', 'M');
        strcpy(about->extension[0], ".tim");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.05");
        strcpy(about->shortname, "TIM");
        strcpy(about->longname, "TIM");
        strcpy(about->name, "TIM PSX Texture Image");
    }
    return about;
}

// 100e6d57.
int GCALL TIM_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && ggeti(magic, 4) == 0x10)
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(TIM)
GIMEX_BOUNDARY_WRITE(TIM)
