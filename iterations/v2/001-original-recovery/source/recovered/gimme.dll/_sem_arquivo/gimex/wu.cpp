// "Wu" colour quantizer 1.04 (Wu, F.Barchard, A.Brownsword): quantizer 1, used by FaceInRace's
// ReduceImage.  gimme.dll 3a43b0f6…, VA 101307a0–1013206c.
//
// Xiaolin Wu's greedy orthogonal bipartition of RGB space ("Efficient Statistical Computations
// for Optimal Color Quantization", Graphics Gems II) with the histogram widened from 5 to 6
// bits per channel (65^3 moment cells) and an optional inverse-colour table.  Box directions
// are 2 red, 1 green, 0 blue as in the published code.  Floating-point expressions follow the
// original's x87 code: a "(double)" marks an integer that the original loads with fild straight
// into a float operation, without rounding it to float first.

#include <string.h>

#include "gimexfilter.h"

#define WU_SIDE 65                                   // 64 levels per channel plus the zero plane
#define WU_CELLS (WU_SIDE * WU_SIDE * WU_SIDE)       // 0x430c1

#define WU_BLUE 0
#define WU_GREEN 1
#define WU_RED 2

typedef int WUMOMENTS[WU_SIDE][WU_SIDE][WU_SIDE];
typedef float WUSQUARES[WU_SIDE][WU_SIDE][WU_SIDE];

// One box of colour space, lower bounds exclusive (0x1c bytes).
struct WUBOX
{
    int r0, r1;
    int g0, g1;
    int b0, b1;
    int vol;
};

// Histogram and cumulative moments (0x28 bytes).
struct WUSTATE
{
    float *m2;                   // +0x00 sum of squared components, WU_CELLS floats
    int *wt;                     // +0x04 pixel counts      } four WU_CELLS arrays in one
    int *mr;                     // +0x08 sum of red        } block, see moments
    int *mg;                     // +0x0c sum of green      }
    int *mb;                     // +0x10 sum of blue       }
    const unsigned char *pixels; // +0x14 image of the last add()
    int width;                   // +0x18
    int height;                  // +0x1c
    int rowbytes;                // +0x20
    int *moments;                // +0x24 the block holding wt, mr, mg and mb
};

// Quantizer handle returned by open() (0x10 bytes).
struct WUHANDLE
{
    unsigned tag;                // 'WUCR'
    int unknown_04;              // 4
    int unknown_08;
    WUSTATE *state;
};

// Inverse-colour table make() returns through its third argument (0x40010 bytes): the palette
// index of every 6-bit colour, index (r << 12) + (g << 6) + b.
struct WUINVERSE
{
    unsigned tag;                // 'INVW'
    int size;                    // sizeof(WUINVERSE)
    unsigned char unknown_08;    // 0
    unsigned char redbits;       // 6
    unsigned char greenbits;     // 6
    unsigned char bluebits;      // 6
    int unknown_0c;              // never written
    unsigned char index[64 * 64 * 64];
};

static_assert(sizeof(WUBOX) == 0x1c, "WUBOX layout");
static_assert(sizeof(WUSTATE) == 0x28, "WUSTATE layout");
static_assert(sizeof(WUINVERSE) == 0x40010, "WUINVERSE layout");

// 101307a0.
GQUANTABOUT *WU_about(void)
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
        strcpy(about->name, "Wu");
        strcpy(about->description, "Wu's (6 bit)");
    }
    return about;
}

// 101308cb.  Allocates the cleared histogram.
static WUSTATE *CreateState(void)
{
    int size = 4 * WU_CELLS * sizeof(int);
    WUSTATE *state = (WUSTATE *)galloc(sizeof(WUSTATE));
    if (!state)
        return 0;
    memset(state, 0, sizeof(WUSTATE));
    state->moments = (int *)galloc(size);
    state->m2 = (float *)galloc(WU_CELLS * sizeof(float));
    if (!state->moments || !state->m2)
    {
        if (state->moments)
            gfree(state->moments);
        if (state->m2)
            gfree(state->m2);
        gfree(state);
        return 0;
    }
    memset(state->moments, 0, size);
    memset(state->m2, 0, WU_CELLS * sizeof(float));
    state->wt = state->moments;
    state->mr = state->wt + WU_CELLS;
    state->mg = state->mr + WU_CELLS;
    state->mb = state->mg + WU_CELLS;
    return state;
}

