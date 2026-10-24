// "ACOM YUV" module 1.06 (FrANK G. Barchard): GIMEX module 47.
// gimme.dll 3a43b0f6…, entry points about 100562cf, is 100564af, open 100565b2, info 1005661b, read 10056749, close 10056bf1,
// wopen 10055650, write 1005569c, wclose 10056269.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100562cf.
GABOUT *YUV_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'Y', 'U', 'V');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x8303;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('A', 'Y', 'U', 'V');
        strcpy(about->extension[0], ".yuv");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.06");
        strcpy(about->shortname, "YUV");
        strcpy(about->longname, "Yuv");
        strcpy(about->name, "ACOM YUV");
    }
    return about;
}

// 10056290.  Two samples of a pair that differ by less than 16 vote 5, or 10 when the first
// lies in 0x61..0xdf.
static int ChromaVote(int first, int second)
{
    int vote = 0;
    if (abs(second - first) < 16)
    {
        vote = 5;
        if (first > 0x60 && first < 0xe0)
            vote = 10;
    }
    return vote;
}

// 100564af.
// A 720Ã—486 4:2:2 frame (0xaadc0 bytes); neighbouring samples of the first 8 bytes vote.
int GCALL YUV_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char sample[8];
    gseek(stream, 0);
    if (gread(stream, sample, 8) && glen(stream) == 0xaadc0)
    {
        score = 20;
        score += ChromaVote(sample[0], sample[4]);
        score += ChromaVote(sample[2], sample[6]);
        score += ChromaVote(sample[5], sample[7]);
        score += ChromaVote(sample[1], sample[3]);
        score += ChromaVote(sample[5], sample[7]);
    }
    return score;
}

GIMEX_BOUNDARY_READ(YUV)
GIMEX_BOUNDARY_WRITE(YUV)
