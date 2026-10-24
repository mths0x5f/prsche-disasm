// "Macintosh Pict" module 1.18 (Frank/Gerry/Laurent): GIMEX module 15.
// gimme.dll 3a43b0f6…, entry points about 100d8750, is 100d8973, open 100d8ac8, info 100db465, read 100db443, close 100d8b31,
// wopen 100d7ff0, write 100d8046, wclose 100d8727.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100d8750.
GABOUT *PICT_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('P', 'I', 'C', 'T');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb347;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('P', 'I', 'C', 'T');
        about->mactype[1] = GTAG('V', 'D', 'A', 'N');
        strcpy(about->extension[0], ".pict");
        strcpy(about->extension[1], ".pic");
        strcpy(about->extension[2], ".pct");
        strcpy(about->author, "Frank/Gerry/Laurent");
        strcpy(about->moduleversion, "1.18");
        strcpy(about->shortname, "PICT");
        strcpy(about->longname, "MacPICT");
        strcpy(about->name, "Macintosh Pict");
    }
    return about;
}

// 100d8973.
// After the 512-byte Macintosh header: picture size, frame rectangle and the version opcode.
int GCALL PICT_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[12];
    int length = glen(stream);
    if (length > 0x20c)
    {
        gseek(stream, 0x200);
        if (gread(stream, header, 12))
        {
            const unsigned char *version = &header[10];
            if (*version == 0)
                version = &header[11];
            int top = ggetm(header + 2, 2);
            int bottom = ggetm(header + 6, 2);
            int left = ggetm(header + 4, 2);
            int right = ggetm(header + 8, 2);
            if (top < bottom && left < right)
            {
                score = 5;
                if (top >= 0 && top <= 0x400 && bottom > 0 && bottom <= 0x800 && left >= 0 && left <= 0x400 &&
                    right > 0 && right <= 0x800)
                    score = 40;
                if (*version == 0x11)
                    score += 25;
                if ((unsigned)ggetm(header, 2) == ((unsigned)(length - 0x200) & 0xffff))
                    score += 35;
            }
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(PICT)
GIMEX_BOUNDARY_WRITE(PICT)
