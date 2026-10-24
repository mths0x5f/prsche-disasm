// IJG 6a (jpeg/, compiled as C) as the JPG module uses it, and its GSTREAM data source.

#ifndef GIMEX_JPGSOURCE_H
#define GIMEX_JPGSOURCE_H

#include <stdio.h>

#include "gimex.h"

extern "C"
{
#include "jpeg/jpeglib.h"
#include "jpeg/jerror.h"
}

void jpeg_gstream_src(j_decompress_ptr cinfo, GSTREAM *stream);   // 10156980

#endif