// 10130867.
void *WU_open(void)
{
    WUHANDLE *handle = (WUHANDLE *)galloc(sizeof(WUHANDLE));
    if (handle)
    {
        WUSTATE *state = CreateState();
        if (state)
        {
            memset(handle, 0, sizeof(WUHANDLE));
            handle->tag = GTAG('W', 'U', 'C', 'R');
            handle->unknown_04 = 4;
            handle->state = state;
            return handle;
        }
        gfree(handle);
    }
    return 0;
}

// 10130a4e.  Adds the image to the histogram: weight, colour sums and squared magnitudes.
static void Hist3d(WUSTATE *state, int *vwt, int *vmr, int *vmg, int *vmb, float *m2)
{
    int table[256];
    for (int i = 0; i < 256; ++i)
        table[i] = i * i;
    for (int y = 0; y < state->height; ++y)
    {
        const unsigned char *pixel = state->pixels + y * state->rowbytes;
        for (int count = state->width; count != 0; --count)
        {
            int r = pixel[2];
            int g = pixel[1];
            int b = pixel[0];
            int inr = (r >> 2) + 1;
            int ing = (g >> 2) + 1;
            int inb = (b >> 2) + 1;
            int ind = inr * WU_SIDE * WU_SIDE + ing * WU_SIDE + inb;
            ++vwt[ind];
            vmr[ind] += r;
            vmg[ind] += g;
            vmb[ind] += b;
            m2[ind] += table[r] + table[g] + table[b];   // at most 3 * 255^2, exact in a float
            pixel += 4;
        }
    }
}

// 101309d1.  Only 32-bit images are accepted.
int GCALL WU_add(void *handle, const GINFO *info, const void *pixels, int rowbytes)
{
    WUSTATE *state = ((WUHANDLE *)handle)->state;
    if (info->bpp != 32)
        return 0;
    state->width = info->width;
    state->height = info->height;
    state->rowbytes = rowbytes;
    state->pixels = (const unsigned char *)pixels;
    Hist3d(state, state->wt, state->mr, state->mg, state->mb, state->m2);
    return 1;
}

// 10131087.  Turns the histogram into cumulative moments.
static void M3d(int *vwt, int *vmr, int *vmg, int *vmb, float *m2)
{
    int area[WU_SIDE], area_r[WU_SIDE], area_g[WU_SIDE], area_b[WU_SIDE];
    float area2[WU_SIDE];
    for (unsigned char r = 1; r <= 64; ++r)
    {
        for (unsigned char i = 0; i <= 64; ++i)
            area2[i] = area[i] = area_r[i] = area_g[i] = area_b[i] = 0;
        for (unsigned char g = 1; g <= 64; ++g)
        {
            int line, line_r, line_g, line_b;
            float line2 = line = line_r = line_g = line_b = 0;
            for (unsigned char b = 1; b <= 64; ++b)
            {
                int ind1 = r * WU_SIDE * WU_SIDE + g * WU_SIDE + b;   // [r][g][b]
                line += vwt[ind1];
                line_r += vmr[ind1];
                line_g += vmg[ind1];
                line_b += vmb[ind1];
                line2 += m2[ind1];
                area[b] += line;
                area_r[b] += line_r;
                area_g[b] += line_g;
                area_b[b] += line_b;
                area2[b] += line2;
                int ind2 = ind1 - WU_SIDE * WU_SIDE;                    // [r - 1][g][b]
                vwt[ind1] = vwt[ind2] + area[b];
                vmr[ind1] = vmr[ind2] + area_r[b];
                vmg[ind1] = vmg[ind2] + area_g[b];
                vmb[ind1] = vmb[ind2] + area_b[b];
                m2[ind1] = m2[ind2] + area2[b];
            }
        }
    }
}

