// about() of the GIMEX filters whose other entry points are not recovered (gimme.dll 3a43b0f6…).
// FaceInRace's GFILTER_find walks the abouts from filter 0 until the name matches, so every
// filter of the original table keeps its about(); open/info/read/close of these filters stay
// null in gimexfilters[] (unresolved boundary, see gimextables.cpp).  Crop, Remap and Size
// are in crop.cpp, remap.cpp and size.cpp.  Repeated assignments to one field (Grey, Fill, Flip,
// Blend, HSV) are in the original code; the later one wins.

#include <string.h>

#include "gimexfilter.h"

// 101291d0.  Filter 0 "FNil" 1.01.
GFILTERABOUT *FNIL_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'L', 'I', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "FBarchard,GShaw");
        strcpy(about->filterversion, "1.01");
        strcpy(about->name, "FNil");
        strcpy(about->description, "Nil");
        about->values = 0;
    }
    return about;
}

// 10122ec0.  Filter 1 "Math" 1.00.
GFILTERABOUT *MATH_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('M', 'A', 'T', 'H');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Math");
        strcpy(about->description, "Math Image");
        about->values = 1;
        about->value[0].type = 0x3;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 0;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "Expression");
        strcpy(about->value[0].help, "");
    }
    return about;
}

// 101223e3.  Filter 2 "Zoom" 1.05.
GFILTERABOUT *ZOOM_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('Z', 'O', 'O', 'M');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Spencer Cathey");
        strcpy(about->filterversion, "1.05");
        strcpy(about->name, "Zoom");
        strcpy(about->description, "Bicubic Zoom");
        about->values = 6;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 2;
        about->value[0].maximum.integer = 4096;
        about->value[0].initial.integer = 320;
        strcpy(about->value[0].name, "Width");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 2;
        about->value[1].maximum.integer = 4096;
        about->value[1].initial.integer = 240;
        strcpy(about->value[1].name, "Height");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x201;
        about->value[2].minimum.integer = 1;
        about->value[2].maximum.integer = 2;
        about->value[2].initial.integer = 1;
        strcpy(about->value[2].name, "Edge Extend");
        strcpy(about->value[2].help, "Solid,Boundary");
        about->value[3].type = 0x801;
        about->value[3].minimum.integer = 0;
        about->value[3].maximum.integer = -1;
        about->value[3].initial.integer = 0;
        strcpy(about->value[3].name, "Solid Colour");
        strcpy(about->value[3].help, "");
        about->value[4].type = 0x2;
        about->value[4].minimum.real = 0.5;
        about->value[4].maximum.real = 4.0;
        about->value[4].initial.real = 2.0;
        strcpy(about->value[4].name, "Kernel Width");
        strcpy(about->value[4].help, "");
        about->value[5].type = 0x2;
        about->value[5].minimum.real = 0.0;
        about->value[5].maximum.real = 2.0;
        about->value[5].initial.real = 0.0;
        strcpy(about->value[5].name, "Kernel Shape");
        strcpy(about->value[5].help, "");
    }
    return about;
}

// 10120f20.  Filter 3 "Grey" 1.03.
GFILTERABOUT *GREY_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('G', 'R', 'E', 'Y');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.03");
        strcpy(about->name, "Grey");
        strcpy(about->description, "Grey Image");
        about->values = 2;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 2;
        about->value[0].maximum.integer = 256;
        about->value[0].initial.integer = 256;
        strcpy(about->value[0].name, "Levels");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = 1;
        about->value[1].initial.integer = 0;
        strcpy(about->value[0].name, "BlendAlpha");
    }
    return about;
}

// 10120950.  Filter 4 "Rect" 1.02.
GFILTERABOUT *RECT_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('R', 'E', 'C', 'T');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_18 = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.02");
        strcpy(about->name, "Rect");
        strcpy(about->description, "Rect Image");
        about->values = 5;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = -1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "X");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = -1;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Y");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x1;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = -1;
        about->value[2].initial.integer = 1;
        strcpy(about->value[2].name, "Width");
        strcpy(about->value[2].help, "");
        about->value[3].type = 0x1;
        about->value[3].minimum.integer = 0;
        about->value[3].maximum.integer = -1;
        about->value[3].initial.integer = 1;
        strcpy(about->value[3].name, "Height");
        strcpy(about->value[3].help, "");
        about->value[4].type = 0x1801;
        about->value[4].minimum.integer = 0;
        about->value[4].maximum.integer = -1;
        about->value[4].initial.integer = 0;
        strcpy(about->value[4].name, "Colour");
        strcpy(about->value[4].help, "");
    }
    return about;
}

