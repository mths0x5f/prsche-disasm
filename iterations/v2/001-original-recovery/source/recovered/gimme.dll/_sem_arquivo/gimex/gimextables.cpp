// The module, filter and quantizer tables linked into gimme.dll (0x10431a50, 0x10432428,
// 0x10432720).  The original order and indices are listed in runs/432-gimme-dll/components.md;
// only recovered entries are present here, so indices after the first missing module differ
// from the original until the missing modules are recovered.  See README.md (boundaries).

#include "gimexfilter.h"

#define GIMEX_MODULE(prefix) \
    GABOUT *prefix##_about(void); \
    int GCALL prefix##_is(GSTREAM *); \
    int GCALL prefix##_open(void **, GSTREAM *, const char *, int); \
    GINFO *GCALL prefix##_info(void *, int); \
    int GCALL prefix##_read(void *, GINFO *, void *, int); \
    int GCALL prefix##_close(void *); \
    int GCALL prefix##_wopen(void **, GSTREAM *, const char *, int); \
    int GCALL prefix##_write(void *, const GINFO *, const void *, int); \
    int GCALL prefix##_wclose(void *);

#define GIMEX_ENTRY(prefix) \
    { prefix##_about, prefix##_is, prefix##_open, prefix##_info, prefix##_read, prefix##_close, \
      prefix##_wopen, prefix##_write, prefix##_wclose }

GIMEX_MODULE(NIL)
GIMEX_MODULE(FSH)
GIMEX_MODULE(BMP)
GIMEX_MODULE(ICO)
GIMEX_MODULE(S3T)
GIMEX_MODULE(TGA)
GIMEX_MODULE(LBM)
GIMEX_MODULE(TIM)
GIMEX_MODULE(HSI)
GIMEX_MODULE(SCT)
GIMEX_MODULE(PSD)
GIMEX_MODULE(ANM)
GIMEX_MODULE(FLM)
GIMEX_MODULE(BIF)
GIMEX_MODULE(SGI)
GIMEX_MODULE(PICT)
GIMEX_MODULE(PCX)
GIMEX_MODULE(PPM)
GIMEX_MODULE(ACT)
GIMEX_MODULE(RLA)
GIMEX_MODULE(MOV)
GIMEX_MODULE(PIX)
GIMEX_MODULE(FLI)
GIMEX_MODULE(GMX)
GIMEX_MODULE(FFN)
GIMEX_MODULE(PSH)
GIMEX_MODULE(SIM)
GIMEX_MODULE(TGV)
GIMEX_MODULE(GIF)
GIMEX_MODULE(VQT)
GIMEX_MODULE(MDEC)
GIMEX_MODULE(PFN)
GIMEX_MODULE(VSH)
GIMEX_MODULE(SFN)
GIMEX_MODULE(NFN)
GIMEX_MODULE(MVI)
GIMEX_MODULE(TXP)
GIMEX_MODULE(CMP)
GIMEX_MODULE(EPS)
GIMEX_MODULE(RAW)
GIMEX_MODULE(GS)
GIMEX_MODULE(INV)
GIMEX_MODULE(S3D)
GIMEX_MODULE(VRM)
GIMEX_MODULE(FSHP)
GIMEX_MODULE(NSH)
GIMEX_MODULE(BAM)
GIMEX_MODULE(YUV)
GIMEX_MODULE(DSH)
GIMEX_MODULE(SSH)
GIMEX_MODULE(QT3)
GIMEX_MODULE(TQI)
GIMEX_MODULE(CLP)
GIMEX_MODULE(AI)
GIMEX_MODULE(OMF)
GIMEX_MODULE(JPG)
GIMEX_MODULE(AVI)
GIMEX_MODULE(PNG)
GIMEX_MODULE(CEL)
GIMEX_MODULE(MPG)
GIMEX_MODULE(TIF)
GIMEX_MODULE(LAY)
GIMEX_MODULE(VAN)
GIMEX_MODULE(QMT)
GIMEX_MODULE(MAD)
GIMEX_MODULE(MAT)
GIMEX_MODULE(FX)
GIMEX_MODULE(PVR)
GIMEX_MODULE(UV)

GMODULE gimexmodules[] = {
    GIMEX_ENTRY(NIL),   // 0  Nil Gimex 1.02
    GIMEX_ENTRY(FSH),   // 1  FSH Shape File 2.07
    { BMP_about, BMP_is, BMP_open, BMP_info, BMP_read, BMP_close, BMP_wopen, BMP_write, BMP_wclose },   // 2  Windows BMP 1.24
    { ICO_about, ICO_is, ICO_open, ICO_info, ICO_read, ICO_close, ICO_wopen, ICO_write, ICO_wclose },   // 3  Windows Icon 1.00
    { S3T_about, S3T_is, S3T_open, S3T_info, S3T_read, S3T_close, S3T_wopen, S3T_write, S3T_wclose },   // 4  S3 Texture 1.03
    { TGA_about, TGA_is, TGA_open, TGA_info, TGA_read, TGA_close, TGA_wopen, TGA_write, TGA_wclose },   // 5  Targa 1.37
    { LBM_about, LBM_is, LBM_open, LBM_info, LBM_read, LBM_close, LBM_wopen, LBM_write, LBM_wclose },   // 6  Amiga ILBM 1.20
    { TIM_about, TIM_is, TIM_open, TIM_info, TIM_read, TIM_close, TIM_wopen, TIM_write, TIM_wclose },   // 7  TIM PSX Texture Image 1.05
    { HSI_about, HSI_is, HSI_open, HSI_info, HSI_read, HSI_close, HSI_wopen, HSI_write, HSI_wclose },   // 8  HSI Raw 1.07
    { SCT_about, SCT_is, SCT_open, SCT_info, SCT_read, SCT_close, SCT_wopen, SCT_write, SCT_wclose },   // 9  Scitex SCT 1.02
    { PSD_about, PSD_is, PSD_open, PSD_info, PSD_read, PSD_close, PSD_wopen, PSD_write, PSD_wclose },   // 10  Adobe Photoshop 4.0 1.13
    { ANM_about, ANM_is, ANM_open, ANM_info, ANM_read, ANM_close, ANM_wopen, ANM_write, ANM_wclose },   // 11  DPaint ANM 1.12
    { FLM_about, FLM_is, FLM_open, FLM_info, FLM_read, FLM_close, FLM_wopen, FLM_write, FLM_wclose },   // 12  Adobe FilmStrip 1.02
    { BIF_about, BIF_is, BIF_open, BIF_info, BIF_read, BIF_close, BIF_wopen, BIF_write, BIF_wclose },   // 13  Binary Info File 1.04
    { SGI_about, SGI_is, SGI_open, SGI_info, SGI_read, SGI_close, SGI_wopen, SGI_write, SGI_wclose },   // 14  SGI RGB Image File 1.07
    { PICT_about, PICT_is, PICT_open, PICT_info, PICT_read, PICT_close, PICT_wopen, PICT_write, PICT_wclose },   // 15  Macintosh Pict 1.18
    { PCX_about, PCX_is, PCX_open, PCX_info, PCX_read, PCX_close, PCX_wopen, PCX_write, PCX_wclose },   // 16  ZSoft PCX 1.05
    { PPM_about, PPM_is, PPM_open, PPM_info, PPM_read, PPM_close, PPM_wopen, PPM_write, PPM_wclose },   // 17  Portable Pixel Map 1.05
    { ACT_about, ACT_is, ACT_open, ACT_info, ACT_read, ACT_close, ACT_wopen, ACT_write, ACT_wclose },   // 18  ACT Photoshop Palette 1.02
    { RLA_about, RLA_is, RLA_open, RLA_info, RLA_read, RLA_close, RLA_wopen, RLA_write, RLA_wclose },   // 19  WaveFront RLA 1.06
    { MOV_about, MOV_is, MOV_open, MOV_info, MOV_read, MOV_close, MOV_wopen, MOV_write, MOV_wclose },   // 20  QuickTime Movie 1.31
    { PIX_about, PIX_is, PIX_open, PIX_info, PIX_read, PIX_close, PIX_wopen, PIX_write, PIX_wclose },   // 21  Alias Pix 1.00
    { FLI_about, FLI_is, FLI_open, FLI_info, FLI_read, FLI_close, FLI_wopen, FLI_write, FLI_wclose },   // 22  FLIC Animation 1.06
    { GMX_about, GMX_is, GMX_open, GMX_info, GMX_read, GMX_close, GMX_wopen, GMX_write, GMX_wclose },   // 23  Gimex Images 2.14
    { FFN_about, FFN_is, FFN_open, FFN_info, FFN_read, FFN_close, FFN_wopen, FFN_write, FFN_wclose },   // 24  PC Font File 2.30
    { PSH_about, PSH_is, PSH_open, PSH_info, PSH_read, PSH_close, PSH_wopen, PSH_write, PSH_wclose },   // 25  PSH Shape File 2.07
    { SIM_about, SIM_is, SIM_open, SIM_info, SIM_read, SIM_close, SIM_wopen, SIM_write, SIM_wclose },   // 26  SoftImage PIC 1.08
    { TGV_about, TGV_is, TGV_open, TGV_info, TGV_read, TGV_close, TGV_wopen, TGV_write, TGV_wclose },   // 27  TGV Movie 1.39
    { GIF_about, GIF_is, GIF_open, GIF_info, GIF_read, GIF_close, GIF_wopen, GIF_write, GIF_wclose },   // 28  Compuserve GIF 1.15
    { VQT_about, VQT_is, VQT_open, VQT_info, VQT_read, VQT_close, VQT_wopen, VQT_write, VQT_wclose },   // 29  ATI VQ Texture 1.02
    { MDEC_about, MDEC_is, MDEC_open, MDEC_info, MDEC_read, MDEC_close, MDEC_wopen, MDEC_write, MDEC_wclose },   // 30  MDEC Movie 1.35
    { PFN_about, PFN_is, PFN_open, PFN_info, PFN_read, PFN_close, PFN_wopen, PFN_write, PFN_wclose },   // 31  PSX Font File 2.30
    { VSH_about, VSH_is, VSH_open, VSH_info, VSH_read, VSH_close, VSH_wopen, VSH_write, VSH_wclose },   // 32  VSH Shape File 2.07
    { SFN_about, SFN_is, SFN_open, SFN_info, SFN_read, SFN_close, SFN_wopen, SFN_write, SFN_wclose },   // 33  Sony2 Font File 2.30
    { NFN_about, NFN_is, NFN_open, NFN_info, NFN_read, NFN_close, NFN_wopen, NFN_write, NFN_wclose },   // 34  Nitendo64 Font File 2.30
    { MVI_about, MVI_is, MVI_open, MVI_info, MVI_read, MVI_close, MVI_wopen, MVI_write, MVI_wclose },   // 35  MVI Movie 1.14
    { TXP_about, TXP_is, TXP_open, TXP_info, TXP_read, TXP_close, TXP_wopen, TXP_write, TXP_wclose },   // 36  Latenight Text Palette 1.03
    { CMP_about, CMP_is, CMP_open, CMP_info, CMP_read, CMP_close, NIL_wopen, NIL_write, NIL_wclose },   // 37  Ninja 3 CharMap 1.04
    { EPS_about, EPS_is, EPS_open, EPS_info, EPS_read, EPS_close, EPS_wopen, EPS_write, EPS_wclose },   // 38  Encapsulated Postscript 1.05
    { RAW_about, RAW_is, RAW_open, RAW_info, RAW_read, RAW_close, RAW_wopen, RAW_write, RAW_wclose },   // 39  Erik Kiss RAW 1.04
    { GS_about, GS_is, GS_open, GS_info, GS_read, GS_close, GS_wopen, GS_write, GS_wclose },   // 40  Raw Grey Scale 1.03
    { INV_about, INV_is, INV_open, INV_info, INV_read, INV_close, INV_wopen, INV_write, INV_wclose },   // 41  Inverse Table 1.02
    { S3D_about, S3D_is, S3D_open, S3D_info, S3D_read, S3D_close, S3D_wopen, S3D_write, S3D_wclose },   // 42  Stareo 3D 1.04
    { VRM_about, VRM_is, VRM_open, VRM_info, VRM_read, VRM_close, VRM_wopen, VRM_write, VRM_wclose },   // 43  PSX VRAM Viewer 1.01
    { FSHP_about, FSHP_is, FSHP_open, FSHP_info, FSHP_read, FSHP_close, FSHP_wopen, FSHP_write, FSHP_wclose },   // 44  Font Shape 1.11
    { NSH_about, NSH_is, NSH_open, NSH_info, NSH_read, NSH_close, NSH_wopen, NSH_write, NSH_wclose },   // 45  NSH Nintendo 64 Shape File 2.07
    { BAM_about, BAM_is, BAM_open, BAM_info, BAM_read, BAM_close, BAM_wopen, BAM_write, BAM_wclose },   // 46  Bank Mask 1.04
    { YUV_about, YUV_is, YUV_open, YUV_info, YUV_read, YUV_close, YUV_wopen, YUV_write, YUV_wclose },   // 47  ACOM YUV 1.06
    { DSH_about, DSH_is, DSH_open, DSH_info, DSH_read, DSH_close, DSH_wopen, DSH_write, DSH_wclose },   // 48  DSH Shape File 2.07
    { SSH_about, SSH_is, SSH_open, SSH_info, SSH_read, SSH_close, SSH_wopen, SSH_write, SSH_wclose },   // 49  SSH Sony Shape File 2.07
    { QT3_about, QT3_is, QT3_open, QT3_info, QT3_read, QT3_close, QT3_wopen, QT3_write, QT3_wclose },   // 50  QuickTime3 Movie 1.00
    { TQI_about, TQI_is, TQI_open, TQI_info, TQI_read, TQI_close, TQI_wopen, TQI_write, TQI_wclose },   // 51  TQI Texture Quantized Image 1.01
    { CLP_about, CLP_is, CLP_open, CLP_info, CLP_read, CLP_close, CLP_wopen, CLP_write, CLP_wclose },   // 52  ClipBoard Gimex 1.03
    { AI_about, AI_is, AI_open, AI_info, AI_read, AI_close, AI_wopen, AI_write, AI_wclose },   // 53  Abobe Illustrator 1.01
    { OMF_about, OMF_is, OMF_open, OMF_info, OMF_read, OMF_close, OMF_wopen, OMF_write, OMF_wclose },   // 54  Open Media Framework 1.01
    { JPG_about, JPG_is, JPG_open, JPG_info, JPG_read, JPG_close, JPG_wopen, JPG_write, JPG_wclose },   // 55  JPeg 1.10
    { AVI_about, AVI_is, AVI_open, AVI_info, AVI_read, AVI_close, AVI_wopen, AVI_write, AVI_wclose },   // 56  Audio Visual Interleave 1.10
    { PNG_about, PNG_is, PNG_open, PNG_info, PNG_read, PNG_close, PNG_wopen, PNG_write, PNG_wclose },   // 57  Portable Network Graphics 1.06
    { CEL_about, CEL_is, CEL_open, CEL_info, CEL_read, CEL_close, NIL_wopen, NIL_write, NIL_wclose },   // 58  3DO Cel 1.11
    { MPG_about, MPG_is, MPG_open, MPG_info, MPG_read, MPG_close, MPG_wopen, MPG_write, MPG_wclose },   // 59  MPEG 1.01
    { TIF_about, TIF_is, TIF_open, TIF_info, TIF_read, TIF_close, TIF_wopen, TIF_write, TIF_wclose },   // 60  Tiff 1.04
    { LAY_about, LAY_is, LAY_open, LAY_info, LAY_read, LAY_close, LAY_wopen, LAY_write, LAY_wclose },   // 61  Layout 1.09
    { VAN_about, VAN_is, VAN_open, VAN_info, VAN_read, VAN_close, VAN_wopen, VAN_write, VAN_wclose },   // 62  VAN DOS/PC 1.00
    { QMT_about, QMT_is, QMT_open, QMT_info, QMT_read, QMT_close, QMT_wopen, QMT_write, QMT_wclose },   // 63  Quake Model Texture Gimex 1.00
    { MAD_about, MAD_is, MAD_open, MAD_info, MAD_read, MAD_close, MAD_wopen, MAD_write, MAD_wclose },   // 64  Madcow Movie 1.09
    { MAT_about, MAT_is, MAT_open, MAT_info, MAT_read, MAT_close, MAT_wopen, MAT_write, MAT_wclose },   // 65  Material 1.02
    { FX_about, FX_is, FX_open, FX_info, FX_read, FX_close, FX_wopen, FX_write, FX_wclose },   // 66  3Dfx Texture 1.05
    { PVR_about, PVR_is, PVR_open, PVR_info, PVR_read, PVR_close, PVR_wopen, PVR_write, PVR_wclose },   // 67  PowerVR Texture 1.01
    { UV_about, UV_is, UV_open, UV_info, UV_read, UV_close, UV_wopen, UV_write, UV_wclose },   // 68  Movie Gimex 1.05
    { 0 } };

GFILTERABOUT *FNIL_about(void);
GFILTERABOUT *MATH_about(void);
GFILTERABOUT *ZOOM_about(void);
GFILTERABOUT *GREY_about(void);
GFILTERABOUT *RECT_about(void);
GFILTERABOUT *XCOLOUR_about(void);
GFILTERABOUT *FILL_about(void);
GFILTERABOUT *INVERT_about(void);
GFILTERABOUT *PRETEN_about(void);
GFILTERABOUT *ROT_about(void);
GFILTERABOUT *WRAP_about(void);
GFILTERABOUT *ACOPY_about(void);
GFILTERABOUT *BLUR_about(void);
GFILTERABOUT *SHARPEN_about(void);
GFILTERABOUT *FLIP_about(void);
GFILTERABOUT *PALSORT_about(void);
GFILTERABOUT *SHRINK_about(void);
GFILTERABOUT *BLEND_about(void);
GFILTERABOUT *HSV_about(void);
GFILTERABOUT *LINE_about(void);
GFILTERABOUT *SCALE_about(void);
GFILTERABOUT *CREEP_about(void);
GFILTERABOUT *CSMAP_about(void);
GFILTERABOUT *EDGE_about(void);
GFILTERABOUT *RADFILL_about(void);
GFILTERABOUT *HSL_about(void);
GFILTERABOUT *FCHANMAP_about(void);
GFILTERABOUT *CONTRAST_about(void);
GFILTERABOUT *DEINTERLACE_about(void);
GFILTERABOUT *CHROMA_about(void);
GFILTERABOUT *SMOOTH_about(void);
GFILTERABOUT *ROTATE_about(void);
GFILTERABOUT *TEXTURE_about(void);
GFILTERABOUT *GAMMA_about(void);
GQUANTABOUT *QNIL_about(void);
GQUANTABOUT *STAT_about(void);
GQUANTABOUT *POPULAR_about(void);
GQUANTABOUT *HIGH_about(void);
GQUANTABOUT *MEDIUM_about(void);
GQUANTABOUT *LOW_about(void);
GQUANTABOUT *EXACT_about(void);
GQUANTABOUT *WU4D_about(void);
GQUANTABOUT *WU5_about(void);

// Filters and quantizers keep the original indices; only Crop, Remap, Size and Wu have their
// other entry points recovered.  A null entry point makes the GFILTER dispatchers return 0;
// the GQUANT dispatchers call without a check, so only Wu may be selected for use.
GFILTER gimexfilters[] = {
    { FNIL_about, 0, 0, 0, 0 },                                  //  0  FNil 1.01
    { MATH_about, 0, 0, 0, 0 },                                  //  1  Math 1.00
    { ZOOM_about, 0, 0, 0, 0 },                                  //  2  Zoom 1.05
    { GREY_about, 0, 0, 0, 0 },                                  //  3  Grey 1.03
    { RECT_about, 0, 0, 0, 0 },                                  //  4  Rect 1.02
    { CROP_about, CROP_open, CROP_info, CROP_read, CROP_close }, //  5  Crop 1.02
    { REMAP_about, REMAP_open, REMAP_info, REMAP_read, REMAP_close }, //  6  Remap 1.04
    { XCOLOUR_about, 0, 0, 0, 0 },                               //  7  Xcolour 1.02
    { FILL_about, 0, 0, 0, 0 },                                  //  8  Fill 1.04
    { INVERT_about, 0, 0, 0, 0 },                                //  9  Invert 1.00
    { PRETEN_about, 0, 0, 0, 0 },                                // 10  Preten 1.00
    { ROT_about, 0, 0, 0, 0 },                                   // 11  Rot 1.00
    { WRAP_about, 0, 0, 0, 0 },                                  // 12  Wrap 1.01
    { ACOPY_about, 0, 0, 0, 0 },                                 // 13  ACopy 1.02
    { BLUR_about, 0, 0, 0, 0 },                                  // 14  Blur 1.00
    { SHARPEN_about, 0, 0, 0, 0 },                               // 15  Sharpen 1.00
    { FLIP_about, 0, 0, 0, 0 },                                  // 16  Flip 1.04
    { PALSORT_about, 0, 0, 0, 0 },                               // 17  PalSort 1.08
    { SHRINK_about, 0, 0, 0, 0 },                                // 18  Shrink 1.00
    { BLEND_about, 0, 0, 0, 0 },                                 // 19  Blend 1.09
    { HSV_about, 0, 0, 0, 0 },                                   // 20  HSV 1.02
    { LINE_about, 0, 0, 0, 0 },                                  // 21  Line 1.00
    { SCALE_about, 0, 0, 0, 0 },                                 // 22  Scale 1.00
    { CREEP_about, 0, 0, 0, 0 },                                 // 23  Creep 1.00
    { CSMAP_about, 0, 0, 0, 0 },                                 // 24  CSMap 1.00
    { EDGE_about, 0, 0, 0, 0 },                                  // 25  Edge 1.03
    { RADFILL_about, 0, 0, 0, 0 },                               // 26  RadFill 1.02
    { HSL_about, 0, 0, 0, 0 },                                   // 27  HSL 1.03
    { FCHANMAP_about, 0, 0, 0, 0 },                              // 28  FChanmap 1.01
    { CONTRAST_about, 0, 0, 0, 0 },                              // 29  Contrast 1.00
    { DEINTERLACE_about, 0, 0, 0, 0 },                           // 30  Deinterlace 1.00
    { SIZE_about, SIZE_open, SIZE_info, SIZE_read, SIZE_close }, // 31  Size 1.05
    { CHROMA_about, 0, 0, 0, 0 },                                // 32  Chroma 1.00
    { SMOOTH_about, 0, 0, 0, 0 },                                // 33  Smooth 1.00
    { ROTATE_about, 0, 0, 0, 0 },                                // 34  Rotate 1.01
    { TEXTURE_about, 0, 0, 0, 0 },                               // 35  Texture 1.00
    { GAMMA_about, 0, 0, 0, 0 },                                 // 36  Gamma 1.00
    { 0 } };

GQUANT gimexquantizers[] = {
    { QNIL_about, 0, 0, 0 },                                     // 0  Nil 1.01
    { WU_about, WU_open, WU_add, WU_make },                      // 1  Wu 1.04
    { STAT_about, 0, 0, 0 },                                     // 2  Stat 1.10
    { POPULAR_about, 0, 0, 0 },                                  // 3  Popular 1.10
    { HIGH_about, 0, 0, 0 },                                     // 4  High 1.10
    { MEDIUM_about, 0, 0, 0 },                                   // 5  Medium 1.30
    { LOW_about, 0, 0, 0 },                                      // 6  Low 1.30
    { EXACT_about, 0, 0, 0 },                                    // 7  Exact 1.01
    { WU4D_about, 0, 0, 0 },                                     // 8  4D Wu 1.04
    { WU5_about, 0, 0, 0 },                                      // 9  Wu5 1.04
    { 0 } };