// 1013145d.  Sum of a moment over the box.
static int Vol(const WUBOX *cube, WUMOMENTS mmt)
{
    return mmt[cube->r1][cube->g1][cube->b1] - mmt[cube->r1][cube->g1][cube->b0] -
           mmt[cube->r1][cube->g0][cube->b1] + mmt[cube->r1][cube->g0][cube->b0] -
           mmt[cube->r0][cube->g1][cube->b1] + mmt[cube->r0][cube->g1][cube->b0] +
           mmt[cube->r0][cube->g0][cube->b1] - mmt[cube->r0][cube->g0][cube->b0];
}

// 10131bc7.  Part of Vol() that does not depend on the cut position along dir.  As published,
// there is no return for any other direction (dir is always one of the three).
#pragma warning(disable : 4715)
static int Bottom(const WUBOX *cube, unsigned char dir, WUMOMENTS mmt)
{
    switch (dir)
    {
    case WU_RED:
        return -mmt[cube->r0][cube->g1][cube->b1] + mmt[cube->r0][cube->g1][cube->b0] +
               mmt[cube->r0][cube->g0][cube->b1] - mmt[cube->r0][cube->g0][cube->b0];
    case WU_GREEN:
        return -mmt[cube->r1][cube->g0][cube->b1] + mmt[cube->r1][cube->g0][cube->b0] +
               mmt[cube->r0][cube->g0][cube->b1] - mmt[cube->r0][cube->g0][cube->b0];
    case WU_BLUE:
        return -mmt[cube->r1][cube->g1][cube->b0] + mmt[cube->r1][cube->g0][cube->b0] +
               mmt[cube->r0][cube->g1][cube->b0] - mmt[cube->r0][cube->g0][cube->b0];
    }
}

// 10131de0.  Remainder of Vol() when the box is cut at pos along dir.
static int Top(const WUBOX *cube, unsigned char dir, int pos, WUMOMENTS mmt)
{
    switch (dir)
    {
    case WU_RED:
        return mmt[pos][cube->g1][cube->b1] - mmt[pos][cube->g1][cube->b0] -
               mmt[pos][cube->g0][cube->b1] + mmt[pos][cube->g0][cube->b0];
    case WU_GREEN:
        return mmt[cube->r1][pos][cube->b1] - mmt[cube->r1][pos][cube->b0] -
               mmt[cube->r0][pos][cube->b1] + mmt[cube->r0][pos][cube->b0];
    case WU_BLUE:
        return mmt[cube->r1][cube->g1][pos] - mmt[cube->r1][cube->g0][pos] -
               mmt[cube->r0][cube->g1][pos] + mmt[cube->r0][cube->g0][pos];
    }
}
#pragma warning(default : 4715)

// 101315a2.  Weighted variance of the box.
static float Var(WUSTATE *state, const WUBOX *cube)
{
    WUSQUARES &m2 = *(WUSQUARES *)state->m2;
    float dr = Vol(cube, *(WUMOMENTS *)state->mr);
    float dg = Vol(cube, *(WUMOMENTS *)state->mg);
    float db = Vol(cube, *(WUMOMENTS *)state->mb);
    float xx = m2[cube->r1][cube->g1][cube->b1] - m2[cube->r1][cube->g1][cube->b0] -
               m2[cube->r1][cube->g0][cube->b1] + m2[cube->r1][cube->g0][cube->b0] -
               m2[cube->r0][cube->g1][cube->b1] + m2[cube->r0][cube->g1][cube->b0] +
               m2[cube->r0][cube->g0][cube->b1] - m2[cube->r0][cube->g0][cube->b0];
    float sum = dr * dr + dg * dg + db * db;
    return xx - sum / (double)Vol(cube, *(WUMOMENTS *)state->wt);
}

