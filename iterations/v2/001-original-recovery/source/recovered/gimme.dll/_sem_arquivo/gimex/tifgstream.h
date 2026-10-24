// libtiff 3.4 (tiff/, compiled as C) over GSTREAM: the platform layer of tifgstream.cpp.

#ifndef GIMEX_TIFGSTREAM_H
#define GIMEX_TIFGSTREAM_H

#include "gimex.h"

struct tiff;

struct tiff *TIFFOpenGStream(const char *name, GSTREAM *stream, const char *mode);   // 1013961d

#endif
