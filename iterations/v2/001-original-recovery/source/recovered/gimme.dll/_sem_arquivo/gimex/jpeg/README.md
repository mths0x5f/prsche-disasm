# IJG JPEG 6a in gimme.dll

Unmodified files from `jpegsrc.v6a.tar.gz` (https://www.ijg.org/files/jpegsrc.v6a.tar.gz,
SHA-256 `0e963fdd29d5049f61f3dc137bdc9437473a0ad505dbcfc8925f0fcad46c5929`); the licence is in
`README` (LEGAL ISSUES). Only the decompressor and common objects the JPG reader uses are here; the
binary also links the compressor (JPG writer, still a boundary) and a second IJG copy near
`10203440` that is not traced.

- The directory name is not attested by the binary.
- `jconfig.h` is recovered, not original (see its header: int boolean, `DEFAULT_MAX_MEM`
  10000000, jmemansi.c).
- `jdatasrc.c` is not used: EA's GSTREAM copy of it is `../jpgsource.cpp` (10156980).
- Version: JVERSION "6a  7-Feb-96" in the message table; `gimme_oracle jpeglib` compares the
  message table and 684 decodes (12 decoder modes) with the original's own IJG at its VAs.