// 10131a07.  Best cut of the box along dir between first and last (-1 in *cut if none).
// The sum is compared before it is rounded into temp, as in the original.
static float Maximize(WUSTATE *state, const WUBOX *cube, unsigned char dir, int first, int last, int *cut,
                      int whole_r, int whole_g, int whole_b, int whole_w)
{
    int base_r = Bottom(cube, dir, *(WUMOMENTS *)state->mr);
    int base_g = Bottom(cube, dir, *(WUMOMENTS *)state->mg);
    int base_b = Bottom(cube, dir, *(WUMOMENTS *)state->mb);
    int base_w = Bottom(cube, dir, *(WUMOMENTS *)state->wt);
    float max = 0.0f;
    *cut = -1;
    for (int i = first; i < last; ++i)
    {
        int half_r = base_r + Top(cube, dir, i, *(WUMOMENTS *)state->mr);
        int half_g = base_g + Top(cube, dir, i, *(WUMOMENTS *)state->mg);
        int half_b = base_b + Top(cube, dir, i, *(WUMOMENTS *)state->mb);
        int half_w = base_w + Top(cube, dir, i, *(WUMOMENTS *)state->wt);
        if (half_w == 0)
            continue;   // never split into an empty box
        float temp = ((double)half_r * half_r + (double)half_g * half_g + (double)half_b * half_b) / half_w;
        half_r = whole_r - half_r;
        half_g = whole_g - half_g;
        half_b = whole_b - half_b;
        half_w = whole_w - half_w;
        if (half_w == 0)
            continue;
        double sum = ((double)half_r * half_r + (double)half_g * half_g + (double)half_b * half_b) / half_w + temp;
        temp = (float)sum;
        if (sum > max)
        {
            max = temp;
            *cut = i;
        }
    }
    return max;
}

// 10131789.  Splits set1 into set1 and set2 along the direction of greatest gain.
static int Cut(WUSTATE *state, WUBOX *set1, WUBOX *set2)
{
    int cutr, cutg, cutb;
    unsigned char dir;
    int whole_r = Vol(set1, *(WUMOMENTS *)state->mr);
    int whole_g = Vol(set1, *(WUMOMENTS *)state->mg);
    int whole_b = Vol(set1, *(WUMOMENTS *)state->mb);
    int whole_w = Vol(set1, *(WUMOMENTS *)state->wt);
    float maxr = Maximize(state, set1, WU_RED, set1->r0 + 1, set1->r1, &cutr, whole_r, whole_g, whole_b, whole_w);
    float maxg = Maximize(state, set1, WU_GREEN, set1->g0 + 1, set1->g1, &cutg, whole_r, whole_g, whole_b, whole_w);
    float maxb = Maximize(state, set1, WU_BLUE, set1->b0 + 1, set1->b1, &cutb, whole_r, whole_g, whole_b, whole_w);
    if (maxr >= maxg && maxr >= maxb)
    {
        dir = WU_RED;
        if (cutr < 0)
            return 0;   // can't split the box
    }
    else if (maxg >= maxr && maxg >= maxb)
        dir = WU_GREEN;
    else
        dir = WU_BLUE;
    set2->r1 = set1->r1;
    set2->g1 = set1->g1;
    set2->b1 = set1->b1;
    switch (dir)
    {
    case WU_RED:
        set2->r0 = set1->r1 = cutr;
        set2->g0 = set1->g0;
        set2->b0 = set1->b0;
        break;
    case WU_GREEN:
        set2->g0 = set1->g1 = cutg;
        set2->r0 = set1->r0;
        set2->b0 = set1->b0;
        break;
    case WU_BLUE:
        set2->b0 = set1->b1 = cutb;
        set2->r0 = set1->r0;
        set2->g0 = set1->g0;
        break;
    }
    set1->vol = (set1->r1 - set1->r0) * (set1->g1 - set1->g0) * (set1->b1 - set1->b0);
    set2->vol = (set2->r1 - set2->r0) * (set2->g1 - set2->g0) * (set2->b1 - set2->b0);
    return 1;
}