// 1011f690.  Filter 7 "Xcolour" 1.02.
GFILTERABOUT *XCOLOUR_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('X', 'C', 'O', 'L');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.02");
        strcpy(about->name, "Xcolour");
        strcpy(about->description, "Xcolour Image");
        about->values = 5;
        about->value[0].type = 0x801;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = -1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "Search");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x801;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = -1;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Replace");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x801;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = -1;
        about->value[2].initial.integer = 0;
        strcpy(about->value[2].name, "SearchMask");
        strcpy(about->value[2].help, "");
        about->value[3].type = 0x801;
        about->value[3].minimum.integer = 0;
        about->value[3].maximum.integer = -1;
        about->value[3].initial.integer = 0;
        strcpy(about->value[3].name, "ReplaceMask");
        strcpy(about->value[3].help, "");
        about->value[4].type = 0x1;
        about->value[4].minimum.integer = 0;
        about->value[4].maximum.integer = 1;
        about->value[4].initial.integer = 0;
        strcpy(about->value[4].name, "SearchNot");
        strcpy(about->value[4].help, "");
    }
    return about;
}

// 1011ec30.  Filter 8 "Fill" 1.04.
GFILTERABOUT *FILL_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'I', 'L', 'L');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_18 = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "G.Shaw, F.Barchard");
        strcpy(about->filterversion, "1.04");
        strcpy(about->name, "Fill");
        strcpy(about->description, "Fill Image");
        about->values = 4;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = -1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "X");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = -1;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Y");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x1801;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = -1;
        about->value[2].initial.integer = 0;
        strcpy(about->value[2].name, "Colour");
        strcpy(about->value[2].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = 255;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Tolerance");
        strcpy(about->value[1].help, "");
    }
    return about;
}

// 1011e820.  Filter 9 "Invert" 1.00.
GFILTERABOUT *INVERT_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'I', 'N', 'V');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Invert");
        strcpy(about->description, "Invert ARGB");
        about->values = 1;
        about->value[0].type = 0x801;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = -1;
        about->value[0].initial.integer = -1;
        strcpy(about->value[0].name, "mask");
        strcpy(about->value[0].help, "");
    }
    return about;
}

// 1011e320.  Filter 10 "Preten" 1.00.
GFILTERABOUT *PRETEN_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('A', 'T', 'E', 'N');
        about->size = sizeof(GFILTERABOUT);
        about->version = 100;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Preten");
        strcpy(about->description, "Preattenuate ARGB");
        about->values = 1;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "method");
        strcpy(about->value[0].help, "preattenuate,unattenuate");
    }
    return about;
}

// 1011dc5e.  Filter 11 "Rot" 1.00.
GFILTERABOUT *ROT_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'R', 'O', 'T');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Rot");
        strcpy(about->description, "Rotate");
        about->values = 1;
        about->value[0].type = 0x201;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 3;
        about->value[0].initial.integer = 1;
        strcpy(about->value[0].name, "Rot");
        strcpy(about->value[0].help, "0,90,180,-90");
    }
    return about;
}

// 1011d810.  Filter 12 "Wrap" 1.01.
GFILTERABOUT *WRAP_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('W', 'R', 'A', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.01");
        strcpy(about->name, "Wrap");
        strcpy(about->description, "Wrap Image");
        about->values = 2;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = -2147483647 - 1;
        about->value[0].maximum.integer = 2147483647;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "X");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = -2147483647 - 1;
        about->value[1].maximum.integer = 2147483647;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Y");
        strcpy(about->value[1].help, "");
    }
    return about;
}

// 1011d3b0.  Filter 13 "ACopy" 1.02.
GFILTERABOUT *ACOPY_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('A', 'C', 'P', 'Y');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.02");
        strcpy(about->name, "ACopy");
        strcpy(about->description, "Alpha Copy");
        about->values = 1;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "method");
        strcpy(about->value[0].help, "rgb,alpha");
    }
    return about;
}

