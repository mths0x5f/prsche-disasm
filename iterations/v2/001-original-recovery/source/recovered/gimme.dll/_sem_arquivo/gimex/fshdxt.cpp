// FSH Shape File module: the 18fb block compressor (4x4 colour blocks with optional alpha).
// gimme.dll 3a43b0f6…, VA 100fc155–10104a9f, called only by the writer for GINFO.compression 3
// (BuildBitmap, 100fa289).  Function names are role names.
//
// Floating point follows the original x87 code operation by operation (the build uses
// /arch:IA32 /fp:precise, so every double expression is evaluated in the same order with the
// same roundings).  Comparisons are written to keep the original's NaN behaviour: the x87
// branches treat an unordered result like "less" or "equal", hence forms such as !(a >= b).
//
// The work arrays are file-scope statics like the original's BSS (0x1046daf8–0x10472158); two
// best-so-far values keep their state between calls as in the original (see ClusterFit).
//
// The writer always passes flags 0 (100fc155), so the alpha encoders (flags 0x100 and 0x200,
// FitAlpha and FitAlphaRamp) are not reached from the FSH entry points.  Recovery boundary:
// FitAlphaRamp reads index values the caller never initialised (10103580 passes an
// uninitialised stack array; only element 0 is cleared), so its first convergence test depends
// on stack contents in the original.  The same reads are kept here.

#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "fsh.h"

// 100fd235 input/output (0x200 bytes, on the stack of CompressBlocks).
struct COLOURBLOCK
{
    int count;                   // +0x000 pixels present in the block
    int unused;
    double colour[16][3];        // +0x008 r, g, b in 0..1
    double weight[3];            // +0x188 channel weights
    int levels;                  // +0x1a0 4 when the block is complete, else 3
    int result;                  // +0x1a4 levels chosen (3 or 4)
    int endpoint[2][3];          // +0x1a8 5:6:5 endpoint values
    int index[16];               // +0x1c0
};

static_assert(sizeof(COLOURBLOCK) == 0x200, "COLOURBLOCK layout");

// 10103580 input/output (0x98 bytes).
struct ALPHABLOCK
{
    int count;                   // +0x00
    float value[16];             // +0x04 alpha in 0..1
    unsigned keepzero;           // +0x44 flags & 0x10000
    unsigned keepone;            // +0x48 flags & 0x20000
    int levels;                  // +0x4c 8 or 6
    int endpoint[2];             // +0x50
    int index[16];               // +0x58
};

static_assert(sizeof(ALPHABLOCK) == 0x98, "ALPHABLOCK layout");

static const int kBits[3] = { 5, 6, 5 };          // 0x1043d3b8 (FitSingleColour)
static const int kRefineBits[3] = { 5, 6, 5 };    // 0x1040c5b8 (RefineEndpoints)

// 0x1043d3c4: palette entry m of a single-colour fit is (a*e0 + b*e1 + c) / d.
static const int kSingleMix[3][4] = { { 1, 0, 0, 1 }, { 1, 1, 0, 2 }, { 1, 2, 1, 3 } };

// 0x1043d3f4 and 0x1043d410: endpoint candidates tried by QuantizeEndpoints, as weights of the
// two fitted endpoints, by mode (3 or 4 levels) and fitted result.
static const int kTrialCount[2][3] = { { 2, 0, 0 }, { 6, 2, 0 } };
static const double kTrialWeight[2][2][6][2][2] = {
    { { { { 2.0, -1.0 }, { 0.0, 1.0 } }, { { 1.0, 0.0 }, { -1.0, 2.0 } } },
      { } },
    { { { { 1.0, 0.0 }, { 0.0, 1.0 } }, { { 1.0, 0.0 }, { -2.0, 3.0 } }, { { 3.0, -2.0 }, { 0.0, 1.0 } },
        { { 2.0, -1.0 }, { -1.0, 2.0 } }, { { 1.5, -0.5 }, { 0.0, 1.0 } }, { { 1.0, 0.0 }, { -0.5, 1.5 } } },
      { { { 1.5, -0.5 }, { 0.0, 1.0 } }, { { 1.0, 0.0 }, { -0.5, 1.5 } } } } };

// FitColours (100fd235)
static double g_inverse;                 // 0x1046dc80 1 / pixel count
static double g_clampweight[3];          // 0x10472090
static double g_mean[3];                 // 0x10470028
static double g_weighted[16][3];         // 0x1046dfc0
static double g_centred[16][3];          // 0x10471ba8
static double g_bounds[2][3];            // 0x1046dc90 -mean, weight - mean
static double g_unique[16][3];           // 0x1046db00
static double g_uniquecentred[16][3];    // 0x1046e148
static double g_uniqueweight[16];        // 0x10471eb0
static double g_axis[3];                 // 0x10471f90
static double g_ends[2][2][3];           // 0x10471b48
static double g_error[2];                // 0x10471ff8
// PrincipalAxis (100fe213)
static double g_matrix[3][3];            // 0x104720a8 (upper triangle)
static double g_square[3][3];            // 0x1046dcf0 (upper triangle)
static double g_trace;                   // 0x10471f48
static double g_scale;                   // 0x10470020
// AxisFromExtremes (100fe78e)
static double g_maxdistance;             // 0x1046dce8
static double g_distance;                // 0x10472008
// SortAlongAxis (100fe919)
static double g_key[16];                 // 0x1046df40
// ClusterFit (100feb87)
static double g_points[16][3];           // 0x1046dd70
static double g_pointweight[16];         // 0x10472010
static double g_sumA[3], g_sumB[3], g_sumC[3];   // 0x104720f0, 0x10472108, 0x10472120
static double g_w2A, g_w2B, g_w2C;       // 0x10471f78, 0x10471f80, 0x10471f88
static double g_wA, g_wB, g_wC;          // 0x1046def0, 0x1046def8, 0x1046df00
static double g_besterror;               // 0x10472148, kept between calls
static double g_bestscale = 1.0;         // 0x1043d3a8, kept between calls
// ClampedClusterFit (100ff449)
static double g_cpoints[16][3];          // 0x1046fea0
static double g_cpointweight[16];        // 0x1046fb10
static double g_csumA[3], g_csumB[3], g_csumC[3];   // 0x1046e2c8, 0x1046e2e0, 0x1046e2f8
static double g_cw2A, g_cw2B, g_cw2C;    // 0x10471fa8, 0x10471fb0, 0x10471fb8
static double g_cwA, g_cwB, g_cwC;       // 0x10471f60, 0x10471f68, 0x10471f70
static double g_cbesterror;              // 0x10472150, kept between calls
static double g_cbestscale = 1.0;        // 0x1043d3b0, kept between calls
// FitSingleColour (101001d1)
static int g_singleready;                // 0x10472158
static unsigned char g_single[256][3][3][3];   // 0x10470040 [value][channel][mix]: set, e0, e1
static double g_singleerror[3];          // 0x1046dcc0
static double g_candidateerror[2];       // 0x1046fc10
// QuantizeEndpoints (101008a5)
static double g_trial[2][3];             // 0x1046df08
static double g_quantizeerror[2];        // 0x10471f30
// RefineEndpoints (10100c5a)
static double g_target;                  // 0x1046dce0
static double g_palette[3][4][4];        // 0x10471d30 [channel][variant][entry]
static double g_entryerror[3][4][16][4]; // 0x1046e310 [channel][variant][pixel][entry]
static double g_refinebest;              // 0x1046df38
// FitAlpha (10103580)
static double g_alphaset[5][16];         // 0x1046fc20
static double g_alphaerror[5];           // 0x1046dd48
// FitAlphaRamp (10103a85)
static double g_count;                   // 0x1046dd38
static double g_reciprocal;              // 0x10471d28
static double g_alphamean;               // 0x1046dcd8
static double g_range[2];                // 0x10471f50 low, high (relative to the mean)
static double g_centredalpha[16];        // 0x1046fb90
static double g_threshold[8];            // 0x10471fc0
static double g_sumii;                   // 0x10471f40
static double g_sumi;                    // 0x1046daf8
static double g_sumiv;                   // 0x10471b40
static double g_rampserror;              // 0x1046e140
static double g_rampscale;               // 0x1046dc88
static double g_previousrange[2];        // 0x10472138
static double g_rampindexerror;          // 0x1046dd40

// ---------------------------------------------------------------------------------------------
// Colour fit helpers

