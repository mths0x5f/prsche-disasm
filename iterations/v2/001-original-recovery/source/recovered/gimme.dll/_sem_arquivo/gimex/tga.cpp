// "Targa" module 1.37 (FrANK G. Barchard): GIMEX module 5.
// gimme.dll 3a43b0f6…, entry points about 100ea480, is 100ea6b0, open 100ea885, info 100ea8ee, read 100eb053, close 100ebad5,
// wopen 100e9700, write 100e9756, wclose 100ea44e.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100ea480.
GABOUT *TGA_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'T', 'G', 'A');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x93d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('T', 'P', 'I', 'C');
        strcpy(about->extension[0], ".tga");
        strcpy(about->extension[1], ".vda");
        strcpy(about->extension[2], ".icb");
        strcpy(about->extension[3], ".vst");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.37");
        strcpy(about->shortname, "TGA");
        strcpy(about->longname, "Targa");
        strcpy(about->name, "Targa");
    }
    return about;
}

// 100ea6b0.
// Targa has no signature: the 18-byte header must hold a plausible colour-map type, image type
// and depth (60), and then plausible sizes and origins (100).
int GCALL TGA_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[18];
    gseek(stream, 0);
    glen(stream);
    score = gread(stream, header, sizeof(header));
    if (score)
    {
        score = 0;
        int width = ggeti(header + 12, 2);
        int height = ggeti(header + 14, 2);
        int depth = ggeti(header + 16, 1);
        int imagetype = ggeti(header + 2, 1);
        int maptype = ggeti(header + 1, 1);
        int mapfirst = ggeti(header + 3, 2);
        int maplength = ggeti(header + 5, 2);
        int mapentrybits = ggeti(header + 7, 1);
        int xorigin = ggeti(header + 8, 2);
        int yorigin = ggeti(header + 10, 2);
        if (maptype >= 0 && maptype <= 1 &&
            ((imagetype >= 1 && imagetype <= 3) || (imagetype >= 9 && imagetype <= 11)) &&
            (depth == 8 || depth == 15 || depth == 16 || depth == 24 || depth == 32))
        {
            score = 60;
            if (width > 0 && width <= 0x800 && height > 0 && height <= 0x800 && mapfirst >= 0 &&
                mapfirst <= 0xff && maplength >= 0 && maplength <= 0x100 && mapentrybits >= 0 &&
                mapentrybits <= 0x20 && xorigin >= -0x400 && xorigin <= 0x400 && yorigin >= -0x400 &&
                yorigin <= 0x400)
                score = 100;
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(TGA)
GIMEX_BOUNDARY_WRITE(TGA)