// 1011cd80.  Filter 14 "Blur" 1.00.
GFILTERABOUT *BLUR_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('B', 'L', 'U', 'R');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Blur");
        strcpy(about->description, "Gausian Blur");
        about->values = 1;
        about->value[0].type = 0x2;
        about->value[0].minimum.real = 0.1;
        about->value[0].maximum.real = 256.0;
        about->value[0].initial.real = 4.0;
        strcpy(about->value[0].name, "Radius");
        strcpy(about->value[0].help, "");
    }
    return about;
}

// 1011c6a0.  Filter 15 "Sharpen" 1.00.
GFILTERABOUT *SHARPEN_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('S', 'H', 'R', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Sharpen");
        strcpy(about->description, "Sharpen");
        about->values = 1;
        about->value[0].type = 0x2;
        about->value[0].minimum.real = 0.1;
        about->value[0].maximum.real = 256.0;
        about->value[0].initial.real = 5.0;
        strcpy(about->value[0].name, "Amount");
        strcpy(about->value[0].help, "");
    }
    return about;
}

// 1011c0a0.  Filter 16 "Flip" 1.04.
GFILTERABOUT *FLIP_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'L', 'I', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "G Shaw/F Barchard");
        strcpy(about->filterversion, "1.04");
        strcpy(about->name, "Flip");
        strcpy(about->description, "Flip");
        about->values = 1;
        about->values = 1;
        about->value[0].type = 0x201;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 3;
        about->value[0].initial.integer = 1;
        strcpy(about->value[0].name, "Direction");
        strcpy(about->value[0].help, "None,Horizontal,Vertical,Both");
    }
    return about;
}

// 1011a8d5.  Filter 17 "PalSort" 1.08.
GFILTERABOUT *PALSORT_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('P', 'S', 'R', 'T');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags &= ~0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "G Shaw/F Barchard");
        strcpy(about->filterversion, "1.08");
        strcpy(about->name, "PalSort");
        strcpy(about->description, "Palette Sort");
        about->values = 2;
        about->value[0].type = 0x201;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 3;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "Method");
        strcpy(about->value[0].help, "Count,ARGB,HVS,WHVS,ICOUNT,YUV");
        about->value[1].type = 0x201;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = 1;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "ForceBlack");
        strcpy(about->value[1].help, "No,Yes");
    }
    return about;
}

// 1011a090.  Filter 18 "Shrink" 1.00.
GFILTERABOUT *SHRINK_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('S', 'H', 'N', 'K');
        about->size = sizeof(GFILTERABOUT);
        about->version = 100;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Shrink");
        strcpy(about->description, "Shrink To Fit");
        about->values = 0;
    }
    return about;
}

// 10118870.  Filter 19 "Blend" 1.09.
GFILTERABOUT *BLEND_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('B', 'L', 'N', 'D');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 2;
        about->unknown_1c = 2;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.09");
        strcpy(about->name, "Blend");
        strcpy(about->description, "Composite Blend");
        about->values = 6;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 4;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "Method");
        strcpy(about->value[0].help, "Alpha,Paste,Sub,Add,Remove");
        about->value[1].type = 0x1801;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = -1;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Colour");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x2;
        about->value[2].minimum.real = -200.0;
        about->value[2].maximum.real = 200.0;
        about->value[2].initial.real = 100.0;
        strcpy(about->value[2].name, "Foreground Percentage");
        strcpy(about->value[2].help, "");
        about->value[3].type = 0x2;
        about->value[3].minimum.real = -200.0;
        about->value[3].maximum.real = 200.0;
        about->value[3].initial.real = 100.0;
        strcpy(about->value[3].name, "Background Percentage");
        strcpy(about->value[3].help, "");
        about->value[4].type = 0x1;
        about->value[4].minimum.integer = 0;
        about->value[4].maximum.integer = 2;
        about->value[4].initial.integer = 0;
        strcpy(about->value[0].name, "Palette Method");
        strcpy(about->value[0].help, "Combine,Background,Foreground");
    }
    return about;
}