// 100fe213.  Dominant eigenvector of the covariance by repeated squaring (normalised by 3.5 over
// the trace before each round).
static void PrincipalAxis(int count, double (*v)[3], double *axis)
{
    int i, r, c, k, largest;
    g_matrix[2][2] = 0.0;
    g_matrix[1][2] = g_matrix[2][2];
    g_matrix[1][1] = g_matrix[1][2];
    g_matrix[0][2] = g_matrix[1][1];
    g_matrix[0][1] = g_matrix[0][2];
    g_matrix[0][0] = g_matrix[0][1];
    for (i = 0; i < count; ++i)
    {
        g_matrix[0][0] = v[i][0] * v[i][0] + g_matrix[0][0];
        g_matrix[0][1] = v[i][0] * v[i][1] + g_matrix[0][1];
        g_matrix[0][2] = v[i][0] * v[i][2] + g_matrix[0][2];
        g_matrix[1][1] = v[i][1] * v[i][1] + g_matrix[1][1];
        g_matrix[1][2] = v[i][1] * v[i][2] + g_matrix[1][2];
        g_matrix[2][2] = v[i][2] * v[i][2] + g_matrix[2][2];
    }
    for (k = 0; k < 3; ++k)
    {
        g_trace = g_matrix[0][0] + g_matrix[1][1] + g_matrix[2][2];
        g_scale = 3.5 / g_trace;
        for (r = 0; r < 3; ++r)
            for (c = r; c < 3; ++c)
                g_matrix[r][c] = g_scale * g_matrix[r][c];
        for (c = 0; c < 4; ++c)
        {
            g_square[0][0] = g_matrix[0][0] * g_matrix[0][0] + g_matrix[0][1] * g_matrix[0][1] + g_matrix[0][2] * g_matrix[0][2];
            g_square[0][1] = g_matrix[0][0] * g_matrix[0][1] + g_matrix[0][1] * g_matrix[1][1] + g_matrix[0][2] * g_matrix[1][2];
            g_square[0][2] = g_matrix[0][0] * g_matrix[0][2] + g_matrix[0][1] * g_matrix[1][2] + g_matrix[0][2] * g_matrix[2][2];
            g_square[1][1] = g_matrix[0][1] * g_matrix[0][1] + g_matrix[1][1] * g_matrix[1][1] + g_matrix[1][2] * g_matrix[1][2];
            g_square[1][2] = g_matrix[0][1] * g_matrix[0][2] + g_matrix[1][1] * g_matrix[1][2] + g_matrix[1][2] * g_matrix[2][2];
            g_square[2][2] = g_matrix[0][2] * g_matrix[0][2] + g_matrix[1][2] * g_matrix[1][2] + g_matrix[2][2] * g_matrix[2][2];
            g_matrix[0][0] = g_square[0][0] * g_square[0][0] + g_square[0][1] * g_square[0][1] + g_square[0][2] * g_square[0][2];
            g_matrix[0][1] = g_square[0][0] * g_square[0][1] + g_square[0][1] * g_square[1][1] + g_square[0][2] * g_square[1][2];
            g_matrix[0][2] = g_square[0][0] * g_square[0][2] + g_square[0][1] * g_square[1][2] + g_square[0][2] * g_square[2][2];
            g_matrix[1][1] = g_square[0][1] * g_square[0][1] + g_square[1][1] * g_square[1][1] + g_square[1][2] * g_square[1][2];
            g_matrix[1][2] = g_square[0][1] * g_square[0][2] + g_square[1][1] * g_square[1][2] + g_square[1][2] * g_square[2][2];
            g_matrix[2][2] = g_square[0][2] * g_square[0][2] + g_square[1][2] * g_square[1][2] + g_square[2][2] * g_square[2][2];
        }
    }
    if (g_matrix[0][0] > g_matrix[1][1])
        largest = g_matrix[0][0] > g_matrix[2][2] ? 0 : 2;
    else
        largest = g_matrix[1][1] > g_matrix[2][2] ? 1 : 2;
    g_scale = 1.0 / sqrt(g_matrix[largest][largest]);
    for (i = 0; i < largest; ++i)
        axis[i] = g_scale * g_square[i][largest];
    for (; i < 3; ++i)
        axis[i] = g_scale * g_square[largest][i];
}

// 100fe78e.  Direction between the two most distant colours.
static void AxisFromExtremes(int count, double (*v)[3], double *axis)
{
    int i, j, a, b;
    double d0, d1, d2;
    g_maxdistance = 0.0;
    for (i = 0; i < count; ++i)
        for (j = i; j < count; ++j)
        {
            d0 = v[i][0] - v[j][0];
            d1 = v[i][1] - v[j][1];
            d2 = v[i][2] - v[j][2];
            g_distance = d0 * d0 + d1 * d1 + d2 * d2;
            if (g_distance > g_maxdistance)
            {
                g_maxdistance = g_distance;
                a = i;
                b = j;
            }
        }
    g_maxdistance = 1.0 / sqrt(g_maxdistance);
    axis[0] = (v[a][0] - v[b][0]) * g_maxdistance;
    axis[1] = (v[a][1] - v[b][1]) * g_maxdistance;
    axis[2] = (v[a][2] - v[b][2]) * g_maxdistance;
}

// 100fe919.  Selection sort of the colours by their projection on the axis; ties go to the
// first (mode 0) or the last (mode 1) candidate.
static void SortAlongAxis(int count, double (*v)[3], double *axis, int *order, int mode)
{
    int left[16];
    int i, j, best;
    for (i = 0; i < count; ++i)
    {
        g_key[i] = v[i][0] * axis[0] + v[i][1] * axis[1] + v[i][2] * axis[2];
        left[i] = 1;
    }
    if (mode == 0)
    {
        for (i = 0; i < count; ++i)
        {
            for (j = 0; j < count && left[j] == 0; ++j)
                ;
            best = j;
            for (j = j + 1; j < count; ++j)
                if (left[j] != 0 && !(g_key[j] >= g_key[best]))
                    best = j;
            left[best] = 0;
            order[i] = best;
        }
    }
    else
    {
        for (i = 0; i < count; ++i)
        {
            for (j = 0; j < count && left[j] == 0; ++j)
                ;
            best = j;
            for (j = j + 1; j < count; ++j)
                if (left[j] != 0 && !(g_key[j] > g_key[best]))
                    best = j;
            left[best] = 0;
            order[i] = best;
        }
    }
}

// 100feb00.  1 when two orders are equal or reversed.
static int SameOrder(int count, const int *a, const int *b)
{
    int i;
    for (i = 0; i < count && a[i] == b[i]; ++i)
        ;
    if (i < count)
        for (i = 0; i < count && a[i] == b[count - 1 - i]; ++i)
            ;
    return i == count;
}

