# libpng 1.0.3 in gimme.dll

Unmodified files from `libpng-1.0.3.tar.gz`
(https://download.sourceforge.net/libpng/libpng-1.0.3.tar.gz, SHA-256
`7518163b4d66cfef59c047e33c26659eeda40f588fd356a158c6caa9344a3e44`); licence in `png.h` and
`README`. Only the reader objects are here (pngpread.c and the writer files are not used; the
binary links the writer for the PNG writer, still a boundary). The directory name is not attested.

- Version string "libpng version 1.0.3 - January 14, 1999" and "1.0.3" passed by the module.
- `PNG_USER_MEM_SUPPORTED` is defined by build.cmd (commented out in this pngconf.h): the module
  calls `png_create_read_struct_2` with galloc/gfree hooks; with it `sizeof(png_info)` 0xb8 and
  `sizeof(png_struct)` 0x21c match png_create_struct_2 (10199663).