// 10117430.  Filter 20 "HSV" 1.02.
GFILTERABOUT *HSV_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'H', 'S', 'V');
        about->size = sizeof(GFILTERABOUT);
        about->version = 100;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.02");
        strcpy(about->name, "HSV");
        strcpy(about->description, "HSV Adjust");
        about->values = 4;
        about->value[0].type = 0x2;
        about->value[0].minimum.real = -180.0;
        about->value[0].maximum.real = 180.0;
        about->value[0].initial.real = 0.0;
        strcpy(about->value[0].name, "Hue");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x2;
        about->value[1].minimum.real = -100.0;
        about->value[1].maximum.real = 100.0;
        about->value[1].initial.real = 0.0;
        strcpy(about->value[1].name, "Saturation");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x2;
        about->value[2].minimum.real = -100.0;
        about->value[2].maximum.real = 100.0;
        about->value[2].initial.real = 0.0;
        strcpy(about->value[2].name, "Brightness");
        strcpy(about->value[2].help, "");
        about->value[3].type = 0x2;
        about->value[3].minimum.real = -100.0;
        about->value[3].maximum.real = 100.0;
        about->value[3].initial.real = 0.0;
        strcpy(about->value[2].name, "Value");
        strcpy(about->value[2].help, "");
    }
    return about;
}

// 10116a20.  Filter 21 "Line" 1.00.
GFILTERABOUT *LINE_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('L', 'I', 'N', 'E');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_18 = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Line");
        strcpy(about->description, "Line Image");
        about->values = 5;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = -1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "X1");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = -1;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Y1");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x1;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = -1;
        about->value[2].initial.integer = 1;
        strcpy(about->value[2].name, "X2");
        strcpy(about->value[2].help, "");
        about->value[3].type = 0x1;
        about->value[3].minimum.integer = 0;
        about->value[3].maximum.integer = -1;
        about->value[3].initial.integer = 1;
        strcpy(about->value[3].name, "Y2");
        strcpy(about->value[3].help, "");
        about->value[4].type = 0x1801;
        about->value[4].minimum.integer = 0;
        about->value[4].maximum.integer = -1;
        about->value[4].initial.integer = 0;
        strcpy(about->value[4].name, "Colour");
        strcpy(about->value[4].help, "");
    }
    return about;
}

// 10016a90.  Filter 22 "Scale" 1.00.
GFILTERABOUT *SCALE_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('S', 'C', 'A', 'L');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Scale");
        strcpy(about->description, "Scale Image");
        about->values = 2;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = -1;
        about->value[0].initial.integer = 1;
        strcpy(about->value[0].name, "Width");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = -1;
        about->value[1].initial.integer = 1;
        strcpy(about->value[1].name, "Height");
        strcpy(about->value[1].help, "");
    }
    return about;
}

// 10116400.  Filter 23 "Creep" 1.00.
GFILTERABOUT *CREEP_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('C', 'R', 'E', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Creep");
        strcpy(about->description, "Creep Image");
        about->values = 2;
        strcpy(about->value[0].name, "Colour");
        about->value[0].type = 0x1801;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = -1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[1].name, "Amount");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = -1;
        about->value[1].initial.integer = 1;
    }
    return about;
}

// 10115ba0.  Filter 24 "CSMap" 1.00.
GFILTERABOUT *CSMAP_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('H', 'M', 'A', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "CSMap");
        strcpy(about->description, "Color Space Remap");
        about->values = 0;
    }
    return about;
}

// 101143a0.  Filter 25 "Edge" 1.03.
GFILTERABOUT *EDGE_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('C', 'L', 'N', 'E');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.03");
        strcpy(about->name, "Edge");
        strcpy(about->description, "Clean Edges");
        about->values = 3;
        about->value[0].type = 0x801;
        strcpy(about->value[0].name, "Back Color");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 0;
        about->value[1].maximum.integer = 10;
        about->value[1].initial.integer = 1;
        strcpy(about->value[1].name, "Num Pixels");
        about->value[2].type = 0x1;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = 2;
        about->value[2].initial.integer = 0;
        strcpy(about->value[2].name, "Operation");
        strcpy(about->value[0].help, "Spikes and Pits,Spikes,Pits");
    }
    return about;
}