// 100feb87.  Exhaustive split of the ordered colours into up to four runs (*levels >= 3 enables
// the fourth); minimises -|sum|^2 / weight by cross multiplication against a best value that is
// static in the original (the first candidate of every call resets it).  Returns the error,
// writes the two endpoints (relative to the mean) and the weighted sum to `sum`.
static double ClusterFit(int *levels, int count, double (*points)[3], double *weights, int *order, double (*ends)[3],
                         double *sum)
{
    int last = 0;
    int split[4];
    int changes, i, j, k, c, l0, l1, l2;
    double t, a, b, error;
    for (i = 0; i < count; ++i)
        for (c = 0; c < 3; ++c)
        {
            g_points[i][c] = points[order[i]][c];
            g_pointweight[i] = weights[order[i]];
        }
    g_wA = 0.0;
    g_w2A = g_wA;
    g_sumA[2] = g_w2A;
    g_sumA[1] = g_sumA[2];
    g_sumA[0] = g_sumA[1];
    g_wB = 0.0;
    g_w2B = g_wB;
    g_sumB[2] = g_w2B;
    g_sumB[1] = g_sumB[2];
    g_sumB[0] = g_sumB[1];
    g_wC = 0.0;
    g_w2C = g_wC;
    g_sumC[2] = g_w2C;
    g_sumC[1] = g_sumC[2];
    g_sumC[0] = g_sumC[1];
    l0 = count;
    for (;;)
    {
        l1 = count;
        for (;;)
        {
            l2 = count;
            for (;;)
            {
                t = -g_sumC[0] * g_sumC[0] - g_sumC[1] * g_sumC[1] - g_sumC[2] * g_sumC[2];
                if (!(g_bestscale * t > g_besterror * g_w2C))
                {
                    g_besterror = t;
                    g_bestscale = g_w2C;
                    split[0] = l0;
                    split[1] = l1;
                    split[2] = l2;
                }
                --l2;
                if (l2 < l1 || *levels < 3)
                    break;
                g_sumC[0] = g_sumC[0] + g_points[l2][0];
                g_sumC[1] = g_sumC[1] + g_points[l2][1];
                g_sumC[2] = g_sumC[2] + g_points[l2][2];
                g_w2C = (5.0 - 2.0 * g_wC - g_pointweight[l2]) * g_pointweight[l2] + g_w2C;
                g_wC = g_wC + g_pointweight[l2];
                last = 3;
            }
            --l1;
            if (l1 < l0)
                break;
            g_sumB[0] = g_sumB[0] + g_points[l1][0];
            g_sumC[0] = g_sumB[0];
            g_sumB[1] = g_sumB[1] + g_points[l1][1];
            g_sumC[1] = g_sumB[1];
            g_sumB[2] = g_sumB[2] + g_points[l1][2];
            g_sumC[2] = g_sumB[2];
            g_w2B = (3.0 - 2.0 * g_wB - g_pointweight[l1]) * g_pointweight[l1] + g_w2B;
            g_w2C = g_w2B;
            g_wB = g_wB + g_pointweight[l1];
            g_wC = g_wB;
            last = 2;
        }
        --l0;
        if (l0 < 1)
            break;
        g_sumA[0] = g_sumA[0] + g_points[l0][0];
        g_sumB[0] = g_sumA[0];
        g_sumC[0] = g_sumB[0];
        g_sumA[1] = g_sumA[1] + g_points[l0][1];
        g_sumB[1] = g_sumA[1];
        g_sumC[1] = g_sumB[1];
        g_sumA[2] = g_sumA[2] + g_points[l0][2];
        g_sumB[2] = g_sumA[2];
        g_sumC[2] = g_sumB[2];
        g_w2A = (1.0 - 2.0 * g_wA - g_pointweight[l0]) * g_pointweight[l0] + g_w2A;
        g_w2B = g_w2A;
        g_w2C = g_w2B;
        g_wA = g_wA + g_pointweight[l0];
        g_wB = g_wA;
        g_wC = g_wB;
        last = 1;
    }
    split[3] = count;
    changes = (split[0] != split[1]) + (split[1] != split[2]) + (split[2] != split[3]);
    if (changes == 1)
    {
        i = 2;
        while (i-- != 0)
            ;
        while (i++ != 0)
            split[i + 1] = split[i];
    }
    g_w2C = 0.0;
    g_wC = g_w2C;
    g_sumC[2] = g_wC;
    g_sumC[1] = g_sumC[2];
    g_sumC[0] = g_sumC[1];
    k = 0;
    j = k;
    last = j;
    for (k = 0; k < 4; ++k)
    {
        for (; j < split[k]; ++j)
        {
            g_wC = (double)k * g_pointweight[j] + g_wC;
            g_w2C = (double)k * k * g_pointweight[j] + g_w2C;
            g_sumC[0] = (double)k * g_points[j][0] + g_sumC[0];
            g_sumC[1] = (double)k * g_points[j][1] + g_sumC[1];
            g_sumC[2] = (double)k * g_points[j][2] + g_sumC[2];
        }
        last += split[k] != count;
    }
    g_w2C = g_w2C - g_wC * g_wC;
    a = -g_wC;
    b = (double)last - g_wC;
    error = -g_sumC[0] * g_sumC[0] - g_sumC[1] * g_sumC[1] - g_sumC[2] * g_sumC[2];
    for (c = 0; c < 3; ++c)
    {
        ends[0][c] = a * g_sumC[c] / g_w2C;
        ends[1][c] = b * g_sumC[c] / g_w2C;
        sum[c] = g_sumC[c];
    }
    *levels = changes == 1 ? 1 : last;
    return error / g_w2C;
}

// One channel of the box-constrained fit (the body is repeated twice in 100ff449).  Returns the
// channel's error term and the clamped endpoint numerators.
static double ClampedChannel(double sum, double low, double high, double a, double b, double aa, double ab, double bb,
                             double d, double w2, double scale, double *first, double *second)
{
    double lo = w2 * low;
    double hi = w2 * high;
    double ta = a * sum;
    double tb = b * sum;
    double loa = lo - ta;
    double hia = hi - ta;
    double t, u, v, p, q;
    lo = (lo - tb) * aa;
    hi = (hi - tb) * aa;
    t = (fabs(loa - 0.0) + loa + (hia - fabs(hia - 0.0))) * 0.5 * ab;
    loa = loa * d;
    hia = hia * d;
    u = (fabs(lo - t) + lo + (hi - fabs(hi - t))) * 0.5;
    t = u * ab;
    u = u * bb;
    v = (fabs(loa - t) + loa + (hia - fabs(hia - t))) * 0.5;
    p = v - u;
    q = a * u - b * v;
    *first = v;
    *second = u;
    return w2 * p * p + q * q - sum * sum * scale;
}

// 100ff449.  ClusterFit with the endpoints clamped to `bounds` (the colour cube relative to the
// mean); its own static best values.
static double ClampedClusterFit(int *levels, int count, double (*points)[3], double *weights, int *order,
                                double (*bounds)[3], double (*ends)[3], double *sum)
{
    int last = 0;
    int split[4];
    int changes, i, j, k, c, l0, l1, l2;
    double a, b, aa, ab, bb, d, scale, error, first, second;
    for (i = 0; i < count; ++i)
        for (c = 0; c < 3; ++c)
        {
            g_cpoints[i][c] = points[order[i]][c];
            g_cpointweight[i] = weights[order[i]];
        }
    g_cwA = 0.0;
    g_cw2A = g_cwA;
    g_csumA[2] = g_cw2A;
    g_csumA[1] = g_csumA[2];
    g_csumA[0] = g_csumA[1];
    g_cwB = 0.0;
    g_cw2B = g_cwB;
    g_csumB[2] = g_cw2B;
    g_csumB[1] = g_csumB[2];
    g_csumB[0] = g_csumB[1];
    g_cwC = 0.0;
    g_cw2C = g_cwC;
    g_csumC[2] = g_cw2C;
    g_csumC[1] = g_csumC[2];
    g_csumC[0] = g_csumC[1];
    l0 = count;
    for (;;)
    {
        l1 = count;
        for (;;)
        {
            l2 = count;
            for (;;)
            {
                a = -g_cwC;
                b = (double)last - g_cwC;
                aa = a * a + g_cw2C;
                ab = a * b + g_cw2C;
                bb = b * b + g_cw2C;
                d = aa * bb;
                scale = g_cw2C * d * d * last * last;
                error = 0.0;
                for (c = 0; c < 3; ++c)
                    error = ClampedChannel(g_csumC[c], bounds[0][c], bounds[1][c], a, b, aa, ab, bb, d, g_cw2C, scale,
                                           &first, &second) + error;
                scale = scale * g_cw2C;
                if (!(g_cbestscale * error > g_cbesterror * scale))
                {
                    g_cbesterror = error;
                    g_cbestscale = scale;
                    split[0] = l0;
                    split[1] = l1;
                    split[2] = l2;
                }
                --l2;
                if (l2 < l1 || *levels < 3)
                    break;
                g_csumC[0] = g_csumC[0] + g_cpoints[l2][0];
                g_csumC[1] = g_csumC[1] + g_cpoints[l2][1];
                g_csumC[2] = g_csumC[2] + g_cpoints[l2][2];
                g_cw2C = (5.0 - 2.0 * g_cwC - g_cpointweight[l2]) * g_cpointweight[l2] + g_cw2C;
                g_cwC = g_cwC + g_cpointweight[l2];
                last = 3;
            }
            --l1;
            if (l1 < l0)
                break;
            g_csumB[0] = g_csumB[0] + g_cpoints[l1][0];
            g_csumC[0] = g_csumB[0];
            g_csumB[1] = g_csumB[1] + g_cpoints[l1][1];
            g_csumC[1] = g_csumB[1];
            g_csumB[2] = g_csumB[2] + g_cpoints[l1][2];
            g_csumC[2] = g_csumB[2];
            g_cw2B = (3.0 - 2.0 * g_cwB - g_cpointweight[l1]) * g_cpointweight[l1] + g_cw2B;
            g_cw2C = g_cw2B;
            g_cwB = g_cwB + g_cpointweight[l1];
            g_cwC = g_cwB;
            last = 2;
        }
        --l0;
        if (l0 < 1)
            break;
        g_csumA[0] = g_csumA[0] + g_cpoints[l0][0];
        g_csumB[0] = g_csumA[0];
        g_csumC[0] = g_csumB[0];
        g_csumA[1] = g_csumA[1] + g_cpoints[l0][1];
        g_csumB[1] = g_csumA[1];
        g_csumC[1] = g_csumB[1];
        g_csumA[2] = g_csumA[2] + g_cpoints[l0][2];
        g_csumB[2] = g_csumA[2];
        g_csumC[2] = g_csumB[2];
        g_cw2A = (1.0 - 2.0 * g_cwA - g_cpointweight[l0]) * g_cpointweight[l0] + g_cw2A;
        g_cw2B = g_cw2A;
        g_cw2C = g_cw2B;
        g_cwA = g_cwA + g_cpointweight[l0];
        g_cwB = g_cwA;
        g_cwC = g_cwB;
        last = 1;
    }
    split[3] = count;
    changes = (split[0] != split[1]) + (split[1] != split[2]) + (split[2] != split[3]);
    if (changes == 1)
    {
        i = 2;
        while (i-- != 0)
            ;
        while (i++ != 0)
            split[i + 1] = split[i];
    }
    g_cw2C = 0.0;
    g_cwC = g_cw2C;
    g_csumC[2] = g_cwC;
    g_csumC[1] = g_csumC[2];
    g_csumC[0] = g_csumC[1];
    k = 0;
    j = k;
    last = j;
    for (k = 0; k < 4; ++k)
    {
        for (; j < split[k]; ++j)
        {
            g_cwC = (double)k * g_cpointweight[j] + g_cwC;
            g_cw2C = (double)k * k * g_cpointweight[j] + g_cw2C;
            g_csumC[0] = (double)k * g_cpoints[j][0] + g_csumC[0];
            g_csumC[1] = (double)k * g_cpoints[j][1] + g_csumC[1];
            g_csumC[2] = (double)k * g_cpoints[j][2] + g_csumC[2];
        }
        last += split[k] != count;
    }
    g_cw2C = g_cw2C - g_cwC * g_cwC;
    a = -g_cwC;
    b = (double)last - g_cwC;
    aa = a * a + g_cw2C;
    ab = a * b + g_cw2C;
    bb = b * b + g_cw2C;
    d = aa * bb;
    scale = g_cw2C * d * d * last * last;
    error = 0.0;
    for (c = 0; c < 3; ++c)
    {
        error = ClampedChannel(g_csumC[c], bounds[0][c], bounds[1][c], a, b, aa, ab, bb, d, g_cw2C, scale, &first,
                               &second) + error;
        ends[0][c] = (first / d + a * g_csumC[c]) / g_cw2C;
        ends[1][c] = (second / d + b * g_csumC[c]) / g_cw2C;
        sum[c] = g_csumC[c];
    }
    *levels = changes == 1 ? 1 : last;
    scale = scale * g_cw2C;
    return error / scale;
}

