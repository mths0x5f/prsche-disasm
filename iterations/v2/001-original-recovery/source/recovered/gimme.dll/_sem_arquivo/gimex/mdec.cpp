// "MDEC Movie" module 1.35 (FrANK G. Barchard): GIMEX module 30.
// gimme.dll 3a43b0f6…, entry points about 1009e99c, is 1009ebdf, open 1009ece6, info 100a1edf, read 100a2022, close 100a5dc4,
// wopen 10092181, write 10092217, wclose 1009d010.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1009e99c.
GABOUT *MDEC_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'S', 'T', 'R');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x8b717;
        about->unknown_14 = 0;
        about->unknown_18 = 8;
        about->mactype[0] = GTAG('.', 'S', 'T', 'R');
        strcpy(about->extension[0], ".str");
        strcpy(about->extension[1], ".xa");
        strcpy(about->extension[2], ".xar");
        strcpy(about->extension[3], ".dct");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.35");
        strcpy(about->shortname, "MDEC");
        strcpy(about->longname, "MDEC");
        strcpy(about->name, "MDEC Movie");
    }
    return about;
}

// 1009ebdf.
// Raw MDEC, a "mTCD" stream, or an EA "SCHl" header followed by an "mTCD" chunk.
int GCALL MDEC_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[12];
    gseek(stream, 0);
    if (!gread(stream, header, 12))
        return score;
    if (ggetm(header, 4) == 0x60010180 || ggetm(header + 8, 4) == 0x60010180 ||
        ggetm(header, 4) == GTAG('m', 'T', 'C', 'D'))
        return 100;
    if (ggetm(header, 4) != GTAG('S', 'C', 'H', 'l'))
        return score;
    int position = gtell(stream);
    score = gseek(stream, position - 12 + ggeti(header + 4, 4));
    if (score == 0)
        return 0;
    score = gread(stream, header, 8);
    if (score == 8 && ggetm(header, 4) == GTAG('m', 'T', 'C', 'D'))
        return 100;
    return 20;
}

GIMEX_BOUNDARY_READ(MDEC)
GIMEX_BOUNDARY_WRITE(MDEC)