// 10131fd9.  Writes label into the inverse table for every colour of the box.
static void Mark(const WUBOX *cube, unsigned char label, WUINVERSE *inverse)
{
    unsigned char *tag = inverse->index;
    for (int r = cube->r0; r < cube->r1; ++r)
        for (int g = cube->g0; g < cube->g1; ++g)
            for (int b = cube->b0; b < cube->b1; ++b)
                tag[(r << 12) + (g << 6) + b] = label;
}

// 10130c74.  Builds a palette of at most `colours` entries and frees the quantizer.  `exact`
// (named after FaceInRace's use) receives a newly allocated WUINVERSE table when it is not
// null; FaceInRace never frees it.  Unused palette entries and empty boxes stay zero.
GCOLOUR *GCALL WU_make(void *handle, int colours, int *exact)
{
    WUINVERSE **inverse = (WUINVERSE **)exact;
    WUSTATE *state = ((WUHANDLE *)handle)->state;
    WUBOX *cube = 0;
    float *vv = 0;
    cube = (WUBOX *)galloc(colours * sizeof(WUBOX));
    vv = (float *)galloc(colours * sizeof(float));
    M3d(state->wt, state->mr, state->mg, state->mb, state->m2);
    cube[0].r0 = cube[0].g0 = cube[0].b0 = 0;
    cube[0].r1 = cube[0].g1 = cube[0].b1 = 64;
    int next = 0;
    int count = colours;
    for (int i = 1; i < count; ++i)
    {
        if (Cut(state, &cube[next], &cube[i]))
        {
            // volume test ensures we won't try to cut a one-cell box
            vv[next] = cube[next].vol > 1 ? Var(state, &cube[next]) : 0.0f;
            vv[i] = cube[i].vol > 1 ? Var(state, &cube[i]) : 0.0f;
        }
        else
        {
            vv[next] = 0.0f;   // don't try to split this box again
            --i;               // didn't create box i
        }
        next = 0;
        float temp = vv[0];
        for (int k = 1; k <= i; ++k)
            if (vv[k] > temp)
            {
                temp = vv[k];
                next = k;
            }
        if (!(temp > 0.0))   // also a NaN, as the original's flag test
        {
            count = i + 1;
            break;
        }
    }
    gfree(state->m2);
    state->m2 = 0;
    GCOLOUR *palette = (GCOLOUR *)galloc(colours * sizeof(GCOLOUR));
    if (inverse)
    {
        *inverse = (WUINVERSE *)galloc(sizeof(WUINVERSE));
        (*inverse)->tag = GTAG('I', 'N', 'V', 'W');
        (*inverse)->size = sizeof(WUINVERSE);
        (*inverse)->unknown_08 = 0;
        (*inverse)->redbits = 6;
        (*inverse)->greenbits = 6;
        (*inverse)->bluebits = 6;
    }
    if (palette)
    {
        memset(palette, 0, colours * sizeof(GCOLOUR));
        if (inverse && *inverse)
            memset((*inverse)->index, 0, sizeof((*inverse)->index));
        for (int k = 0; k < count; ++k)
        {
            if (inverse && *inverse)
                Mark(&cube[k], k, *inverse);
            int weight = Vol(&cube[k], *(WUMOMENTS *)state->wt);
            if (weight)
            {
                palette[k].a = 0xff;
                palette[k].r = Vol(&cube[k], *(WUMOMENTS *)state->mr) / weight;
                palette[k].g = Vol(&cube[k], *(WUMOMENTS *)state->mg) / weight;
                palette[k].b = Vol(&cube[k], *(WUMOMENTS *)state->mb) / weight;
            }
        }
    }
    if (cube)
        gfree(cube);
    if (vv)
        gfree(vv);
    if (state->moments)
        gfree(state->moments);
    if (state->m2)
        gfree(state->m2);
    gfree(state);
    gfree(handle);
    return palette;
}