// 101001d1.  Single-colour block: the best 5:6:5 endpoint pair per channel and palette entry
// comes from a table built on first use.  `colour` holds the weighted colours, `weight` the
// clamped channel weights.
static double FitSingleColour(int *levels, int count, double (*colour)[3], double *weight, int (*ends)[3], int *index)
{
    int choice[3][3];
    int pick[2];
    int c, e0, e1, m, value, target, step, s, v, i, e;
    double difference;
    if (g_singleready == 0)
    {
        g_singleready = 1;
        for (c = 0; c < 3; ++c)
            for (e0 = (1 << kBits[c]) - 1; e0 >= 0; --e0)
                for (e1 = (1 << kBits[c]) - 1; e1 >= 0; --e1)
                {
                    int v0 = e0 << (8 - kBits[c]) | e0 >> (kBits[c] * 2 - 8);
                    int v1 = e1 << (8 - kBits[c]) | e1 >> (kBits[c] * 2 - 8);
                    for (m = 0; m < 3; ++m)
                    {
                        value = (kSingleMix[m][0] * v0 + kSingleMix[m][1] * v1 + kSingleMix[m][2]) / kSingleMix[m][3];
                        unsigned char *entry = g_single[value][c][m];
                        if (entry[0] == 0 || abs(entry[2] - entry[1]) > abs(v1 - v0))
                        {
                            entry[0] = 1;
                            entry[1] = (unsigned char)(e0 << (8 - kBits[c]));
                            entry[2] = (unsigned char)(e1 << (8 - kBits[c]));
                        }
                    }
                }
    }
    for (m = 0; m < *levels - 1; ++m)
    {
        g_singleerror[m] = 0.0;
        for (c = 0; c < 3; ++c)
        {
            target = (int)floor(colour[0][c] * 255.0 / weight[c] + 0.5);
            if (target < 0)
                target = 0;
            else if (target >= 0x100)
                target = 0xff;
            step = 1;
            for (s = 0; s < 2; ++s, step = -step)
            {
                v = target;
                if (g_single[v][c][m][0] == 0 || (colour[0][c] * 255.0 / weight[c] - target) * step > 0.0)
                {
                    v = target + step;
                    if (v < 0)
                        v = 0;
                    else if (v >= 0x100)
                        v = 0xff;
                    while (g_single[v][c][m][0] == 0)
                        v += step;
                }
                g_candidateerror[s] = 0.0;
                for (i = 0; i < count; ++i)
                {
                    difference = (double)v * weight[c] - colour[i][c] * 255.0;
                    g_candidateerror[s] = difference * difference + g_candidateerror[s];
                }
                pick[s] = v;
            }
            if (!(g_candidateerror[0] >= g_candidateerror[1]))
            {
                g_singleerror[m] = g_candidateerror[0] + g_singleerror[m];
                choice[c][m] = pick[0];
            }
            else if (g_candidateerror[0] > g_candidateerror[1])
            {
                g_singleerror[m] = g_candidateerror[1] + g_singleerror[m];
                choice[c][m] = pick[1];
            }
            else
            {
                g_singleerror[m] = g_candidateerror[1] + g_singleerror[m];
                choice[c][m] = (target & 1) ? pick[0] : pick[1];
            }
        }
    }
    if (*levels == 4)
    {
        if (g_singleerror[0] > g_singleerror[1])
            m = g_singleerror[1] > g_singleerror[2] ? 2 : 1;
        else
            m = g_singleerror[0] > g_singleerror[2] ? 2 : 0;
    }
    else if (*levels == 3)
    {
        m = g_singleerror[0] > g_singleerror[1] ? 1 : 0;
    }
    for (c = 0; c < 3; ++c)
        for (e = 0; e < 2; ++e)
            ends[e][c] = g_single[choice[c][m]][c][m][1 + e] >> (8 - kBits[c]);
    for (c = 0; c < count; ++c)
        index[c] = m + 1;
    if (m != 0)
        *levels = m + 2;
    return g_singleerror[m];
}

