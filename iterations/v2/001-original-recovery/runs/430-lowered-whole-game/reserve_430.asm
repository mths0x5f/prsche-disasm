; Run 430: reserves 0x00401000..0x006e3000 inside the host EXE (based at 0x00400000).
; Sorting as .text$a puts it first in .text, at RVA 0x1000; the runtime copies the original
; Porsche.exe sections over it and makes it non-executable.
.686
.model flat
reserve SEGMENT ALIGN(4096) READ EXECUTE ALIAS(".text$a") 'CODE'
PUBLIC _reserve430
_reserve430 db 2E2000h dup(0)
reserve ENDS
END