// 10113060.  Filter 26 "RadFill" 1.02.
GFILTERABOUT *RADFILL_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('R', 'F', 'I', 'L');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.02");
        strcpy(about->name, "RadFill");
        strcpy(about->description, "Radius Fill");
        about->values = 8;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 360;
        about->value[0].initial.integer = 5;
        strcpy(about->value[0].name, "Hue+");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = -360;
        about->value[1].maximum.integer = 0;
        about->value[1].initial.integer = -5;
        strcpy(about->value[1].name, "Hue-");
        about->value[2].type = 0x1;
        about->value[2].minimum.integer = 0;
        about->value[2].maximum.integer = 100;
        about->value[2].initial.integer = 100;
        strcpy(about->value[2].name, "Sat+");
        about->value[3].type = 0x1;
        about->value[3].minimum.integer = -100;
        about->value[3].maximum.integer = 0;
        about->value[3].initial.integer = -100;
        strcpy(about->value[3].name, "Sat-");
        about->value[4].type = 0x1;
        about->value[4].minimum.integer = 100;
        about->value[4].maximum.integer = 0;
        about->value[4].initial.integer = 25;
        strcpy(about->value[4].name, "Val+");
        about->value[5].type = 0x1;
        about->value[5].minimum.integer = -100;
        about->value[5].maximum.integer = 0;
        about->value[5].initial.integer = -25;
        strcpy(about->value[5].name, "Val-");
        about->value[6].type = 0x1;
        about->value[6].minimum.integer = 0;
        about->value[6].maximum.integer = 50;
        about->value[6].initial.integer = 10;
        strcpy(about->value[6].name, "Radius");
        about->value[7].type = 0x801;
        strcpy(about->value[7].name, "Fill Color");
    }
    return about;
}

// 101120e0.  Filter 27 "HSL" 1.03.
GFILTERABOUT *HSL_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'H', 'S', 'V');
        about->size = sizeof(GFILTERABOUT);
        about->version = 100;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.03");
        strcpy(about->name, "HSL");
        strcpy(about->description, "HSL Adjust");
        about->values = 4;
        about->value[0].type = 0x2;
        about->value[0].minimum.real = -180.0;
        about->value[0].maximum.real = 180.0;
        about->value[0].initial.real = 0.0;
        strcpy(about->value[0].name, "Hue");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x2;
        about->value[1].minimum.real = -100.0;
        about->value[1].maximum.real = 100.0;
        about->value[1].initial.real = 0.0;
        strcpy(about->value[1].name, "Saturation");
        strcpy(about->value[1].help, "");
        about->value[2].type = 0x2;
        about->value[2].minimum.real = -100.0;
        about->value[2].maximum.real = 100.0;
        about->value[2].initial.real = 0.0;
        strcpy(about->value[2].name, "Lightness");
        strcpy(about->value[2].help, "");
        about->value[3].type = 0x3;
        about->value[3].initial.real = 0.0;
        strcpy(about->value[3].name, "Mask");
    }
    return about;
}

// 10111e80.  Filter 28 "FChanmap" 1.01.
GFILTERABOUT *FCHANMAP_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'L', 'I', 'P');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "FBarchard,GShaw");
        strcpy(about->filterversion, "1.01");
        strcpy(about->name, "FChanmap");
        strcpy(about->description, "Chanmap");
        about->values = 0;
    }
    return about;
}

// 101117f0.  Filter 29 "Contrast" 1.00.
GFILTERABOUT *CONTRAST_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('C', 'O', 'N', 'T');
        about->size = sizeof(GFILTERABOUT);
        about->version = 100;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Contrast");
        strcpy(about->description, "Contrast/Brightness Adjust");
        about->values = 2;
        about->value[0].type = 0x2;
        about->value[0].minimum.real = -100.0;
        about->value[0].maximum.real = 100.0;
        about->value[0].initial.real = 0.0;
        strcpy(about->value[0].name, "Contrast");
        strcpy(about->value[0].help, "");
        about->value[1].type = 0x2;
        about->value[1].minimum.real = -100.0;
        about->value[1].maximum.real = 100.0;
        about->value[1].initial.real = 0.0;
        strcpy(about->value[1].name, "Brightness");
        strcpy(about->value[1].help, "");
    }
    return about;
}

// 101114a0.  Filter 30 "Deinterlace" 1.00.
GFILTERABOUT *DEINTERLACE_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('D', 'I', 'N', 'T');
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "G Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Deinterlace");
        strcpy(about->description, "Deinterlace");
        about->values = 1;
        about->value[0].type = 0x201;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 1;
        about->value[0].initial.integer = 0;
        strcpy(about->value[0].name, "Scan Line");
        strcpy(about->value[0].help, "Odd,Even");
    }
    return about;
}