// 10100c5a.  Rounds the fitted endpoints (relative to `weight`) down and up in every channel,
// tries the 64 combinations against the pixels and keeps the best; then assigns the indices.
// The original unrolls the pixel loop of the search (a switch on the count, falling through).
static double RefineEndpoints(int levels, int count, double (*colour)[3], double *pixelweight, double *weight,
                              double (*ends)[3], int (*out)[3], int *index)
{
    int code[3][4][4];
    int best = 0;
    int c, e, v, j, i, combination, step, q;
    double s0, s1, s2, s3, low, high, total, error, distance, nearest;
    double *entry;
    const double *pr, *pg, *pb;
    for (c = 0; c < 3; ++c)
    {
        step = 1 << (8 - kRefineBits[c]);
        for (e = 0; e < 2; ++e)
        {
            if (!(weight[c] < 0.0 || weight[c] > 0.0))
                g_target = 0.0;
            else
                g_target = ends[e][c] / weight[c] * 255.0;
            q = (int)floor(g_target);
            if (q < 0)
                q = 0;
            else if (q >= 0x100)
                q = 0x100 - step;
            q &= 0x100 - step;
            if ((double)(q + (q >> kRefineBits[c])) > g_target)
                q = q - step < 0 ? q : q - step;
            code[c][e + 1][e] = q + (q >> kRefineBits[c]);
            code[c][0][e] = code[c][e + 1][e];
            q = q + step < 0x100 ? q + step : q;
            code[c][3][e] = q + (q >> kRefineBits[c]);
            code[c][2 - e][e] = code[c][3][e];
        }
    }
    if (levels == 3)
    {
        for (c = 0; c < 3; ++c)
            for (v = 0; v < 4; ++v)
            {
                code[c][v][2] = (code[c][v][0] + code[c][v][1]) / 2;
                for (j = 0; j < 3; ++j)
                    g_palette[c][v][j] = (double)code[c][v][j] * weight[c] / 255.0;
                entry = &g_entryerror[0][0][0][0] + c * 0x100 + v * 0x40;
                for (i = 0; i < count; ++i)
                    for (j = 0; j < 3; ++j)
                        *entry++ = (colour[i][c] - g_palette[c][v][j]) * pixelweight[i] * (colour[i][c] - g_palette[c][v][j]);
            }
    }
    else if (levels == 4)
    {
        for (c = 0; c < 3; ++c)
            for (v = 0; v < 4; ++v)
            {
                code[c][v][2] = (code[c][v][0] * 2 + code[c][v][1] + 1) / 3;
                code[c][v][3] = (code[c][v][0] + code[c][v][1] * 2 + 1) / 3;
                for (j = 0; j < 4; ++j)
                    g_palette[c][v][j] = (double)code[c][v][j] * weight[c] / 255.0;
                entry = &g_entryerror[0][0][0][0] + c * 0x100 + v * 0x40;
                for (i = 0; i < count; ++i)
                    for (j = 0; j < 4; ++j)
                        *entry++ = (colour[i][c] - g_palette[c][v][j]) * pixelweight[i] * (colour[i][c] - g_palette[c][v][j]);
            }
    }
    if (levels == 4)
    {
        g_refinebest = (weight[0] * weight[0] + weight[1] * weight[1] + weight[2] * weight[2]) * 2 * 16.0;
        best = -1;
        for (combination = 0; combination < 0x40; ++combination)
        {
            const double *r = &g_entryerror[0][0][0][0] + (combination & 3) * 0x40;
            const double *g = &g_entryerror[1][0][0][0] + (combination >> 2 & 3) * 0x40;
            const double *b = &g_entryerror[2][0][0][0] + (combination >> 4) * 0x40;
            total = 0.0;
            for (i = count - 1; i >= 0 && i < 16; --i)
            {
                s0 = r[i * 4] + g[i * 4] + b[i * 4];
                s1 = r[i * 4 + 1] + g[i * 4 + 1] + b[i * 4 + 1];
                low = s0 + s1 - fabs(s0 - s1);
                s2 = r[i * 4 + 2] + g[i * 4 + 2] + b[i * 4 + 2];
                s3 = r[i * 4 + 3] + g[i * 4 + 3] + b[i * 4 + 3];
                high = s2 + s3 - fabs(s2 - s3);
                total = high + low - fabs(high - low) + total;
            }
            if (!(total >= g_refinebest))
            {
                g_refinebest = total;
                best = combination;
            }
        }
    }
    else if (levels == 3)
    {
        g_refinebest = (weight[0] * weight[0] + weight[1] * weight[1] + weight[2] * weight[2]) * 2 * 16.0;
        best = -1;
        for (combination = 0; combination < 0x40; ++combination)
        {
            const double *r = &g_entryerror[0][0][0][0] + (combination & 3) * 0x40;
            const double *g = &g_entryerror[1][0][0][0] + (combination >> 2 & 3) * 0x40;
            const double *b = &g_entryerror[2][0][0][0] + (combination >> 4) * 0x40;
            total = 0.0;
            for (i = count - 1; i >= 0 && i < 16; --i)
            {
                s0 = r[i * 3] + g[i * 3] + b[i * 3];
                s1 = r[i * 3 + 1] + g[i * 3 + 1] + b[i * 3 + 1];
                low = s0 + s1 - fabs(s0 - s1);
                s2 = (r[i * 3 + 2] + g[i * 3 + 2] + b[i * 3 + 2]) * 2;
                total = s2 + low - fabs(s2 - low) + total;
            }
            if (!(total >= g_refinebest))
            {
                g_refinebest = total;
                best = combination;
            }
        }
    }
    pr = g_palette[0][best & 3];
    pg = g_palette[1][best >> 2 & 3];
    pb = g_palette[2][best >> 4];
    for (c = 0; c < 3; ++c)
        for (e = 0; e < 2; ++e)
            out[e][c] = code[c][best >> (c * 2) & 3][e] >> (8 - kRefineBits[c]);
    error = 0.0;
    for (i = 0; i < count; ++i)
    {
        nearest = (weight[0] * weight[0] + weight[1] * weight[1] + weight[2] * weight[2]) * 2;
        index[i] = -1;
        for (j = 0; j < levels; ++j)
        {
            distance = ((colour[i][0] - pr[j]) * (colour[i][0] - pr[j]) + (colour[i][1] - pg[j]) * (colour[i][1] - pg[j]) +
                        (colour[i][2] - pb[j]) * (colour[i][2] - pb[j])) * pixelweight[i];
            if (!(distance >= nearest))
            {
                nearest = distance;
                index[i] = j;
            }
        }
        error = error + nearest;
    }
    return error;
}

// 101008a5.  Refines the fitted endpoints in the given mode, then tries the candidate endpoint
// mixes of kTrialWeight in both modes and keeps the lowest error.
static double QuantizeEndpoints(int *result, int levels, int count, double (*colour)[3], double *pixelweight,
                                double *weight, double (*ends)[3], int (*out)[3], int *index)
{
    int mode[2];
    int quantized[2][2][3];
    int indices[2][16];
    int current = 0;
    int m, k, e, c, i;
    mode[current] = *result == 4;
    g_quantizeerror[current] = RefineEndpoints(mode[current] + 3, count, colour, pixelweight, weight, ends,
                                               quantized[current], indices[current]);
    current = 1 - current;
    levels -= 2;
    *result -= 2;
    for (m = 0; m < levels; ++m)
        for (k = 0; k < kTrialCount[m][*result]; ++k)
        {
            for (e = 0; e < 2; ++e)
                for (c = 0; c < 3; ++c)
                    g_trial[e][c] = kTrialWeight[m][*result][k][e][0] * ends[0][c] +
                                    kTrialWeight[m][*result][k][e][1] * ends[1][c];
            mode[current] = m;
            g_quantizeerror[current] = RefineEndpoints(m + 3, count, colour, pixelweight, weight, g_trial,
                                                       quantized[current], indices[current]);
            if (!(g_quantizeerror[current] >= g_quantizeerror[1 - current]))
                current = 1 - current;
        }
    current = 1 - current;
    for (i = 0; i < count; ++i)
        index[i] = indices[current][i];
    for (e = 0; e < 2; ++e)
        for (c = 0; c < 3; ++c)
            out[e][c] = quantized[current][e][c];
    *result = mode[current] + 3;
    return g_quantizeerror[current];
}

