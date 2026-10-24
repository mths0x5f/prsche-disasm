/* jconfig.h for the IJG 6a library inside gimme.dll (3a43b0f6...).
 *
 * Recovered, not original: IJG ships no jconfig.h for Win32 in 6a and EA's own one is not
 * available.  The settings are the jconfig.doc defaults except where the binary says otherwise:
 *   - boolean stays int (jmorecfg.h default): the JPG module reads density_unit at cinfo+0x11c
 *     and X_density at +0x11e and passes structsize 0x1d0, which is the int-boolean layout.
 *   - DEFAULT_MAX_MEM is 10000000: jpeg_mem_init of jmemansi.c returns 0x989680 (101d45e1).
 *   - NO_GETENV is not defined: jinit_memory_mgr (101a1b40) reads "JPEGMEM".
 */

#define HAVE_PROTOTYPES
#define HAVE_UNSIGNED_CHAR
#define HAVE_UNSIGNED_SHORT
#undef CHAR_IS_UNSIGNED
#define HAVE_STDDEF_H
#define HAVE_STDLIB_H
#undef NEED_BSD_STRINGS
#undef NEED_SYS_TYPES_H
#undef NEED_FAR_POINTERS
#undef NEED_SHORT_EXTERNAL_NAMES
#undef INCOMPLETE_TYPES_BROKEN

#ifdef JPEG_INTERNALS

#undef RIGHT_SHIFT_IS_UNSIGNED
#define DEFAULT_MAX_MEM 10000000L

#endif /* JPEG_INTERNALS */
