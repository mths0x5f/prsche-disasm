// about() of the GIMEX colour quantizers whose other entry points are not recovered
// (gimme.dll 3a43b0f6…).  GQUANT_find walks the abouts from quantizer 0 until the name
// matches; open/add/make of these quantizers stay null in gimexquantizers[].  Wu is in wu.cpp.

#include <string.h>

#include "gimexfilter.h"

// 10132070.  Quantizer 0 "Nil" 1.01.
GQUANTABOUT *QNIL_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('N', 'I', 'L', 'C');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->quantversion, "1.01");
        strcpy(about->name, "Nil");
        strcpy(about->description, "Nil");
    }
    return about;
}

// 1012fc70.  Quantizer 2 "Stat" 1.10.
GQUANTABOUT *STAT_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('S', 'T', 'A', 'T');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        strcpy(about->author, "Laurent Ancessi");
        strcpy(about->quantversion, "1.10");
        strcpy(about->name, "Stat");
        strcpy(about->description, "Stat Colours");
    }
    return about;
}

// 1012f140.  Quantizer 3 "Popular" 1.10.
GQUANTABOUT *POPULAR_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('P', 'O', 'P', 'L');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        strcpy(about->author, "Laurent Ancessi");
        strcpy(about->quantversion, "1.10");
        strcpy(about->name, "Popular");
        strcpy(about->description, "Popular Colours");
    }
    return about;
}

// 1012e610.  Quantizer 4 "High" 1.10.
GQUANTABOUT *HIGH_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('H', 'I', 'G', 'H');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        strcpy(about->author, "Laurent Ancessi");
        strcpy(about->quantversion, "1.10");
        strcpy(about->name, "High");
        strcpy(about->description, "High Colours");
    }
    return about;
}

// 1012dad0.  Quantizer 5 "Medium" 1.30.
GQUANTABOUT *MEDIUM_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('M', 'E', 'D', 'S');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        strcpy(about->author, "Laurent Ancessi");
        strcpy(about->quantversion, "1.30");
        strcpy(about->name, "Medium");
        strcpy(about->description, "Medium Colours");
    }
    return about;
}

// 1012cfb0.  Quantizer 6 "Low" 1.30.
GQUANTABOUT *LOW_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('L', 'O', 'W', 'S');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        strcpy(about->author, "Laurent Ancessi");
        strcpy(about->quantversion, "1.30");
        strcpy(about->name, "Low");
        strcpy(about->description, "Low Colours");
    }
    return about;
}

// 1012ca50.  Quantizer 7 "Exact" 1.01.
GQUANTABOUT *EXACT_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('X', 'A', 'C', 'T');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        about->flags &= ~0x1;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->quantversion, "1.01");
        strcpy(about->name, "Exact");
        strcpy(about->description, "Exact Histogram");
    }
    return about;
}

// 1012ace0.  Quantizer 8 "4D Wu" 1.04.
GQUANTABOUT *WU4D_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('4', 'D', 'W', 'U');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        strcpy(about->author, "K.Okuda,J.Lefferts");
        strcpy(about->quantversion, "1.04");
        strcpy(about->name, "4D Wu");
        strcpy(about->description, "4D Wu with alpha");
    }
    return about;
}

// 10129420.  Quantizer 9 "Wu5" 1.04.
GQUANTABOUT *WU5_about(void)
{
    GQUANTABOUT *about = (GQUANTABOUT *)galloc(sizeof(GQUANTABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GQUANTABOUT));
        about->tag = GTAG('W', 'U', 'C', 'R');
        about->size = sizeof(GQUANTABOUT);
        about->version = 150;
        about->flags |= 0x1;
        strcpy(about->author, "Wu, F.Barchard, A.Brownsword");
        strcpy(about->quantversion, "1.04");
        strcpy(about->name, "Wu5");
        strcpy(about->description, "Wu's (5 bit)");
    }
    return about;
}