// 100fd235.  Colour fit of one block: single colour, two colours, or principal-axis ordering
// with cluster fits (unconstrained, then box-constrained if an endpoint leaves the cube),
// iterated until the order repeats; ends with QuantizeEndpoints.
static void FitColours(COLOURBLOCK *block)
{
    int same = 1;
    int result[2];
    int slot, tries, outside;
    int map[16];
    int order[16][16];
    int bestorder[2][16];
    int indices[16];
    int wrapped, which, repeated = 0;
    int count, unique, i, j, k, c, e;
    outside = 0;
    if (!block)
        return;
    count = block->count;
    if (count == 0)
        return;
    g_inverse = 1.0 / (double)count;
    for (c = 0; c < 3; ++c)
        g_clampweight[c] = !(block->weight[c] >= 0.0) ? 0.0 : block->weight[c];
    for (c = 0; c < 3; ++c)
    {
        g_mean[c] = 0.0;
        for (i = 0; i < count; ++i)
        {
            same &= !(fabs(block->colour[i][c] - block->colour[0][c]) >= 1.0 / 2048);
            g_weighted[i][c] = block->colour[i][c] * g_clampweight[c];
            g_mean[c] = g_weighted[i][c] + g_mean[c];
        }
    }
    if (same)
    {
        result[0] = block->levels;
        FitSingleColour(&result[0], count, g_weighted, g_clampweight, block->endpoint, block->index);
        block->result = result[0];
        return;
    }
    for (c = 0; c < 3; ++c)
    {
        g_mean[c] = g_mean[c] / (double)count;
        for (i = 0; i < count; ++i)
            g_centred[i][c] = g_weighted[i][c] - g_mean[c];
        g_bounds[0][c] = -g_mean[c];
        g_bounds[1][c] = g_clampweight[c] - g_mean[c];
    }
    unique = 0;
    for (i = 0; i < count; ++i)
    {
        for (j = 0; j < unique; ++j)
            if (!(g_unique[j][0] < g_weighted[i][0] || g_unique[j][0] > g_weighted[i][0]) &&
                !(g_unique[j][1] < g_weighted[i][1] || g_unique[j][1] > g_weighted[i][1]) &&
                !(g_unique[j][2] < g_weighted[i][2] || g_unique[j][2] > g_weighted[i][2]))
                break;
        if (j == unique)
        {
            memcpy(g_unique[j], g_weighted[i], sizeof(g_unique[j]));
            memcpy(g_uniquecentred[j], g_centred[i], sizeof(g_uniquecentred[j]));
            g_uniqueweight[j] = 1.0;
            ++unique;
        }
        else
        {
            g_uniquecentred[j][0] = g_uniquecentred[j][0] + g_centred[i][0];
            g_uniquecentred[j][1] = g_uniquecentred[j][1] + g_centred[i][1];
            g_uniquecentred[j][2] = g_uniquecentred[j][2] + g_centred[i][2];
            g_uniqueweight[j] = g_uniqueweight[j] + 1.0;
        }
        map[i] = j;
    }
    for (i = 0; i < unique; ++i)
    {
        g_uniqueweight[i] = g_inverse * g_uniqueweight[i];
        g_uniquecentred[i][0] = g_inverse * g_uniquecentred[i][0];
        g_uniquecentred[i][1] = g_inverse * g_uniquecentred[i][1];
        g_uniquecentred[i][2] = g_inverse * g_uniquecentred[i][2];
    }
    if (unique == 2)
    {
        block->result = 2;
        QuantizeEndpoints(&block->result, block->levels, 2, g_unique, g_uniqueweight, g_clampweight, g_unique,
                          block->endpoint, indices);
        for (i = 0; i < count; ++i)
            block->index[i] = indices[map[i]];
        return;
    }
    slot = 0;
    wrapped = slot;
    PrincipalAxis(count, g_centred, g_axis);
    SortAlongAxis(unique, g_unique, g_axis, order[slot], 0);
    for (i = 0; i < 2; ++i)
    {
        tries = 16;
        do
        {
            result[i] = block->levels - 1;
            if (i + tries - 1 == 16)
            {
                AxisFromExtremes(unique, g_unique, g_axis);
            }
            else
            {
                g_error[i] = ClusterFit(&result[i], unique, g_uniquecentred, g_uniqueweight, order[slot], g_ends[i],
                                        g_axis);
                which = i;
            }
            slot = (slot + 1) % 16;
            wrapped |= slot == 0;
            for (k = 0; k < 2; ++k)
            {
                SortAlongAxis(unique, g_unique, g_axis, order[slot], k);
                for (j = slot - 1; j >= 0; --j)
                {
                    repeated = SameOrder(unique, order[j], order[slot]);
                    if (repeated)
                        break;
                }
                if (!repeated && wrapped)
                    for (j = slot + 1; j < 16; ++j)
                    {
                        repeated = SameOrder(unique, order[j], order[slot]);
                        if (repeated)
                            break;
                    }
                if (!repeated || tries == 0)
                    break;
            }
        } while (tries-- != 0 && !repeated);
        for (j = 0; j < unique; ++j)
            bestorder[i][j] = order[slot][j];
    }
    if (which == 1)
        which = g_error[0] >= g_error[1] ? 1 : 0;
    outside = 0;
    for (i = 0; i < 2; ++i)
        for (c = 0; c < 3; ++c)
            outside = outside || !(g_ends[which][i][c] >= g_bounds[0][c]) || g_ends[which][i][c] > g_bounds[1][c] ? 1 : 0;
    if (outside)
    {
        for (i = 0; i < unique; ++i)
            order[0][i] = bestorder[which][i];
        tries = 8;
        slot = 0;
        wrapped = slot;
        do
        {
            result[which] = block->levels - 1;
            g_error[which] = ClampedClusterFit(&result[which], unique, g_uniquecentred, g_uniqueweight, order[slot],
                                               g_bounds, g_ends[which], g_axis);
            slot = (slot + 1) % 16;
            wrapped |= slot == 0;
            for (k = 0; k < 2; ++k)
            {
                SortAlongAxis(unique, g_unique, g_axis, order[slot], k);
                for (j = slot - 1; j >= 0; --j)
                {
                    repeated = SameOrder(unique, order[j], order[slot]);
                    if (repeated)
                        break;
                }
                if (!repeated && wrapped)
                    for (j = slot + 1; j < 16; ++j)
                    {
                        repeated = SameOrder(unique, order[j], order[slot]);
                        if (repeated)
                            break;
                    }
                if (!repeated)
                    break;
            }
        } while (tries-- != 0 && !repeated);
    }
    for (e = 0; e < 2; ++e)
        for (c = 0; c < 3; ++c)
            g_ends[1 - which][e][c] = g_ends[which][e][c] + g_mean[c];
    block->result = result[which] + 1;
    QuantizeEndpoints(&block->result, block->levels, unique, g_unique, g_uniqueweight, g_clampweight,
                      g_ends[1 - which], block->endpoint, indices);
    for (i = 0; i < count; ++i)
        block->index[i] = indices[map[i]];
}

// ---------------------------------------------------------------------------------------------
// Alpha fit (flags 0x200; not reached from the FSH writer)

