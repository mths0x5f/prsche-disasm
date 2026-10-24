// Library oracle: the public libraries linked into the recovered gimme.dll against the original's
// own copies, called at their VAs with the same structures.
//
//   gimme_oracle jpeglib <original.dll> <list.txt> [--pad]
//       Message table of jpeg_std_error, then every file decoded by both IJG copies in several
//       modes (scaling, DCT methods, colour quantization, colour conversion, block smoothing,
//       no fancy upsampling).  Compares the decompressor's scalar fields after jpeg_read_header
//       and jpeg_start_decompress, every scanline, the colormap, the warning count and the error
//       code of a failed decode.
//
// The struct layouts are the same on both sides (IJG 6a, int boolean, structsize 0x1d0).

#include <stdlib.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>

#include "../_sem_arquivo/gimex/jpgsource.h"

typedef GSTREAM *(GCALL *OpenFn)(const char *);
typedef int(GCALL *CloseFn)(GSTREAM *);

namespace liboracle
{

struct JpegApi
{
    const char *label;
    jpeg_error_mgr *(*std_error)(jpeg_error_mgr *);
    void (*create)(j_decompress_ptr, int, size_t);
    void (*source)(j_decompress_ptr, GSTREAM *);
    int (*read_header)(j_decompress_ptr, boolean);
    boolean (*start)(j_decompress_ptr);
    JDIMENSION (*read_scanlines)(j_decompress_ptr, JSAMPARRAY, JDIMENSION);
    boolean (*finish)(j_decompress_ptr);
    void (*destroy)(j_decompress_ptr);
    OpenFn open;
    CloseFn close;
};

static JpegApi OriginalJpeg()
{
    JpegApi api = { "original",
                    (jpeg_error_mgr * (*)(jpeg_error_mgr *))0x10155e70,
                    (void (*)(j_decompress_ptr, int, size_t))0x10156130,
                    (void (*)(j_decompress_ptr, GSTREAM *))0x10156980,
                    (int (*)(j_decompress_ptr, boolean))0x10156316,
                    (boolean(*)(j_decompress_ptr))0x10156b50,
                    (JDIMENSION(*)(j_decompress_ptr, JSAMPARRAY, JDIMENSION))0x10156ddf,
                    (boolean(*)(j_decompress_ptr))0x10156869,
                    (void (*)(j_decompress_ptr))0x10156286,
                    (OpenFn)0x10003650,
                    (CloseFn)0x10003d20 };
    return api;
}

static JpegApi RecoveredJpeg()
{
    JpegApi api = { "recovered", jpeg_std_error, jpeg_CreateDecompress, jpeg_gstream_src, jpeg_read_header,
                    jpeg_start_decompress, jpeg_read_scanlines, jpeg_finish_decompress,
                    jpeg_destroy_decompress, gopen, gclose };
    return api;
}

struct OracleError
{
    jpeg_error_mgr pub;
    jmp_buf buffer;
};

static void OracleErrorExit(j_common_ptr cinfo)
{
    longjmp(((OracleError *)cinfo->err)->buffer, 1);
}

// Everything a decode produces, flattened into one byte string for comparison.
struct Result
{
    unsigned char *data;
    size_t size, capacity;
    void Add(const void *p, size_t n)
    {
        if (size + n > capacity)
        {
            capacity = (size + n) * 2;
            data = (unsigned char *)realloc(data, capacity);
        }
        memcpy(data + size, p, n);
        size += n;
    }
    template <class T> void Put(T v) { Add(&v, sizeof(v)); }
};

static void Fields(Result &r, j_decompress_ptr c)
{
#define F(x) r.Put(c->x)
    F(image_width); F(image_height); F(num_components); F(jpeg_color_space); F(out_color_space);
    F(scale_num); F(scale_denom); F(output_gamma); F(buffered_image); F(raw_data_out); F(dct_method);
    F(do_fancy_upsampling); F(do_block_smoothing); F(quantize_colors); F(dither_mode);
    F(two_pass_quantize); F(desired_number_of_colors); F(enable_1pass_quant); F(enable_external_quant);
    F(enable_2pass_quant); F(output_width); F(output_height); F(out_color_components);
    F(output_components); F(rec_outbuf_height); F(actual_number_of_colors); F(output_scanline);
    F(input_scan_number); F(input_iMCU_row); F(output_scan_number); F(output_iMCU_row);
    F(data_precision); F(progressive_mode); F(arith_code); F(restart_interval); F(saw_JFIF_marker);
    F(density_unit); F(X_density); F(Y_density); F(saw_Adobe_marker); F(Adobe_transform);
    F(CCIR601_sampling); F(max_h_samp_factor); F(max_v_samp_factor); F(min_DCT_scaled_size);
    F(total_iMCU_rows); F(comps_in_scan); F(MCUs_per_row); F(MCU_rows_in_scan); F(blocks_in_MCU);
    F(Ss); F(Se); F(Ah); F(Al); F(unread_marker);
#undef F
}

// mode: 0 default, 1-3 scale 1/2,1/4,1/8, 4 IFAST, 5 FLOAT, 6 1-pass quant 64 colours FS,
// 7 2-pass quant 32, 8 grayscale output, 9 no fancy upsampling, 10 1-pass ordered dither,
// 11 no block smoothing.
static const int MODES = 12;

static void Decode(const JpegApi &api, const char *name, int mode, Result &r)
{
    r.data = 0;
    r.size = r.capacity = 0;
    GSTREAM *stream = api.open(name);
    if (!stream)
    {
        r.Put(-1);
        return;
    }
    OracleError error;
    jpeg_decompress_struct cinfo;
    int stage = 0;
    cinfo.err = api.std_error(&error.pub);
    error.pub.error_exit = OracleErrorExit;
    if (setjmp(error.buffer))
    {
        r.Put(0x7fffffff);
        r.Put(stage);
        r.Put(error.pub.msg_code);
        r.Put(error.pub.num_warnings);
        api.destroy(&cinfo);
        api.close(stream);
        return;
    }
    api.create(&cinfo, JPEG_LIB_VERSION, sizeof(cinfo));
    api.source(&cinfo, stream);
    stage = 1;
    r.Put(api.read_header(&cinfo, TRUE));
    Fields(r, &cinfo);
    switch (mode)
    {
    case 1: cinfo.scale_denom = 2; break;
    case 2: cinfo.scale_denom = 4; break;
    case 3: cinfo.scale_denom = 8; break;
    case 4: cinfo.dct_method = JDCT_IFAST; break;
    case 5: cinfo.dct_method = JDCT_FLOAT; break;
    case 6: cinfo.quantize_colors = TRUE; cinfo.two_pass_quantize = FALSE; cinfo.desired_number_of_colors = 64; break;
    case 7: cinfo.quantize_colors = TRUE; cinfo.desired_number_of_colors = 32; break;
    case 8: cinfo.out_color_space = JCS_GRAYSCALE; break;
    case 9: cinfo.do_fancy_upsampling = FALSE; break;
    case 10: cinfo.quantize_colors = TRUE; cinfo.two_pass_quantize = FALSE; cinfo.dither_mode = JDITHER_ORDERED; break;
    case 11: cinfo.do_block_smoothing = FALSE; break;
    }
    stage = 2;
    r.Put(api.start(&cinfo));
    Fields(r, &cinfo);
    if (cinfo.quantize_colors && cinfo.colormap)
        for (int c = 0; c < cinfo.out_color_components; ++c)
            r.Add(cinfo.colormap[c], cinfo.actual_number_of_colors);
    int stride = cinfo.output_width * cinfo.output_components;
    JSAMPARRAY rows = (*cinfo.mem->alloc_sarray)((j_common_ptr)&cinfo, JPOOL_IMAGE, stride, 1);
    stage = 3;
    while (cinfo.output_scanline < cinfo.output_height)
    {
        r.Put(api.read_scanlines(&cinfo, rows, 1));
        r.Add(rows[0], stride);
    }
    stage = 4;
    r.Put(api.finish(&cinfo));
    r.Put(error.pub.num_warnings);
    api.destroy(&cinfo);
    api.close(stream);
}

static int MessageTable()
{
    jpeg_error_mgr a, b;
    OriginalJpeg().std_error(&a);
    jpeg_std_error(&b);
    int differs = a.last_jpeg_message != b.last_jpeg_message;
    for (int i = 0; !differs && i <= a.last_jpeg_message; ++i)
    {
        const char *x = a.jpeg_message_table[i], *y = b.jpeg_message_table[i];
        if ((x == 0) != (y == 0) || (x && strcmp(x, y) != 0))
        {
            printf("message %d differs: \"%s\" / \"%s\"\n", i, x ? x : "(null)", y ? y : "(null)");
            differs = 1;
        }
    }
    printf("jpeg_std_error message table: %d messages %s (\"%s\")\n", a.last_jpeg_message + 1,
           differs ? "DIFF" : "MATCH", a.jpeg_message_table[JMSG_VERSION]);
    return differs;
}

int JpegLib(int argc, char **argv)
{
    FILE *list = fopen(argv[3], "r");
    if (!list)
        return 2;
    int failures = MessageTable(), cases = 0;
    char line[260];
    JpegApi apis[2] = { OriginalJpeg(), RecoveredJpeg() };
    while (fgets(line, sizeof(line), list))
    {
        line[strcspn(line, "\r\n")] = 0;
        if (!line[0])
            continue;
        for (int mode = 0; mode < MODES; ++mode)
        {
            Result r[2];
            for (int s = 0; s < 2; ++s)
                Decode(apis[s], line, mode, r[s]);
            bool same = r[0].size == r[1].size && memcmp(r[0].data, r[1].data, r[0].size) == 0;
            ++cases;
            if (!same)
            {
                ++failures;
                size_t at = 0;
                while (at < r[0].size && at < r[1].size && r[0].data[at] == r[1].data[at])
                    ++at;
                printf("DIFF %s mode %d at byte %u (sizes %u/%u)\n", line, mode, (unsigned)at, (unsigned)r[0].size,
                       (unsigned)r[1].size);
            }
            free(r[0].data);
            free(r[1].data);
        }
    }
    printf("%d decodes compared, %d differ: %s\n", cases, failures, failures ? "FAIL" : "PASS");
    return failures != 0;
}

}  // namespace liboracle