// 1010ffe0.  Filter 32 "Chroma" 1.00.
GFILTERABOUT *CHROMA_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Chroma");
        strcpy(about->description, "Chroma Key");
        about->values = 1;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 255;
        about->value[0].initial.integer = 45;
        strcpy(about->value[0].name, "Tolerance");
    }
    return about;
}

// 1010f2a0.  Filter 33 "Smooth" 1.00.
GFILTERABOUT *SMOOTH_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->size = sizeof(GFILTERABOUT);
        about->version = 105;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 1;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Smooth");
        strcpy(about->description, "Smooth Edges");
        about->values = 2;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 0;
        about->value[0].maximum.integer = 255;
        about->value[0].initial.integer = 70;
        strcpy(about->value[0].name, "Threshold");
        about->value[1].type = 0x1;
        about->value[1].minimum.integer = 1;
        about->value[1].maximum.integer = 16;
        about->value[1].initial.integer = 1;
        strcpy(about->value[1].name, "Radius");
    }
    return about;
}

// 1010db10.  Filter 34 "Rotate" 1.01.
GFILTERABOUT *ROTATE_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.01");
        strcpy(about->name, "Rotate");
        strcpy(about->description, "Rotate");
        about->values = 3;
        about->value[0].type = 0x2;
        about->value[0].minimum.real = 0.0;
        about->value[0].maximum.real = 6.28318530718;
        about->value[0].initial.real = 0.0;
        strcpy(about->value[0].name, "Angle");
        about->value[1].type = 0x1801;
        about->value[1].initial.integer = 0;
        strcpy(about->value[1].name, "Colour");
        about->value[2].type = 0x1;
        about->value[2].initial.integer = 1;
        strcpy(about->value[2].name, "Interpolate");
    }
    return about;
}

// 1010d1e2.  Filter 35 "Texture" 1.00.
GFILTERABOUT *TEXTURE_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('F', 'T', 'E', 'X');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags &= ~0x1;
        about->flags |= 0x2;
        about->minimages = 0;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Gerry Shaw");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Texture");
        strcpy(about->description, "Texture Map");
        about->values = 2;
        about->value[0].type = 0x1;
        about->value[0].minimum.integer = 2;
        about->value[0].maximum.integer = 999;
        about->value[0].initial.integer = 3;
        strcpy(about->value[0].name, "NumVertices");
        about->value[1].type = 0x3;
        strcpy(about->value[1].name, "Vertices");
    }
    return about;
}

// 1010ba60.  Filter 36 "Gamma" 1.00.
GFILTERABOUT *GAMMA_about(void)
{
    GFILTERABOUT *about = (GFILTERABOUT *)galloc(sizeof(GFILTERABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GFILTERABOUT));
        about->tag = GTAG('G', 'A', 'M', 'A');
        about->size = sizeof(GFILTERABOUT);
        about->version = 104;
        about->flags |= 0x1;
        about->flags |= 0x2;
        about->minimages = 1;
        about->maximages = 1;
        about->unknown_1c = 0;
        strcpy(about->author, "Frank Barchard");
        strcpy(about->filterversion, "1.00");
        strcpy(about->name, "Gamma");
        strcpy(about->description, "Gamma Correct");
        about->values = 4;
        about->value[0].type = 0x2;
        about->value[0].minimum.real = -4.0;
        about->value[0].maximum.real = 4.0;
        about->value[0].initial.real = 1.0;
        strcpy(about->value[0].name, "AlphaGamma");
        about->value[1].type = 0x2;
        about->value[1].minimum.real = -4.0;
        about->value[1].maximum.real = 4.0;
        about->value[1].initial.real = 1.0;
        strcpy(about->value[1].name, "RedGamma");
        about->value[2].type = 0x2;
        about->value[2].minimum.real = -4.0;
        about->value[2].maximum.real = 4.0;
        about->value[2].initial.real = 1.0;
        strcpy(about->value[2].name, "GreenGamma");
        about->value[3].type = 0x2;
        about->value[3].minimum.real = -4.0;
        about->value[3].maximum.real = 4.0;
        about->value[3].initial.real = 1.0;
        strcpy(about->value[3].name, "BlueGamma");
    }
    return about;
}