// 10103a85.  Fits `levels` evenly spaced values to n alphas: assigns the values to ramp steps,
// solves the endpoints by least squares with clamping, and tries moving single extreme values
// between neighbouring steps; at most 0x40 rounds.  Returns the squared error in 0..255 units.
static double FitAlphaRamp(int levels, int n, double *value, int *ends, int *index)
{
    int tries = 0x40;
    int count[8];
    int lowest[8];
    int highest[8];
    int code[8];
    int same, used, i, j, s, k, best;
    double a, b, aa, ab, bb, d, scale, p, q, ta, tb, pa, qa, t, u, v;
    double sign, shifted, base, sv, sii;
    if (n == 0)
        return 0.0;
    g_count = (double)n;
    g_reciprocal = 1.0 / g_count;
    g_range[1] = value[0];
    g_range[0] = g_range[1];
    g_alphamean = g_range[0];
    index[0] = 0;
    for (i = 1; i < n; ++i)
    {
        if (g_range[0] > value[i])
            g_range[0] = value[i];
        if (!(g_range[1] >= value[i]))
            g_range[1] = value[i];
        g_alphamean = g_alphamean + value[i];
        index[0] = 0;
    }
    g_alphamean = g_alphamean * g_reciprocal;
    for (i = 0; i < n; ++i)
        g_centredalpha[i] = value[i] - g_alphamean;
    g_range[0] = g_range[0] - g_alphamean;
    g_range[1] = g_range[1] - g_alphamean;
    do
    {
        same = 1;
        for (i = 0; i < levels - 1; ++i)
        {
            g_threshold[i] = (g_range[1] - g_range[0]) / (double)(levels - 1) * ((double)i + 0.5) + g_range[0];
            count[i] = 0;
        }
        count[levels - 1] = 0;
        for (i = 0; i < n; ++i)
        {
            for (j = 0; j < levels - 1 && g_centredalpha[i] >= g_threshold[j]; ++j)
                ;
            ++count[j];
            same &= index[i] == j;
            index[i] = j;
        }
        used = 0;
        for (j = 0; j < levels; ++j)
            used += count[j] != 0;
        if (used == 1)
            break;
        g_sumii = 0.0;
        g_sumi = g_sumii;
        g_sumiv = g_sumi;
        for (i = 0; i < n; ++i)
        {
            g_sumiv = (double)index[i] * g_centredalpha[i] + g_sumiv;
            g_sumi = (double)index[i] + g_sumi;
            g_sumii = (double)index[i] * index[i] + g_sumii;
        }
        g_sumi = g_sumi * g_reciprocal;
        g_sumii = g_sumii - g_count * g_sumi * g_sumi;
        a = -g_sumi;
        b = (double)levels - 1.0 - g_sumi;
        aa = g_count * a * a + g_sumii;
        ab = g_count * a * b + g_sumii;
        bb = g_count * b * b + g_sumii;
        d = aa * bb;
        scale = g_sumii * d * d * ((double)levels - 1.0) * ((double)levels - 1.0);
        p = -g_alphamean * g_sumii;
        q = (1.0 - g_alphamean) * g_sumii;
        ta = a * g_sumiv;
        tb = b * g_sumiv;
        pa = p - ta;
        qa = q - ta;
        p = (p - tb) * aa;
        q = (q - tb) * aa;
        t = (fabs(pa - 0.0) + pa + (qa - fabs(qa - 0.0))) * 0.5 * ab;
        pa = pa * d;
        qa = qa * d;
        u = (fabs(p - t) + p + (q - fabs(q - t))) * 0.5;
        t = u * ab;
        u = u * bb;
        v = (fabs(pa - t) + pa + (qa - fabs(qa - t))) * 0.5;
        pa = v - u;
        qa = a * u - b * v;
        g_rampserror = g_sumii * pa * pa + g_count * qa * qa - g_sumiv * g_sumiv * scale;
        g_rampscale = scale * g_sumii;
        g_previousrange[0] = g_range[0];
        g_previousrange[1] = g_range[1];
        g_range[0] = (v / d + a * g_sumiv) / g_sumii;
        g_range[1] = (u / d + b * g_sumiv) / g_sumii;
        if (tries-- == 0)
            break;
        if (same)
        {
            for (j = 0; j < levels; ++j)
                lowest[j] = -1;
            for (i = 0; i < n; ++i)
            {
                j = index[i];
                if (lowest[j] == -1)
                {
                    highest[j] = i;
                    lowest[j] = i;
                }
                else
                {
                    if (g_centredalpha[lowest[j]] > g_centredalpha[i])
                        lowest[j] = i;
                    if (!(g_centredalpha[highest[j]] >= g_centredalpha[i]))
                        highest[j] = i;
                }
            }
            for (s = 0; s < 2; ++s)
            {
                sign = s == 0 ? 1.0 : -1.0;
                shifted = sign * g_reciprocal + g_sumi;
                base = g_sumii + 1.0 - (sign + sign) * g_sumi - g_reciprocal;
                for (j = s; j < levels + s - 1; ++j)
                {
                    if (count[j] != 0 && (count[j] > 1 || used > 2))
                    {
                        sv = sign * g_centredalpha[(s == 0 ? highest : lowest)[j]] + g_sumiv;
                        sii = (sign + sign) * j + base;
                        a = -shifted;
                        b = (double)levels - 1.0 - shifted;
                        aa = g_count * a * a + sii;
                        ab = g_count * a * b + sii;
                        bb = g_count * b * b + sii;
                        d = aa * bb;
                        scale = sii * d * d * ((double)levels - 1.0) * ((double)levels - 1.0);
                        p = -g_alphamean * sii;
                        q = (1.0 - g_alphamean) * sii;
                        ta = a * sv;
                        tb = b * sv;
                        pa = p - ta;
                        qa = q - ta;
                        p = (p - tb) * aa;
                        q = (q - tb) * aa;
                        t = (fabs(pa - 0.0) + pa + (qa - fabs(qa - 0.0))) * 0.5 * ab;
                        pa = pa * d;
                        qa = qa * d;
                        u = (fabs(p - t) + p + (q - fabs(q - t))) * 0.5;
                        t = u * ab;
                        u = u * bb;
                        v = (fabs(pa - t) + pa + (qa - fabs(qa - t))) * 0.5;
                        pa = v - u;
                        qa = a * u - b * v;
                        t = sii * pa * pa + g_count * qa * qa - sv * sv * scale;
                        scale = scale * sii;
                        if (!(t * g_rampscale >= g_rampserror * scale))
                        {
                            g_range[0] = (v / d + a * sv) / sii;
                            g_range[1] = (u / d + b * sv) / sii;
                            g_rampserror = t;
                            g_rampscale = scale;
                            same = 0;
                            break;
                        }
                    }
                }
                if (same == 0)
                    break;
            }
        }
    } while (same == 0);
    for (k = 0; k < 2; ++k)
    {
        code[k] = (int)floor((g_alphamean + g_range[k]) * 255.0 + 0.5);
        if (code[k] < 0)
            code[k] = 0;
        else if (code[k] > 0xff)
            code[k] = 0xff;
    }
    for (k = 2; k < levels; ++k)
        code[k] = ((levels - k) * code[0] + (k - 1) * code[1] + (levels - 2) / 2) / (levels - 1);
    ends[0] = code[0];
    ends[1] = code[1];
    g_rampindexerror = 0.0;
    for (i = 0; i < n; ++i)
    {
        best = 0;
        for (k = 1; k < levels; ++k)
            if (fabs(code[best] - value[i] * 255.0) > fabs(code[k] - value[i] * 255.0))
                best = k;
        index[i] = best;
        g_rampindexerror = (code[best] - value[i] * 255.0) * (code[best] - value[i] * 255.0) + g_rampindexerror;
    }
    return g_rampindexerror;
}

// 10103580.  Tries an 8-step ramp and 6-step ramps (which reserve indices 6 and 7 for 0 and
// 1) on all values, on the values other than 0, other than 1, and other than both; keeps the
// lowest error, honouring the "keep exact 0 / 1" flags.
static void FitAlpha(ALPHABLOCK *block)
{
    int levels[5] = { 8, 6, 6, 6, 6 };
    int haszero[5] = { 0, 0, 1, 0, 1 };
    int hasone[5] = { 0, 0, 0, 1, 1 };
    int n[5];
    int attempt[5];
    int ends[5][2];
    int index[5][16];
    int wantzero, wantone, best, i, s, k;
    double value;
    for (s = 0; s < 5; ++s)
        n[s] = 0;
    for (i = 0; i < block->count; ++i)
    {
        g_alphaset[0][n[0]++] = block->value[i];
        g_alphaset[1][n[1]++] = block->value[i];
        value = block->value[i];
        if (value < 0.0 || value > 0.0)
            g_alphaset[2][n[2]++] = block->value[i];
        if (value < 1.0 || value > 1.0)
            g_alphaset[3][n[3]++] = block->value[i];
        if ((value < 0.0 || value > 0.0) && (value < 1.0 || value > 1.0))
            g_alphaset[4][n[4]++] = block->value[i];
    }
    wantzero = block->keepzero != 0 && n[0] != n[2] ? 1 : 0;
    wantone = block->keepone != 0 && n[0] != n[3] ? 1 : 0;
    attempt[0] = 1;
    attempt[1] = 1;
    attempt[2] = n[2] != n[1];
    attempt[3] = n[3] != n[1];
    attempt[4] = n[4] != n[1];
    for (s = 0; s < 5; ++s)
    {
        if (attempt[s] == 0)
            continue;
        g_alphaerror[s] = FitAlphaRamp(levels[s], n[s], g_alphaset[s], ends[s], index[s]);
        attempt[s] = 1;
        if (wantzero && !haszero[s])
            attempt[s] &= ends[s][0] == 0 || ends[s][1] == 0 ? 1 : 0;
        if (wantone && !hasone[s])
            attempt[s] &= ends[s][0] == 1 || ends[s][1] == 1 ? 1 : 0;
    }
    for (s = 0; s < 5 && attempt[s] == 0; ++s)
        ;
    best = s;
    for (s = s + 1; s < 5; ++s)
        if (attempt[s] != 0 && !(g_alphaerror[s] >= g_alphaerror[best]))
            best = s;
    block->levels = levels[best];
    block->endpoint[0] = ends[best][0];
    block->endpoint[1] = ends[best][1];
    k = 0;
    for (i = 0; i < block->count; ++i)
    {
        value = block->value[i];
        if (!(value < 0.0 || value > 0.0) && haszero[best] != 0)
            block->index[i] = 6;
        else if (!(value < 1.0 || value > 1.0) && hasone[best] != 0)
            block->index[i] = 7;
        else
            block->index[i] = index[best][k++];
    }
}

// ---------------------------------------------------------------------------------------------
// Block coding

// 100fc31a.  Codes `height` rows of 4-pixel-wide GCOLOUR data (`stride` bytes per row) as
// 8-byte colour blocks, preceded per block by 8 bytes of alpha for flags 0x100 (4-bit) or
// 0x200 (ramp).  Returns the bytes written.
static int CodeBlocks(int width, int height, unsigned stride, const unsigned char *source, unsigned char *destination,
                      unsigned flags, const float *weights)
{
    int columnstep = 4;
    const unsigned char *rowstart = source;
    unsigned char *out = destination;
    const unsigned char *block, *p;
    COLOURBLOCK colour;
    ALPHABLOCK alpha;
    int map[16];
    unsigned short ends[2], swap;
    unsigned short alpha4;
    unsigned bits;
    int swapped, x, y, rows, columns, r, c, i, v, end;
    for (y = 0; y < height; y += 4, rowstart += stride * 4)
    {
        rows = height - y < 4 ? height - y : 4;
        block = rowstart;
        for (x = 0; x < width; x += 4, block += columnstep * 4)
        {
            bits = 0;
            for (i = 0; i < 3; ++i)
                colour.weight[i] = weights[i];
            columns = width - x < 4 ? width - x : 4;
            colour.count = 0;
            p = block;
            if ((flags & 0xff) == 0 || (flags & 0xff) == 1 || (flags & 0xff) == 2)
            {
                // The original repeats this loop once for each of the three modes.
                i = 0;
                for (r = 0; r < 4; ++r, p += (stride >> 2) * 4 - 0x10)
                    for (c = 0; c < 4; ++c, p += 4)
                    {
                        if (c < columns && r < rows)
                        {
                            map[i++] = colour.count;
                            double *e = colour.colour[colour.count++];
                            e[0] = (double)p[2] / 255.0;
                            e[1] = (double)p[1] / 255.0;
                            e[2] = (double)p[0] / 255.0;
                        }
                        else
                        {
                            map[i++] = -1;
                        }
                    }
            }
            colour.levels = (colour.count >= columns * rows) + 3;
            if (colour.count == 0)
            {
                for (i = 0; i < 2; ++i)
                {
                    colour.endpoint[i][2] = 0;
                    colour.endpoint[i][1] = 0;
                    colour.endpoint[i][0] = 0;
                }
            }
            else
            {
                FitColours(&colour);
            }
            for (i = 0; i < 2; ++i)
                ends[i] = (unsigned short)(colour.endpoint[i][0] << 11 | colour.endpoint[i][1] << 5 | colour.endpoint[i][2]);
            if (ends[0] == ends[1])
            {
                ends[1] = ends[1] + 1;
                for (i = 0; i < colour.count; ++i)
                    colour.index[i] = 0;
                colour.result = 3;
            }
            if ((ends[0] > ends[1]) == (colour.result == 3))
            {
                swap = ends[0];
                ends[0] = ends[1];
                ends[1] = swap;
                swapped = 1;
            }
            else
            {
                swapped = 0;
            }
            for (i = 0; i < 2; ++i)
            {
                gputi(out, ends[i], 2);
                out += 2;
            }
            for (i = 15; i >= 0; --i)
            {
                bits <<= 2;
                if (map[i] < 0)
                {
                    bits |= 3;
                }
                else
                {
                    bits |= colour.index[map[i]];
                    if (swapped)
                    {
                        if (colour.result == 4)
                            bits ^= 1;
                        else
                            bits ^= (bits & 2) >> 1 ^ 1;
                    }
                }
            }
            gputi(out, bits, 4);
            out += 4;
            if ((flags & 0xff00) == 0x100)
            {
                p = block;
                for (r = 0; r < 4; ++r, p += (stride >> 2) * 4 - 0x10)
                {
                    if (r < rows)
                    {
                        for (c = 0; c < 4; ++c, p += 4)
                        {
                            if (c < columns)
                                alpha4 = (unsigned short)((int)(alpha4 & 0xffff) >> 4 | (p[3] * 0xf + 0x80) / 0xff << 12);
                            else
                                alpha4 = (unsigned short)(alpha4 >> 4);
                        }
                        gputi(out, alpha4 & 0xffff, 2);
                    }
                    else
                    {
                        gputi(out, 0, 2);
                    }
                    out += 2;
                }
            }
            else if ((flags & 0xff00) == 0x200)
            {
                p = block;
                alpha.count = 0;
                i = 0;
                for (r = 0; r < 4; ++r, p += (stride >> 2) * 4 - 0x10)
                    for (c = 0; c < 4; ++c, p += 4)
                    {
                        if (c < columns && r < rows)
                        {
                            map[i++] = alpha.count;
                            alpha.value[alpha.count++] = p[3] == 0xff ? 1.0f : (float)((double)p[3] / 255.0f);
                        }
                        else
                        {
                            map[i++] = -1;
                        }
                    }
                alpha.keepzero = flags & 0x10000;
                alpha.keepone = flags & 0x20000;
                if (alpha.count == 0)
                {
                    alpha.endpoint[1] = 0;
                    alpha.endpoint[0] = alpha.endpoint[1];
                }
                else
                {
                    FitAlpha(&alpha);
                }
                if (alpha.endpoint[0] == alpha.endpoint[1])
                {
                    alpha.endpoint[1] = alpha.endpoint[1] + 1;
                    for (i = 0; i < alpha.count; ++i)
                        alpha.index[i] = 0;
                    alpha.levels = 6;
                }
                if ((alpha.endpoint[0] > alpha.endpoint[1]) == (alpha.levels == 6))
                {
                    end = alpha.endpoint[0];
                    alpha.endpoint[0] = alpha.endpoint[1];
                    alpha.endpoint[1] = end;
                    swapped = 1;
                }
                else
                {
                    swapped = 0;
                }
                for (i = 0; i < 2; ++i)
                    *out++ = (unsigned char)alpha.endpoint[i];
                bits = 0;
                i = 0;
                for (r = 0; r < 4; ++r)
                {
                    for (c = 0; c < 4; ++c, ++i)
                    {
                        bits >>= 3;
                        if (map[i] >= 0)
                        {
                            v = alpha.index[map[i]];
                            if (swapped)
                            {
                                if (alpha.levels == 8)
                                    v = v > 1 ? 9 - v : v == 0;
                                else if (alpha.levels == 6)
                                    v = v > 5 ? v : (v > 1 ? 7 - v : v == 0);
                            }
                            bits |= v << 21;
                        }
                    }
                    if (r & 1)
                    {
                        gputi(out, bits, 4);
                        out += 3;
                        bits = 0;
                    }
                }
            }
        }
    }
    return (int)(out - destination);
}

// 100fc227 (stdcall in the original).  18fb header: input size (3 bytes) and the alpha kind
// (1 for flags 0x100, 2 for 0x200); channel weights 0.3, 0.4, 0.3.
static int GCALL PackBlocks(const unsigned char *blocks, int size, unsigned char *destination, unsigned *flags)
{
    float weights[3] = { 0.3f, 0.4f, 0.3f };
    int written = 0;
    unsigned char *header = destination;
    unsigned mode;
    int kind, columns, rowbytes, rows;
    if (flags)
    {
        mode = *flags;
        columns = 4;
        rowbytes = 0x10;
        rows = size / rowbytes;
        if (mode & 0x100)
            kind = 1;
        else
            kind = (mode & 0x200) ? 2 : 0;
        gputm(header, 0x18fb, 2);
        gputm(header + 2, size, 3);
        gputm(header + 5, kind, 1);
        written = CodeBlocks(columns, rows, rowbytes, blocks, destination + 8, mode, weights);
    }
    return written + 8;
}

// 10104936.  Copies the image into 4x4 blocks of GCOLOUR (64 bytes each, in rows of blocks),
// zero-padding partial blocks.
static void GatherBlocks(int width, int height, int rowbytes, const unsigned char *pixels, unsigned char *blocks)
{
    unsigned char *out = blocks;
    const unsigned char *line;
    int y, x, r, rows, columns, padrows, padcolumns;
    for (y = 0; y < height; y += 4)
    {
        if (y + 4 > height)
        {
            rows = height - y;
            padrows = 4 - rows;
        }
        else
        {
            rows = 4;
            padrows = 0;
        }
        line = pixels + y * rowbytes;
        for (x = 0; x < width; x += 4)
        {
            if (x + 4 > width)
            {
                columns = width - x;
                padcolumns = 4 - columns;
            }
            else
            {
                columns = 4;
                padcolumns = 0;
            }
            for (r = 0; r < rows; ++r)
            {
                memcpy(out, line + r * rowbytes, columns * 4);
                if (padcolumns)
                    memset(out + columns * 4, 0, padcolumns * 4);
                out += 0x10;
            }
            for (r = 0; r < padrows; ++r)
            {
                memset(out, 0, 0x10);
                out += 0x10;
            }
            line += 0x10;
        }
    }
}

// 100fc155.  Block-packs the image into the bitmap data at `destination`; the header's size
// field is then replaced by width * height * 2 and +6 by the width.  Returns the 16-aligned size.
int FSH_CompressBlocks(const GINFO *info, int rowbytes, const void *pixels, unsigned char *destination)
{
    unsigned flags = 0;
    int written = 0;
    int size = ((info->width + 3) & ~3) * ((info->height + 3) & ~3) * 4;
    unsigned char *blocks = (unsigned char *)galloc(size);
    if (blocks)
    {
        GatherBlocks(info->width, info->height, rowbytes, (const unsigned char *)pixels, blocks);
        written = (PackBlocks(blocks, size, destination, &flags) + 0xf) & ~0xf;
        gputm(destination + 2, info->width * info->height * 2, 3);
        gputm(destination + 6, info->width, 2);
        gfree(blocks);
    }
    return written;
}
